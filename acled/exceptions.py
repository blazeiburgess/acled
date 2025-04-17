class ApiError(Exception):
    """
    Exception raised for errors returned by the API.
    """

class AcledMissingAuthError(ValueError):
    """
    Custom exception class for authentication-related errors in ACLED-related operations.
    """
