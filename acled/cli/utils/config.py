"""CLI configuration utilities."""

import os
from typing import Optional

from acled.cli.utils.auth import CredentialManager, AuthenticationError


class CLIConfig:
    """Configuration class for CLI operations."""

    def __init__(self, args):
        self.args = args
        self.verbose = getattr(args, 'verbose', False)
        self.quiet = getattr(args, 'quiet', False)
        self.format = getattr(args, 'format', 'json')
        self.output_file = getattr(args, 'output', None)

        # Authentication
        self.api_key = self._get_api_key()
        self.email = self._get_email()

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
                stored_api_key, _ = credential_manager.get_credentials()
                return stored_api_key
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
                _, stored_email = credential_manager.get_credentials()
                return stored_email
        except AuthenticationError:
            pass

        return None
