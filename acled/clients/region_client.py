"""Client module for accessing region data from the ACLED API.

This module provides a client for retrieving information about geographical regions
where events have been recorded in the ACLED database. It allows filtering by
region ID, name, event dates, and event counts to retrieve specific regions and
their statistics.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import requests

from acled.clients.base_http_client import BaseHttpClient
from acled.models import Region
from acled.models.enums import ExportType
from acled.exceptions import ApiError

class RegionClient(BaseHttpClient):
    """
    Client for interacting with the ACLED region endpoint.
    """

    def __init__(self, api_key: str, email: str):
        super().__init__(api_key, email)
        self.endpoint = "/region/read"

    def get_data(
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
            export_type (Optional[str | ExportType]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters.

        Returns:
            List[Region]: A list of Regions matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
        """
        params: Dict[str, Any] = query_params.copy() if query_params else {}

        # Map arguments to query parameters, handling type conversions
        if region is not None:
            params['region'] = str(region)
        if region_name is not None:
            params['region_name'] = region_name
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
                region_list = response.get('data', [])
                return [self._parse_region(region) for region in region_list]
            error_info = response.get('error', [{'message': 'Unknown error'}])[0]
            error_message = error_info.get('message', 'Unknown error')
            raise ApiError(f"API Error: {error_message}")
        except requests.HTTPError as e:
            raise ApiError(f"HTTP Error: {str(e)}") from e

    def _parse_region(self, region_data: Dict[str, Any]) -> Region:
        """
        Parses raw region data into a Region TypedDict.

        Args:
            region_data (Dict[str, Any]): Raw region data.

        Returns:
            Region: Parsed Region.

        Raises:
            ValueError: If there's an error during parsing.
        """
        try:
            region_data['region'] = int(region_data.get('region', 0))

            # Parse first_event_date if it's a string
            if isinstance(region_data['first_event_date'], str):
                region_data['first_event_date'] = datetime.strptime(
                    region_data['first_event_date'], '%Y-%m-%d'
                ).date()

            # Parse last_event_date if it's a string
            if isinstance(region_data['last_event_date'], str):
                region_data['last_event_date'] = datetime.strptime(
                    region_data['last_event_date'], '%Y-%m-%d'
                ).date()
            region_data['event_count'] = int(region_data.get('event_count', 0))

            return region_data  # This will be of type Region
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing region data: {str(e)}") from e
