"""Tests for output formatters."""

import unittest
from unittest.mock import patch

import pytest


class TestJSONFormatter(unittest.TestCase):
    """Test JSONFormatter class."""
    
    def test_format_dict(self):
        """Test formatting a dictionary."""
        from acled.cli.formatters.json import JSONFormatter
        
        formatter = JSONFormatter()
        data = {"key": "value", "number": 42}
        result = formatter.format(data)
        
        self.assertIn('"key": "value"', result)
        self.assertIn('"number": 42', result)
    
    def test_format_list(self):
        """Test formatting a list."""
        from acled.cli.formatters.json import JSONFormatter
        
        formatter = JSONFormatter()
        data = [{"id": 1}, {"id": 2}]
        result = formatter.format(data)
        
        self.assertIn('"id": 1', result)
        self.assertIn('"id": 2', result)
    
    def test_format_empty(self):
        """Test formatting empty data."""
        from acled.cli.formatters.json import JSONFormatter
        
        formatter = JSONFormatter()
        result = formatter.format([])
        
        self.assertEqual(result, "[]")


class TestCSVFormatter(unittest.TestCase):
    """Test CSVFormatter class."""
    
    def test_format_list_of_dicts(self):
        """Test formatting a list of dictionaries."""
        from acled.cli.formatters.csv import CSVFormatter
        
        formatter = CSVFormatter()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        result = formatter.format(data)
        
        lines = result.strip().split('\n')
        self.assertEqual(lines[0], "name,age")
        self.assertIn("Alice,30", lines[1])
        self.assertIn("Bob,25", lines[2])
    
    def test_format_single_dict(self):
        """Test formatting a single dictionary."""
        from acled.cli.formatters.csv import CSVFormatter
        
        formatter = CSVFormatter()
        data = {"name": "Alice", "age": 30}
        result = formatter.format(data)
        
        lines = result.strip().split('\n')
        self.assertEqual(lines[0], "name,age")
        self.assertIn("Alice,30", lines[1])
    
    def test_format_empty(self):
        """Test formatting empty data."""
        from acled.cli.formatters.csv import CSVFormatter
        
        formatter = CSVFormatter()
        result = formatter.format([])
        
        self.assertEqual(result, "")
    
    def test_format_non_dict(self):
        """Test formatting non-dictionary data."""
        from acled.cli.formatters.csv import CSVFormatter
        
        formatter = CSVFormatter()
        result = formatter.format("simple string")
        
        self.assertEqual(result, "simple string")


class TestTableFormatter(unittest.TestCase):
    """Test TableFormatter class."""
    
    @patch('acled.cli.formatters.table.HAS_TABULATE', True)
    @patch('acled.cli.formatters.table.tabulate')
    def test_format_list_of_dicts(self, mock_tabulate):
        """Test formatting a list of dictionaries."""
        from acled.cli.formatters.table import TableFormatter
        
        mock_tabulate.return_value = "Mock table output"
        
        formatter = TableFormatter()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        result = formatter.format(data)
        
        mock_tabulate.assert_called_once()
        args, kwargs = mock_tabulate.call_args
        self.assertEqual(kwargs['headers'], ['name', 'age'])
        self.assertEqual(kwargs['tablefmt'], 'grid')
        self.assertEqual(result, "Mock table output")
    
    @patch('acled.cli.formatters.table.HAS_TABULATE', True)
    @patch('acled.cli.formatters.table.tabulate')
    def test_format_single_dict(self, mock_tabulate):
        """Test formatting a single dictionary."""
        from acled.cli.formatters.table import TableFormatter
        
        mock_tabulate.return_value = "Mock table output"
        
        formatter = TableFormatter()
        data = {"name": "Alice", "age": 30}
        result = formatter.format(data)
        
        mock_tabulate.assert_called_once()
        args, kwargs = mock_tabulate.call_args
        self.assertEqual(kwargs['headers'], ['name', 'age'])
        self.assertEqual(result, "Mock table output")
    
    def test_format_empty(self):
        """Test formatting empty data."""
        from acled.cli.formatters.table import TableFormatter
        
        formatter = TableFormatter()
        result = formatter.format([])
        
        self.assertEqual(result, "No data to display")
    
    @patch('acled.cli.formatters.table.HAS_TABULATE', False)
    def test_format_no_tabulate(self):
        """Test error when tabulate is not available."""
        from acled.cli.formatters.table import TableFormatter
        
        formatter = TableFormatter()
        
        with self.assertRaises(ImportError) as context:
            formatter.format([{"test": "data"}])
        
        self.assertIn("tabulate is required", str(context.exception))


