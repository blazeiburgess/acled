#!/usr/bin/env python3
"""ACLED CLI - Command-line interface for the ACLED API."""

import argparse
import sys
from typing import List, Optional

from acled.cli.commands.auth import AuthCommand
from acled.cli.commands.data import DataCommand
from acled.cli.utils.config import CLIConfig
from acled.exceptions import AcledMissingAuthError


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='acled',
        description='Command-line interface for the ACLED API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Authenticate (first time setup)
  acled auth login

  # Get recent events from Syria
  acled data --country Syria --year 2024 --limit 10

  # Get data with table output
  acled data --country Nigeria --format table

  # Get help for a specific command
  acled data --help
        '''
    )

    # Global options
    parser.add_argument(
        '--version',
        action='version',
        version=f'acled {get_version()}'
    )
    parser.add_argument(
        '--api-key',
        help='ACLED API key (can also use ACLED_API_KEY env var)'
    )
    parser.add_argument(
        '--email',
        help='Email address for API access (can also use ACLED_EMAIL env var)'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'table', 'summary'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-essential output'
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )

    # Register command parsers
    AuthCommand.register_parser(subparsers)
    DataCommand.register_parser(subparsers)

    return parser


def get_version() -> str:
    """Get the package version."""
    try:
        from acled._version import version
        return version
    except ImportError:
        return "0.1.7"  # fallback


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Handle case where no command is provided
    if not args.command:
        parser.print_help()
        return 1

    # Initialize configuration
    config = CLIConfig(args)

    # Command mapping
    commands = {
        'auth': AuthCommand,
        'data': DataCommand,
    }

    # Execute command
    try:
        command_class = commands[args.command]
        command = command_class(config)
        return command.execute(args)
    except AcledMissingAuthError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nPlease authenticate using one of these methods:", file=sys.stderr)
        print("  1. acled auth login  (recommended - secure storage)", file=sys.stderr)
        print("  2. --api-key and --email options", file=sys.stderr)
        print("  3. ACLED_API_KEY and ACLED_EMAIL environment variables", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        if config.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
