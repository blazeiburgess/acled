"""Authentication commands for secure credential management."""

import argparse
import getpass
import sys
from typing import Optional

from acled.cli.utils.auth import CredentialManager, AuthenticationError
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
            '--api-key',
            help='ACLED API key (will prompt if not provided)'
        )
        login_parser.add_argument(
            '--email',
            help='Email address (will prompt if not provided)'
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
        elif args.auth_command == 'logout':
            return self._handle_logout(args)
        elif args.auth_command == 'status':
            return self._handle_status(args)
        elif args.auth_command == 'test':
            return self._handle_test(args)
        else:
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
            
            # Get credentials
            api_key = args.api_key
            email = args.email
            
            # Prompt for missing credentials
            if not api_key:
                api_key = getpass.getpass("ACLED API Key: ")
                if not api_key.strip():
                    print("Error: API key is required.")
                    return 1
            
            if not email:
                email = input("Email address: ")
                if not email.strip():
                    print("Error: Email address is required.")
                    return 1
            
            # Validate credentials by testing with API
            print("Validating credentials...")
            if not self._validate_credentials(api_key.strip(), email.strip()):
                print("Error: Invalid credentials. Please check your API key and email.")
                return 1
            
            # Store credentials securely
            self.credential_manager.store_credentials(api_key.strip(), email.strip())
            print("✓ Credentials stored securely.")
            print("You can now use ACLED CLI commands without providing credentials.")
            
            return 0
            
        except KeyboardInterrupt:
            print("\nLogin cancelled.")
            return 130
        except Exception as e:
            print(f"Error storing credentials: {e}")
            return 1
    
    def _handle_logout(self, args: argparse.Namespace) -> int:
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
    
    def _handle_status(self, args: argparse.Namespace) -> int:
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
    
    def _handle_test(self, args: argparse.Namespace) -> int:
        """Handle test command."""
        try:
            if not self.credential_manager.has_stored_credentials():
                print("✗ No stored credentials. Use 'acled auth login' first.")
                return 1
            
            api_key, email = self.credential_manager.get_credentials()
            print("Testing stored credentials...")
            
            if self._validate_credentials(api_key, email):
                print("✓ Credentials are valid.")
                return 0
            else:
                print("✗ Stored credentials are invalid.")
                print("Use 'acled auth login --force' to update them.")
                return 1
                
        except Exception as e:
            print(f"Error testing credentials: {e}")
            return 1
    
    def _validate_credentials(self, api_key: str, email: str) -> bool:
        """Validate credentials by making a test API call."""
        try:
            # Create a client with the provided credentials
            client = AcledClient(api_key=api_key, email=email)
            
            # Make a minimal test request (limit=1 to minimize data usage)
            client.get_data(limit=1)
            return True
            
        except Exception:
            return False