"""Main client module for the ACLED API.

This module provides the primary client interface for the ACLED API wrapper.
It aggregates all specialized clients into a single, unified interface,
allowing users to access all ACLED API endpoints through a single client instance.
This simplifies usage and provides a consistent entry point for all API interactions.
"""

from typing import Optional

from acled.clients.acled_data_client import AcledDataClient
from acled.clients.actor_client import ActorClient
from acled.clients.actor_type_client import ActorTypeClient
from acled.clients.country_client import CountryClient
from acled.clients.region_client import RegionClient


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
        """Returns the get_data method from the AcledDataClient.

        Returns:
            Callable: A method to fetch ACLED event data with various filters.
        """
        return self._acled_data_client.get_data

    @property
    def get_actor_data(self):
        """Returns the get_data method from the ActorClient.

        Returns:
            Callable: A method to fetch ACLED actor data with various filters.
        """
        return self._actor_client.get_data

    @property
    def get_actor_type_data(self):
        """Returns the get_data method from the ActorTypeClient.

        Returns:
            Callable: A method to fetch ACLED actor type data with various filters.
        """
        return self._actor_type_client.get_data

    @property
    def get_country_data(self):
        """Returns the get_data method from the CountryClient.

        Returns:
            Callable: A method to fetch ACLED country data with various filters.
        """
        return self._country_client.get_data

    @property
    def get_region_data(self):
        """Returns the get_data method from the RegionClient.

        Returns:
            Callable: A method to fetch ACLED region data with various filters.
        """
        return self._region_client.get_data
