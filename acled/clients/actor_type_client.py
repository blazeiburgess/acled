"""Client module for accessing actor type data from the ACLED API.

This module provides a client for retrieving information about different types
of actors (e.g., state forces, rebel groups, protesters) from the ACLED database.
It allows filtering by various criteria such as actor type ID, name, and event dates.
"""

from typing import Any, Dict, List, Optional, Union
import requests
from datetime import datetime, date

from acled.clients.base_http_client import BaseHttpClient
from acled.models import ActorType
from acled.models.enums import ExportType
from acled.exceptions import ApiError

class ActorTypeClient(BaseHttpClient):
    """
    Client for interacting with the ACLED actor type endpoint.
    """

    def __init__(self, api_key: str, email: str):
        super().__init__(api_key, email)
        self.endpoint = "/actortype/read"

    def get_data(
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
            export_type (Optional[str | ExportType]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters.

        Returns:
            List[ActorType]: A list of Actor Types matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
        """
        params: Dict[str, Any] = query_params.copy() if query_params else {}

        # Map arguments to query parameters, handling type conversions
        if actor_type_id is not None:
            params['actor_type_id'] = str(actor_type_id)
        if actor_type_name is not None:
            params['actor_type_name'] = actor_type_name
        if first_event_date is not None:
            if isinstance(first_event_date, date):
                params['first_event_date'] = first_event_date.strftime('%Y-%m-%d')
            else:
                params['first_event_date'] = first_event_date
        if last_event_date is not None:
            if isinstance(last_event_date, date):
                params['last_event_date'] = last_event_date.strftime('%Y-%m-%d')
            else:
                params['last_event_date'] = last_event_date
        if event_count is not None:
            params['event_count'] = str(event_count)
        if export_type is not None:
            if isinstance(export_type, ExportType):
                params['export_type'] = export_type.value
            else:
                params['export_type'] = export_type
        params['limit'] = str(limit) if limit else '50'
        if page is not None:
            params['page'] = str(page)

        # Perform the API request
        try:
            response = self._get(self.endpoint, params=params)
            if response.get('success'):
                actor_type_list = response.get('data', [])
                return [self._parse_actor_type(actor_type) for actor_type in actor_type_list]
            error_info = response.get('error', [{'message': 'Unknown error'}])[0]
            error_message = error_info.get('message', 'Unknown error')
            raise ApiError(f"API Error: {error_message}")
        except requests.HTTPError as e:
            raise ApiError(f"HTTP Error: {str(e)}") from e

    def _parse_actor_type(self, actor_type_data: Dict[str, Any]) -> ActorType:
        """
        Parses raw actor type data into an ActorType TypedDict.

        Args:
            actor_type_data (Dict[str, Any]): Raw actor type data.

        Returns:
            ActorType: Parsed ActorType.

        Raises:
            ValueError: If there's an error during parsing.
        """
        try:
            actor_type_data['actor_type_id'] = int(actor_type_data.get('actor_type_id', 0))

            # Parse first_event_date if it's a string
            if isinstance(actor_type_data['first_event_date'], str):
                actor_type_data['first_event_date'] = datetime.strptime(
                    actor_type_data['first_event_date'], '%Y-%m-%d'
                ).date()

            # Parse last_event_date if it's a string
            if isinstance(actor_type_data['last_event_date'], str):
                actor_type_data['last_event_date'] = datetime.strptime(
                    actor_type_data['last_event_date'], '%Y-%m-%d'
                ).date()
            actor_type_data['event_count'] = int(actor_type_data.get('event_count', 0))

            return actor_type_data  # This will be of type ActorType
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing actor type data: {str(e)}") from e
