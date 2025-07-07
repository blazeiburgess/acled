"""Data command for retrieving ACLED events."""

import argparse
from typing import Optional

from acled.cli.commands.base import BaseCommand
from acled.models.enums import ExportType


class DataCommand(BaseCommand):
    """Command for retrieving ACLED event data."""
    
    @classmethod
    def register_parser(cls, subparsers: argparse._SubParsersAction) -> None:
        """Register the data command parser."""
        parser = subparsers.add_parser(
            'data',
            help='Retrieve ACLED event data',
            description='Retrieve event data from the ACLED database with various filters.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  # Get recent events from Syria
  acled data --country Syria --year 2024
  
  # Get violent events with high fatalities
  acled data --event-type "Violence against civilians" --fatalities 10
  
  # Get events in a specific region with date range
  acled data --region 1 --start-date 2024-01-01 --end-date 2024-12-31
            '''
        )
        
        # Location filters
        location_group = parser.add_argument_group('Location Filters')
        location_group.add_argument(
            '--country',
            help='Filter by country name'
        )
        location_group.add_argument(
            '--region',
            type=int,
            help='Filter by region number'
        )
        location_group.add_argument(
            '--iso',
            type=int,
            help='Filter by ISO country code'
        )
        
        # Time filters
        time_group = parser.add_argument_group('Time Filters')
        time_group.add_argument(
            '--year',
            type=int,
            help='Filter by year'
        )
        time_group.add_argument(
            '--start-date',
            help='Start date (YYYY-MM-DD format)'
        )
        time_group.add_argument(
            '--end-date',
            help='End date (YYYY-MM-DD format)'
        )
        
        # Event filters
        event_group = parser.add_argument_group('Event Filters')
        event_group.add_argument(
            '--event-type',
            help='Filter by event type'
        )
        event_group.add_argument(
            '--fatalities',
            type=int,
            help='Filter by minimum number of fatalities'
        )
        
        # Add common options
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
    
    def execute(self, args: argparse.Namespace) -> int:
        """Execute the data command."""
        # Build parameters dictionary
        params = {}
        
        # Location parameters
        if args.country:
            params['country'] = args.country
        if args.region:
            params['region'] = args.region
        if args.iso:
            params['iso'] = args.iso
        
        # Time parameters
        if args.year:
            params['year'] = args.year
        if args.start_date:
            params['event_date'] = args.start_date
        
        # Event parameters
        if args.event_type:
            params['event_type'] = args.event_type
        if args.fatalities:
            params['fatalities'] = args.fatalities
        
        # Common parameters
        params['limit'] = args.limit
        if args.page:
            params['page'] = args.page
        if hasattr(args, 'export_type') and args.export_type:
            params['export_type'] = ExportType(args.export_type)
        
        # Execute query
        if not self.config.quiet:
            print(f"Fetching ACLED data with {len(params)} filters...")
        
        try:
            data = self.client.get_data(**params)
            
            if not self.config.quiet:
                print(f"Retrieved {len(data)} records")
            
            # Output data
            self.output_data(
                data,
                self.config.format,
                self.config.output_file
            )
            
            return 0
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return 1
