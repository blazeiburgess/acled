import pytest
from acled.exceptions import (
    ApiError,
    AcledMissingAuthError,
    NetworkError,
    TimeoutError,
    RateLimitError,
    RetryError,
    ServerError,
    ClientError
)

def test_api_error():
    """Test that ApiError can be instantiated and raised."""
    error_message = "Test API error"
    with pytest.raises(ApiError) as excinfo:
        raise ApiError(error_message)
    assert str(excinfo.value) == error_message

def test_acled_missing_auth_error():
    """Test that AcledMissingAuthError can be instantiated and raised."""
    error_message = "Missing authentication credentials"
    with pytest.raises(AcledMissingAuthError) as excinfo:
        raise AcledMissingAuthError(error_message)
    assert str(excinfo.value) == error_message
    # Verify it's a subclass of ValueError
    assert isinstance(excinfo.value, ValueError)

def test_network_error():
    """Test that NetworkError can be instantiated and raised."""
    error_message = "Network connectivity issue"
    with pytest.raises(NetworkError) as excinfo:
        raise NetworkError(error_message)
    assert str(excinfo.value) == error_message
    # Verify it's a subclass of ApiError
    assert isinstance(excinfo.value, ApiError)

def test_timeout_error():
    """Test that TimeoutError can be instantiated and raised."""
    error_message = "Request timed out"
    with pytest.raises(TimeoutError) as excinfo:
        raise TimeoutError(error_message)
    assert str(excinfo.value) == error_message
    # Verify it's a subclass of ApiError
    assert isinstance(excinfo.value, ApiError)

def test_rate_limit_error():
    """Test that RateLimitError can be instantiated and raised."""
    error_message = "Rate limit exceeded"
    with pytest.raises(RateLimitError) as excinfo:
        raise RateLimitError(error_message)
    assert str(excinfo.value) == error_message
    # Verify it's a subclass of ApiError
    assert isinstance(excinfo.value, ApiError)

def test_retry_error():
    """Test that RetryError can be instantiated and raised."""
    error_message = "Maximum retry attempts exhausted"
    with pytest.raises(RetryError) as excinfo:
        raise RetryError(error_message)
    assert str(excinfo.value) == error_message
    # Verify it's a subclass of ApiError
    assert isinstance(excinfo.value, ApiError)

def test_server_error():
    """Test that ServerError can be instantiated and raised."""
    error_message = "Server error (5xx)"
    with pytest.raises(ServerError) as excinfo:
        raise ServerError(error_message)
    assert str(excinfo.value) == error_message
    # Verify it's a subclass of ApiError
    assert isinstance(excinfo.value, ApiError)

def test_client_error():
    """Test that ClientError can be instantiated and raised."""
    error_message = "Client error (4xx)"
    with pytest.raises(ClientError) as excinfo:
        raise ClientError(error_message)
    assert str(excinfo.value) == error_message
    # Verify it's a subclass of ApiError
    assert isinstance(excinfo.value, ApiError)