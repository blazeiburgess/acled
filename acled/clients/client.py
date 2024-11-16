from typing import Optional

from .acled_data_client import AcledDataClient


class AcledClient:
    """
    Main ACLED client that provides access to different API endpoints.
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            email: Optional[str] = None
    ):
        self.api_key = api_key
        self.email = email
        self.acled_data_client = AcledDataClient(api_key, email)


    @property
    def get_data(self):
        return self.acled_data_client.get_data

