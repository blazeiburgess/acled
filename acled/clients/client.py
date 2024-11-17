from typing import Optional

from .acled_data_client import AcledDataClient
from .actor_client import ActorClient
from .actor_type_client import ActorTypeClient
from .country_client import CountryClient
from .region_client import RegionClient


class AcledClient:
    """
    Main ACLED client that provides access to different API endpoints.

    This client aggregates several sub-clients to provide a relatively complete interface for
    interacting with the ACLED API. Each sub-client is responsible for a specific endpoint,
    making it easier to organize and manage the API interactions while still providing a
    single point of entry.

    Methods:
        get_data:
            Returns:
                Function to fetch the ACLED data.

        get_actor_data:
            Returns:
                Function to fetch the actor data.

        get_actor_type_data:
            Returns:
                Function to fetch the actor type data.

        get_country_data:
            Returns:
                Function to fetch country data.

        get_region_data:
            Returns:
                Function to fetch region data.
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            email: Optional[str] = None
    ):
        self._acled_data_client = AcledDataClient(api_key, email)
        self._actor_client = ActorClient(api_key, email)
        self._country_client = CountryClient(api_key, email)
        self._region_client = RegionClient(api_key, email)
        self._actor_type_client = ActorTypeClient(api_key, email)


    @property
    def get_data(self):
        return self._acled_data_client.get_data

    @property
    def get_actor_data(self):
        return self._actor_client.get_data

    @property
    def get_actor_type_data(self):
        return self._actor_type_client.get_data

    @property
    def get_country_data(self):
        return self._country_client.get_data

    @property
    def get_region_data(self):
        return self._region_client.get_data