class TestSummaryFormatter(unittest.TestCase):
    """Test SummaryFormatter class."""
    
    def test_format_empty(self):
        """Test formatting empty data."""
        from acled.cli.formatters.summary import SummaryFormatter
        
        formatter = SummaryFormatter()
        result = formatter.format([])
        
        self.assertEqual(result, "No items found")
    
    def test_format_single_item(self):
        """Test formatting single item."""
        from acled.cli.formatters.summary import SummaryFormatter
        
        formatter = SummaryFormatter()
        data = [{"event_date": "2024-01-01", "country": "Test Country"}]
        result = formatter.format(data)
        
        self.assertIn("1 item found", result)
        self.assertIn("event_date: 2024-01-01", result)
        self.assertIn("country: Test Country", result)
    
    def test_format_multiple_items(self):
        """Test formatting multiple items."""
        from acled.cli.formatters.summary import SummaryFormatter
        
        formatter = SummaryFormatter()
        data = [
            {"event_date": "2024-01-01", "country": "Country 1"},
            {"event_date": "2024-01-02", "country": "Country 2"}
        ]
        result = formatter.format(data)
        
        self.assertIn("2 items found", result)
        self.assertIn("Item 1:", result)
        self.assertIn("Item 2:", result)
    
    def test_format_many_items(self):
        """Test formatting many items (should truncate)."""
        from acled.cli.formatters.summary import SummaryFormatter
        
        formatter = SummaryFormatter()
        data = [{"id": i} for i in range(10)]  # 10 items
        result = formatter.format(data)
        
        self.assertIn("10 items found", result)
        self.assertIn("... and 5 more items", result)  # Should show first 5 + message
    
    def test_format_single_dict(self):
        """Test formatting single dictionary."""
        from acled.cli.formatters.summary import SummaryFormatter
        
        formatter = SummaryFormatter()
        data = {"event_date": "2024-01-01", "country": "Test Country"}
        result = formatter.format(data)
        
        self.assertIn("event_date: 2024-01-01", result)
        self.assertIn("country: Test Country", result)


class TestFormatterFactory(unittest.TestCase):
    """Test formatter factory function."""
    
    def test_get_json_formatter(self):
        """Test getting JSON formatter."""
        from acled.cli.formatters import get_formatter
        from acled.cli.formatters.json import JSONFormatter
        
        formatter = get_formatter('json')
        self.assertIsInstance(formatter, JSONFormatter)
    
    def test_get_csv_formatter(self):
        """Test getting CSV formatter."""
        from acled.cli.formatters import get_formatter
        from acled.cli.formatters.csv import CSVFormatter
        
        formatter = get_formatter('csv')
        self.assertIsInstance(formatter, CSVFormatter)
    
    def test_get_table_formatter(self):
        """Test getting table formatter."""
        from acled.cli.formatters import get_formatter
        from acled.cli.formatters.table import TableFormatter
        
        formatter = get_formatter('table')
        self.assertIsInstance(formatter, TableFormatter)
    
    def test_get_summary_formatter(self):
        """Test getting summary formatter."""
        from acled.cli.formatters import get_formatter
        from acled.cli.formatters.summary import SummaryFormatter
        
        formatter = get_formatter('summary')
        self.assertIsInstance(formatter, SummaryFormatter)
    
    def test_get_unknown_formatter(self):
        """Test error for unknown formatter."""
        from acled.cli.formatters import get_formatter
        
        with self.assertRaises(ValueError) as context:
            get_formatter('unknown')
        
        self.assertIn("Unknown format: unknown", str(context.exception))


if __name__ == '__main__':
    unittest.main()