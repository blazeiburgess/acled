"""Authentication module for ACLED API.

This module provides multiple authentication strategies for the ACLED API:
- Legacy key/email authentication
- OAuth token-based authentication
- Cookie-based session authentication

The module automatically selects the best available method, preferring
modern authentication (OAuth/Cookie) over legacy when possible.
"""

import os
import platform
import tempfile
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from os import environ
import json
import warnings

import requests
from requests.exceptions import RequestException

from acled.exceptions import AcledMissingAuthError, ApiError
from acled.log import AcledLogger


class AuthMethod(ABC):
    """Abstract base class for ACLED authentication methods."""

    @abstractmethod
    def authenticate(self, session: requests.Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply authentication to request parameters or session.

        Args:
            session: The requests session to potentially modify
            params: Request parameters to potentially modify

        Returns:
            Modified parameters dictionary
        """

    @abstractmethod
    def refresh_if_needed(self, session: requests.Session) -> None:
        """Refresh authentication if necessary (e.g., for expired tokens).

        Args:
            session: The requests session to potentially update
        """

    @abstractmethod
    def force_refresh(self, session: requests.Session) -> None:
        """Force a credential refresh (e.g., after a 401/403 response).

        Unlike refresh_if_needed which checks expiry times, this method
        unconditionally refreshes credentials.

        Args:
            session: The requests session to update with new credentials
        """

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if the authentication is currently valid.

        Returns:
            True if authenticated and valid, False otherwise
        """


class LegacyKeyEmailAuth(AuthMethod):
    """Legacy authentication using API key and email.

    .. deprecated::
        Legacy key/email authentication is deprecated and will be removed in a
        future release. ACLED no longer supports API key/email query parameter
        authentication. Use OAuth (``ACLED_USERNAME``/``ACLED_PASSWORD``) instead.
    """

    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        """Initialize legacy authentication.

        Args:
            api_key: ACLED API key (falls back to ACLED_API_KEY env var)
            email: Email associated with API key (falls back to ACLED_EMAIL env var)

        Raises:
            AcledMissingAuthError: If api_key or email is missing
        """
        warnings.warn(
            "Legacy key/email authentication is deprecated and will be removed "
            "in a future release. ACLED no longer supports API key/email query "
            "parameter authentication. Use OAuth with ACLED_USERNAME and "
            "ACLED_PASSWORD environment variables instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.api_key = api_key if api_key else environ.get("ACLED_API_KEY")
        if not self.api_key:
            raise AcledMissingAuthError("API key is required for legacy authentication")

        self.email = email if email else environ.get("ACLED_EMAIL")
        if not self.email:
            raise AcledMissingAuthError("Email is required for legacy authentication")

        self.log = AcledLogger().get_logger()
        self.log.info("Initialized legacy key/email authentication")

    def authenticate(self, session: requests.Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add API key and email to request parameters.

        Args:
            session: Not used in legacy auth
            params: Request parameters to modify

        Returns:
            Parameters with added authentication
        """
        params['key'] = self.api_key
        params['email'] = self.email
        return params

    def refresh_if_needed(self, session: requests.Session) -> None:
        """No refresh needed for legacy authentication."""

    def force_refresh(self, session: requests.Session) -> None:
        """No refresh possible for legacy authentication (static credentials)."""

    def is_authenticated(self) -> bool:
        """Check if API key and email are present.

        Returns:
            True if both api_key and email are set
        """
        return bool(self.api_key and self.email)


class OAuthTokenAuth(AuthMethod):
    """OAuth token-based authentication for ACLED API.

    This authentication method uses OAuth2 password grant flow to obtain
    access tokens that are valid for 24 hours, with refresh tokens valid
    for 14 days. The token is included in the Authorization header.
    """

    TOKEN_ENDPOINT = "https://acleddata.com/oauth/token"
    CLIENT_ID = "acled"
    GRANT_TYPE_PASSWORD = "password"
    GRANT_TYPE_REFRESH = "refresh_token"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token_file: Optional[str] = None
    ):
        """Initialize OAuth authentication.

        Args:
            username: ACLED username/email (falls back to env vars)
            password: ACLED password (falls back to ACLED_PASSWORD env var)
            token_file: Optional file path to save/load tokens for persistence

        Raises:
            AcledMissingAuthError: If username/password are not provided
        """
        # Username can come from ACLED_USERNAME or ACLED_EMAIL (interchangeable)
        self.username = (
            username if username else
            environ.get("ACLED_USERNAME") or environ.get("ACLED_EMAIL")
        )
        self.password = password if password else environ.get("ACLED_PASSWORD")
        self.token_file = token_file

        # Token storage
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.access_token_expires_at: Optional[datetime] = None
        self.refresh_token_expires_at: Optional[datetime] = None

        self.log = AcledLogger().get_logger()

        # Validate we have credentials
        if not (self.username and self.password):
            raise AcledMissingAuthError(
                "OAuth authentication requires username/email and password"
            )

        # Try to load existing tokens if token_file specified
        if self.token_file:
            try:
                self.load_tokens(self.token_file)
                self.log.info("Loaded existing OAuth tokens from file")
            except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as e:
                self.log.debug("Could not load tokens from %s: %s", self.token_file, e)

        # If we don't have valid tokens, obtain them
        if not self.is_authenticated():
            self._obtain_token()

        self.log.info("Initialized OAuth token authentication")

    def _obtain_token(self) -> None:
        """Obtain new access and refresh tokens using credentials.

        Raises:
            ApiError: If token request fails
        """
        self.log.info("Obtaining new OAuth tokens")

        data = {
            "grant_type": self.GRANT_TYPE_PASSWORD,
            "client_id": self.CLIENT_ID,
            "username": self.username,
            "password": self.password
        }

        try:
            response = requests.post(
                self.TOKEN_ENDPOINT,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response.raise_for_status()

            token_data = response.json()
            self._process_token_response(token_data)

        except RequestException as e:
            self.log.error("Failed to obtain OAuth token: %s", str(e))
            raise ApiError(f"Failed to obtain OAuth token: {str(e)}") from e

    def _refresh_access_token(self) -> None:
        """Refresh the access token using the refresh token.

        Raises:
            ApiError: If refresh fails
        """
        if not self.refresh_token:
            raise ApiError("No refresh token available")

        self.log.info("Refreshing OAuth access token")

        data = {
            "grant_type": self.GRANT_TYPE_REFRESH,
            "client_id": self.CLIENT_ID,
            "refresh_token": self.refresh_token
        }

        try:
            response = requests.post(
                self.TOKEN_ENDPOINT,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response.raise_for_status()

            token_data = response.json()
            self._process_token_response(token_data)

        except RequestException as e:
            self.log.error("Failed to refresh OAuth token: %s", str(e))
            # If refresh fails, try to get new token with credentials
            if self.username and self.password:
                self.log.info("Refresh failed, obtaining new token with credentials")
                self._obtain_token()
            else:
                raise ApiError(f"Failed to refresh OAuth token: {str(e)}") from e

    def _process_token_response(self, token_data: Dict[str, Any]) -> None:
        """Process and store token response data.

        Args:
            token_data: Response from token endpoint
        """
        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token", self.refresh_token)

        # Calculate expiry times
        now = datetime.now()

        # Access token expires in 24 hours (minus 5 minutes buffer)
        expires_in = token_data.get("expires_in", 86400)  # Default 24 hours
        self.access_token_expires_at = now + timedelta(seconds=expires_in - 300)

        # Refresh token expires in 14 days (minus 1 hour buffer)
        refresh_expires_in = token_data.get("refresh_token_expires_in", 1209600)  # Default 14 days
        self.refresh_token_expires_at = now + timedelta(seconds=refresh_expires_in - 3600)

        self.log.debug("Token obtained, expires at %s", self.access_token_expires_at)
        self._persist_tokens()

    def _persist_tokens(self) -> None:
        """Save tokens to disk if a token file is configured."""
        if self.token_file:
            self.save_tokens(self.token_file)

    def authenticate(self, session: requests.Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add Bearer token to session headers.

        Args:
            session: The requests session to modify
            params: Request parameters (not modified for OAuth)

        Returns:
            Unmodified parameters (auth is in headers)
        """
        if self.access_token:
            session.headers["Authorization"] = f"Bearer {self.access_token}"
        return params

    def refresh_if_needed(self, session: requests.Session) -> None:
        """Refresh token if it's expired or about to expire.

        Args:
            session: The requests session to update with new token
        """
        if not self.access_token_expires_at:
            # If we don't know expiry, assume token needs refresh
            if self.refresh_token:
                self._refresh_access_token()
            elif self.username and self.password:
                self._obtain_token()
            return

        now = datetime.now()

        # Check if access token needs refresh
        if now >= self.access_token_expires_at:
            if self.refresh_token and (
                not self.refresh_token_expires_at or now < self.refresh_token_expires_at
            ):
                self._refresh_access_token()
            elif self.username and self.password:
                self._obtain_token()
            else:
                raise ApiError("OAuth token expired and cannot be refreshed")

        # Update session header with current token
        if self.access_token:
            session.headers["Authorization"] = f"Bearer {self.access_token}"

    def force_refresh(self, session: requests.Session) -> None:
        """Force token refresh after a 401/403 response.

        Tries refresh token first, falls back to password grant.

        Args:
            session: The requests session to update with new token
        """
        self.log.info("Forcing OAuth token refresh")
        if self.refresh_token:
            try:
                self._refresh_access_token()
            except (ApiError, RequestException):
                if self.username and self.password:
                    self._obtain_token()
                else:
                    raise
        elif self.username and self.password:
            self._obtain_token()
        else:
            raise ApiError("Cannot refresh OAuth token: no refresh token or credentials")

        if self.access_token:
            session.headers["Authorization"] = f"Bearer {self.access_token}"

    def is_authenticated(self) -> bool:
        """Check if we have a valid access token.

        Returns:
            True if access token exists and is not expired
        """
        if not self.access_token:
            return False

        if not self.access_token_expires_at:
            # Assume valid if we have a token but don't know expiry
            return True

        return datetime.now() < self.access_token_expires_at

    def get_tokens(self) -> Tuple[Optional[str], Optional[str]]:
        """Get current access and refresh tokens.

        Returns:
            Tuple of (access_token, refresh_token)
        """
        return self.access_token, self.refresh_token

    def save_tokens(self, filepath: str) -> None:
        """Save tokens to a JSON file with restricted permissions.

        Args:
            filepath: Path to save tokens to
        """

        token_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "access_token_expires_at": (
                self.access_token_expires_at.isoformat()
                if self.access_token_expires_at else None
            ),
            "refresh_token_expires_at": (
                self.refresh_token_expires_at.isoformat()
                if self.refresh_token_expires_at else None
            )
        }

        # Atomic write: write to temp file, then rename
        dirpath = os.path.dirname(os.path.abspath(filepath))
        fd, tmp_path = tempfile.mkstemp(dir=dirpath, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, indent=2)
            # Set restrictive permissions before rename (Unix)
            if platform.system() != "Windows":
                os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, filepath)
        except Exception:
            # Clean up temp file on failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        self.log.info("Tokens saved to %s", filepath)

    def load_tokens(self, filepath: str) -> None:
        """Load tokens from a JSON file.

        Args:
            filepath: Path to load tokens from
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            token_data = json.load(f)

        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token")

        # Parse expiry times
        if token_data.get("access_token_expires_at"):
            self.access_token_expires_at = datetime.fromisoformat(
                token_data["access_token_expires_at"]
            )

        if token_data.get("refresh_token_expires_at"):
            self.refresh_token_expires_at = datetime.fromisoformat(
                token_data["refresh_token_expires_at"]
            )

        self.log.info("Tokens loaded from %s", filepath)


class CookieAuth(AuthMethod):
    """Cookie-based session authentication for ACLED API.

    This method uses session cookies obtained by logging into the ACLED
    website. It provides CSRF and logout tokens for session management.
    """

    LOGIN_ENDPOINT = "https://acleddata.com/user/login?_format=json"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize cookie authentication.

        Args:
            username: ACLED username/email (falls back to env vars)
            password: ACLED password (falls back to ACLED_PASSWORD env var)

        Raises:
            AcledMissingAuthError: If username/password are not provided
        """
        # Username can come from ACLED_USERNAME or ACLED_EMAIL (interchangeable)
        self.username = (
            username if username else
            environ.get("ACLED_USERNAME") or environ.get("ACLED_EMAIL")
        )
        self.password = password if password else environ.get("ACLED_PASSWORD")

        # Session data storage
        self.csrf_token: Optional[str] = None
        self.logout_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.cookies: Optional[Dict[str, str]] = None

        self.log = AcledLogger().get_logger()

        # Validate we have credentials
        if not (self.username and self.password):
            raise AcledMissingAuthError(
                "Cookie authentication requires username/email and password"
            )

        # Obtain session on initialization
        self._login()

        self.log.info("Initialized cookie-based authentication")

    def _login(self) -> None:
        """Login to ACLED and obtain session cookies.

        Raises:
            ApiError: If login fails
        """
        self.log.info("Logging in to ACLED for cookie-based auth")

        data = {
            "name": self.username,
            "pass": self.password
        }

        try:
            response = requests.post(
                self.LOGIN_ENDPOINT,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            auth_data = response.json()

            # Store authentication data
            self.csrf_token = auth_data.get("csrf_token")
            self.logout_token = auth_data.get("logout_token")
            self.user_id = str(auth_data.get("uid", ""))

            # Store cookies from response
            self.cookies = dict(response.cookies)

            self.log.debug("Login successful, obtained CSRF token and session cookies")

        except RequestException as e:
            self.log.error("Failed to login for cookie auth: %s", str(e))
            raise ApiError(f"Failed to login for cookie auth: {str(e)}") from e

    def authenticate(self, session: requests.Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply session cookies to the request session.

        Args:
            session: The requests session to modify
            params: Request parameters (not modified for cookie auth)

        Returns:
            Unmodified parameters (auth is in cookies)
        """
        if self.cookies:
            session.cookies.update(self.cookies)

        # Add CSRF token to headers if available
        if self.csrf_token:
            session.headers["X-CSRF-Token"] = self.csrf_token

        return params

    def refresh_if_needed(self, session: requests.Session) -> None:
        """Re-login if session appears to be invalid.

        For cookie auth, we don't have explicit expiry info,
        so we may need to retry login on auth failures.

        Args:
            session: The requests session to update
        """
        # Cookie sessions typically last for browser session
        # We'll handle re-login on 401/403 errors in the client
        if self.cookies:
            session.cookies.update(self.cookies)

        if self.csrf_token:
            session.headers["X-CSRF-Token"] = self.csrf_token

    def force_refresh(self, session: requests.Session) -> None:
        """Force re-login after a 401/403 response.

        Args:
            session: The requests session to update with new cookies
        """
        self.log.info("Forcing cookie re-login")
        self._login()

        if self.cookies:
            session.cookies.update(self.cookies)
        if self.csrf_token:
            session.headers["X-CSRF-Token"] = self.csrf_token

    def is_authenticated(self) -> bool:
        """Check if we have valid session cookies.

        Returns:
            True if cookies and tokens are present
        """
        return bool(self.cookies and self.csrf_token)

    def get_tokens(self) -> Dict[str, Optional[str]]:
        """Get current session tokens.

        Returns:
            Dictionary with csrf_token, logout_token, and user_id
        """
        return {
            "csrf_token": self.csrf_token,
            "logout_token": self.logout_token,
            "user_id": self.user_id
        }


class AuthFactory:
    """Factory for creating authentication method instances."""

    @staticmethod
    def create_auth(
        method: str = "auto",
        **kwargs
    ) -> AuthMethod:
        """Create an authentication method instance.

        Args:
            method: Authentication method ('legacy', 'oauth', 'cookie', or 'auto')
            **kwargs: Method-specific parameters

        Returns:
            AuthMethod instance

        Raises:
            ValueError: If method is not recognized
            AcledMissingAuthError: If required credentials are missing
        """
        method = method.lower()

        if method == "legacy":
            return LegacyKeyEmailAuth(
                api_key=kwargs.get("api_key"),
                email=kwargs.get("email")
            )
        if method == "oauth":
            return OAuthTokenAuth(
                username=kwargs.get("username") or kwargs.get("email"),
                password=kwargs.get("password"),
                token_file=kwargs.get("token_file")
            )
        if method == "cookie":
            return CookieAuth(
                username=kwargs.get("username") or kwargs.get("email"),
                password=kwargs.get("password")
            )
        if method == "auto":
            # Auto-detect best method based on available credentials
            return AuthFactory._auto_detect(**kwargs)
        raise ValueError(f"Unknown authentication method: {method}")

    @staticmethod
    def _auto_detect(**kwargs) -> AuthMethod:
        """Auto-detect the best authentication method based on available credentials.

        Priority order:
        1. OAuth (if username/password available)
        2. Cookie (if OAuth fails but username/password available)
        3. Legacy (if only API key/email available)

        Args:
            **kwargs: Credential parameters

        Returns:
            AuthMethod instance

        Raises:
            AcledMissingAuthError: If no valid credentials found
        """
        # Check what credentials we have
        username = kwargs.get("username") or kwargs.get("email")
        password = kwargs.get("password")
        api_key = kwargs.get("api_key")
        email = kwargs.get("email")

        # Prefer OAuth if we have username/password
        if username and password:
            last_error: Optional[Exception] = None
            try:
                return OAuthTokenAuth(
                    username=username,
                    password=password,
                    token_file=kwargs.get("token_file")
                )
            except AcledMissingAuthError:
                pass  # Missing creds — try next method
            except ApiError as e:
                if getattr(e, 'status_code', None) in (401, 403):
                    raise  # Bad credentials — don't silently try next method
                last_error = e

            try:
                return CookieAuth(username=username, password=password)
            except AcledMissingAuthError:
                pass
            except ApiError as e:
                if getattr(e, 'status_code', None) in (401, 403):
                    raise
                last_error = e

            # Both failed — fall back to legacy if available
            if api_key and email:
                return LegacyKeyEmailAuth(api_key=api_key, email=email)
            if last_error is not None:
                raise last_error
            raise AcledMissingAuthError(
                "OAuth and Cookie authentication failed. "
                "No legacy credentials available as fallback."
            )

        # Use legacy if only API key/email available
        elif api_key and email:
            return LegacyKeyEmailAuth(api_key=api_key, email=email)

        else:
            raise AcledMissingAuthError(
                "No valid authentication credentials provided. "
                "Need either username/password or api_key/email."
            )

    @staticmethod
    def from_environment(method: Optional[str] = None) -> AuthMethod:
        """Create authentication from environment variables.

        Environment variables:
        - ACLED_USERNAME or ACLED_EMAIL: Username/email (interchangeable)
        - ACLED_PASSWORD: Password for OAuth/Cookie auth
        - ACLED_API_KEY: API key for legacy auth
        - ACLED_EMAIL: Email for legacy auth (if not using as username)

        Args:
            method: Force specific method, or auto-detect from env vars

        Returns:
            AuthMethod instance

        Raises:
            AcledMissingAuthError: If no valid auth configuration found
        """
        # Gather credentials from environment
        username = environ.get("ACLED_USERNAME") or environ.get("ACLED_EMAIL")
        password = environ.get("ACLED_PASSWORD")
        api_key = environ.get("ACLED_API_KEY")
        email = environ.get("ACLED_EMAIL")

        # If method specified, use it
        if method and method != "auto":
            return AuthFactory.create_auth(
                method,
                username=username,
                password=password,
                api_key=api_key,
                email=email
            )

        # Auto-detect based on available environment variables
        # Priority: OAuth/Cookie > Legacy
        if username and password:
            # Try OAuth first, fall back to cookie only if the auth method
            # is unavailable (not if credentials are invalid)
            last_error: Optional[Exception] = None
            try:
                return AuthFactory.create_auth(
                    "oauth",
                    username=username,
                    password=password
                )
            except AcledMissingAuthError:
                pass
            except ApiError as e:
                if getattr(e, 'status_code', None) in (401, 403):
                    raise
                last_error = e

            try:
                return AuthFactory.create_auth(
                    "cookie",
                    username=username,
                    password=password
                )
            except AcledMissingAuthError:
                pass
            except ApiError as e:
                if getattr(e, 'status_code', None) in (401, 403):
                    raise
                last_error = e

            if api_key and email:
                return AuthFactory.create_auth(
                    "legacy",
                    api_key=api_key,
                    email=email
                )
            if last_error is not None:
                raise last_error
            raise AcledMissingAuthError(
                "OAuth and Cookie authentication failed from environment. "
                "No legacy credentials available as fallback."
            )

        elif api_key and email:
            return AuthFactory.create_auth(
                "legacy",
                api_key=api_key,
                email=email
            )

        else:
            raise AcledMissingAuthError(
                "No authentication credentials found in environment. "
                "Set either ACLED_USERNAME/ACLED_PASSWORD for modern auth or "
                "ACLED_API_KEY/ACLED_EMAIL for legacy auth."
            )
