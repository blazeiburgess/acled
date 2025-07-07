"""Client module for presumably accessing deleted data from the ACLED API.

This module provides a client for retrieving information about deleted records
from the ACLED database.
"""

from acled.clients import BaseHttpClient


class DeletedClient(BaseHttpClient):
    """Client for presumably accessing deleted data from the ACLED API.

    This class provides methods to retrieve information about records that have
    been deleted from the ACLED database.
    """
    pass
