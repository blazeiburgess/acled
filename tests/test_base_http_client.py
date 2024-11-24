# tests/test_base_http_client.py

import pytest
from unittest.mock import patch, MagicMock

import requests

from acled.clients.base_http_client import BaseHttpClient
from acled.exceptions import AcledMissingAuthError

@pytest.fixture
def mock_environ():
    with patch('acled.clients.base_http_client.environ') as mock_env:
        mock_env.get.side_effect = lambda key, default=None: {
            'ACLED_API_HOST': 'https://test.api.com',
            'ACLED_API_KEY': 'test_api_key',
            'ACLED_EMAIL': 'test@email.com'
        }.get(key, default)
        yield mock_env

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
    assert client.BASE_URL == 'https://api.acleddata.com'
    mock_requests_session.headers.update.assert_called_once_with({'Content-Type': 'application/json'})

def test_init_with_environ_credentials(mock_environ, mock_requests_session, mock_logger):
    mock_environ.get.side_effect = lambda key, default=None: {
        'ACLED_EMAIL': 'test@email.com',
        'ACLED_API_KEY': 'test_api_key'
    }.get(key, default)

    client = BaseHttpClient()
    assert client.api_key == 'test_api_key'
    assert client.email == 'test@email.com'
    assert client.BASE_URL == 'https://api.acleddata.com'

def test_init_missing_api_key(mock_environ, mock_requests_session, mock_logger):
    mock_environ.get.side_effect = lambda key, default=None: {
        'ACLED_API_HOST': 'https://test.api.com',
        'ACLED_EMAIL': 'test@email.com'
    }.get(key, default)
    with pytest.raises(AcledMissingAuthError, match="API key is required"):
        BaseHttpClient()

def test_init_missing_email(mock_environ, mock_requests_session, mock_logger):
    mock_environ.get.side_effect = lambda key, default=None: {
        'ACLED_API_KEY': 'test_api_key'
    }.get(key, default)
    with pytest.raises(AcledMissingAuthError, match="Email is required"):
        BaseHttpClient()

def test_get_request(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {'data': 'test'}
    mock_requests_session.get.return_value = mock_response

    result = client._get('/test', {'param': 'value'})

    mock_requests_session.get.assert_called_once_with(
        'https://api.acleddata.com/test',
        params={'param': 'value', 'key': 'test_api_key', 'email': 'test@email.com'}
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
        'https://api.acleddata.com/test',
        params={'key': 'test_api_key', 'email': 'test@email.com'}
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
        'https://api.acleddata.com/test',
        json={'param': 'value', 'key': 'test_api_key', 'email': 'test@email.com'}
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
        'https://api.acleddata.com/test',
        json={'key': 'test_api_key', 'email': 'test@email.com'}
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
        mock_env.get.side_effect = lambda key, default=None: {
            'ACLED_API_KEY': 'test_api_key',
            'ACLED_EMAIL': 'test@email.com',
        }.get(key, default)
        client = BaseHttpClient()
        assert client.BASE_URL == "https://api.acleddata.com"

def test_logger_initialization(mock_environ, mock_requests_session, mock_logger):
    client = BaseHttpClient()
    mock_logger.debug.assert_not_called()  # Ensure logger is not used in initialization
    client._get('/test')
    assert mock_logger.debug.call_count == 3  # Called for URL, params, and response content

if __name__ == "__main__":
    pytest.main()
