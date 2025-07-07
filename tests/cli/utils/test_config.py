"""Tests for CLI configuration utilities."""

import os
import unittest
from unittest.mock import Mock, patch

import pytest


class TestCLIConfig(unittest.TestCase):
    """Test CLIConfig class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_args = Mock()
        self.mock_args.verbose = False
        self.mock_args.quiet = False
        self.mock_args.format = 'json'
        self.mock_args.output = None
        self.mock_args.api_key = None
        self.mock_args.email = None
    
    def test_config_initialization_with_args(self):
        """Test CLIConfig initialization with arguments."""
        from acled.cli.utils.config import CLIConfig
        
        self.mock_args.verbose = True
        self.mock_args.quiet = False
        self.mock_args.format = 'table'
        self.mock_args.output = 'output.csv'
        self.mock_args.api_key = 'test_key'
        self.mock_args.email = 'test@example.com'
        
        config = CLIConfig(self.mock_args)
        
        self.assertTrue(config.verbose)
        self.assertFalse(config.quiet)
        self.assertEqual(config.format, 'table')
        self.assertEqual(config.output_file, 'output.csv')
        self.assertEqual(config.api_key, 'test_key')
        self.assertEqual(config.email, 'test@example.com')
    
    def test_config_defaults(self):
        """Test CLIConfig uses defaults for missing args."""
        from acled.cli.utils.config import CLIConfig
        
        # Remove some attributes to test defaults
        delattr(self.mock_args, 'verbose')
        delattr(self.mock_args, 'format')
        
        config = CLIConfig(self.mock_args)
        
        self.assertFalse(config.verbose)  # Default
        self.assertEqual(config.format, 'json')  # Default
    
    @patch.dict(os.environ, {'ACLED_API_KEY': 'env_key', 'ACLED_EMAIL': 'env@example.com'})
    def test_credentials_from_environment(self):
        """Test credentials are loaded from environment variables."""
        from acled.cli.utils.config import CLIConfig
        
        config = CLIConfig(self.mock_args)
        
        self.assertEqual(config.api_key, 'env_key')
        self.assertEqual(config.email, 'env@example.com')
    
    def test_credentials_args_override_environment(self):
        """Test CLI args override environment variables."""
        from acled.cli.utils.config import CLIConfig
        
        self.mock_args.api_key = 'args_key'
        self.mock_args.email = 'args@example.com'
        
        with patch.dict(os.environ, {'ACLED_API_KEY': 'env_key', 'ACLED_EMAIL': 'env@example.com'}):
            config = CLIConfig(self.mock_args)
            
            self.assertEqual(config.api_key, 'args_key')
            self.assertEqual(config.email, 'args@example.com')
    
    @patch('acled.cli.utils.config.CredentialManager')
    def test_credentials_from_stored(self, mock_credential_manager_class):
        """Test credentials are loaded from stored credentials."""
        from acled.cli.utils.config import CLIConfig
        
        # Mock credential manager
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = True
        mock_manager.get_credentials.return_value = ('stored_key', 'stored@example.com')
        mock_credential_manager_class.return_value = mock_manager
        
        config = CLIConfig(self.mock_args)
        
        self.assertEqual(config.api_key, 'stored_key')
        self.assertEqual(config.email, 'stored@example.com')
    
    @patch('acled.cli.utils.config.CredentialManager')
    def test_credentials_priority_order(self, mock_credential_manager_class):
        """Test credential priority: args > env > stored."""
        from acled.cli.utils.config import CLIConfig
        
        # Mock credential manager
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = True
        mock_manager.get_credentials.return_value = ('stored_key', 'stored@example.com')
        mock_credential_manager_class.return_value = mock_manager
        
        # Set args (highest priority)
        self.mock_args.api_key = 'args_key'
        # Set env (medium priority)
        # Leave stored as fallback (lowest priority)
        
        with patch.dict(os.environ, {'ACLED_EMAIL': 'env@example.com'}):
            config = CLIConfig(self.mock_args)
            
            # Args should override everything
            self.assertEqual(config.api_key, 'args_key')
            # Env should override stored
            self.assertEqual(config.email, 'env@example.com')
    
    @patch('acled.cli.utils.config.CredentialManager')
    def test_stored_credentials_auth_error(self, mock_credential_manager_class):
        """Test handling of AuthenticationError from stored credentials."""
        from acled.cli.utils.config import CLIConfig
        from acled.cli.utils.auth import AuthenticationError
        
        # Mock credential manager to raise error
        mock_manager = Mock()
        mock_manager.has_stored_credentials.side_effect = AuthenticationError("Test error")
        mock_credential_manager_class.return_value = mock_manager
        
        config = CLIConfig(self.mock_args)
        
        # Should fallback gracefully
        self.assertIsNone(config.api_key)
        self.assertIsNone(config.email)
    
    @patch('acled.cli.utils.config.CredentialManager')
    def test_stored_credentials_no_credentials(self, mock_credential_manager_class):
        """Test handling when no stored credentials exist."""
        from acled.cli.utils.config import CLIConfig
        
        # Mock credential manager with no credentials
        mock_manager = Mock()
        mock_manager.has_stored_credentials.return_value = False
        mock_credential_manager_class.return_value = mock_manager
        
        config = CLIConfig(self.mock_args)
        
        # Should be None when no credentials anywhere
        self.assertIsNone(config.api_key)
        self.assertIsNone(config.email)


if __name__ == '__main__':
    unittest.main()