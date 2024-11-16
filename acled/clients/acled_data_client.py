from typing import Any, Dict, List, Optional, Union

import requests
from datetime import datetime, date

from .base_http_client import BaseHttpClient
from ..models.data_models import AcledEvent
from ..models.enums import ExportType
from ..exceptions import ApiError


class AcledDataClient(BaseHttpClient):
    """
    Client for interacting with the ACLED main dataset endpoint.
    """

    def __init__(self, api_key: str, email: str):
        super().__init__(api_key, email)
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
        timestamp: Optional[Union[int, str, date]] = None,
        export_type: Optional[str | ExportType] = ExportType.JSON,
        limit: int = 50,
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
            export_type (Optional[str]): Specify the export type ('json', 'xml', 'csv', etc.).
            query_params (Optional[Dict[str, Any]]): Additional query parameters (e.g., to use '_where' suffix).

        Returns:
            List[AcledEvent]: A list of ACLED events matching the filters.

        Raises:
            ApiError: If there's an error with the API request or response.
        """
        params: Dict[str, Any] = query_params.copy() if query_params else {}

        # Map arguments to query parameters, handling type conversions
        if event_id_cnty is not None:
            params['event_id_cnty'] = event_id_cnty
        if event_date is not None:
            if isinstance(event_date, date):
                event_date_str = event_date.strftime('%Y-%m-%d')
            else:
                event_date_str = event_date
            params['event_date'] = event_date_str
        if year is not None:
            params['year'] = str(year)
        if time_precision is not None:
            params['time_precision'] = str(time_precision)
        if disorder_type is not None:
            params['disorder_type'] = disorder_type
        if event_type is not None:
            params['event_type'] = event_type
        if sub_event_type is not None:
            params['sub_event_type'] = sub_event_type
        if actor1 is not None:
            params['actor1'] = actor1
        if assoc_actor_1 is not None:
            params['assoc_actor_1'] = assoc_actor_1
        if inter1 is not None:
            params['inter1'] = str(inter1)
        if actor2 is not None:
            params['actor2'] = actor2
        if assoc_actor_2 is not None:
            params['assoc_actor_2'] = assoc_actor_2
        if inter2 is not None:
            params['inter2'] = str(inter2)
        if interaction is not None:
            params['interaction'] = str(interaction)
        if civilian_targeting is not None:
            params['civilian_targeting'] = civilian_targeting
        if iso is not None:
            params['iso'] = str(iso)
        if region is not None:
            params['region'] = str(region)
        if country is not None:
            params['country'] = country
        if admin1 is not None:
            params['admin1'] = admin1
        if admin2 is not None:
            params['admin2'] = admin2
        if admin3 is not None:
            params['admin3'] = admin3
        if location is not None:
            params['location'] = location
        if latitude is not None:
            params['latitude'] = str(latitude)
        if longitude is not None:
            params['longitude'] = str(longitude)
        if geo_precision is not None:
            params['geo_precision'] = str(geo_precision)
        if source is not None:
            params['source'] = source
        if source_scale is not None:
            params['source_scale'] = source_scale
        if notes is not None:
            params['notes'] = notes
        if fatalities is not None:
            params['fatalities'] = str(fatalities)
        if timestamp is not None:
            if isinstance(timestamp, date):
                timestamp_str = timestamp.strftime('%Y-%m-%d')
            else:
                timestamp_str = str(timestamp)
            params['timestamp'] = timestamp_str
        if export_type is not None:
            if isinstance(export_type, ExportType):
                params['export_type'] = export_type.value
            else:
                params['export_type'] = export_type
        params['limit'] = limit if limit else 50

        # Perform the API request
        try:
            response = self._get(self.endpoint, params=params)
            if response.get('success'):
                event_list = response.get('data', [])
                return [self._parse_event(event) for event in event_list]
            else:
                error_message = response.get('error', [{'message': 'Unknown error'}])[0]['message']
                raise ApiError(f"API Error: {error_message}")
        except requests.HTTPError as e:
            raise ApiError(f"HTTP Error: {str(e)}")

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
            event_data['event_date'] = datetime.strptime(
                event_data['event_date'], '%Y-%m-%d'
            ).date()
            event_data['year'] = int(event_data['year'])
            event_data['time_precision'] = int(event_data.get('time_precision', 0))
            event_data['latitude'] = float(event_data.get('latitude', 0.0))
            event_data['longitude'] = float(event_data.get('longitude', 0.0))
            event_data['fatalities'] = int(event_data.get('fatalities', 0))
            event_data['timestamp'] = datetime.fromtimestamp(
                int(event_data['timestamp'])
            )

            return event_data
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing event data: {str(e)}")