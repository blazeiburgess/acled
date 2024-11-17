from typing import Optional

from .acled_data_client import AcledDataClient
from .actor_client import ActorClient
from .actor_type_client import ActorTypeClient
from .country_client import CountryClient
from .region_client import RegionClient


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
        self.actor_client = ActorClient(api_key, email)
        self.country_client = CountryClient(api_key, email)
        self.region_client = RegionClient(api_key, email)
        self.actor_type_client = ActorTypeClient(api_key, email)


    @property
    def get_data(self):
        return self.acled_data_client.get_data

    @property
    def get_actor_data(self):
        return self.actor_client.get_data

    @property
    def get_actor_type_data(self):
        return self.actor_type_client.get_data

    @property
    def get_country_data(self):
        return self.country_client.get_data

    @property
    def get_region_data(self):
        return self.region_client.get_data
