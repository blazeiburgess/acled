class ApiError(Exception):
    """
    Exception raised for errors returned by the API.
    """
    pass

class AcledMissingAuthError(ValueError):
    pass