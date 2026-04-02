"""Base HTTP client module for the ACLED API.

This module provides a base HTTP client class that handles common functionality
for all ACLED API clients, including authentication, request handling, retries,
error handling, and parameter processing. It serves as the foundation for all
specialized client classes that interact with specific ACLED API endpoints.
"""

from typing import Any, Dict, Optional, TypeVar, Union
from os import environ
import time
import random
from datetime import date, datetime
import warnings

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

from acled.exceptions import (
    ApiError, NetworkError, TimeoutError,
    RetryError, RateLimitError, ServerError, ClientError
)
from acled.log import AcledLogger
from acled.auth import AuthMethod, AuthFactory, LegacyKeyEmailAuth

T = TypeVar('T')

_VALID_AUTH_METHODS = {'auto', 'oauth', 'cookie', 'legacy'}
_SENSITIVE_KEYS = {'key', 'api_key', 'email', 'password', 'access_token', 'refresh_token'}


def _redact_params(params):
    """Return a copy of params with sensitive values replaced by '***'."""
    if not isinstance(params, dict):
        return params
    return {k: ('***' if k in _SENSITIVE_KEYS else v) for k, v in params.items()}


def _validate_auth_method_arg(auth_method):
    """Detect legacy positional constructor usage and raise a helpful error."""
    if (isinstance(auth_method, str)
            and not isinstance(auth_method, AuthMethod)
            and auth_method.lower() not in _VALID_AUTH_METHODS):
        raise TypeError(
            f"Unknown auth method '{auth_method}'. "
            "The positional (api_key, email) constructor has been removed. "
            "Use keyword arguments instead: "
            "AcledClient(api_key='...', email='...') or "
            "AcledClient(auth_method='legacy', api_key='...', email='...')"
        )


def _handle_legacy_positional_args(auth_method, auth_kwargs):
    """Detect and handle legacy positional (api_key, email) constructor usage.

    Returns:
        (auth_method, auth_kwargs) — possibly rewritten for legacy auth, or
        the original values if no legacy pattern was detected.
    """
    email = auth_kwargs.pop("_legacy_email", None)
    if email is not None and auth_method is not None:
        # Two positional args: AcledClient("api_key", "email@example.com")
        warnings.warn(
            "Positional (api_key, email) constructor is deprecated. "
            "Use keyword arguments instead: "
            "AcledClient(api_key='...', email='...')",
            DeprecationWarning,
            stacklevel=4
        )
        auth_kwargs["api_key"] = auth_method
        auth_kwargs["email"] = email
        return None, auth_kwargs
    return auth_method, auth_kwargs


