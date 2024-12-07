from typing import Any, Dict, Optional
from os import environ

import requests

from acled.exceptions import AcledMissingAuthError
from acled.log import AcledLogger


class BaseHttpClient(object):
    """
    A base HTTP client that provides basic GET and POST request functionality.
    """
    BASE_URL = environ.get("ACLED_API_HOST", "https://api.acleddata.com")

    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        self.api_key = api_key if api_key else environ.get("ACLED_API_KEY")
        if not self.api_key:
            raise AcledMissingAuthError("API key is required")
        self.email = email if email else environ.get("ACLED_EMAIL")
        if not self.email:
            raise AcledMissingAuthError("Email is required")
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.log = AcledLogger().get_logger()

    def _get(
            self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if params is None:
            params = {}
        # Include API key and email in all requests
        params['key'] = self.api_key
        params['email'] = self.email
        url = f"{self.BASE_URL}{endpoint}"

        self.log.debug(f"Constructed URL: {url}")
        self.log.debug(f"Query Parameters: {params}")

        response = self.session.get(url, params=params)
        response.raise_for_status()
        self.log.debug(f"Response content:\n{response.content}")
        return response.json()

    def _post(
            self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if data is None:
            data = {}
        # Include API key and email in all requests
        data['key'] = self.api_key
        data['email'] = self.email
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
