"""Table output formatter."""

from typing import Any

from .base import BaseFormatter

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


class TableFormatter(BaseFormatter):
    """Table output formatter."""
    
    def format(self, data: Any) -> str:
        """Format data as a table."""
        if not HAS_TABULATE:
            raise ImportError("tabulate is required for table output. Install with: pip install acled[cli]")
        
        if not data:
            return "No data to display"
        
        if isinstance(data, list) and len(data) > 0:
            # Get headers from first item
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                rows = []
                for item in data:
                    rows.append([str(item.get(h, '')) for h in headers])
                return tabulate(rows, headers=headers, tablefmt='grid')
        
        # Handle single dict
        if isinstance(data, dict):
            headers = list(data.keys())
            rows = [[str(data.get(h, '')) for h in headers]]
            return tabulate(rows, headers=headers, tablefmt='grid')
        
        return str(data)