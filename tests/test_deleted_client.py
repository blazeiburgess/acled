import pytest
from unittest.mock import patch
from acled.clients.deleted_client import DeletedClient
from acled.clients.base_http_client import BaseHttpClient
from acled.exceptions import ApiError


def test_deleted_client_inheritance():
    """Test that DeletedClient inherits from BaseHttpClient."""
    client = DeletedClient(api_key="test_key", email="test@example.com")
    assert isinstance(client, BaseHttpClient)
    assert isinstance(client, DeletedClient)


def test_deleted_client_initialization():
    """Test that DeletedClient can be initialized with API credentials."""
    client = DeletedClient(api_key="test_key", email="test@example.com")
    assert client.api_key == "test_key"
    assert client.email == "test@example.com"
    assert client.endpoint == "/deleted/read"


def test_get_data_returns_deleted_events():
    """Test that get_data parses deleted event responses."""
    with patch('acled.clients.deleted_client.DeletedClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'event_id_cnty': 'AMP1',
                    'deleted_timestamp': '1625825678'
                },
                {
                    'event_id_cnty': 'ISR11235',
                    'deleted_timestamp': '1626104642'
                }
            ]
        }

        client = DeletedClient(api_key="test_key", email="test@example.com")
        result = client.get_data()

        assert len(result) == 2
        assert result[0]['event_id_cnty'] == 'AMP1'
        assert result[0]['deleted_timestamp'] == 1625825678
        assert result[1]['event_id_cnty'] == 'ISR11235'
        assert result[1]['deleted_timestamp'] == 1626104642


def test_get_data_with_event_id_filter():
    """Test that get_data passes event_id_cnty filter."""
    with patch('acled.clients.deleted_client.DeletedClient._get') as mock_get:
        mock_get.return_value = {'success': True, 'data': []}

        client = DeletedClient(api_key="test_key", email="test@example.com")
        client.get_data(event_id_cnty='AMP1')

        _, kwargs = mock_get.call_args
        assert kwargs['params']['event_id_cnty'] == 'AMP1'


def test_get_data_with_timestamp_filter():
    """Test that get_data passes deleted_timestamp filter."""
    with patch('acled.clients.deleted_client.DeletedClient._get') as mock_get:
        mock_get.return_value = {'success': True, 'data': []}

        client = DeletedClient(api_key="test_key", email="test@example.com")
        client.get_data(deleted_timestamp=1625825678)

        _, kwargs = mock_get.call_args
        assert kwargs['params']['deleted_timestamp'] == '1625825678'


def test_parse_deleted_event_missing_timestamp():
    """Test parsing deleted event data with missing timestamp."""
    client = DeletedClient(api_key="test_key", email="test@example.com")

    data = {'event_id_cnty': 'TEST123'}
    result = client._parse_deleted_event(data)

    assert result['event_id_cnty'] == 'TEST123'
    assert 'deleted_timestamp' not in result


def test_get_data_api_error():
    """Test that get_data raises ApiError on API failure."""
    with patch('acled.clients.deleted_client.DeletedClient._get') as mock_get:
        mock_get.return_value = {
            'success': False,
            'error': [{'message': 'Access denied'}]
        }

        client = DeletedClient(api_key="test_key", email="test@example.com")

        with pytest.raises(ApiError, match="Access denied"):
            client.get_data()


def test_get_data_query_params():
    """Test that query_params with _where suffix are passed through."""
    with patch('acled.clients.deleted_client.DeletedClient._get') as mock_get:
        mock_get.return_value = {'success': True, 'data': []}

        client = DeletedClient(api_key="test_key", email="test@example.com")
        client.get_data(
            deleted_timestamp=1625825678,
            query_params={'deleted_timestamp_where': 'BETWEEN'}
        )

        _, kwargs = mock_get.call_args
        assert kwargs['params']['deleted_timestamp'] == '1625825678'
        assert kwargs['params']['deleted_timestamp_where'] == 'BETWEEN'
