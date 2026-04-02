"""CLI configuration utilities."""

import os
from typing import Optional, Dict, Any

from acled.cli.utils.auth import CredentialManager, AuthenticationError
from acled.auth import AuthMethod, AuthFactory
from acled.exceptions import AcledMissingAuthError


_NOT_LOADED = object()


class CLIConfig:
    """Configuration class for CLI operations."""

    def __init__(self, args):
        self.args = args
        self.verbose = getattr(args, 'verbose', False)
        self.quiet = getattr(args, 'quiet', False)
        self.format = getattr(args, 'format', 'json')
        self.output_file = getattr(args, 'output', None)

        # Authentication (backward compatibility)
        self.api_key = self._get_api_key()
        self.email = self._get_email()

        # Deferred authentication - constructed on first access
        self._auth_method = _NOT_LOADED
        self._auth_kwargs = _NOT_LOADED

    @property
    def auth_method(self) -> Optional[AuthMethod]:
        """Get authentication method, constructed lazily on first access."""
        if self._auth_method is _NOT_LOADED:
            self._auth_method = self._get_auth_method()
        return self._auth_method

    @auth_method.setter
    def auth_method(self, value):
        self._auth_method = value

    @property
    def auth_kwargs(self) -> Dict[str, Any]:
        """Get authentication kwargs, constructed lazily on first access."""
        if self._auth_kwargs is _NOT_LOADED:
            self._auth_kwargs = self._get_auth_kwargs()
        return self._auth_kwargs

    def _get_api_key(self) -> Optional[str]:
        """Get API key from arguments, environment, or stored credentials."""
        # Priority: CLI args > environment > stored credentials
        api_key = getattr(self.args, 'api_key', None)
        if api_key:
            return api_key

        api_key = os.environ.get('ACLED_API_KEY')
        if api_key:
            return api_key

        # Try to get from stored credentials
        try:
            credential_manager = CredentialManager()
            if credential_manager.has_stored_credentials():
                creds = credential_manager.get_credentials()
                if creds.get('auth_method') == 'legacy':
                    return creds.get('api_key')
                return None
        except AuthenticationError:
            pass

        return None

    def _get_email(self) -> Optional[str]:
        """Get email from arguments, environment, or stored credentials."""
        # Priority: CLI args > environment > stored credentials
        email = getattr(self.args, 'email', None)
        if email:
            return email

        email = os.environ.get('ACLED_EMAIL')
        if email:
            return email

        # Try to get from stored credentials
        try:
            credential_manager = CredentialManager()
            if credential_manager.has_stored_credentials():
                creds = credential_manager.get_credentials()
                if creds.get('auth_method') == 'legacy':
                    return creds.get('email')
        except AuthenticationError:
            pass

        return None

    def _get_auth_method(self) -> Optional[AuthMethod]:
        """Get authentication method from CLI args, environment, or stored credentials."""
        # If CLI args have api_key/email, use legacy auth
        if getattr(self.args, 'api_key', None) or getattr(self.args, 'email', None):
            return None  # Will use legacy auth with api_key/email

        # Use AuthFactory.from_environment() for consistent precedence with the library
        try:
            return AuthFactory.from_environment()
        except AcledMissingAuthError:
            pass

        # Try to get from stored credentials
        try:
            credential_manager = CredentialManager()
            if credential_manager.has_stored_credentials():
                creds = credential_manager.get_credentials()
                auth_method = creds.get('auth_method', 'legacy')

                if auth_method == 'oauth':
                    return AuthFactory.create_auth(
                        'oauth',
                        username=creds.get('username'),
                        password=creds.get('password'),
                        token_file=credential_manager.get_token_file()
                    )
                elif auth_method == 'cookie':
                    return AuthFactory.create_auth(
                        'cookie',
                        username=creds.get('username'),
                        password=creds.get('password')
                    )
                else:
                    # For legacy, we'll use api_key/email properties
                    return None
        except AuthenticationError:
            pass

        return None

    def _get_auth_kwargs(self) -> Dict[str, Any]:
        """Get authentication kwargs for client initialization."""
        # If we have an auth_method object, no kwargs needed
        if self.auth_method:
            return {}

        # Otherwise, use legacy api_key/email if available
        kwargs = {}
        if self.api_key:
            kwargs['api_key'] = self.api_key
        if self.email:
            kwargs['email'] = self.email
        return kwargs
