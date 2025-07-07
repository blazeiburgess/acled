import pytest
from acled.clients.deleted_client import DeletedClient
from acled.clients.base_http_client import BaseHttpClient

def test_deleted_client_inheritance():
    """Test that DeletedClient inherits from BaseHttpClient."""
    client = DeletedClient(api_key="test_key", email="test@example.com")
    assert isinstance(client, BaseHttpClient)
    assert isinstance(client, DeletedClient)

def test_deleted_client_initialization():
    """Test that DeletedClient can be initialized with API credentials."""
    api_key = "test_key"
    email = "test@example.com"
    client = DeletedClient(api_key=api_key, email=email)
    assert client.api_key == api_key
    assert client.email == email