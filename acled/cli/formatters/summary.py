"""Summary output formatter."""

from typing import Any

from .base import BaseFormatter


class SummaryFormatter(BaseFormatter):
    """Summary output formatter."""

    def format(self, data: Any) -> str:
        """Format data as a summary."""
        if isinstance(data, list):
            count = len(data)
            if count == 0:
                return "No items found"
            elif count == 1:
                return f"1 item found:\n{self._format_single_item(data[0])}"
            else:
                return f"{count} items found\n" + "\n".join(
                    f"Item {i+1}: {self._format_single_item(item)}"
                    for i, item in enumerate(data[:5])  # Show first 5 items
                ) + (f"\n... and {count - 5} more items" if count > 5 else "")

        # Handle non-list data
        if not data:
            return "No data"

        return self._format_single_item(data)

    def _format_single_item(self, item: Any) -> str:
        """Format a single item for summary display."""
        if isinstance(item, dict):
            # For ACLED data, try to show key fields
            key_fields = ['event_date', 'country', 'event_type', 'fatalities', 'actor_name', 'region_name']
            summary_parts = []

            for field in key_fields:
                if field in item and item[field] is not None:
                    summary_parts.append(f"{field}: {item[field]}")

            if summary_parts:
                return ", ".join(summary_parts)
            else:
                # Fallback to first few fields
                items_to_show = list(item.items())[:3]
                return ", ".join(f"{k}: {v}" for k, v in items_to_show)

        return str(item)
