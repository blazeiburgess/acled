import pytest
from unittest.mock import patch, MagicMock
import os
from datetime import date, datetime

from acled.clients import AcledClient
from acled.clients.acled_data_client import AcledDataClient
from acled.clients.actor_client import ActorClient
from acled.exceptions import ApiError, AcledMissingAuthError

class TestInputValidation:
    def test_missing_api_key(self):
        """Test that an error is raised when API key is missing"""
        with patch.dict(os.environ, {'ACLED_EMAIL': 'test@example.com'}, clear=True):
            with pytest.raises(AcledMissingAuthError, match="API key is required"):
                AcledClient()

    def test_missing_email(self):
        """Test that an error is raised when email is missing"""
        with patch.dict(os.environ, {'ACLED_API_KEY': 'test_key'}, clear=True):
            with pytest.raises(AcledMissingAuthError, match="Email is required"):
                AcledClient()

    def test_invalid_date_format(self):
        """Test handling of invalid date format"""
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        
        # Mock the _get method to avoid actual API calls
        with patch.object(AcledDataClient, '_get') as mock_get:
            mock_get.return_value = {'success': True, 'data': []}
            
            # Test with invalid date format
            client.get_data(event_date="invalid-date-format")
            
            # Verify the parameter was passed as is (validation happens on API side)
            args, kwargs = mock_get.call_args
            assert kwargs['params']['event_date'] == 'invalid-date-format'

    def test_invalid_numeric_parameters(self):
        """Test handling of invalid numeric parameters"""
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        
        # Mock the _get method to avoid actual API calls
        with patch.object(AcledDataClient, '_get') as mock_get:
            mock_get.return_value = {'success': True, 'data': []}
            
            # Test with invalid numeric values
            client.get_data(year="not-a-number", fatalities="not-a-number")
            
            # Verify the parameters were converted to strings
            args, kwargs = mock_get.call_args
            assert kwargs['params']['year'] == 'not-a-number'
            assert kwargs['params']['fatalities'] == 'not-a-number'

    def test_empty_parameters(self):
        """Test handling of empty parameters"""
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        
        # Mock the _get method to avoid actual API calls
        with patch.object(AcledDataClient, '_get') as mock_get:
            mock_get.return_value = {'success': True, 'data': []}
            
            # Test with empty parameters
            client.get_data(event_id_cnty="", country="")
            
            # Verify empty strings are passed as is
            args, kwargs = mock_get.call_args
            assert kwargs['params']['event_id_cnty'] == ''
            assert kwargs['params']['country'] == ''

    def test_none_parameters_not_included(self):
        """Test that None parameters are not included in the request"""
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        
        # Mock the _get method to avoid actual API calls
        with patch.object(AcledDataClient, '_get') as mock_get:
            mock_get.return_value = {'success': True, 'data': []}
            
            # Test with None parameters
            client.get_data(event_id_cnty=None, country=None)
            
            # Verify None parameters are not included
            args, kwargs = mock_get.call_args
            assert 'event_id_cnty' not in kwargs['params']
            assert 'country' not in kwargs['params']

    def test_api_error_handling(self):
        """Test handling of API errors"""
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        
        # Mock the _get method to return an error
        with patch.object(AcledDataClient, '_get') as mock_get:
            mock_get.return_value = {
                'success': False,
                'error': [{'message': 'Invalid parameter'}]
            }
            
            # Test that ApiError is raised with the correct message
            with pytest.raises(ApiError, match="API Error: Invalid parameter"):
                client.get_data()

    def test_http_error_handling(self):
        """Test handling of HTTP errors"""
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        
        # Mock the _get method to raise an HTTPError
        with patch.object(AcledDataClient, '_get') as mock_get:
            mock_get.side_effect = Exception("HTTP Error")
            
            # Test that ApiError is raised with the correct message
            with pytest.raises(Exception):
                client.get_data()

    def test_invalid_event_date_range(self):
        """Test handling of invalid event date range"""
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        
        # Mock the _get method to avoid actual API calls
        with patch.object(AcledDataClient, '_get') as mock_get:
            mock_get.return_value = {'success': True, 'data': []}
            
            # Test with invalid date range format
            client.get_data(event_date="2023-01-01|invalid-date")
            
            # Verify the parameter was passed as is (validation happens on API side)
            args, kwargs = mock_get.call_args
            assert kwargs['params']['event_date'] == '2023-01-01|invalid-date'

    def test_actor_client_invalid_parameters(self):
        """Test handling of invalid parameters in ActorClient"""
        client = ActorClient(api_key="test_key", email="test@example.com")
        
        # Mock the _get method to avoid actual API calls
        with patch.object(ActorClient, '_get') as mock_get:
            mock_get.return_value = {'success': True, 'data': []}
            
            # Test with invalid parameters
            client.get_data(
                actor_name='123',  # Should be converted to string
                first_event_date="invalid-date",
                event_count="not-a-number"
            )
            
            # Verify the parameters were handled appropriately
            args, kwargs = mock_get.call_args
            assert kwargs['params']['actor_name'] == '123'
            assert kwargs['params']['first_event_date'] == 'invalid-date'
            assert kwargs['params']['event_count'] == 'not-a-number'

    def test_parse_event_missing_required_fields(self):
        """Test parsing event data with missing required fields"""
        client = AcledDataClient(api_key="test_key", email="test@example.com")
        
        # Test with missing required fields
        event_data = {
            'event_id_cnty': 'TEST123',
            # Missing event_date
            'year': '2023',
            'timestamp': '1672531200'
        }
        
        with pytest.raises(ValueError, match="Error parsing event data"):
            client._parse_event(event_data)

    def test_parse_actor_missing_required_fields(self):
        """Test parsing actor data with missing required fields"""
        client = ActorClient(api_key="test_key", email="test@example.com")
        
        # Test with missing required fields
        actor_data = {
            'actor_name': 'Test Actor',
            # Missing first_event_date
            'last_event_date': '2023-01-31',
            'event_count': '10'
        }
        
        with pytest.raises(ValueError, match="Error parsing actor data"):
            client._parse_actor(actor_data)