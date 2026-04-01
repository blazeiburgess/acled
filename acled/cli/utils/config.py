"""CLI configuration utilities."""

import os
from typing import Optional, Dict, Any

from acled.cli.utils.auth import CredentialManager, AuthenticationError
from acled.auth import AuthMethod, AuthFactory


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
        
        # New authentication system
        self.auth_method = self._get_auth_method()
        self.auth_kwargs = self._get_auth_kwargs()

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
        """Get authentication method from stored credentials or environment."""
        # If CLI args have api_key/email, use legacy auth
        if getattr(self.args, 'api_key', None) or getattr(self.args, 'email', None):
            return None  # Will use legacy auth with api_key/email
        
        # Check environment variables
        if os.environ.get('ACLED_API_KEY') and os.environ.get('ACLED_EMAIL'):
            return None  # Will use legacy auth from env
        elif os.environ.get('ACLED_USERNAME') and os.environ.get('ACLED_PASSWORD'):
            return AuthFactory.create_auth(
                'auto',
                username=os.environ.get('ACLED_USERNAME'),
                password=os.environ.get('ACLED_PASSWORD')
            )
        
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
                        password=creds.get('password')
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
