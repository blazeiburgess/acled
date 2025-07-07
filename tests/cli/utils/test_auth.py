"""Tests for authentication utilities."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest


class TestAuthenticationError(unittest.TestCase):
    """Test AuthenticationError exception."""
    
    def test_authentication_error_creation(self):
        """Test AuthenticationError can be created and raised."""
        from acled.cli.utils.auth import AuthenticationError
        
        error = AuthenticationError("Test error")
        self.assertEqual(str(error), "Test error")
        
        with self.assertRaises(AuthenticationError):
            raise AuthenticationError("Test error")


class TestCredentialManager(unittest.TestCase):
    """Test CredentialManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_api_key = "test_api_key_123"
        self.test_email = "test@example.com"
        
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: self._cleanup_temp_dir())
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except OSError:
            pass
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', False)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', False)
    def test_credential_manager_no_dependencies(self):
        """Test CredentialManager raises error when no dependencies available."""
        from acled.cli.utils.auth import CredentialManager, AuthenticationError
        
        with self.assertRaises(AuthenticationError) as context:
            CredentialManager()
        
        self.assertIn("Neither keyring nor cryptography is available", str(context.exception))
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', True)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', True)
    @patch('acled.cli.utils.auth.keyring')
    def test_credential_manager_prefers_keyring(self, mock_keyring):
        """Test CredentialManager prefers keyring when available."""
        from acled.cli.utils.auth import CredentialManager
        
        # Mock keyring as available
        mock_keyring.get_keyring.return_value = Mock()
        
        manager = CredentialManager()
        self.assertTrue(manager.use_keyring)
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', True)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', True)
    @patch('acled.cli.utils.auth.keyring')
    def test_credential_manager_falls_back_to_encryption(self, mock_keyring):
        """Test CredentialManager falls back to encryption when keyring fails."""
        from acled.cli.utils.auth import CredentialManager
        
        # Mock keyring as failing
        mock_keyring.get_keyring.side_effect = Exception("Keyring not available")
        
        manager = CredentialManager()
        self.assertFalse(manager.use_keyring)
        self.assertTrue(manager.use_encryption)
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', True)
    @patch('acled.cli.utils.auth.keyring')
    def test_store_credentials_with_keyring(self, mock_keyring):
        """Test storing credentials with keyring."""
        from acled.cli.utils.auth import CredentialManager
        
        # Mock keyring as available
        mock_keyring.get_keyring.return_value = Mock()
        
        manager = CredentialManager()
        manager.store_credentials(self.test_api_key, self.test_email)
        
        # Verify keyring calls
        mock_keyring.set_password.assert_any_call("acled-cli", "api-key", self.test_api_key)
        mock_keyring.set_password.assert_any_call("acled-cli", "email", self.test_email)
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', True)
    @patch('acled.cli.utils.auth.keyring')
    def test_get_credentials_with_keyring(self, mock_keyring):
        """Test retrieving credentials with keyring."""
        from acled.cli.utils.auth import CredentialManager
        
        # Mock keyring as available
        mock_keyring.get_keyring.return_value = Mock()
        mock_keyring.get_password.side_effect = lambda service, username: {
            ("acled-cli", "api-key"): self.test_api_key,
            ("acled-cli", "email"): self.test_email
        }.get((service, username))
        
        manager = CredentialManager()
        api_key, email = manager.get_credentials()
        
        self.assertEqual(api_key, self.test_api_key)
        self.assertEqual(email, self.test_email)
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', True)
    @patch('acled.cli.utils.auth.keyring')
    def test_get_credentials_missing_from_keyring(self, mock_keyring):
        """Test retrieving missing credentials from keyring raises error."""
        from acled.cli.utils.auth import CredentialManager, AuthenticationError
        
        # Mock keyring as available but returning None
        mock_keyring.get_keyring.return_value = Mock()
        mock_keyring.get_password.return_value = None
        
        manager = CredentialManager()
        
        with self.assertRaises(AuthenticationError):
            manager.get_credentials()
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', True)
    @patch('acled.cli.utils.auth.keyring')
    def test_clear_credentials_with_keyring(self, mock_keyring):
        """Test clearing credentials with keyring."""
        from acled.cli.utils.auth import CredentialManager
        
        # Mock keyring as available
        mock_keyring.get_keyring.return_value = Mock()
        
        manager = CredentialManager()
        manager.clear_credentials()
        
        # Verify keyring delete calls
        mock_keyring.delete_password.assert_any_call("acled-cli", "api-key")
        mock_keyring.delete_password.assert_any_call("acled-cli", "email")
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', False)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', True)
    def test_store_credentials_with_encryption(self):
        """Test storing credentials with file encryption."""
        from acled.cli.utils.auth import CredentialManager
        
        with patch.object(CredentialManager, '_get_config_dir', return_value=Path(self.temp_dir)):
            manager = CredentialManager()
            manager.store_credentials(self.test_api_key, self.test_email)
            
            # Verify file was created
            credentials_file = Path(self.temp_dir) / "credentials.enc"
            self.assertTrue(credentials_file.exists())
            
            # Verify file has content
            self.assertGreater(credentials_file.stat().st_size, 0)
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', False)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', True)
    def test_get_credentials_with_encryption(self):
        """Test retrieving credentials with file encryption."""
        from acled.cli.utils.auth import CredentialManager
        
        with patch.object(CredentialManager, '_get_config_dir', return_value=Path(self.temp_dir)):
            manager = CredentialManager()
            
            # Store first
            manager.store_credentials(self.test_api_key, self.test_email)
            
            # Then retrieve
            api_key, email = manager.get_credentials()
            
            self.assertEqual(api_key, self.test_api_key)
            self.assertEqual(email, self.test_email)
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', False)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', True)
    def test_get_credentials_missing_file(self):
        """Test retrieving credentials when file doesn't exist."""
        from acled.cli.utils.auth import CredentialManager, AuthenticationError
        
        with patch.object(CredentialManager, '_get_config_dir', return_value=Path(self.temp_dir)):
            manager = CredentialManager()
            
            with self.assertRaises(AuthenticationError):
                manager.get_credentials()
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', False)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', True)
    def test_has_stored_credentials(self):
        """Test checking if credentials are stored."""
        from acled.cli.utils.auth import CredentialManager
        
        with patch.object(CredentialManager, '_get_config_dir', return_value=Path(self.temp_dir)):
            manager = CredentialManager()
            
            # Initially no credentials
            self.assertFalse(manager.has_stored_credentials())
            
            # Store credentials
            manager.store_credentials(self.test_api_key, self.test_email)
            
            # Now should have credentials
            self.assertTrue(manager.has_stored_credentials())
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', False)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', True)
    def test_get_stored_email(self):
        """Test getting just the stored email."""
        from acled.cli.utils.auth import CredentialManager
        
        with patch.object(CredentialManager, '_get_config_dir', return_value=Path(self.temp_dir)):
            manager = CredentialManager()
            
            # Initially no email
            self.assertIsNone(manager.get_stored_email())
            
            # Store credentials
            manager.store_credentials(self.test_api_key, self.test_email)
            
            # Should return email
            self.assertEqual(manager.get_stored_email(), self.test_email)
    
    @patch('acled.cli.utils.auth.HAS_KEYRING', False)
    @patch('acled.cli.utils.auth.HAS_CRYPTOGRAPHY', True)
    def test_clear_credentials_with_encryption(self):
        """Test clearing encrypted credentials."""
        from acled.cli.utils.auth import CredentialManager
        
        with patch.object(CredentialManager, '_get_config_dir', return_value=Path(self.temp_dir)):
            manager = CredentialManager()
            
            # Store credentials
            manager.store_credentials(self.test_api_key, self.test_email)
            self.assertTrue(manager.has_stored_credentials())
            
            # Clear credentials
            manager.clear_credentials()
            self.assertFalse(manager.has_stored_credentials())
    
    @patch('acled.cli.utils.auth.platform.system')
    def test_get_config_dir_windows(self, mock_system):
        """Test config directory on Windows."""
        from acled.cli.utils.auth import CredentialManager
        
        mock_system.return_value = "Windows"
        
        with patch.dict(os.environ, {'APPDATA': self.temp_dir}):
            manager = CredentialManager.__new__(CredentialManager)  # Don't call __init__
            config_dir = manager._get_config_dir()
            
            expected = Path(self.temp_dir) / "acled-cli"
            self.assertEqual(config_dir, expected)
    
    @patch('acled.cli.utils.auth.platform.system')
    def test_get_config_dir_macos(self, mock_system):
        """Test config directory on macOS."""
        from acled.cli.utils.auth import CredentialManager
        
        mock_system.return_value = "Darwin"
        
        manager = CredentialManager.__new__(CredentialManager)  # Don't call __init__
        
        with patch('pathlib.Path.expanduser') as mock_expanduser:
            mock_expanduser.return_value = Path(self.temp_dir) / "acled-cli"
            config_dir = manager._get_config_dir()
            
            self.assertEqual(config_dir, Path(self.temp_dir) / "acled-cli")
    
    @patch('acled.cli.utils.auth.platform.system')
    def test_get_config_dir_linux(self, mock_system):
        """Test config directory on Linux."""
        from acled.cli.utils.auth import CredentialManager
        
        mock_system.return_value = "Linux"
        
        manager = CredentialManager.__new__(CredentialManager)  # Don't call __init__
        
        with patch.dict(os.environ, {'XDG_CONFIG_HOME': self.temp_dir}):
            config_dir = manager._get_config_dir()
            
            expected = Path(self.temp_dir) / "acled-cli"
            self.assertEqual(config_dir, expected)


if __name__ == '__main__':
    unittest.main()