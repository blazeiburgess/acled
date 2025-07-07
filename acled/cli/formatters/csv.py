"""CSV output formatter."""

import csv
import io
from typing import Any

from .base import BaseFormatter


class CSVFormatter(BaseFormatter):
    """CSV output formatter."""
    
    def format(self, data: Any) -> str:
        """Format data as CSV."""
        if not data:
            return ""
        
        # Handle list of dicts
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys(), lineterminator='\n')
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        
        # Handle single dict
        if isinstance(data, dict):
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data.keys(), lineterminator='\n')
            writer.writeheader()
            writer.writerow(data)
            return output.getvalue()
        
        # Fallback to string representation
        return str(data)