"""Tests for main CLI entry point."""

import unittest
from io import StringIO
from unittest.mock import Mock, patch

import pytest


class TestMainCLI(unittest.TestCase):
    """Test main CLI functionality."""
    
    def test_create_parser(self):
        """Test parser creation."""
        from acled.cli.main import create_parser
        
        parser = create_parser()
        
        # Test basic parsing
        args = parser.parse_args(['auth', 'status'])
        self.assertEqual(args.command, 'auth')
        
        # Test global options
        args = parser.parse_args(['--format', 'table', 'data', '--country', 'Syria'])
        self.assertEqual(args.format, 'table')
        self.assertEqual(args.command, 'data')
    
    def test_main_no_command(self):
        """Test main with no command prints help."""
        from acled.cli.main import main
        
        with patch('acled.cli.main.create_parser') as mock_create_parser:
            mock_parser = Mock()
            mock_parser.parse_args.return_value = Mock(command=None)
            mock_create_parser.return_value = mock_parser
            
            result = main([])
            
            self.assertEqual(result, 1)
            mock_parser.print_help.assert_called_once()
    
    def test_main_auth_command(self):
        """Test main with auth command."""
        from acled.cli.main import main
        
        with patch('acled.cli.main.AuthCommand') as mock_auth_class:
            with patch('acled.cli.main.CLIConfig') as mock_config_class:
                with patch('acled.cli.main.create_parser') as mock_create_parser:
                    mock_command = Mock()
                    mock_command.execute.return_value = 0
                    mock_auth_class.return_value = mock_command
                    
                    mock_config = Mock()
                    mock_config_class.return_value = mock_config
                    
                    # Mock parser to return auth command
                    mock_parser = Mock()
                    mock_args = Mock()
                    mock_args.command = 'auth'
                    mock_parser.parse_args.return_value = mock_args
                    mock_create_parser.return_value = mock_parser
                    
                    result = main(['auth', 'status'])
                    
                    self.assertEqual(result, 0)
                    mock_auth_class.assert_called_once_with(mock_config)
                    mock_command.execute.assert_called_once()
    
    def test_main_data_command(self):
        """Test main with data command."""
        from acled.cli.main import main
        
        with patch('acled.cli.main.DataCommand') as mock_data_class:
            with patch('acled.cli.main.CLIConfig') as mock_config_class:
                with patch('acled.cli.main.create_parser') as mock_create_parser:
                    mock_command = Mock()
                    mock_command.execute.return_value = 0
                    mock_data_class.return_value = mock_command
                    
                    mock_config = Mock()
                    mock_config_class.return_value = mock_config
                    
                    # Mock parser to return data command
                    mock_parser = Mock()
                    mock_args = Mock()
                    mock_args.command = 'data'
                    mock_parser.parse_args.return_value = mock_args
                    mock_create_parser.return_value = mock_parser
                    
                    result = main(['data', '--country', 'Syria'])
                    
                    self.assertEqual(result, 0)
                    mock_data_class.assert_called_once_with(mock_config)
                    mock_command.execute.assert_called_once()
    
    def test_main_missing_auth_error(self):
        """Test main handles missing authentication error."""
        from acled.cli.main import main
        from acled.exceptions import AcledMissingAuthError
        
        with patch('acled.cli.main.DataCommand') as mock_data_class:
            with patch('acled.cli.main.CLIConfig') as mock_config_class:
                with patch('acled.cli.main.create_parser') as mock_create_parser:
                    mock_command = Mock()
                    mock_command.execute.side_effect = AcledMissingAuthError("Missing credentials")
                    mock_data_class.return_value = mock_command
                    
                    mock_config = Mock()
                    mock_config_class.return_value = mock_config
                    
                    # Mock parser to return data command
                    mock_parser = Mock()
                    mock_args = Mock()
                    mock_args.command = 'data'
                    mock_parser.parse_args.return_value = mock_args
                    mock_create_parser.return_value = mock_parser
                    
                    with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                        result = main(['data', '--country', 'Syria'])
                        
                        self.assertEqual(result, 1)
                        stderr_output = mock_stderr.getvalue()
                        self.assertIn("Missing credentials", stderr_output)
                        self.assertIn("acled auth login", stderr_output)
    
    def test_main_keyboard_interrupt(self):
        """Test main handles keyboard interrupt."""
        from acled.cli.main import main
        
        with patch('acled.cli.main.DataCommand') as mock_data_class:
            with patch('acled.cli.main.CLIConfig') as mock_config_class:
                with patch('acled.cli.main.create_parser') as mock_create_parser:
                    mock_command = Mock()
                    mock_command.execute.side_effect = KeyboardInterrupt()
                    mock_data_class.return_value = mock_command
                    
                    mock_config = Mock()
                    mock_config_class.return_value = mock_config
                    
                    # Mock parser to return data command
                    mock_parser = Mock()
                    mock_args = Mock()
                    mock_args.command = 'data'
                    mock_parser.parse_args.return_value = mock_args
                    mock_create_parser.return_value = mock_parser
                    
                    with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                        result = main(['data', '--country', 'Syria'])
                        
                        self.assertEqual(result, 130)
                        stderr_output = mock_stderr.getvalue()
                        self.assertIn("Operation cancelled", stderr_output)
    
    def test_main_general_exception_verbose(self):
        """Test main handles general exception in verbose mode."""
        from acled.cli.main import main
        
        with patch('acled.cli.main.DataCommand') as mock_data_class:
            with patch('acled.cli.main.CLIConfig') as mock_config_class:
                with patch('acled.cli.main.create_parser') as mock_create_parser:
                    mock_command = Mock()
                    mock_command.execute.side_effect = Exception("Test error")
                    mock_data_class.return_value = mock_command
                    
                    mock_config = Mock()
                    mock_config.verbose = True
                    mock_config_class.return_value = mock_config
                    
                    # Mock parser to return data command
                    mock_parser = Mock()
                    mock_args = Mock()
                    mock_args.command = 'data'
                    mock_parser.parse_args.return_value = mock_args
                    mock_create_parser.return_value = mock_parser
                    
                    with patch('traceback.print_exc') as mock_print_exc:
                        result = main(['data', '--country', 'Syria'])
                        
                        self.assertEqual(result, 1)
                        mock_print_exc.assert_called_once()
    
    def test_main_general_exception_quiet(self):
        """Test main handles general exception in quiet mode."""
        from acled.cli.main import main
        
        with patch('acled.cli.main.DataCommand') as mock_data_class:
            with patch('acled.cli.main.CLIConfig') as mock_config_class:
                with patch('acled.cli.main.create_parser') as mock_create_parser:
                    mock_command = Mock()
                    mock_command.execute.side_effect = Exception("Test error")
                    mock_data_class.return_value = mock_command
                    
                    mock_config = Mock()
                    mock_config.verbose = False
                    mock_config_class.return_value = mock_config
                    
                    # Mock parser to return data command
                    mock_parser = Mock()
                    mock_args = Mock()
                    mock_args.command = 'data'
                    mock_parser.parse_args.return_value = mock_args
                    mock_create_parser.return_value = mock_parser
                    
                    with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                        result = main(['data', '--country', 'Syria'])
                        
                        self.assertEqual(result, 1)
                        stderr_output = mock_stderr.getvalue()
                        self.assertIn("Test error", stderr_output)
    
    def test_get_version(self):
        """Test version retrieval."""
        from acled.cli.main import get_version
        
        # Test fallback version by mocking the import to raise ImportError
        with patch('builtins.__import__', side_effect=ImportError):
            version = get_version()
            self.assertEqual(version, "0.1.7")


if __name__ == '__main__':
    unittest.main()