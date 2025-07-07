"""Output formatters for CLI."""

from .json import JSONFormatter
from .csv import CSVFormatter
from .table import TableFormatter
from .summary import SummaryFormatter


def get_formatter(format_type: str):
    """Get formatter instance by type."""
    formatters = {
        'json': JSONFormatter,
        'csv': CSVFormatter, 
        'table': TableFormatter,
        'summary': SummaryFormatter,
    }
    
    formatter_class = formatters.get(format_type)
    if not formatter_class:
        raise ValueError(f"Unknown format: {format_type}")
    
    return formatter_class()