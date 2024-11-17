from typing import Any, Dict, List, Optional, Union
import requests
from datetime import datetime, date

from .base_http_client import BaseHttpClient
from ..models.data_models import Actor
from ..models.enums import ExportType
from ..exceptions import ApiError


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
            export_type (Optional[str | ExportType]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters.

        Returns:
            List[Actor]: A list of Actors matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
        """
        params: Dict[str, Any] = query_params.copy() if query_params else {}

        # Map arguments to query parameters, handling type conversions
        if actor_name is not None:
            params['actor_name'] = actor_name
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
                actor_list = response.get('data', [])
                return [self._parse_actor(actor) for actor in actor_list]
            else:
                error_info = response.get('error', [{'message': 'Unknown error'}])[0]
                error_message = error_info.get('message', 'Unknown error')
                raise ApiError(f"API Error: {error_message}")
        except requests.HTTPError as e:
            raise ApiError(f"HTTP Error: {str(e)}")

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
