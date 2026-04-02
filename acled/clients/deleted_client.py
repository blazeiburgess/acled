"""Client module for accessing deleted event records from the ACLED API.

This module provides a client for retrieving information about events that
have been removed from the ACLED dataset, either because they were identified
as duplicates or fell outside of ACLED's scope.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import date
import requests

from acled.clients.base_http_client import BaseHttpClient
from acled.models import DeletedEvent
from acled.models.enums import ExportType
from acled.exceptions import ApiError


class DeletedClient(BaseHttpClient):
    """
    Client for interacting with the ACLED deleted events endpoint.
    """

    def __init__(self, **kwargs):
        """Initialize the deleted events client.

        Args:
            **kwargs: Authentication parameters passed to BaseHttpClient
        """
        super().__init__(**kwargs)
        self.endpoint = "/deleted/read"

    def get_data(
        self,
        event_id_cnty: Optional[str] = None,
        deleted_timestamp: Optional[Union[int, str, date]] = None,
        export_type: Optional[Union[str, ExportType]] = ExportType.JSON,
        limit: int = 50,
        page: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> List[DeletedEvent]:
        """
        Retrieves deleted event records based on the provided filters.

        Args:
            event_id_cnty (Optional[str]): Filter by event ID (supports LIKE).
            deleted_timestamp (Optional[Union[int, str, date]]): Filter by deletion timestamp (>= value).
            export_type (Optional[Union[str, ExportType]]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters (e.g., to use '_where' suffix).

        Returns:
            List[DeletedEvent]: A list of deleted event records matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
        """
        params: Dict[str, Any] = query_params.copy() if query_params else {}

        if event_id_cnty is not None:
            params['event_id_cnty'] = event_id_cnty
        if deleted_timestamp is not None:
            if isinstance(deleted_timestamp, date):
                params['deleted_timestamp'] = deleted_timestamp.strftime('%Y-%m-%d')
            else:
                params['deleted_timestamp'] = str(deleted_timestamp)
        if export_type is not None:
            if isinstance(export_type, ExportType):
                params['export_type'] = export_type.value
            else:
                params['export_type'] = export_type
        params['limit'] = str(limit) if limit else '50'
        if page is not None:
            params['page'] = str(page)

        try:
            response = self._get(self.endpoint, params=params)
            if response.get('success'):
                deleted_list = response.get('data', [])
                return [self._parse_deleted_event(d) for d in deleted_list]

            error_info = response.get('error', [{'message': 'Unknown error'}])[0]
            error_message = error_info.get('message', 'Unknown error')
            raise ApiError(f"API Error: {error_message}")
        except requests.HTTPError as e:
            raise ApiError(f"HTTP Error: {str(e)}") from e

    def _parse_deleted_event(self, data: Dict[str, Any]) -> DeletedEvent:
        """
        Parses raw deleted event data into a DeletedEvent TypedDict.

        Args:
            data (Dict[str, Any]): Raw deleted event data.

        Returns:
            DeletedEvent: Parsed deleted event.

        Raises:
            ValueError: If there's an error during parsing.
        """
        try:
            val = data.get('deleted_timestamp')
            if val is not None:
                try:
                    data['deleted_timestamp'] = int(val)
                except (ValueError, TypeError):
                    pass

            return data
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing deleted event data: {str(e)}") from e
