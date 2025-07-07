"""Tests for base command class."""

import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestBaseCommand(unittest.TestCase):
    """Test BaseCommand class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.api_key = 'test_key'
        self.mock_config.email = 'test@example.com'
        self.mock_config.quiet = False
        
        # Create temp directory for file tests
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: self._cleanup_temp_dir())
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except OSError:
            pass
    
    @patch('acled.cli.commands.base.AcledClient')
    def test_base_command_initialization(self, mock_client_class):
        """Test BaseCommand initializes with config and client."""
        from acled.cli.commands.base import BaseCommand
        
        # Mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create concrete implementation for testing
        class TestCommand(BaseCommand):
            @classmethod
            def register_parser(cls, subparsers):
                pass
            
            def execute(self, args):
                return 0
        
        command = TestCommand(self.mock_config)
        
        self.assertEqual(command.config, self.mock_config)
        self.assertEqual(command.client, mock_client)
        mock_client_class.assert_called_once_with(
            api_key='test_key',
            email='test@example.com'
        )
    
    def test_base_command_is_abstract(self):
        """Test BaseCommand cannot be instantiated directly."""
        from acled.cli.commands.base import BaseCommand
        
        with self.assertRaises(TypeError):
            BaseCommand(self.mock_config)
    
    @patch('acled.cli.commands.base.get_formatter')
    def test_output_data_to_stdout(self, mock_get_formatter):
        """Test output_data writes to stdout."""
        from acled.cli.commands.base import BaseCommand
        
        # Mock formatter
        mock_formatter = Mock()
        mock_formatter.format.return_value = '{"test": "data"}'
        mock_get_formatter.return_value = mock_formatter
        
        # Create concrete implementation
        class TestCommand(BaseCommand):
            @classmethod
            def register_parser(cls, subparsers):
                pass
            
            def execute(self, args):
                return 0
        
        with patch('acled.cli.commands.base.AcledClient'):
            command = TestCommand(self.mock_config)
        
        test_data = [{"test": "data"}]
        
        with patch('builtins.print') as mock_print:
            command.output_data(test_data, 'json')
            
            mock_get_formatter.assert_called_once_with('json')
            mock_formatter.format.assert_called_once_with(test_data)
            mock_print.assert_called_once_with('{"test": "data"}')
    
    @patch('acled.cli.commands.base.get_formatter')
    def test_output_data_to_file(self, mock_get_formatter):
        """Test output_data writes to file."""
        from acled.cli.commands.base import BaseCommand
        
        # Mock formatter
        mock_formatter = Mock()
        mock_formatter.format.return_value = '{"test": "data"}'
        mock_get_formatter.return_value = mock_formatter
        
        # Create concrete implementation
        class TestCommand(BaseCommand):
            @classmethod
            def register_parser(cls, subparsers):
                pass
            
            def execute(self, args):
                return 0
        
        with patch('acled.cli.commands.base.AcledClient'):
            command = TestCommand(self.mock_config)
        
        test_data = [{"test": "data"}]
        output_file = Path(self.temp_dir) / "output.json"
        
        with patch('builtins.print') as mock_print:
            command.output_data(test_data, 'json', str(output_file))
            
            # Check file was written
            self.assertTrue(output_file.exists())
            with open(output_file, 'r') as f:
                content = f.read()
            self.assertEqual(content, '{"test": "data"}')
            
            # Check success message was printed
            mock_print.assert_called_once_with(f"Output written to {output_file}")
    
    @patch('acled.cli.commands.base.get_formatter')
    def test_output_data_to_file_quiet_mode(self, mock_get_formatter):
        """Test output_data doesn't print success message in quiet mode."""
        from acled.cli.commands.base import BaseCommand
        
        # Set config to quiet mode
        self.mock_config.quiet = True
        
        # Mock formatter
        mock_formatter = Mock()
        mock_formatter.format.return_value = '{"test": "data"}'
        mock_get_formatter.return_value = mock_formatter
        
        # Create concrete implementation
        class TestCommand(BaseCommand):
            @classmethod
            def register_parser(cls, subparsers):
                pass
            
            def execute(self, args):
                return 0
        
        with patch('acled.cli.commands.base.AcledClient'):
            command = TestCommand(self.mock_config)
        
        test_data = [{"test": "data"}]
        output_file = Path(self.temp_dir) / "output.json"
        
        with patch('builtins.print') as mock_print:
            command.output_data(test_data, 'json', str(output_file))
            
            # File should still be written
            self.assertTrue(output_file.exists())
            
            # But no success message should be printed
            mock_print.assert_not_called()
    
    def test_add_common_filters(self):
        """Test add_common_filters adds expected arguments."""
        from acled.cli.commands.base import BaseCommand
        
        # Create concrete implementation
        class TestCommand(BaseCommand):
            @classmethod
            def register_parser(cls, subparsers):
                pass
            
            def execute(self, args):
                return 0
        
        with patch('acled.cli.commands.base.AcledClient'):
            command = TestCommand(self.mock_config)
        
        # Create a parser to test with
        parser = argparse.ArgumentParser()
        command.add_common_filters(parser)
        
        # Test parsing with common arguments
        args = parser.parse_args(['--limit', '100', '--page', '2', '--export-type', 'csv'])
        
        self.assertEqual(args.limit, 100)
        self.assertEqual(args.page, 2)
        self.assertEqual(args.export_type, 'csv')
    
    def test_add_common_filters_defaults(self):
        """Test add_common_filters sets correct defaults."""
        from acled.cli.commands.base import BaseCommand
        
        # Create concrete implementation
        class TestCommand(BaseCommand):
            @classmethod
            def register_parser(cls, subparsers):
                pass
            
            def execute(self, args):
                return 0
        
        with patch('acled.cli.commands.base.AcledClient'):
            command = TestCommand(self.mock_config)
        
        # Create a parser to test with
        parser = argparse.ArgumentParser()
        command.add_common_filters(parser)
        
        # Test parsing with no arguments (should use defaults)
        args = parser.parse_args([])
        
        self.assertEqual(args.limit, 50)  # Default
        self.assertIsNone(args.page)  # No default
        self.assertEqual(args.export_type, 'json')  # Default


if __name__ == '__main__':
    unittest.main()