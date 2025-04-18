import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

import requests

from acled.clients.acled_data_client import AcledDataClient
from acled.models.enums import ExportType
from acled.exceptions import ApiError

@pytest.fixture
def mock_base_http_client():
    with patch('acled.clients.acled_data_client.BaseHttpClient') as mock_base:
        yield mock_base

@pytest.fixture
def client():
    return AcledDataClient(api_key="test_key", email="test@example.com")

@pytest.fixture
def mock_get_response():
    with patch.object(AcledDataClient, '_get') as mock_get:
        yield mock_get

class TestAcledDataClient:
    def test_init(self):
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        assert client.api_key == "test_key"
        assert client.email == "test@example.com"
        assert client.endpoint == "/acled/read"

    def test_get_data_success(self, client, mock_get_response):
        # Mock successful response
        mock_response = {
            'success': True,
            'data': [
                {
                    'event_id_cnty': 'TEST123',
                    'event_date': '2023-01-01',
                    'year': '2023',
                    'time_precision': '1',
                    'latitude': '10.123',
                    'longitude': '20.456',
                    'fatalities': '5',
                    'timestamp': '1672531200'  # 2023-01-01 00:00:00
                }
            ]
        }
        mock_get_response.return_value = mock_response

        # Call the method
        result = client.get_data(event_id_cnty="TEST123", limit=10)

        # Verify the result
        assert len(result) == 1
        assert result[0]['event_id_cnty'] == 'TEST123'
        assert result[0]['event_date'] == date(2023, 1, 1)
        assert result[0]['year'] == 2023
        assert result[0]['time_precision'] == 1
        assert result[0]['latitude'] == 10.123
        assert result[0]['longitude'] == 20.456
        assert result[0]['fatalities'] == 5
        assert isinstance(result[0]['timestamp'], datetime)

        # Verify the API call
        mock_get_response.assert_called_once()
        args, kwargs = mock_get_response.call_args
        assert args[0] == "/acled/read"
        assert kwargs['params']['event_id_cnty'] == 'TEST123'
        assert kwargs['params']['limit'] == 10
        assert kwargs['params']['export_type'] == 'json'

    def test_get_data_with_date_objects(self, client, mock_get_response):
        # Mock successful response
        mock_response = {
            'success': True,
            'data': [
                {
                    'event_id_cnty': 'TEST123',
                    'event_date': '2023-01-01',
                    'year': '2023',
                    'time_precision': '1',
                    'latitude': '10.123',
                    'longitude': '20.456',
                    'fatalities': '5',
                    'timestamp': '1672531200'  # 2023-01-01 00:00:00
                }
            ]
        }
        mock_get_response.return_value = mock_response

        # Call with date objects
        test_date = date(2023, 1, 1)
        result = client.get_data(event_date=test_date, timestamp=test_date)

        # Verify the API call
        args, kwargs = mock_get_response.call_args
        assert kwargs['params']['event_date'] == '2023-01-01'
        assert kwargs['params']['timestamp'] == '2023-01-01'

    def test_get_data_with_export_type_enum(self, client, mock_get_response):
        # Mock successful response
        mock_response = {
            'success': True,
            'data': []
        }
        mock_get_response.return_value = mock_response

        # Call with ExportType enum
        client.get_data(export_type=ExportType.CSV)

        # Verify the API call
        args, kwargs = mock_get_response.call_args
        assert kwargs['params']['export_type'] == 'csv'

    def test_get_data_api_error(self, client, mock_get_response):
        # Mock error response
        mock_response = {
            'success': False,
            'error': [{'message': 'Test error message'}]
        }
        mock_get_response.return_value = mock_response

        # Verify that ApiError is raised
        with pytest.raises(ApiError, match="API Error: Test error message"):
            client.get_data()

    def test_get_data_http_error(self, client, mock_get_response):
        # Mock HTTP error
        mock_get_response.side_effect = requests.HTTPError("Test HTTP error")

        # Verify that ApiError is raised
        with pytest.raises(ApiError, match="HTTP Error: Test HTTP error"):
            client.get_data()

    def test_parse_event_success(self, client):
        # Test event data parsing
        event_data = {
            'event_id_cnty': 'TEST123',
            'event_date': '2023-01-01',
            'year': '2023',
            'time_precision': '1',
            'latitude': '10.123',
            'longitude': '20.456',
            'fatalities': '5',
            'timestamp': '1672531200'  # 2023-01-01 00:00:00
        }

        result = client._parse_event(event_data)

        assert result['event_id_cnty'] == 'TEST123'
        assert result['event_date'] == date(2023, 1, 1)
        assert result['year'] == 2023
        assert result['time_precision'] == 1
        assert result['latitude'] == 10.123
        assert result['longitude'] == 20.456
        assert result['fatalities'] == 5
        assert isinstance(result['timestamp'], datetime)

    def test_parse_event_error(self, client):
        # Test parsing error handling
        event_data = {
            'event_id_cnty': 'TEST123',
            'event_date': 'invalid-date',  # Invalid date format
            'year': '2023',
            'timestamp': '1672531200'
        }

        with pytest.raises(ValueError, match="Error parsing event data"):
            client._parse_event(event_data)

    def test_all_parameters(self, client, mock_get_response):
        # Mock successful response
        mock_response = {
            'success': True,
            'data': []
        }
        mock_get_response.return_value = mock_response

        # Call with all parameters
        client.get_data(
            event_id_cnty="TEST123",
            event_date="2023-01-01",
            year=2023,
            time_precision=1,
            disorder_type="Test",
            event_type="Test",
            sub_event_type="Test",
            actor1="Test",
            assoc_actor_1="Test",
            inter1=1,
            actor2="Test",
            assoc_actor_2="Test",
            inter2=1,
            interaction=1,
            civilian_targeting="Test",
            iso=1,
            region=1,
            country="Test",
            admin1="Test",
            admin2="Test",
            admin3="Test",
            location="Test",
            latitude=10.123,
            longitude=20.456,
            geo_precision=1,
            source="Test",
            source_scale="Test",
            notes="Test",
            fatalities=5,
            timestamp="2023-01-01",
            export_type=ExportType.JSON,
            limit=10,
            page=1
        )

        # Verify all parameters are passed correctly
        args, kwargs = mock_get_response.call_args
        params = kwargs['params']
        assert params['event_id_cnty'] == 'TEST123'
        assert params['event_date'] == '2023-01-01'
        assert params['year'] == '2023'
        assert params['time_precision'] == '1'
        assert params['disorder_type'] == 'Test'
        assert params['event_type'] == 'Test'
        assert params['sub_event_type'] == 'Test'
        assert params['actor1'] == 'Test'
        assert params['assoc_actor_1'] == 'Test'
        assert params['inter1'] == '1'
        assert params['actor2'] == 'Test'
        assert params['assoc_actor_2'] == 'Test'
        assert params['inter2'] == '1'
        assert params['interaction'] == '1'
        assert params['civilian_targeting'] == 'Test'
        assert params['iso'] == '1'
        assert params['region'] == '1'
        assert params['country'] == 'Test'
        assert params['admin1'] == 'Test'
        assert params['admin2'] == 'Test'
        assert params['admin3'] == 'Test'
        assert params['location'] == 'Test'
        assert params['latitude'] == '10.123'
        assert params['longitude'] == '20.456'
        assert params['geo_precision'] == '1'
        assert params['source'] == 'Test'
        assert params['source_scale'] == 'Test'
        assert params['notes'] == 'Test'
        assert params['fatalities'] == '5'
        assert params['timestamp'] == '2023-01-01'
        assert params['export_type'] == 'json'
        assert params['limit'] == 10
        assert params['page'] == 1