"""Authentication commands for secure credential management."""

import argparse
import getpass
from typing import Optional

from acled.auth import AuthFactory, CookieAuth, OAuthTokenAuth
from acled.cli.utils.auth import CredentialManager
from acled.clients import AcledClient


class AuthCommand:
    """Command for managing authentication credentials."""

    def __init__(self, config):
        # Don't initialize parent client for auth commands
        self.config = config
        self.credential_manager = CredentialManager()

    @classmethod
    def register_parser(cls, subparsers: argparse._SubParsersAction) -> None:
        """Register the auth command parser."""
        parser = subparsers.add_parser(
            'auth',
            help='Manage authentication credentials',
            description='Login, logout, and manage stored ACLED API credentials.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  # Interactive login (prompts for credentials)
  acled auth login

  # Login with provided credentials
  acled auth login --api-key YOUR_KEY --email your@email.com

  # Check current authentication status
  acled auth status

  # Logout and clear stored credentials
  acled auth logout

  # Test stored credentials
  acled auth test
            '''
        )

        subparsers_auth = parser.add_subparsers(
            dest='auth_command',
            help='Authentication commands',
            metavar='COMMAND'
        )

        # Login command
        login_parser = subparsers_auth.add_parser(
            'login',
            help='Store API credentials securely'
        )
        login_parser.add_argument(
            '--method',
            choices=['auto', 'legacy', 'oauth', 'cookie'],
            default='auto',
            help='Authentication method (default: auto-detect best available)'
        )
        # Legacy auth options
        login_parser.add_argument(
            '--api-key',
            help='ACLED API key (for legacy auth, will prompt if not provided)'
        )
        login_parser.add_argument(
            '--email',
            help='Email address (for legacy auth, will prompt if not provided)'
        )
        # OAuth options
        login_parser.add_argument(
            '--username',
            help='ACLED username (for OAuth, will prompt if not provided)'
        )
        login_parser.add_argument(
            '--password',
            help='ACLED password (for OAuth, will prompt if not provided)'
        )
        login_parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing stored credentials'
        )

        # Logout command
        subparsers_auth.add_parser(
            'logout',
            help='Remove stored credentials'
        )

        # Status command
        subparsers_auth.add_parser(
            'status',
            help='Show authentication status'
        )

        # Test command
        subparsers_auth.add_parser(
            'test',
            help='Test stored credentials with API'
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the auth command."""
        if not hasattr(args, 'auth_command') or not args.auth_command:
            print("Error: No auth command specified. Use 'acled auth --help' for options.")
            return 1

        if args.auth_command == 'login':
            return self._handle_login(args)
        if args.auth_command == 'logout':
            return self._handle_logout(args)
        if args.auth_command == 'status':
            return self._handle_status(args)
        if args.auth_command == 'test':
            return self._handle_test(args)
        print(f"Error: Unknown auth command: {args.auth_command}")
        return 1

    def _handle_login(self, args: argparse.Namespace) -> int:
        """Handle login command."""
        try:
            # Check if credentials already exist
            if self.credential_manager.has_stored_credentials() and not args.force:
                print("Credentials are already stored.")
                print("Use 'acled auth login --force' to overwrite, or 'acled auth logout' first.")
                return 1

            auth_method = args.method

            # For auto mode, detect based on provided credentials
            if auth_method == 'auto':
                # Check what credentials we're getting
                has_username = bool(args.username or args.email)
                has_password = bool(args.password)
                has_api_key = bool(args.api_key)

                if has_username or has_password:
                    # Modern auth - will auto-select OAuth or Cookie
                    auth_method = 'oauth'  # Factory will handle fallback to cookie
                elif has_api_key:
                    auth_method = 'legacy'
                else:
                    # Will prompt for credentials, default to modern auth
                    print("Choose authentication method:")
                    print("1. Modern (OAuth/Cookie) - Recommended")
                    print("2. Legacy (API Key/Email)")
                    choice = input("Enter choice (1 or 2): ").strip()
                    if choice == "2":
                        auth_method = 'legacy'
                    else:
                        auth_method = 'oauth'

            if auth_method == 'legacy':
                # Get legacy credentials
                api_key = args.api_key
                email = args.email

                # Prompt for missing credentials
                if not api_key:
                    api_key = getpass.getpass("ACLED API Key: ")
                    if not api_key.strip():
                        print("Error: API key is required for legacy authentication.")
                        return 1

                if not email:
                    email = input("Email address: ")
                    if not email.strip():
                        print("Error: Email address is required for legacy authentication.")
                        return 1

                # Validate credentials by testing with API
                print("Validating credentials...")
                if not self._validate_legacy_credentials(api_key.strip(), email.strip()):
                    print("Error: Invalid credentials. Please check your API key and email.")
                    return 1

                # Store credentials securely
                self.credential_manager.store_credentials(
                    api_key=api_key.strip(),
                    email=email.strip(),
                    auth_method='legacy'
                )

            else:  # oauth or cookie
                # Handle modern authentication (OAuth/Cookie)
                username = args.username or args.email  # Accept either
                password = args.password

                # Prompt for missing credentials
                if not username:
                    username = input("ACLED Username/Email: ")
                    if not username.strip():
                        print("Error: Username/email is required for authentication.")
                        return 1

                if not password:
                    password = getpass.getpass("ACLED Password: ")
                    if not password.strip():
                        print("Error: Password is required for authentication.")
                        return 1

                # Validate credentials
                print(f"Validating {auth_method} credentials...")
                if auth_method == 'cookie':
                    if not self._validate_cookie_credentials(username.strip(), password.strip()):
                        print("Error: Failed to authenticate with cookie method.")
                        return 1
                    validated_method = 'cookie'
                else:  # oauth or auto (which tries oauth first)
                    validated_method = self._validate_modern_credentials(username.strip(), password.strip())
                    if not validated_method:
                        print("Error: Failed to authenticate. Please check your credentials.")
                        return 1
                    auth_method = validated_method

                # Store credentials
                self.credential_manager.store_credentials(
                    username=username.strip(),
                    password=password.strip(),
                    auth_method=validated_method
                )

            print(f"✓ Credentials stored securely using {auth_method} authentication.")
            print("You can now use ACLED CLI commands without providing credentials.")

            return 0

        except KeyboardInterrupt:
            print("\nLogin cancelled.")
            return 130
        except Exception as e:
            print(f"Error storing credentials: {e}")
            return 1

    def _handle_logout(self, _args: argparse.Namespace) -> int:
        """Handle logout command."""
        try:
            if not self.credential_manager.has_stored_credentials():
                print("No stored credentials found.")
                return 0

            self.credential_manager.clear_credentials()
            print("✓ Credentials cleared.")
            return 0

        except Exception as e:
            print(f"Error clearing credentials: {e}")
            return 1

    def _handle_status(self, _args: argparse.Namespace) -> int:
        """Handle status command."""
        try:
            if self.credential_manager.has_stored_credentials():
                stored_email = self.credential_manager.get_stored_email()
                print(f"✓ Authenticated as: {stored_email}")
                print("Use 'acled auth test' to verify credentials are working.")
            else:
                print("✗ Not authenticated.")
                print("Use 'acled auth login' to store credentials.")

            return 0

        except Exception as e:
            print(f"Error checking status: {e}")
            return 1

    def _handle_test(self, _args: argparse.Namespace) -> int:
        """Handle test command."""
        try:
            if not self.credential_manager.has_stored_credentials():
                print("✗ No stored credentials. Use 'acled auth login' first.")
                return 1

            creds = self.credential_manager.get_credentials()
            auth_method = creds.get('auth_method', 'legacy')
            print(f"Testing stored {auth_method} credentials...")

            if auth_method == 'legacy':
                api_key = creds.get('api_key')
                email = creds.get('email')
                if self._validate_legacy_credentials(api_key, email):
                    print("✓ Credentials are valid.")
                    return 0
            else:  # modern auth (oauth/cookie)
                # Create auth instance from stored credentials
                try:
                    username = creds.get('username') or creds.get('email')
                    password = creds.get('password')
                    if not username or not password:
                        print("✗ Incomplete credentials stored.")
                        return 1

                    # Try with stored method first
                    try:
                        auth = AuthFactory.create_auth(
                            auth_method,
                            username=username,
                            password=password
                        )
                        client = AcledClient(auth_method=auth)
                        client.get_data(limit=1)
                        print(f"✓ {auth_method.capitalize()} credentials are valid.")
                        return 0
                    except Exception:
                        # Try auto-detect as fallback
                        auth = AuthFactory.create_auth(
                            'auto',
                            username=username,
                            password=password
                        )
                        client = AcledClient(auth_method=auth)
                        client.get_data(limit=1)
                        print("✓ Credentials are valid.")
                        return 0
                except Exception:
                    pass

            print("✗ Stored credentials are invalid.")
            print("Use 'acled auth login --force' to update them.")
            return 1

        except Exception as e:
            print(f"Error testing credentials: {e}")
            return 1

    def _validate_legacy_credentials(self, api_key: str, email: str) -> bool:
        """Validate legacy credentials by making a test API call."""
        try:
            # Create a client with the provided credentials
            client = AcledClient(auth_method="legacy", api_key=api_key, email=email)

            # Make a minimal test request (limit=1 to minimize data usage)
            client.get_data(limit=1)
            return True

        except Exception:
            return False

    def _validate_modern_credentials(self, username: str, password: str) -> Optional[str]:
        """Validate modern credentials by testing authentication.

        Returns:
            The auth method that succeeded ('oauth' or 'cookie'), or None on failure.
        """
        try:
            # Try OAuth first, with token caching
            token_file = self.credential_manager.get_token_file()
            auth = OAuthTokenAuth(username=username, password=password, token_file=token_file)
            client = AcledClient(auth_method=auth)
            client.get_data(limit=1)
            # Save tokens now that we know they work
            auth.save_tokens(token_file)
            return 'oauth'
        except Exception:
            # If OAuth fails, try cookie
            try:
                auth = CookieAuth(username=username, password=password)
                client = AcledClient(auth_method=auth)
                client.get_data(limit=1)
                return 'cookie'
            except Exception:
                return None

    def _validate_cookie_credentials(self, username: str, password: str) -> bool:
        """Validate cookie credentials by testing authentication."""
        try:
            auth = CookieAuth(username=username, password=password)
            client = AcledClient(auth_method=auth)
            client.get_data(limit=1)
            return True
        except Exception:
            return False
