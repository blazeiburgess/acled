"""Tests for the authentication module."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from acled.auth import (
    AuthMethod, LegacyKeyEmailAuth, OAuthTokenAuth, 
    AuthFactory
)
from acled.exceptions import AcledMissingAuthError, ApiError


class TestLegacyKeyEmailAuth:
    """Test legacy API key/email authentication."""
    
    def test_init_with_credentials(self):
        """Test initialization with API key and email."""
        auth = LegacyKeyEmailAuth(api_key="test_key", email="test@example.com")
        assert auth.api_key == "test_key"
        assert auth.email == "test@example.com"
        assert auth.is_authenticated()
    
    def test_init_from_environment(self):
        """Test initialization from environment variables."""
        with patch.dict(os.environ, {
            'ACLED_API_KEY': 'env_key',
            'ACLED_EMAIL': 'env@example.com'
        }):
            auth = LegacyKeyEmailAuth()
            assert auth.api_key == "env_key"
            assert auth.email == "env@example.com"
    
    def test_init_missing_api_key(self):
        """Test initialization fails without API key."""
        with pytest.raises(AcledMissingAuthError, match="API key is required"):
            LegacyKeyEmailAuth(email="test@example.com")
    
    def test_init_missing_email(self):
        """Test initialization fails without email."""
        with pytest.raises(AcledMissingAuthError, match="Email is required"):
            LegacyKeyEmailAuth(api_key="test_key")
    
    def test_authenticate_adds_credentials_to_params(self):
        """Test that authenticate adds credentials to parameters."""
        auth = LegacyKeyEmailAuth(api_key="test_key", email="test@example.com")
        session = Mock()
        params = {"param1": "value1"}
        
        result = auth.authenticate(session, params)
        
        assert result["key"] == "test_key"
        assert result["email"] == "test@example.com"
        assert result["param1"] == "value1"
    
    def test_refresh_if_needed_does_nothing(self):
        """Test that refresh_if_needed does nothing for legacy auth."""
        auth = LegacyKeyEmailAuth(api_key="test_key", email="test@example.com")
        session = Mock()
        
        # Should not raise any exceptions
        auth.refresh_if_needed(session)


class TestOAuthTokenAuth:
    """Test OAuth token-based authentication."""
    
    @patch('acled.auth.requests.post')
    def test_init_with_credentials(self, mock_post):
        """Test initialization with username and password."""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 86400,
            "refresh_token_expires_in": 1209600
        }
        mock_post.return_value = mock_response
        
        auth = OAuthTokenAuth(username="test_user", password="test_pass")
        
        assert auth.username == "test_user"
        assert auth.password == "test_pass"
        assert auth.access_token == "test_access_token"
        assert auth.refresh_token == "test_refresh_token"
        assert auth.is_authenticated()
        
        # Verify token endpoint was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://acleddata.com/oauth/token"
        assert call_args[1]["data"]["grant_type"] == "password"
        assert call_args[1]["data"]["username"] == "test_user"
        assert call_args[1]["data"]["password"] == "test_pass"
    
    def test_init_from_environment(self):
        """Test initialization from environment variables."""
        with patch.dict(os.environ, {
            'ACLED_USERNAME': 'env_user',
            'ACLED_PASSWORD': 'env_pass'
        }):
            with patch('acled.auth.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "access_token": "test_token",
                    "refresh_token": "refresh_token",
                    "expires_in": 86400
                }
                mock_post.return_value = mock_response
                
                auth = OAuthTokenAuth()
                assert auth.username == "env_user"
                assert auth.password == "env_pass"
    
    def test_init_missing_credentials(self):
        """Test initialization fails without credentials."""
        with pytest.raises(AcledMissingAuthError):
            OAuthTokenAuth()
    
    @patch('acled.auth.requests.post')
    def test_refresh_access_token(self, mock_post):
        """Test refreshing access token with refresh token."""
        # Create auth with initial tokens
        auth = OAuthTokenAuth.__new__(OAuthTokenAuth)
        auth.username = "test_user"
        auth.password = "test_pass"
        auth.access_token = "old_token"
        auth.refresh_token = "refresh_token"
        auth.access_token_expires_at = datetime.now() - timedelta(hours=1)
        auth.refresh_token_expires_at = datetime.now() + timedelta(days=7)
        auth.token_file = None
        auth.log = MagicMock()

        # Mock refresh response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 86400
        }
        mock_post.return_value = mock_response

        auth._refresh_access_token()

        assert auth.access_token == "new_access_token"
        assert auth.refresh_token == "new_refresh_token"

        # Verify refresh endpoint was called
        call_args = mock_post.call_args
        assert call_args[1]["data"]["grant_type"] == "refresh_token"
        assert call_args[1]["data"]["refresh_token"] == "refresh_token"
    
    def test_authenticate_adds_bearer_token(self):
        """Test that authenticate adds Bearer token to session headers."""
        auth = OAuthTokenAuth.__new__(OAuthTokenAuth)
        auth.access_token = "test_token"
        auth.log = MagicMock()
        
        session = Mock()
        session.headers = {}
        params = {"param1": "value1"}
        
        result = auth.authenticate(session, params)
        
        assert session.headers["Authorization"] == "Bearer test_token"
        assert result == params  # Params should be unchanged
    
    @patch('acled.auth.requests.post')
    def test_refresh_if_needed_when_expired(self, mock_post):
        """Test that refresh_if_needed refreshes expired token."""
        auth = OAuthTokenAuth.__new__(OAuthTokenAuth)
        auth.username = "test_user"
        auth.password = "test_pass"
        auth.access_token = "old_token"
        auth.refresh_token = "refresh_token"
        auth.access_token_expires_at = datetime.now() - timedelta(hours=1)
        auth.refresh_token_expires_at = datetime.now() + timedelta(days=7)
        auth.token_file = None
        auth.log = MagicMock()

        # Mock refresh response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "expires_in": 86400
        }
        mock_post.return_value = mock_response

        session = Mock()
        session.headers = {}

        auth.refresh_if_needed(session)

        assert auth.access_token == "new_token"
        assert session.headers["Authorization"] == "Bearer new_token"


class TestOAuthTokenPersistence:
    """Test that tokens are persisted to disk after refresh."""

    @patch('acled.auth.requests.post')
    def test_persist_tokens_after_refresh(self, mock_post):
        """Test tokens are saved to file after refresh."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "initial_access",
            "refresh_token": "initial_refresh",
            "expires_in": 86400,
            "refresh_token_expires_in": 1209600
        }
        mock_post.return_value = mock_response

        with patch.object(OAuthTokenAuth, 'save_tokens') as mock_save:
            auth = OAuthTokenAuth(
                username='user', password='pass', token_file='/tmp/tokens.json'
            )
            # save_tokens should have been called during init via _persist_tokens
            mock_save.assert_called_with('/tmp/tokens.json')
            mock_save.reset_mock()

            # Simulate token refresh
            mock_response.json.return_value = {
                "access_token": "refreshed_access",
                "refresh_token": "refreshed_refresh",
                "expires_in": 86400,
            }
            auth._refresh_access_token()

            # save_tokens should be called again after refresh
            mock_save.assert_called_with('/tmp/tokens.json')

    @patch('acled.auth.requests.post')
    def test_no_persist_without_token_file(self, mock_post):
        """Test tokens are not saved when no token_file is set."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh_token",
            "expires_in": 86400,
        }
        mock_post.return_value = mock_response

        with patch.object(OAuthTokenAuth, 'save_tokens') as mock_save:
            auth = OAuthTokenAuth(username='user', password='pass')
            mock_save.assert_not_called()


class TestAuthFactory:
    """Test AuthFactory for creating authentication instances."""
    
    def test_create_legacy_auth(self):
        """Test creating legacy authentication."""
        auth = AuthFactory.create_auth(
            "legacy",
            api_key="test_key",
            email="test@example.com"
        )
        
        assert isinstance(auth, LegacyKeyEmailAuth)
        assert auth.api_key == "test_key"
        assert auth.email == "test@example.com"
    
    @patch('acled.auth.requests.post')
    def test_create_oauth_auth(self, mock_post):
        """Test creating OAuth authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh_token",
            "expires_in": 86400
        }
        mock_post.return_value = mock_response
        
        auth = AuthFactory.create_auth(
            "oauth",
            username="test_user",
            password="test_pass"
        )
        
        assert isinstance(auth, OAuthTokenAuth)
        assert auth.username == "test_user"
        assert auth.password == "test_pass"
    
    def test_create_unknown_method(self):
        """Test creating auth with unknown method raises error."""
        with pytest.raises(ValueError, match="Unknown authentication method"):
            AuthFactory.create_auth("unknown")
    
    def test_from_environment_legacy(self):
        """Test auto-detecting legacy auth from environment."""
        with patch.dict(os.environ, {
            'ACLED_API_KEY': 'env_key',
            'ACLED_EMAIL': 'env@example.com'
        }, clear=True):
            auth = AuthFactory.from_environment()
            assert isinstance(auth, LegacyKeyEmailAuth)
            assert auth.api_key == "env_key"
            assert auth.email == "env@example.com"
    
    @patch('acled.auth.requests.post')
    def test_from_environment_oauth(self, mock_post):
        """Test auto-detecting OAuth auth from environment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh_token",
            "expires_in": 86400
        }
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {
            'ACLED_USERNAME': 'env_user',
            'ACLED_PASSWORD': 'env_pass'
        }, clear=True):
            auth = AuthFactory.from_environment()
            assert isinstance(auth, OAuthTokenAuth)
            assert auth.username == "env_user"
            assert auth.password == "env_pass"
    
    def test_from_environment_no_credentials(self):
        """Test from_environment fails with no credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AcledMissingAuthError):
                AuthFactory.from_environment()