class BaseHttpClient:
    """
    A base HTTP client that provides basic GET and POST request functionality.
    """
    BASE_URL = environ.get("ACLED_API_HOST", "https://acleddata.com/api")
    # Default retry settings
    MAX_RETRIES = int(environ.get("ACLED_MAX_RETRIES", "3"))
    RETRY_BACKOFF_FACTOR = float(environ.get("ACLED_RETRY_BACKOFF_FACTOR", "0.5"))
    RETRY_STATUS_CODES = [429, 500, 502, 503, 504]  # Rate limit and server errors
    DEFAULT_TIMEOUT = int(environ.get("ACLED_REQUEST_TIMEOUT", "30"))  # seconds

    def __init__(self, auth_method: Optional[Union[str, AuthMethod]] = None, _legacy_email: Optional[str] = None, **auth_kwargs):
        """Initialize the base HTTP client with authentication.

        Args:
            auth_method: Authentication method (AuthMethod instance, method name, or None for auto)
            _legacy_email: Deprecated positional email arg for backward compatibility
            **auth_kwargs: Authentication parameters (username, password, api_key, email, etc.)
        """
        self.log = AcledLogger().get_logger()

        auth_kwargs["_legacy_email"] = _legacy_email
        auth_method, auth_kwargs = _handle_legacy_positional_args(auth_method, auth_kwargs)
        _validate_auth_method_arg(auth_method)

        # Simple auth handling - delegate all logic to AuthFactory
        if isinstance(auth_method, AuthMethod):
            self.auth = auth_method
        elif auth_method:
            self.auth = AuthFactory.create_auth(auth_method, **auth_kwargs)
        elif auth_kwargs:
            self.auth = AuthFactory.create_auth("auto", **auth_kwargs)
        else:
            self.auth = AuthFactory.from_environment()

        # Legacy attributes for backward compatibility
        if isinstance(self.auth, LegacyKeyEmailAuth):
            self.api_key = self.auth.api_key
            self.email = self.auth.email
        else:
            self.api_key = None
            self.email = None

        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def process_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process and prepare parameters for API requests.

        Args:
            params: Dictionary of parameters to process

        Returns:
            Processed parameters dictionary
        """
        processed_params = params.copy() if params else {}

        # Process parameters to handle different types
        for key, value in list(processed_params.items()):
            if value is None:
                # Remove None values
                del processed_params[key]
            elif isinstance(value, date) and not isinstance(value, datetime):
                # Format date objects
                processed_params[key] = value.strftime('%Y-%m-%d')
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                # Convert numbers to strings
                processed_params[key] = str(value)
            elif hasattr(value, 'value'):
                # Handle enum types
                processed_params[key] = value.value

        # Apply authentication to parameters
        processed_params = self.auth.authenticate(self.session, processed_params)

        return processed_params

    def _request_with_retries(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry logic for transient failures.

        Args:
            method: HTTP method ('get' or 'post')
            endpoint: API endpoint
            params: Query parameters for GET requests
            data: JSON data for POST requests
            timeout: Request timeout in seconds

        Returns:
            API response as dictionary

        Raises:
            NetworkError: For network connectivity issues
            TimeoutError: When the request times out
            RateLimitError: When API rate limits are exceeded
            ServerError: For 5xx server errors
            ClientError: For 4xx client errors
            RetryError: When maximum retry attempts are exhausted
            ApiError: For other API-related errors
        """
        url = f"{self.BASE_URL}{endpoint}"
        timeout = timeout or self.DEFAULT_TIMEOUT

        # Refresh authentication if needed (non-fatal — will retry via 401 path)
        try:
            self.auth.refresh_if_needed(self.session)
        except Exception as e:
            self.log.warning("Pre-request auth refresh failed: %s", str(e))

        processed_params = self.process_params(params) if method.lower() == 'get' else None
        processed_data = self.process_params(data) if method.lower() == 'post' else None

        # Log request details
        self.log.info("Making %s request to %s", method.upper(), endpoint)
        if processed_params:
            self.log.debug("Query Parameters: %s", _redact_params(processed_params))
        if processed_data:
            self.log.debug("Request Data: %s", _redact_params(processed_data))

        retries = 0
        last_exception = None
        auth_refreshed = False

        while retries <= self.MAX_RETRIES:
            try:
                if retries > 0:
                    # Calculate backoff time with jitter
                    backoff = self.RETRY_BACKOFF_FACTOR * (2 ** (retries - 1))
                    jitter = random.uniform(0, 0.1 * backoff)  # 10% jitter
                    sleep_time = backoff + jitter

                    self.log.warning(
                        "Retry attempt %s/%s for %s after %.2fs",
                        retries, self.MAX_RETRIES, endpoint, sleep_time
                    )
                    time.sleep(sleep_time)

                if method.lower() == 'get':
                    response = self.session.get(url, params=processed_params, timeout=timeout)
                else:  # post
                    response = self.session.post(url, json=processed_data, timeout=timeout)

                # Log response status
                self.log.debug("Response status: %s", response.status_code)

                # Check for rate limiting
                if response.status_code == 429:
                    if retries >= self.MAX_RETRIES:
                        raise RateLimitError(
                            f"Rate limited after {self.MAX_RETRIES} retries"
                        )
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.log.warning("Rate limited. Retry after %ss", retry_after)
                    time.sleep(retry_after)
                    retries += 1
                    continue

                # Handle auth errors with token refresh (once)
                if response.status_code in (401, 403) and not auth_refreshed:
                    self.log.warning(
                        "Auth error (%s), refreshing credentials and retrying",
                        response.status_code
                    )
                    try:
                        self.auth.force_refresh(self.session)
                        processed_params = self.process_params(params) if method.lower() == 'get' else None
                        processed_data = self.process_params(data) if method.lower() == 'post' else None
                    except Exception as e:
                        self.log.warning("Auth refresh failed: %s", str(e))
                        last_exception = ApiError(f"Auth refresh failed: {str(e)}")
                    auth_refreshed = True
                    retries += 1
                    continue

                # Raise HTTPError for 4xx/5xx status codes
                response.raise_for_status()

                # Log success
                self.log.info("Request to %s successful", endpoint)
                self.log.debug("Response content length: %s", len(response.content))

                return response.json()

            except Timeout as e:
                self.log.error("Request timeout: %s", str(e))
                last_exception = TimeoutError(f"Request timed out: {str(e)}")
            except ConnectionError as e:
                self.log.error("Network error: %s", str(e))
                last_exception = NetworkError(f"Network connection error: {str(e)}")
            except HTTPError as e:
                status_code = getattr(getattr(e, "response", None), "status_code", None)
                self.log.error("HTTP error: %s (status code: %s)", str(e), status_code)
                if status_code and 500 <= status_code < 600:
                    last_exception = ServerError(f"Server error ({status_code}): {str(e)}")
                elif status_code and 400 <= status_code < 500:
                    raise ClientError(f"Client error ({status_code}): {str(e)}") from e
                else:
                    raise ApiError(f"HTTP error ({status_code}): {str(e)}") from e
            except RequestException as e:
                self.log.error("Request error: %s", str(e))
                last_exception = ApiError(f"Request error: {str(e)}")
            except Exception as e:
                self.log.error("Unexpected error: %s", str(e))
                raise ApiError(f"Unexpected error: {str(e)}") from e

            retries += 1

        # If we've exhausted retries, raise the last exception or RetryError
        if last_exception:
            raise RetryError(f"Max retries ({self.MAX_RETRIES}) exceeded. Last error: {str(last_exception)}")
        raise RetryError(f"Max retries ({self.MAX_RETRIES}) exceeded.")

    def _get(
            self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the API with retry logic.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary
        """
        return self._request_with_retries('get', endpoint, params=params)

    def _post(
            self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request to the API with retry logic.

        Args:
            endpoint: API endpoint
            data: JSON data

        Returns:
            API response as dictionary
        """
        return self._request_with_retries('post', endpoint, data=data)
