from typing import Any, Dict, List, Optional, Union
import requests
from datetime import datetime, date

from .base_http_client import BaseHttpClient
from ..models.data_models import Country
from ..models.enums import ExportType
from ..exceptions import ApiError

class CountryClient(BaseHttpClient):
    """
    Client for interacting with the ACLED country endpoint.
    """

    def __init__(self, api_key: str, email: str):
        super().__init__(api_key, email)
        self.endpoint = "/country/read"

    def get_data(
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
            export_type (Optional[str | ExportType]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters.

        Returns:
            List[Country]: A list of Countries matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
        """
        params: Dict[str, Any] = query_params.copy() if query_params else {}

        # Map arguments to query parameters, handling type conversions
        if country is not None:
            params['country'] = country
        if iso is not None:
            params['iso'] = str(iso)
        if iso3 is not None:
            params['iso3'] = iso3
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
                country_list = response.get('data', [])
                return [self._parse_country(country) for country in country_list]
            else:
                error_info = response.get('error', [{'message': 'Unknown error'}])[0]
                error_message = error_info.get('message', 'Unknown error')
                raise ApiError(f"API Error: {error_message}")
        except requests.HTTPError as e:
            raise ApiError(f"HTTP Error: {str(e)}")

    def _parse_country(self, country_data: Dict[str, Any]) -> Country:
        """
        Parses raw country data into a Country TypedDict.

        Args:
            country_data (Dict[str, Any]): Raw country data.

        Returns:
            Country: Parsed Country.

        Raises:
            ValueError: If there's an error during parsing.
        """
        try:
            country_data['first_event_date'] = datetime.strptime(
                country_data['first_event_date'], '%Y-%m-%d'
            ).date()
            country_data['last_event_date'] = datetime.strptime(
                country_data['last_event_date'], '%Y-%m-%d'
            ).date()
            country_data['iso'] = int(country_data.get('iso', 0))
            country_data['event_count'] = int(country_data.get('event_count', 0))

            return country_data  # This will be of type Country
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing country data: {str(e)}")
