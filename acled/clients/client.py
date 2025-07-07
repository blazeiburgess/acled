"""Main client module for the ACLED API.

This module provides the primary client interface for the ACLED API wrapper.
It aggregates all specialized clients into a single, unified interface,
allowing users to access all ACLED API endpoints through a single client instance.
This simplifies usage and provides a consistent entry point for all API interactions.
"""

from typing import Optional, Any, Dict, List, Union
from datetime import datetime, date

from acled.clients.acled_data_client import AcledDataClient
from acled.clients.actor_client import ActorClient
from acled.clients.actor_type_client import ActorTypeClient
from acled.clients.country_client import CountryClient
from acled.clients.region_client import RegionClient
from acled.models import AcledEvent, Actor, ActorType, Country, Region
from acled.models.enums import ExportType


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


    def get_data(
        self,
        event_id_cnty: Optional[str] = None,
        event_date: Optional[Union[str, date]] = None,
        year: Optional[int] = None,
        time_precision: Optional[int] = None,
        disorder_type: Optional[str] = None,
        event_type: Optional[str] = None,
        sub_event_type: Optional[str] = None,
        actor1: Optional[str] = None,
        assoc_actor_1: Optional[str] = None,
        inter1: Optional[int] = None,
        actor2: Optional[str] = None,
        assoc_actor_2: Optional[str] = None,
        inter2: Optional[int] = None,
        interaction: Optional[int] = None,
        civilian_targeting: Optional[str] = None,
        iso: Optional[int] = None,
        region: Optional[int] = None,
        country: Optional[str] = None,
        admin1: Optional[str] = None,
        admin2: Optional[str] = None,
        admin3: Optional[str] = None,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        geo_precision: Optional[int] = None,
        source: Optional[str] = None,
        source_scale: Optional[str] = None,
        notes: Optional[str] = None,
        fatalities: Optional[int] = None,
        timestamp: Optional[Union[int, str, date]] = None,
        export_type: Optional[Union[str, ExportType]] = ExportType.JSON,
        limit: int = 50,
        page: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> List[AcledEvent]:
        """
        Retrieves ACLED data based on the provided filters.

        Args:
            event_id_cnty (Optional[str]): Filter by event ID country (supports LIKE).
            event_date (Optional[Union[str, date]]): Filter by event date (format 'yyyy-mm-dd').
            year (Optional[int]): Filter by year.
            time_precision (Optional[int]): Filter by time precision.
            disorder_type (Optional[str]): Filter by disorder type (supports LIKE).
            event_type (Optional[str]): Filter by event type (supports LIKE).
            sub_event_type (Optional[str]): Filter by sub-event type (supports LIKE).
            actor1 (Optional[str]): Filter by actor1 (supports LIKE).
            assoc_actor_1 (Optional[str]): Filter by associated actor1 (supports LIKE).
            inter1 (Optional[int]): Filter by inter1 code.
            actor2 (Optional[str]): Filter by actor2 (supports LIKE).
            assoc_actor_2 (Optional[str]): Filter by associated actor2 (supports LIKE).
            inter2 (Optional[int]): Filter by inter2 code.
            interaction (Optional[int]): Filter by interaction code.
            civilian_targeting (Optional[str]): Filter by civilian targeting (supports LIKE).
            iso (Optional[int]): Filter by ISO country code.
            region (Optional[int]): Filter by region number.
            country (Optional[str]): Filter by country name.
            admin1 (Optional[str]): Filter by admin1 (supports LIKE).
            admin2 (Optional[str]): Filter by admin2 (supports LIKE).
            admin3 (Optional[str]): Filter by admin3 (supports LIKE).
            location (Optional[str]): Filter by location (supports LIKE).
            latitude (Optional[float]): Filter by latitude.
            longitude (Optional[float]): Filter by longitude.
            geo_precision (Optional[int]): Filter by geographic precision.
            source (Optional[str]): Filter by source (supports LIKE).
            source_scale (Optional[str]): Filter by source scale (supports LIKE).
            notes (Optional[str]): Filter by notes (supports LIKE).
            fatalities (Optional[int]): Filter by number of fatalities.
            timestamp (Optional[Union[int, str, date]]): Filter by timestamp (>= value).
            export_type (Optional[Union[str, ExportType]]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters (e.g., to use '_where' suffix).

        Returns:
            List[AcledEvent]: A list of ACLED events matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
            NetworkError: For network connectivity issues.
            TimeoutError: When the request times out.
            RateLimitError: When API rate limits are exceeded.
            ServerError: For 5xx server errors.
            ClientError: For 4xx client errors.
            RetryError: When maximum retry attempts are exhausted.
        """
        return self._acled_data_client.get_data(
            event_id_cnty=event_id_cnty,
            event_date=event_date,
            year=year,
            time_precision=time_precision,
            disorder_type=disorder_type,
            event_type=event_type,
            sub_event_type=sub_event_type,
            actor1=actor1,
            assoc_actor_1=assoc_actor_1,
            inter1=inter1,
            actor2=actor2,
            assoc_actor_2=assoc_actor_2,
            inter2=inter2,
            interaction=interaction,
            civilian_targeting=civilian_targeting,
            iso=iso,
            region=region,
            country=country,
            admin1=admin1,
            admin2=admin2,
            admin3=admin3,
            location=location,
            latitude=latitude,
            longitude=longitude,
            geo_precision=geo_precision,
            source=source,
            source_scale=source_scale,
            notes=notes,
            fatalities=fatalities,
            timestamp=timestamp,
            export_type=export_type,
            limit=limit,
            page=page,
            query_params=query_params,
        )

    def get_actor_data(
        self,
        actor_name: Optional[str] = None,
        first_event_date: Optional[Union[str, date]] = None,
        last_event_date: Optional[Union[str, date]] = None,
        event_count: Optional[int] = None,
        export_type: Optional[Union[str, ExportType]] = ExportType.JSON,
        limit: int = 50,
        page: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> List[Actor]:
        """
        Retrieves Actor data based on the provided filters.

        Args:
            actor_name (Optional[str]): Filter by actor name (supports LIKE).
            first_event_date (Optional[Union[str, date]]): Filter by first event date (format 'yyyy-mm-dd').
            last_event_date (Optional[Union[str, date]]): Filter by last event date (format 'yyyy-mm-dd').
            event_count (Optional[int]): Filter by event count.
            export_type (Optional[Union[str, ExportType]]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters.

        Returns:
            List[Actor]: A list of Actors matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
            NetworkError: For network connectivity issues.
            TimeoutError: When the request times out.
            RateLimitError: When API rate limits are exceeded.
            ServerError: For 5xx server errors.
            ClientError: For 4xx client errors.
            RetryError: When maximum retry attempts are exhausted.
        """
        return self._actor_client.get_data(
            actor_name=actor_name,
            first_event_date=first_event_date,
            last_event_date=last_event_date,
            event_count=event_count,
            export_type=export_type,
            limit=limit,
            page=page,
            query_params=query_params,
        )

    def get_actor_type_data(
        self,
        actor_type_id: Optional[int] = None,
        actor_type_name: Optional[str] = None,
        first_event_date: Optional[Union[str, date]] = None,
        last_event_date: Optional[Union[str, date]] = None,
        event_count: Optional[int] = None,
        export_type: Optional[Union[str, ExportType]] = ExportType.JSON,
        limit: int = 50,
        page: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> List[ActorType]:
        """
        Retrieves Actor Type data based on the provided filters.

        Args:
            actor_type_id (Optional[int]): Filter by actor type ID.
            actor_type_name (Optional[str]): Filter by actor type name (supports LIKE).
            first_event_date (Optional[Union[str, date]]): Filter by first event date (format 'yyyy-mm-dd').
            last_event_date (Optional[Union[str, date]]): Filter by last event date (format 'yyyy-mm-dd').
            event_count (Optional[int]): Filter by event count (default query is >=).
            export_type (Optional[Union[str, ExportType]]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters.

        Returns:
            List[ActorType]: A list of Actor Types matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
            NetworkError: For network connectivity issues.
            TimeoutError: When the request times out.
            RateLimitError: When API rate limits are exceeded.
            ServerError: For 5xx server errors.
            ClientError: For 4xx client errors.
            RetryError: When maximum retry attempts are exhausted.
        """
        return self._actor_type_client.get_data(
            actor_type_id=actor_type_id,
            actor_type_name=actor_type_name,
            first_event_date=first_event_date,
            last_event_date=last_event_date,
            event_count=event_count,
            export_type=export_type,
            limit=limit,
            page=page,
            query_params=query_params,
        )

    def get_country_data(
        self,
        country: Optional[str] = None,
        iso: Optional[int] = None,
        iso3: Optional[str] = None,
        first_event_date: Optional[Union[str, date]] = None,
        last_event_date: Optional[Union[str, date]] = None,
        event_count: Optional[int] = None,
        export_type: Optional[Union[str, ExportType]] = ExportType.JSON,
        limit: int = 50,
        page: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> List[Country]:
        """
        Retrieves Country data based on the provided filters.

        Args:
            country (Optional[str]): Filter by country name (supports LIKE).
            iso (Optional[int]): Filter by ISO country code.
            iso3 (Optional[str]): Filter by ISO3 country code.
            first_event_date (Optional[Union[str, date]]): Filter by first event date (format 'yyyy-mm-dd').
            last_event_date (Optional[Union[str, date]]): Filter by last event date (format 'yyyy-mm-dd').
            event_count (Optional[int]): Filter by event count (default query is >=).
            export_type (Optional[Union[str, ExportType]]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters.

        Returns:
            List[Country]: A list of Countries matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
            NetworkError: For network connectivity issues.
            TimeoutError: When the request times out.
            RateLimitError: When API rate limits are exceeded.
            ServerError: For 5xx server errors.
            ClientError: For 4xx client errors.
            RetryError: When maximum retry attempts are exhausted.
        """
        return self._country_client.get_data(
            country=country,
            iso=iso,
            iso3=iso3,
            first_event_date=first_event_date,
            last_event_date=last_event_date,
            event_count=event_count,
            export_type=export_type,
            limit=limit,
            page=page,
            query_params=query_params,
        )

    def get_region_data(
        self,
        region: Optional[int] = None,
        region_name: Optional[str] = None,
        first_event_date: Optional[Union[str, date]] = None,
        last_event_date: Optional[Union[str, date]] = None,
        event_count: Optional[int] = None,
        export_type: Optional[Union[str, ExportType]] = ExportType.JSON,
        limit: int = 50,
        page: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> List[Region]:
        """
        Retrieves Region data based on the provided filters.

        Args:
            region (Optional[int]): Filter by region ID.
            region_name (Optional[str]): Filter by region name (supports LIKE).
            first_event_date (Optional[Union[str, date]]): Filter by first event date (format 'yyyy-mm-dd').
            last_event_date (Optional[Union[str, date]]): Filter by last event date (format 'yyyy-mm-dd').
            event_count (Optional[int]): Filter by event count (default query is >=).
            export_type (Optional[Union[str, ExportType]]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters.

        Returns:
            List[Region]: A list of Regions matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
            NetworkError: For network connectivity issues.
            TimeoutError: When the request times out.
            RateLimitError: When API rate limits are exceeded.
            ServerError: For 5xx server errors.
            ClientError: For 4xx client errors.
            RetryError: When maximum retry attempts are exhausted.
        """
        return self._region_client.get_data(
            region=region,
            region_name=region_name,
            first_event_date=first_event_date,
            last_event_date=last_event_date,
            event_count=event_count,
            export_type=export_type,
            limit=limit,
            page=page,
            query_params=query_params,
        )
