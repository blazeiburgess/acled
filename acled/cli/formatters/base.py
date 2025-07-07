"""Base formatter class."""

from abc import ABC, abstractmethod
from typing import Any


class BaseFormatter(ABC):
    """Base class for output formatters."""

    @abstractmethod
    def format(self, data: Any) -> str:
        """Format data for output."""
