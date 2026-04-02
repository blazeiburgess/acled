import pytest
from unittest.mock import patch
from acled.clients.cast_client import CastClient
from acled.clients.base_http_client import BaseHttpClient
from acled.models.enums import ExportType
from acled.exceptions import ApiError


def test_cast_client_initialization():
    """Test that CastClient can be initialized with API credentials."""
    client = CastClient(api_key="test_key", email="test@example.com")
    assert isinstance(client, BaseHttpClient)
    assert client.endpoint == "/cast/read"


def test_get_data_with_country_and_year():
    """Test that get_data correctly passes country and year filters."""
    with patch('acled.clients.cast_client.CastClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'country': 'Somalia',
                    'admin1': 'Banadir',
                    'month': 'January',
                    'year': '2025',
                    'total_forecast': '11',
                    'battles_forecast': '5',
                    'erv_forecast': '3',
                    'vac_forecast': '3',
                    'total_observed': '7',
                    'battles_observed': '2',
                    'erv_observed': '3',
                    'vac_observed': '2',
                    'timestamp': '1706745600'
                }
            ]
        }

        client = CastClient(api_key="test_key", email="test@example.com")
        result = client.get_data(country='Somalia', year=2025)

        assert len(result) == 1
        assert result[0]['country'] == 'Somalia'
        assert result[0]['admin1'] == 'Banadir'
        assert result[0]['year'] == 2025
        assert result[0]['total_forecast'] == 11
        assert result[0]['total_observed'] == 7
        assert result[0]['timestamp'] == 1706745600

        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        assert kwargs['params']['country'] == 'Somalia'
        assert kwargs['params']['year'] == '2025'


def test_get_data_with_fields():
    """Test that get_data passes the fields parameter."""
    with patch('acled.clients.cast_client.CastClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {'country': 'Somalia', 'total_forecast': '11'}
            ]
        }

        client = CastClient(api_key="test_key", email="test@example.com")
        result = client.get_data(fields='country|total_forecast')

        assert len(result) == 1
        _, kwargs = mock_get.call_args
        assert kwargs['params']['fields'] == 'country|total_forecast'


def test_parse_cast_forecast_partial_data():
    """Test parsing CAST data with missing fields (e.g. when using fields param)."""
    client = CastClient(api_key="test_key", email="test@example.com")

    data = {'country': 'Somalia', 'total_forecast': '15'}
    result = client._parse_cast_forecast(data)

    assert result['country'] == 'Somalia'
    assert result['total_forecast'] == 15
    assert 'year' not in result
    assert 'battles_forecast' not in result


def test_parse_cast_forecast_non_numeric_values():
    """Test parsing CAST data with non-numeric values in int fields."""
    client = CastClient(api_key="test_key", email="test@example.com")

    data = {'country': 'Somalia', 'year': 'not-a-number', 'total_forecast': '10'}
    result = client._parse_cast_forecast(data)

    assert result['country'] == 'Somalia'
    assert result['year'] == 'not-a-number'  # Kept as-is
    assert result['total_forecast'] == 10


def test_get_data_api_error():
    """Test that get_data raises ApiError on API failure."""
    with patch('acled.clients.cast_client.CastClient._get') as mock_get:
        mock_get.return_value = {
            'success': False,
            'error': [{'message': 'Unauthorized'}]
        }

        client = CastClient(api_key="test_key", email="test@example.com")

        with pytest.raises(ApiError, match="Unauthorized"):
            client.get_data()


def test_get_data_query_params():
    """Test that query_params with _where suffix are passed through."""
    with patch('acled.clients.cast_client.CastClient._get') as mock_get:
        mock_get.return_value = {'success': True, 'data': []}

        client = CastClient(api_key="test_key", email="test@example.com")
        client.get_data(
            total_forecast=10,
            query_params={'total_forecast_where': '>'}
        )

        _, kwargs = mock_get.call_args
        assert kwargs['params']['total_forecast'] == '10'
        assert kwargs['params']['total_forecast_where'] == '>'
