"""Base command class for ACLED CLI."""

import argparse
from abc import ABC, abstractmethod
from typing import Any, Optional

from acled.clients import AcledClient
from acled.cli.utils.config import CLIConfig
from acled.cli.formatters import get_formatter


class BaseCommand(ABC):
    """Base class for all CLI commands."""

    def __init__(self, config: CLIConfig):
        self.config = config
        self.client = AcledClient(
            api_key=config.api_key,
            email=config.email
        )

    @classmethod
    @abstractmethod
    def register_parser(cls, subparsers: argparse._SubParsersAction) -> None:
        """Register the command's argument parser."""

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """Execute the command."""

    def output_data(self, data: Any, format_type: str, output_file: Optional[str] = None) -> None:
        """Output data using the specified formatter."""
        formatter = get_formatter(format_type)
        formatted_data = formatter.format(data)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_data)
            if not self.config.quiet:
                print(f"Output written to {output_file}")
        else:
            print(formatted_data)

    def add_common_filters(self, parser: argparse.ArgumentParser) -> None:
        """Add common filtering options to a parser."""
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Number of records to retrieve (default: 50)'
        )
        parser.add_argument(
            '--page',
            type=int,
            help='Page number for pagination'
        )
        parser.add_argument(
            '--export-type',
            choices=['json', 'xml', 'csv'],
            default='json',
            help='API export type (default: json)'
        )
