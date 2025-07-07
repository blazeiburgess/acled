"""Tests for authentication command."""

import argparse
import unittest
from io import StringIO
from unittest.mock import Mock, patch, call

import pytest


class TestAuthCommand(unittest.TestCase):
    """Test AuthCommand class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.quiet = False
    
    def test_auth_command_initialization(self):
        """Test AuthCommand initializes without calling parent constructor."""
        from acled.cli.commands.auth import AuthCommand
        
        with patch('acled.cli.commands.auth.CredentialManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            command = AuthCommand(self.mock_config)
            
            self.assertEqual(command.config, self.mock_config)
            self.assertEqual(command.credential_manager, mock_manager)
            mock_manager_class.assert_called_once()
    
    def test_register_parser(self):
        """Test AuthCommand registers parser correctly."""
        from acled.cli.commands.auth import AuthCommand
        
        subparsers = Mock()
        mock_parser = Mock()
        mock_subparsers_auth = Mock()
        
        subparsers.add_parser.return_value = mock_parser
        mock_parser.add_subparsers.return_value = mock_subparsers_auth
        
        AuthCommand.register_parser(subparsers)
        
        # Verify main parser was added
        subparsers.add_parser.assert_called_once_with(
            'auth',
            help='Manage authentication credentials',
            description='Login, logout, and manage stored ACLED API credentials.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=unittest.mock.ANY
        )
        
        # Verify subcommands were added
        self.assertEqual(mock_subparsers_auth.add_parser.call_count, 4)  # login, logout, status, test
    
    def test_execute_no_auth_command(self):
        """Test execute with no auth subcommand specified."""
        from acled.cli.commands.auth import AuthCommand
        
        with patch('acled.cli.commands.auth.CredentialManager'):
            command = AuthCommand(self.mock_config)
        
        mock_args = Mock()
        mock_args.auth_command = None
        
        with patch('builtins.print') as mock_print:
            result = command.execute(mock_args)
            
            self.assertEqual(result, 1)
            mock_print.assert_called_once_with("Error: No auth command specified. Use 'acled auth --help' for options.")
    
    def test_execute_unknown_auth_command(self):
        """Test execute with unknown auth subcommand."""
        from acled.cli.commands.auth import AuthCommand
        
        with patch('acled.cli.commands.auth.CredentialManager'):
            command = AuthCommand(self.mock_config)
        
        mock_args = Mock()
        mock_args.auth_command = 'unknown'
        
        with patch('builtins.print') as mock_print:
            result = command.execute(mock_args)
            
            self.assertEqual(result, 1)
            mock_print.assert_called_once_with("Error: Unknown auth command: unknown")
    
    @patch('acled.cli.commands.auth.getpass.getpass')
    @patch('builtins.input')
    def test_login_interactive(self, mock_input, mock_getpass):
        """Test interactive login flow."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = False
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        # Mock user input
        mock_getpass.return_value = 'test_api_key'
        mock_input.return_value = 'test@example.com'
        
        # Mock credential validation
        command._validate_credentials = Mock(return_value=True)
        
        mock_args = Mock()
        mock_args.api_key = None
        mock_args.email = None
        mock_args.force = False
        
        with patch('builtins.print') as mock_print:
            result = command._handle_login(mock_args)
            
            self.assertEqual(result, 0)
            mock_manager.store_credentials.assert_called_once_with('test_api_key', 'test@example.com')
            mock_print.assert_called_with("You can now use ACLED CLI commands without providing credentials.")
    
    def test_login_with_provided_credentials(self):
        """Test login with credentials provided via arguments."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = False
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        # Mock credential validation
        command._validate_credentials = Mock(return_value=True)
        
        mock_args = Mock()
        mock_args.api_key = 'test_api_key'
        mock_args.email = 'test@example.com'
        mock_args.force = False
        
        with patch('builtins.print') as mock_print:
            result = command._handle_login(mock_args)
            
            self.assertEqual(result, 0)
            mock_manager.store_credentials.assert_called_once_with('test_api_key', 'test@example.com')
    
    def test_login_credentials_already_exist(self):
        """Test login when credentials already exist."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = True
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        mock_args = Mock()
        mock_args.force = False
        
        with patch('builtins.print') as mock_print:
            result = command._handle_login(mock_args)
            
            self.assertEqual(result, 1)
            mock_print.assert_called_with("Use 'acled auth login --force' to overwrite, or 'acled auth logout' first.")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = False
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        # Mock credential validation to return False
        command._validate_credentials = Mock(return_value=False)
        
        mock_args = Mock()
        mock_args.api_key = 'invalid_key'
        mock_args.email = 'test@example.com'
        mock_args.force = False
        
        with patch('builtins.print') as mock_print:
            result = command._handle_login(mock_args)
            
            self.assertEqual(result, 1)
            mock_print.assert_called_with("Error: Invalid credentials. Please check your API key and email.")
    
    def test_logout_with_credentials(self):
        """Test logout when credentials exist."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = True
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        mock_args = Mock()
        
        with patch('builtins.print') as mock_print:
            result = command._handle_logout(mock_args)
            
            self.assertEqual(result, 0)
            mock_manager.clear_credentials.assert_called_once()
            mock_print.assert_called_with("✓ Credentials cleared.")
    
    def test_logout_no_credentials(self):
        """Test logout when no credentials exist."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = False
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        mock_args = Mock()
        
        with patch('builtins.print') as mock_print:
            result = command._handle_logout(mock_args)
            
            self.assertEqual(result, 0)
            mock_print.assert_called_with("No stored credentials found.")
    
    def test_status_authenticated(self):
        """Test status when authenticated."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = True
        mock_manager.get_stored_email.return_value = 'test@example.com'
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        mock_args = Mock()
        
        with patch('builtins.print') as mock_print:
            result = command._handle_status(mock_args)
            
            self.assertEqual(result, 0)
            expected_calls = [
                call("✓ Authenticated as: test@example.com"),
                call("Use 'acled auth test' to verify credentials are working.")
            ]
            mock_print.assert_has_calls(expected_calls)
    
    def test_status_not_authenticated(self):
        """Test status when not authenticated."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = False
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        mock_args = Mock()
        
        with patch('builtins.print') as mock_print:
            result = command._handle_status(mock_args)
            
            self.assertEqual(result, 0)
            expected_calls = [
                call("✗ Not authenticated."),
                call("Use 'acled auth login' to store credentials.")
            ]
            mock_print.assert_has_calls(expected_calls)
    
    def test_test_valid_credentials(self):
        """Test testing valid stored credentials."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = True
        mock_manager.get_credentials.return_value = ('test_key', 'test@example.com')
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        # Mock credential validation
        command._validate_credentials = Mock(return_value=True)
        
        mock_args = Mock()
        
        with patch('builtins.print') as mock_print:
            result = command._handle_test(mock_args)
            
            self.assertEqual(result, 0)
            mock_print.assert_called_with("✓ Credentials are valid.")
    
    def test_test_invalid_credentials(self):
        """Test testing invalid stored credentials."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = True
        mock_manager.get_credentials.return_value = ('invalid_key', 'test@example.com')
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        # Mock credential validation
        command._validate_credentials = Mock(return_value=False)
        
        mock_args = Mock()
        
        with patch('builtins.print') as mock_print:
            result = command._handle_test(mock_args)
            
            self.assertEqual(result, 1)
            expected_calls = [
                call("✗ Stored credentials are invalid."),
                call("Use 'acled auth login --force' to update them.")
            ]
            mock_print.assert_has_calls(expected_calls)
    
    def test_test_no_stored_credentials(self):
        """Test testing when no credentials are stored."""
        from acled.cli.commands.auth import AuthCommand
        
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = False
        
        with patch('acled.cli.commands.auth.CredentialManager', return_value=mock_manager):
            command = AuthCommand(self.mock_config)
        
        mock_args = Mock()
        
        with patch('builtins.print') as mock_print:
            result = command._handle_test(mock_args)
            
            self.assertEqual(result, 1)
            mock_print.assert_called_with("✗ No stored credentials. Use 'acled auth login' first.")
    
    @patch('acled.cli.commands.auth.AcledClient')
    def test_validate_credentials_success(self, mock_client_class):
        """Test credential validation success."""
        from acled.cli.commands.auth import AuthCommand
        
        # Mock client that succeeds
        mock_client = Mock()
        mock_client.get_data.return_value = [{"test": "data"}]
        mock_client_class.return_value = mock_client
        
        with patch('acled.cli.commands.auth.CredentialManager'):
            command = AuthCommand(self.mock_config)
        
        result = command._validate_credentials('test_key', 'test@example.com')
        
        self.assertTrue(result)
        mock_client_class.assert_called_once_with(api_key='test_key', email='test@example.com')
        mock_client.get_data.assert_called_once_with(limit=1)
    
    @patch('acled.cli.commands.auth.AcledClient')
    def test_validate_credentials_failure(self, mock_client_class):
        """Test credential validation failure."""
        from acled.cli.commands.auth import AuthCommand
        
        # Mock client that raises exception
        mock_client = Mock()
        mock_client.get_data.side_effect = Exception("Invalid credentials")
        mock_client_class.return_value = mock_client
        
        with patch('acled.cli.commands.auth.CredentialManager'):
            command = AuthCommand(self.mock_config)
        
        result = command._validate_credentials('invalid_key', 'test@example.com')
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()