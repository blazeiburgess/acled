"""Exception classes for the ACLED package.

This module defines custom exception classes used throughout the ACLED package
to handle various error conditions, including API errors, authentication issues,
network problems, and rate limiting.
"""


class ApiError(Exception):
    """
    Exception raised for errors returned by the API.
    """


class AcledMissingAuthError(ValueError):
    """
    Custom exception class for authentication-related errors in ACLED-related operations.
    """


class NetworkError(ApiError):
    """
    Exception raised for network connectivity issues.
    """


class TimeoutError(ApiError):
    """
    Exception raised when a request times out.
    """


class RateLimitError(ApiError):
    """
    Exception raised when API rate limits are exceeded.
    """


class RetryError(ApiError):
    """
    Exception raised when maximum retry attempts are exhausted.
    """


class ServerError(ApiError):
    """
    Exception raised for 5xx server errors.
    """


class ClientError(ApiError):
    """
    Exception raised for 4xx client errors.
    """
