import pytest
from unittest.mock import patch, MagicMock

import requests

from acled.clients.base_http_client import BaseHttpClient
from acled.exceptions import AcledMissingAuthError

@pytest.fixture
def mock_environ():
    env_dict = {
        'ACLED_API_HOST': 'https://test.api.com',
        'ACLED_API_KEY': 'test_api_key',
        'ACLED_EMAIL': 'test@email.com'
    }
    with patch('acled.clients.base_http_client.environ') as mock_env_client:
        with patch('acled.auth.environ') as mock_env_auth:
            mock_env_client.get.side_effect = lambda key, default=None: env_dict.get(key, default)
            mock_env_auth.get.side_effect = lambda key, default=None: env_dict.get(key, default)
            yield mock_env_client

@pytest.fixture
def mock_requests_session():
    with patch('acled.clients.base_http_client.requests.Session') as mock_session:
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        yield mock_session_instance

@pytest.fixture
def mock_logger():
    with patch('acled.clients.base_http_client.AcledLogger') as mock_logger:
        mock_logger_instance = MagicMock()
        mock_logger.return_value.get_logger.return_value = mock_logger_instance
        yield mock_logger_instance

def test_init_with_provided_credentials(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient(api_key='provided_key', email='provided@email.com')
    assert client.api_key == 'provided_key'
    assert client.email == 'provided@email.com'
    assert client.BASE_URL == 'https://acleddata.com/api'
    mock_requests_session.headers.update.assert_called_once_with({'Content-Type': 'application/json'})

def test_init_with_environ_credentials(mock_environ, mock_requests_session, mock_logger):
    mock_environ.get.side_effect = lambda key, default=None: {
        'ACLED_EMAIL': 'test@email.com',
        'ACLED_API_KEY': 'test_api_key'
    }.get(key, default)

    client = BaseHttpClient()
    assert client.api_key == 'test_api_key'
    assert client.email == 'test@email.com'
    assert client.BASE_URL == 'https://acleddata.com/api'

def test_init_missing_api_key(mock_environ, mock_requests_session, mock_logger):
    # Clear environment to ensure no authentication is found
    with patch('acled.auth.environ') as mock_auth_env:
        mock_auth_env.get.return_value = None
        with pytest.raises(AcledMissingAuthError, match="No authentication credentials"):
            BaseHttpClient()

def test_init_missing_email(mock_environ, mock_requests_session, mock_logger):
    # Set only API key without email
    with patch('acled.auth.environ') as mock_auth_env:
        mock_auth_env.get.side_effect = lambda key, default=None: {
            'ACLED_API_KEY': 'test_api_key'
        }.get(key, default)
        with pytest.raises(AcledMissingAuthError, match="Email is required|No authentication credentials"):
            BaseHttpClient()

def test_get_request(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {'data': 'test'}
    mock_requests_session.get.return_value = mock_response

    result = client._get('/test', {'param': 'value'})

    mock_requests_session.get.assert_called_once_with(
        'https://acleddata.com/api/test',
        params={'param': 'value', 'key': 'test_api_key', 'email': 'test@email.com'},
        timeout=30
    )
    mock_response.raise_for_status.assert_called_once()
    assert result == {'data': 'test'}
    mock_logger.debug.assert_called()

def test_get_request_without_params(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {'data': 'test'}
    mock_requests_session.get.return_value = mock_response

    result = client._get('/test')

    mock_requests_session.get.assert_called_once_with(
        'https://acleddata.com/api/test',
        params={'key': 'test_api_key', 'email': 'test@email.com'},
        timeout=30
    )
    mock_response.raise_for_status.assert_called_once()
    assert result == {'data': 'test'}

def test_post_request(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {'data': 'test'}
    mock_requests_session.post.return_value = mock_response

    result = client._post('/test', {'param': 'value'})

    mock_requests_session.post.assert_called_once_with(
        'https://acleddata.com/api/test',
        json={'param': 'value', 'key': 'test_api_key', 'email': 'test@email.com'},
        timeout=30
    )
    mock_response.raise_for_status.assert_called_once()
    assert result == {'data': 'test'}

def test_post_request_without_data(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {'data': 'test'}
    mock_requests_session.post.return_value = mock_response

    result = client._post('/test')

    mock_requests_session.post.assert_called_once_with(
        'https://acleddata.com/api/test',
        json={'key': 'test_api_key', 'email': 'test@email.com'},
        timeout=30
    )
    mock_response.raise_for_status.assert_called_once()
    assert result == {'data': 'test'}

def test_get_request_raises_exception(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
    mock_requests_session.get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        client._get('/test')

def test_post_request_raises_exception(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    mock_requests_session.post.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        client._post('/test')

def test_base_url_default(mock_requests_session, mock_logger):
    with patch('acled.clients.base_http_client.environ') as mock_env:
        with patch('acled.auth.environ') as mock_auth_env:
            env_dict = {
                'ACLED_API_KEY': 'test_api_key',
                'ACLED_EMAIL': 'test@email.com',
            }
            mock_env.get.side_effect = lambda key, default=None: env_dict.get(key, default)
            mock_auth_env.get.side_effect = lambda key, default=None: env_dict.get(key, default)
            client = BaseHttpClient()
            assert client.BASE_URL == "https://acleddata.com/api"

def test_logger_initialization(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_logger.debug.assert_not_called()  # Ensure logger is not used in initialization
    client._get('/test')
    assert mock_logger.debug.call_count == 3  # Called for URL, params, and response content

def test_401_triggers_token_refresh_and_retry(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()

    # First response: 401, second response: 200
    mock_response_401 = MagicMock()
    mock_response_401.status_code = 401
    mock_response_401.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")

    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.json.return_value = {'data': 'test'}
    mock_response_200.content = b'{"data": "test"}'

    mock_requests_session.get.side_effect = [mock_response_401, mock_response_200]

    with patch.object(client.auth, 'force_refresh') as mock_force_refresh:
        result = client._get('/test', {'param': 'value'})

    mock_force_refresh.assert_called_once_with(client.session)
    assert result == {'data': 'test'}
    assert mock_requests_session.get.call_count == 2


def test_401_twice_raises_after_refresh(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()

    # Both responses return 401
    mock_response_401 = MagicMock()
    mock_response_401.status_code = 401
    mock_response_401.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")

    mock_requests_session.get.return_value = mock_response_401

    with patch.object(client.auth, 'force_refresh'):
        with pytest.raises(requests.HTTPError):
            client._get('/test')


def test_legacy_positional_args_raises_helpful_error(mock_environ, mock_requests_session, mock_logger):
    """Test that passing an unrecognized string as first positional arg gives a clear error."""
    with pytest.raises(TypeError, match="Unknown auth method"):
        BaseHttpClient("some_random_string")


def test_legacy_two_positional_args_backward_compat(mock_environ, mock_requests_session, mock_logger):
    """Test that BaseHttpClient('api_key', 'email') still works with a deprecation warning."""
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        client = BaseHttpClient("my_api_key", "user@example.com")

        assert client.api_key == "my_api_key"
        assert client.email == "user@example.com"

        # Should have emitted a DeprecationWarning
        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)
                                and "positional" in str(x.message).lower()]
        assert len(deprecation_warnings) >= 1


def test_force_refresh_failure_is_retryable(mock_environ, mock_requests_session, mock_logger):
    """Test that force_refresh() failure doesn't immediately abort the request."""
    from acled.exceptions import ApiError, RetryError

    client = BaseHttpClient()

    # All responses return 401
    mock_response_401 = MagicMock()
    mock_response_401.status_code = 401
    mock_response_401.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")

    mock_requests_session.get.return_value = mock_response_401

    mock_force_refresh = MagicMock(side_effect=ApiError("Token endpoint down"))
    with patch.object(client.auth, 'force_refresh', mock_force_refresh):
        # Should exhaust retries rather than raising ApiError immediately
        with pytest.raises((requests.HTTPError, RetryError)):
            client._get('/test')

    # force_refresh was called (once, since auth_refreshed gets set)
    assert mock_force_refresh.call_count == 1


def test_pre_request_refresh_failure_continues(mock_environ, mock_requests_session, mock_logger):
    """Test that refresh_if_needed() failure before retry loop doesn't abort."""
    from acled.exceptions import ApiError

    client = BaseHttpClient()

    # refresh_if_needed fails but the request succeeds
    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.json.return_value = {'data': 'test'}
    mock_response_200.content = b'{"data": "test"}'
    mock_requests_session.get.return_value = mock_response_200

    with patch.object(client.auth, 'refresh_if_needed', side_effect=ApiError("Token refresh failed")):
        result = client._get('/test')

    assert result == {'data': 'test'}


if __name__ == "__main__":
    pytest.main()
