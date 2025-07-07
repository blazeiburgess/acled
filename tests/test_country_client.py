import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from acled.clients.country_client import CountryClient
from acled.models.enums import ExportType
from acled.exceptions import ApiError

def test_country_client_initialization():
    """Test that CountryClient can be initialized with API credentials."""
    api_key = "test_key"
    email = "test@example.com"
    client = CountryClient(api_key=api_key, email=email)
    assert client.api_key == api_key
    assert client.email == email
    assert client.endpoint == "/country/read"

def test_get_data_with_country():
    """Test that get_data correctly filters by country."""
    with patch('acled.clients.country_client.CountryClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'country': 'Yemen',
                    'iso': '887',
                    'iso3': 'YEM',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '100'
                }
            ]
        }
        
        client = CountryClient(api_key="test_key", email="test@example.com")
        result = client.get_data(country='Yemen')
        
        assert len(result) == 1
        assert result[0]['country'] == 'Yemen'
        assert result[0]['iso'] == 887
        assert result[0]['iso3'] == 'YEM'
        assert result[0]['first_event_date'] == date(2023, 1, 1)
        assert result[0]['last_event_date'] == date(2023, 1, 31)
        assert result[0]['event_count'] == 100
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['country'] == 'Yemen'

def test_get_data_with_iso():
    """Test that get_data correctly filters by ISO code."""
    with patch('acled.clients.country_client.CountryClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'country': 'Yemen',
                    'iso': '887',
                    'iso3': 'YEM',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '100'
                }
            ]
        }
        
        client = CountryClient(api_key="test_key", email="test@example.com")
        result = client.get_data(iso=887)
        
        assert len(result) == 1
        assert result[0]['iso'] == 887
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['iso'] == '887'

def test_get_data_with_iso3():
    """Test that get_data correctly filters by ISO3 code."""
    with patch('acled.clients.country_client.CountryClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'country': 'Yemen',
                    'iso': '887',
                    'iso3': 'YEM',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '100'
                }
            ]
        }
        
        client = CountryClient(api_key="test_key", email="test@example.com")
        result = client.get_data(iso3='YEM')
        
        assert len(result) == 1
        assert result[0]['iso3'] == 'YEM'
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['iso3'] == 'YEM'

def test_get_data_with_date_filters():
    """Test that get_data correctly filters by date fields."""
    with patch('acled.clients.country_client.CountryClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'country': 'Yemen',
                    'iso': '887',
                    'iso3': 'YEM',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '100'
                }
            ]
        }
        
        client = CountryClient(api_key="test_key", email="test@example.com")
        
        # Test with string dates
        result = client.get_data(
            first_event_date='2023-01-01',
            last_event_date='2023-01-31'
        )
        
        assert len(result) == 1
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['first_event_date'] == '2023-01-01'
        assert kwargs['params']['last_event_date'] == '2023-01-31'
        
        # Reset mock for next test
        mock_get.reset_mock()
        
        # Test with date objects
        result = client.get_data(
            first_event_date=date(2023, 1, 1),
            last_event_date=date(2023, 1, 31)
        )
        
        assert len(result) == 1
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['first_event_date'] == '2023-01-01'
        assert kwargs['params']['last_event_date'] == '2023-01-31'

def test_get_data_with_event_count():
    """Test that get_data correctly filters by event_count."""
    with patch('acled.clients.country_client.CountryClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'country': 'Yemen',
                    'iso': '887',
                    'iso3': 'YEM',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '100'
                }
            ]
        }
        
        client = CountryClient(api_key="test_key", email="test@example.com")
        result = client.get_data(event_count=100)
        
        assert len(result) == 1
        assert result[0]['event_count'] == 100
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['event_count'] == '100'

def test_get_data_with_export_type():
    """Test that get_data correctly sets the export_type."""
    with patch('acled.clients.country_client.CountryClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'country': 'Yemen',
                    'iso': '887',
                    'iso3': 'YEM',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '100'
                }
            ]
        }
        
        client = CountryClient(api_key="test_key", email="test@example.com")
        
        # Test with ExportType enum
        result = client.get_data(export_type=ExportType.JSON)
        
        assert len(result) == 1
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['export_type'] == 'json'
        
        # Reset mock for next test
        mock_get.reset_mock()
        
        # Test with string
        result = client.get_data(export_type='csv')
        
        assert len(result) == 1
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['export_type'] == 'csv'

def test_get_data_with_pagination():
    """Test that get_data correctly handles pagination parameters."""
    with patch('acled.clients.country_client.CountryClient._get') as mock_get:
        mock_get.return_value = {
            'success': True,
            'data': [
                {
                    'country': 'Yemen',
                    'iso': '887',
                    'iso3': 'YEM',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '100'
                }
            ]
        }
        
        client = CountryClient(api_key="test_key", email="test@example.com")
        result = client.get_data(limit=10, page=2)
        
        assert len(result) == 1
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['limit'] == '10'
        assert kwargs['params']['page'] == '2'

def test_get_data_with_api_error():
    """Test that get_data correctly handles API errors."""
    with patch('acled.clients.country_client.CountryClient._get') as mock_get:
        mock_get.return_value = {
            'success': False,
            'error': [{'message': 'Test error message'}]
        }
        
        client = CountryClient(api_key="test_key", email="test@example.com")
        
        with pytest.raises(ApiError) as excinfo:
            client.get_data()
        
        assert "API Error: Test error message" in str(excinfo.value)