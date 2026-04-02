"""Client module for accessing CAST (Conflict Alert System) data from the ACLED API.

This module provides a client for retrieving conflict forecast and observed
event data. CAST provides monthly forecasts of political violence events
broken down by type (battles, explosions/remote violence, violence against
civilians) at the country and first-level administrative division level.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import date
import requests

from acled.clients.base_http_client import BaseHttpClient
from acled.models import CastForecast
from acled.models.enums import ExportType
from acled.exceptions import ApiError


class CastClient(BaseHttpClient):
    """
    Client for interacting with the ACLED CAST endpoint.
    """

    def __init__(self, **kwargs):
        """Initialize the CAST client.

        Args:
            **kwargs: Authentication parameters passed to BaseHttpClient
        """
        super().__init__(**kwargs)
        self.endpoint = "/cast/read"

    def get_data(
        self,
        country: Optional[str] = None,
        admin1: Optional[str] = None,
        month: Optional[str] = None,
        year: Optional[int] = None,
        total_forecast: Optional[int] = None,
        battles_forecast: Optional[int] = None,
        erv_forecast: Optional[int] = None,
        vac_forecast: Optional[int] = None,
        total_observed: Optional[int] = None,
        battles_observed: Optional[int] = None,
        erv_observed: Optional[int] = None,
        vac_observed: Optional[int] = None,
        timestamp: Optional[Union[int, str, date]] = None,
        fields: Optional[str] = None,
        export_type: Optional[Union[str, ExportType]] = ExportType.JSON,
        limit: int = 50,
        page: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> List[CastForecast]:
        """
        Retrieves CAST forecast data based on the provided filters.

        Args:
            country (Optional[str]): Filter by country name (supports LIKE).
            admin1 (Optional[str]): Filter by first-level administrative division (supports LIKE).
            month (Optional[str]): Filter by month (supports LIKE).
            year (Optional[int]): Filter by year.
            total_forecast (Optional[int]): Filter by total forecasted events.
            battles_forecast (Optional[int]): Filter by forecasted battle events.
            erv_forecast (Optional[int]): Filter by forecasted explosions/remote violence events.
            vac_forecast (Optional[int]): Filter by forecasted violence against civilians events.
            total_observed (Optional[int]): Filter by total observed events.
            battles_observed (Optional[int]): Filter by observed battle events.
            erv_observed (Optional[int]): Filter by observed explosions/remote violence events.
            vac_observed (Optional[int]): Filter by observed violence against civilians events.
            timestamp (Optional[Union[int, str, date]]): Filter by timestamp (>= value).
            fields (Optional[str]): Pipe-separated list of fields to return (e.g. 'country|year|total_forecast').
            export_type (Optional[Union[str, ExportType]]): Specify the export type ('json', 'xml', 'csv', etc.).
            limit (int): Number of records to retrieve (default is 50).
            page (Optional[int]): Page number for pagination.
            query_params (Optional[Dict[str, Any]]): Additional query parameters (e.g., to use '_where' suffix).

        Returns:
            List[CastForecast]: A list of CAST forecasts matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
        """
        params: Dict[str, Any] = query_params.copy() if query_params else {}

        # Map arguments to query parameters, handling type conversions
        if country is not None:
            params['country'] = country
        if admin1 is not None:
            params['admin1'] = admin1
        if month is not None:
            params['month'] = month
        if year is not None:
            params['year'] = str(year)
        if total_forecast is not None:
            params['total_forecast'] = str(total_forecast)
        if battles_forecast is not None:
            params['battles_forecast'] = str(battles_forecast)
        if erv_forecast is not None:
            params['erv_forecast'] = str(erv_forecast)
        if vac_forecast is not None:
            params['vac_forecast'] = str(vac_forecast)
        if total_observed is not None:
            params['total_observed'] = str(total_observed)
        if battles_observed is not None:
            params['battles_observed'] = str(battles_observed)
        if erv_observed is not None:
            params['erv_observed'] = str(erv_observed)
        if vac_observed is not None:
            params['vac_observed'] = str(vac_observed)
        if timestamp is not None:
            if isinstance(timestamp, date):
                params['timestamp'] = timestamp.strftime('%Y-%m-%d')
            else:
                params['timestamp'] = str(timestamp)
        if fields is not None:
            params['fields'] = fields
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
                forecast_list = response.get('data', [])
                return [self._parse_cast_forecast(f) for f in forecast_list]

            error_info = response.get('error', [{'message': 'Unknown error'}])[0]
            error_message = error_info.get('message', 'Unknown error')
            raise ApiError(f"API Error: {error_message}")
        except requests.HTTPError as e:
            raise ApiError(f"HTTP Error: {str(e)}") from e

    def _parse_cast_forecast(self, data: Dict[str, Any]) -> CastForecast:
        """
        Parses raw CAST data into a CastForecast TypedDict.

        Args:
            data (Dict[str, Any]): Raw CAST forecast data.

        Returns:
            CastForecast: Parsed forecast.

        Raises:
            ValueError: If there's an error during parsing.
        """
        try:
            int_fields = [
                'year', 'total_forecast', 'battles_forecast', 'erv_forecast',
                'vac_forecast', 'total_observed', 'battles_observed',
                'erv_observed', 'vac_observed', 'timestamp',
            ]
            for field in int_fields:
                val = data.get(field)
                if val is not None:
                    try:
                        data[field] = int(val)
                    except (ValueError, TypeError):
                        pass

            return data
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing CAST data: {str(e)}") from e
