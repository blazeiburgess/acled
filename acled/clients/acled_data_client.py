"""Client module for accessing the main ACLED dataset.

This module provides a client for retrieving event data from the ACLED database.
It allows filtering by numerous criteria such as event type, date, location,
actors involved, and many other attributes to retrieve specific conflict and
disorder events from around the world.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from datetime import datetime, date, timezone

from acled.clients.base_http_client import BaseHttpClient
from acled.models import AcledEvent
from acled.models.enums import ResponseFormat
from acled.exceptions import ApiError, NetworkError, TimeoutError, RateLimitError, RetryError, ServerError, ClientError


class AcledDataClient(BaseHttpClient):
    """
    Client for interacting with the ACLED main dataset endpoint.
    """

    def __init__(self, **kwargs):
        """Initialize the ACLED data client.
        
        Args:
            **kwargs: Authentication parameters passed to BaseHttpClient
        """
        super().__init__(**kwargs)
        self.endpoint = "/acled/read"

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
        tags: Optional[str] = None,
        timestamp: Optional[Union[int, str, date]] = None,
        fields: Optional[str] = None,
        export_type: Optional[str] = None,
        response_format: Optional[Union[str, ResponseFormat]] = ResponseFormat.JSON,
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
            tags (Optional[str]): Filter by tags (supports LIKE).
            timestamp (Optional[Union[int, str, date]]): Filter by timestamp (>= value).
            fields (Optional[str]): Pipe-separated list of fields to return (e.g. 'country|event_date|fatalities').
            export_type (Optional[str]): Data structure format — 'dyadic' (default) or 'monadic'.
            response_format (Optional[Union[str, ResponseFormat]]): Response serialization format ('json', 'csv', etc.).
            limit (int): Number of records to retrieve (default: 50; API default is 5000).
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
        # Create a dictionary of all parameters that aren't None
        params = {
            'event_id_cnty': event_id_cnty,
            'event_date': event_date,
            'year': year,
            'time_precision': time_precision,
            'disorder_type': disorder_type,
            'event_type': event_type,
            'sub_event_type': sub_event_type,
            'actor1': actor1,
            'assoc_actor_1': assoc_actor_1,
            'inter1': inter1,
            'actor2': actor2,
            'assoc_actor_2': assoc_actor_2,
            'inter2': inter2,
            'interaction': interaction,
            'civilian_targeting': civilian_targeting,
            'iso': iso,
            'region': region,
            'country': country,
            'admin1': admin1,
            'admin2': admin2,
            'admin3': admin3,
            'location': location,
            'latitude': latitude,
            'longitude': longitude,
            'geo_precision': geo_precision,
            'source': source,
            'source_scale': source_scale,
            'notes': notes,
            'fatalities': fatalities,
            'tags': tags,
            'timestamp': timestamp,
            'fields': fields,
            'export_type': export_type,
            'limit': limit or 50,
            'page': page
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        # Map response_format to _format (the actual API parameter)
        if response_format is not None:
            if isinstance(response_format, ResponseFormat):
                params['_format'] = response_format.value
            else:
                params['_format'] = response_format

        # Add any additional query parameters
        if query_params:
            params.update(query_params)

        # Log the request
        self.log.info("Fetching ACLED data with %s parameters", len(params))

        # Perform the API request
        try:
            response = self._get(self.endpoint, params=params)

            if response.get('success'):
                event_list = response.get('data', [])
                self.log.info("Retrieved %s events from ACLED API", len(event_list))
                return [self._parse_event(event) for event in event_list]
            error_info = response.get('error', [{'message': 'Unknown error'}])[0]
            error_message = error_info.get('message', 'Unknown error')
            self.log.error("API Error: %s", error_message)
            raise ApiError(f"API Error: {error_message}")

        except (NetworkError, TimeoutError, RateLimitError, ServerError, ClientError, RetryError):
            # These exceptions are already logged in BaseHttpClient
            raise
        except Exception as e:
            self.log.error("Unexpected error in get_data: %s", str(e))
            raise ApiError(f"Unexpected error: {str(e)}") from e

    def _parse_event(self, event_data: Dict[str, Any]) -> AcledEvent:
        """
        Parses raw event data into an AcledEvent TypedDict.

        Args:
            event_data (Dict[str, Any]): Raw event data.

        Returns:
            AcledEvent: Parsed ACLED event.

        Raises:
            ValueError: If there's an error during parsing.
        """
        try:
            if isinstance(event_data.get('event_date'), str):
                event_data['event_date'] = datetime.strptime(
                    event_data['event_date'], '%Y-%m-%d'
                ).date()
            if event_data.get('year') is not None:
                event_data['year'] = int(event_data['year'])
            if event_data.get('time_precision') is not None:
                event_data['time_precision'] = int(event_data['time_precision'])
            if event_data.get('latitude') is not None:
                event_data['latitude'] = float(event_data['latitude'])
            if event_data.get('longitude') is not None:
                event_data['longitude'] = float(event_data['longitude'])
            if event_data.get('fatalities') is not None:
                event_data['fatalities'] = int(event_data['fatalities'])
            if event_data.get('timestamp') is not None:
                event_data['timestamp'] = datetime.fromtimestamp(
                    int(event_data['timestamp']), tz=timezone.utc
                )

            return event_data
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing event data: {str(e)}") from e
