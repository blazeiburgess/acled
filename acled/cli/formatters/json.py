"""JSON output formatter."""

import json
from typing import Any

from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """JSON output formatter."""
    
    def format(self, data: Any) -> str:
        """Format data as JSON."""
        return json.dumps(data, indent=2, default=str)