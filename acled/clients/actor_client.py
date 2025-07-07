"""Client module for accessing actor data from the ACLED API.

This module provides a client for retrieving information about actors involved
in events recorded in the ACLED database. It allows filtering by actor name,
event dates, and event counts to retrieve specific actors and their statistics.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date

from acled.clients.base_http_client import BaseHttpClient
from acled.models import Actor
from acled.models.enums import ExportType
from acled.exceptions import ApiError, NetworkError, TimeoutError, RateLimitError, RetryError, ServerError, ClientError


class ActorClient(BaseHttpClient):
    """
    Client for interacting with the ACLED actor endpoint.
    """

    def __init__(self, api_key: str, email: str):
        super().__init__(api_key, email)
        self.endpoint = "/actor/read"

    def get_data(
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
        # Create a dictionary of all parameters that aren't None
        params = {
            'actor_name': actor_name,
            'first_event_date': first_event_date,
            'last_event_date': last_event_date,
            'event_count': event_count,
            'export_type': export_type,
            'limit': limit,
            'page': page
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        # Add any additional query parameters
        if query_params:
            params.update(query_params)

        # Log the request
        self.log.info("Fetching actor data with %s parameters", len(params))

        # Perform the API request
        try:
            response = self._get(self.endpoint, params=params)

            if response.get('success'):
                actor_list = response.get('data', [])
                self.log.info("Retrieved %s actors from ACLED API", len(actor_list))
                return [self._parse_actor(actor) for actor in actor_list]
            else:
                error_info = response.get('error', [{'message': 'Unknown error'}])[0]
                error_message = error_info.get('message', 'Unknown error')
                self.log.error("API Error: %s", error_message)
                raise ApiError(f"API Error: {error_message}")

        except (NetworkError, TimeoutError, RateLimitError, ServerError, ClientError, RetryError) as e:
            # These exceptions are already logged in BaseHttpClient
            raise
        except Exception as e:
            self.log.error("Unexpected error in get_data: %s", str(e))
            raise ApiError(f"Unexpected error: {str(e)}")

    def _parse_actor(self, actor_data: Dict[str, Any]) -> Actor:
        """
        Parses raw actor data into an Actor TypedDict.

        Args:
            actor_data (Dict[str, Any]): Raw actor data.

        Returns:
            Actor: Parsed Actor.

        Raises:
            ValueError: If there's an error during parsing.
        """
        try:
            actor_data['first_event_date'] = datetime.strptime(
                actor_data['first_event_date'], '%Y-%m-%d'
            ).date()
            actor_data['last_event_date'] = datetime.strptime(
                actor_data['last_event_date'], '%Y-%m-%d'
            ).date()
            actor_data['event_count'] = int(actor_data.get('event_count', 0))

            return actor_data
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing actor data: {str(e)}")
