import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

import requests

from acled.clients.actor_client import ActorClient
from acled.models.enums import ExportType
from acled.exceptions import ApiError

@pytest.fixture
def mock_base_http_client():
    with patch('acled.clients.actor_client.BaseHttpClient') as mock_base:
        yield mock_base

@pytest.fixture
def client():
    return ActorClient(api_key="test_key", email="test@example.com")

@pytest.fixture
def mock_get_response():
    with patch.object(ActorClient, '_get') as mock_get:
        yield mock_get

class TestActorClient:
    def test_init(self):
        client = ActorClient(api_key="test_key", email="test@example.com")
        assert client.api_key == "test_key"
        assert client.email == "test@example.com"
        assert client.endpoint == "/actor/read"

    def test_get_data_success(self, client, mock_get_response):
        # Mock successful response
        mock_response = {
            'success': True,
            'data': [
                {
                    'actor_name': 'Test Actor',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '10'
                }
            ]
        }
        mock_get_response.return_value = mock_response

        # Call the method
        result = client.get_data(actor_name="Test Actor", limit=10)

        # Verify the result
        assert len(result) == 1
        assert result[0]['actor_name'] == 'Test Actor'
        assert result[0]['first_event_date'] == date(2023, 1, 1)
        assert result[0]['last_event_date'] == date(2023, 1, 31)
        assert result[0]['event_count'] == 10

        # Verify the API call
        mock_get_response.assert_called_once()
        args, kwargs = mock_get_response.call_args
        assert args[0] == "/actor/read"
        assert kwargs['params']['actor_name'] == 'Test Actor'
        assert kwargs['params']['limit'] == 10
        assert kwargs['params']['export_type'] == 'json'

    def test_get_data_with_date_objects(self, client, mock_get_response):
        # Mock successful response
        mock_response = {
            'success': True,
            'data': [
                {
                    'actor_name': 'Test Actor',
                    'first_event_date': '2023-01-01',
                    'last_event_date': '2023-01-31',
                    'event_count': '10'
                }
            ]
        }
        mock_get_response.return_value = mock_response

        # Call with date objects
        first_date = date(2023, 1, 1)
        last_date = date(2023, 1, 31)
        result = client.get_data(first_event_date=first_date, last_event_date=last_date)

        # Verify the API call
        args, kwargs = mock_get_response.call_args
        assert kwargs['params']['first_event_date'] == '2023-01-01'
        assert kwargs['params']['last_event_date'] == '2023-01-31'

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

    def test_parse_actor_success(self, client):
        # Test actor data parsing
        actor_data = {
            'actor_name': 'Test Actor',
            'first_event_date': '2023-01-01',
            'last_event_date': '2023-01-31',
            'event_count': '10'
        }

        result = client._parse_actor(actor_data)

        assert result['actor_name'] == 'Test Actor'
        assert result['first_event_date'] == date(2023, 1, 1)
        assert result['last_event_date'] == date(2023, 1, 31)
        assert result['event_count'] == 10

    def test_parse_actor_error(self, client):
        # Test parsing error handling
        actor_data = {
            'actor_name': 'Test Actor',
            'first_event_date': 'invalid-date',  # Invalid date format
            'last_event_date': '2023-01-31',
            'event_count': '10'
        }

        with pytest.raises(ValueError, match="Error parsing actor data"):
            client._parse_actor(actor_data)

    def test_all_parameters(self, client, mock_get_response):
        # Mock successful response
        mock_response = {
            'success': True,
            'data': []
        }
        mock_get_response.return_value = mock_response

        # Call with all parameters
        client.get_data(
            actor_name="Test Actor",
            first_event_date="2023-01-01",
            last_event_date="2023-01-31",
            event_count=10,
            export_type=ExportType.JSON,
            limit=10,
            page=1,
            query_params={"additional_param": "value"}
        )

        # Verify all parameters are passed correctly
        args, kwargs = mock_get_response.call_args
        params = kwargs['params']
        assert params['actor_name'] == 'Test Actor'
        assert params['first_event_date'] == '2023-01-01'
        assert params['last_event_date'] == '2023-01-31'
        assert params['event_count'] == '10'
        assert params['export_type'] == 'json'
        assert params['limit'] == '10'
        assert params['page'] == '1'
        assert params['additional_param'] == 'value'