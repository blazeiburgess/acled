"""Integration tests for the ACLED client."""

import os
import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from acled import AcledClient


MOCK_EVENT_RESPONSE = {
    'success': True,
    'data': [
        {
            'event_id_cnty': 'TEST123',
            'event_date': '2023-01-01',
            'year': '2023',
            'time_precision': '1',
            'disorder_type': 'Political violence',
            'event_type': 'Battles',
            'sub_event_type': 'Armed clash',
            'actor1': 'Test Actor 1',
            'actor2': 'Test Actor 2',
            'country': 'Test Country',
            'latitude': '10.123',
            'longitude': '20.456',
            'fatalities': '5',
            'timestamp': '1672531200'
        }
    ]
}

MOCK_ACTOR_RESPONSE = {
    'success': True,
    'data': [
        {
            'mal_actor_id': 'AFRA00001',
            'label': 'Test Actor',
        }
    ]
}

MOCK_COUNTRY_RESPONSE = {
    'success': True,
    'data': [
        {
            'iso': 'TC',
            'name': 'TEST COUNTRY',
            'nicename': 'Test Country',
            'iso3': 'TST',
            'numcode': '999',
            'phonecode': 1
        }
    ]
}

MOCK_ERROR_RESPONSE = {
    'success': False,
    'error': [{'message': 'Not found'}]
}


@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    with patch('acled.clients.base_http_client.requests.Session') as mock_session:
        session_instance = MagicMock()

        def mock_get(url, **kwargs):
            response = MagicMock()
            response.status_code = 200
            response.content = b'{"success": true}'

            if '/acled/read' in url:
                response.json.return_value = MOCK_EVENT_RESPONSE
            elif '/actor/read' in url:
                response.json.return_value = MOCK_ACTOR_RESPONSE
            elif '/country/read' in url:
                response.json.return_value = MOCK_COUNTRY_RESPONSE
            else:
                response.status_code = 404
                response.json.return_value = MOCK_ERROR_RESPONSE

            return response

        session_instance.get.side_effect = mock_get
        mock_session.return_value = session_instance
        yield mock_session


@pytest.fixture
def client():
    """Create a client with test credentials."""
    with patch.dict(os.environ, {
        'ACLED_API_KEY': 'test_key',
        'ACLED_EMAIL': 'test@example.com'
    }):
        return AcledClient()


class TestIntegration:
    def test_get_data_integration(self, mock_session):
        """Test that the main client can retrieve ACLED data."""
        with patch.dict(os.environ, {'ACLED_API_KEY': 'test_key', 'ACLED_EMAIL': 'test@example.com'}):
            client = AcledClient()
        events = client.get_data(limit=10, country='Test Country')
        assert len(events) == 1
        assert events[0]['event_id_cnty'] == 'TEST123'
        assert events[0]['event_date'] == date(2023, 1, 1)
        assert events[0]['year'] == 2023

    def test_get_actor_data_integration(self, mock_session):
        """Test that the main client can retrieve actor data."""
        with patch.dict(os.environ, {'ACLED_API_KEY': 'test_key', 'ACLED_EMAIL': 'test@example.com'}):
            client = AcledClient()
        actors = client.get_actor_data(limit=10)
        assert len(actors) == 1
        assert actors[0]['label'] == 'Test Actor'

    def test_get_country_data_integration(self, mock_session):
        """Test that the main client can retrieve country data."""
        with patch.dict(os.environ, {'ACLED_API_KEY': 'test_key', 'ACLED_EMAIL': 'test@example.com'}):
            client = AcledClient()
        countries = client.get_country_data()
        assert len(countries) == 1
        assert countries[0]['nicename'] == 'Test Country'
        assert countries[0]['iso3'] == 'TST'

    def test_error_handling_integration(self, mock_session):
        """Test that errors are properly propagated through the client layers."""
        with patch.dict(os.environ, {'ACLED_API_KEY': 'test_key', 'ACLED_EMAIL': 'test@example.com'}):
            client = AcledClient()
        mock_session.return_value.get.side_effect = None
        response = MagicMock()
        response.status_code = 200
        response.content = b'{}'
        response.json.return_value = MOCK_ERROR_RESPONSE
        mock_session.return_value.get.return_value = response

        from acled.exceptions import ApiError
        with pytest.raises(ApiError):
            client.get_data(limit=10)
