# Unofficial ACLED API Wrapper

A Python library that unofficially wraps the ACLED (Armed Conflict Location & Event Data) API. This library provides a convenient interface for accessing and analyzing conflict and protest data from around the world.

[ACLED (Armed Conflict Location & Event Data Project)](https://acleddata.com/) is a disaggregated data collection, analysis, and crisis mapping project that tracks political violence and protest events across the world.

## Installation

Install via `pip`:

```bash
pip install acled
```

## Python Library Authentication

All requests to the ACLED API require authentication with a valid API key and the email that is registered to that API key. You can obtain these by registering on the [ACLED website](https://acleddata.com/register/).

You can provide authentication credentials in two ways:

### 1. Environment Variables

Set the following environment variables:

- `ACLED_API_KEY` - Your ACLED API key
- `ACLED_EMAIL` - The email associated with your API key

### 2. Direct Parameters

Pass the credentials directly when initializing the client:

```python
client = AcledClient(api_key="your_api_key", email="your_email")
```

## Basic Usage

### Example with Environment Variables

```python
from acled import AcledClient
from acled.models import AcledEvent
from typing import List, Dict

# Initialize the client (uses environment variables)
client = AcledClient()

# Fetch data with optional filters
filters: Dict[str, int | str] = {
    'limit': 10,
    'event_date': '2023-01-01|2023-01-31'
}

events: List[AcledEvent] = client.get_data(params=filters)

# Iterate over events
for event in events:
    print(event['event_id_cnty'], event['event_date'], event['notes'])
```

### Example with Direct Credentials

```python
from acled import AcledClient
from acled.models import AcledEvent
from typing import List

# Initialize the client with credentials
client = AcledClient(api_key="your_api_key", email="your_email")

# Fetch data with optional filters
filters = {
    'limit': 10,
    'event_date': '2023-01-01|2023-01-31'
}

events: List[AcledEvent] = client.get_data(params=filters)

# Iterate over events
for event in events:
    print(event['event_id_cnty'], event['event_date'], event['notes'])
```

## Advanced Usage

### Filtering Data

The API supports various filtering options for retrieving specific data:

```python
from acled import AcledClient
from acled.models.enums import ExportType

client = AcledClient()

# Fetch data with multiple filters
events = client.get_data(
    country='Yemen',           # Filter by country
    year=2023,                 # Filter by year
    event_type='Battles',      # Filter by event type
    fatalities=5,              # Filter by fatalities
    export_type=ExportType.JSON,  # Specify export format
    limit=5,                   # Limit number of results
)

for event in events:
    print(f"{event['country']} - {event['event_date']} - {event['fatalities']} fatalities - {event['event_type']}")
```

### Using Filter Operators

You can use different operators for filtering by appending a `_where` suffix to parameter names in the `query_params` dictionary:

```python
from acled import AcledClient

client = AcledClient()

# Filter events with more than 5 fatalities
events = client.get_data(
    country='Yemen',
    fatalities=5,
    limit=10,
    query_params={
        'fatalities_where': '>',  # Greater than
    }
)

# Filter events with event_type containing the word "Violence"
events = client.get_data(
    limit=10,
    query_params={
        'event_type': 'Violence',
        'event_type_where': 'LIKE',  # LIKE operator for partial matching
    }
)
```

Available operators:
- `=` (default): Exact match
- `>`: Greater than
- `<`: Less than
- `>=`: Greater than or equal to
- `<=`: Less than or equal to
- `LIKE`: Partial match (case-insensitive)

### Date Range Filtering

For date ranges, use the pipe character (`|`) to separate start and end dates:

```python
events = client.get_data(
    event_date='2023-01-01|2023-12-31',  # Events from Jan 1 to Dec 31, 2023
    limit=50
)
```

## Available Endpoints

The library provides access to several ACLED API endpoints through specialized clients:

### 1. Event Data (Main Data)

```python
# Get event data
events = client.get_data(limit=10)
```

### 2. Actor Data

```python
# Get actor data
actors = client.get_actor_data(limit=10)
for actor in actors:
    print(actor['actor_name'], actor['event_count'])
```

### 3. Country Data

```python
# Get country data
countries = client.get_country_data(limit=10)
for country in countries:
    print(country['country'], country['event_count'])
```

### 4. Region Data

```python
# Get region data
regions = client.get_region_data(limit=10)
for region in regions:
    print(region['region_name'], region['event_count'])
```

### 5. Actor Type Data

```python
# Get actor type data
actor_types = client.get_actor_type_data(limit=10)
for actor_type in actor_types:
    print(actor_type['actor_type_name'], actor_type['event_count'])
```

## Data Models

The library provides TypedDict models for the data returned by the API:

### AcledEvent

Represents an event with fields including:
- `event_id_cnty`: Unique identifier for the event
- `event_date`: Date of the event
- `year`: Year of the event
- `time_precision`: Precision of the event time (1=exact date, 2=approximate date, 3=estimated date)
- `disorder_type`: Type of disorder (Political violence, Demonstrations, etc.)
- `event_type`: Type of event (Battles, Violence against civilians, etc.)
- `sub_event_type`: Sub-type of event
- `actor1`, `actor2`: Primary actors involved in the event
- `location`: Location name
- `latitude`, `longitude`: Geographic coordinates
- `fatalities`: Number of reported fatalities
- `notes`: Description of the event

### Actor

Represents an actor with fields including:
- `actor_name`: Name of the actor
- `first_event_date`: Date of the actor's first recorded event
- `last_event_date`: Date of the actor's most recent recorded event
- `event_count`: Total number of events involving this actor

### Country

Represents a country with fields including:
- `country`: Country name
- `iso`: ISO country code
- `iso3`: ISO3 country code
- `event_count`: Total number of events in this country

### Region

Represents a region with fields including:
- `region`: Region ID
- `region_name`: Region name
- `event_count`: Total number of events in this region

### ActorType

Represents an actor type with fields including:
- `actor_type_id`: Actor type ID
- `actor_type_name`: Actor type name
- `event_count`: Total number of events involving this actor type

## Enums and Constants

The library provides several enum classes for standardized values:

### TimePrecision

```python
from acled.models.enums import TimePrecision

# Use in filters or check values in events
time_precision = TimePrecision.EXACT_DATE  # 1
```

- `EXACT_DATE` (1): The exact date is known
- `APPROXIMATE_DATE` (2): The date is approximate
- `ESTIMATED_DATE` (3): The date is estimated

### DisorderType

```python
from acled.models.enums import DisorderType

# Use in filters
disorder_type = DisorderType.POLITICAL_VIOLENCE  # "Political violence"
```

- `POLITICAL_VIOLENCE`: "Political violence"
- `DEMONSTRATIONS`: "Demonstrations"
- `STRATEGIC_DEVELOPMENTS`: "Strategic developments"

### ExportType

```python
from acled.models.enums import ExportType

# Specify the format of the returned data
export_type = ExportType.JSON  # "json"
```

- `JSON`: "json"
- `XML`: "xml"
- `CSV`: "csv"
- `XLSX`: "xlsx"
- `TXT`: "txt"

### Actor

```python
from acled.models.enums import Actor

# Use for inter1 and inter2 values
actor_type = Actor.STATE_FORCES  # 1
```

- `STATE_FORCES` (1)
- `REBEL_FORCES` (2)
- `MILITIA_GROUPS` (3)
- `COMMUNAL_IDENTITY_GROUPS` (4)
- `RIOTERS` (5)
- `PROTESTERS` (6)
- `CIVILIANS` (7)
- `FOREIGN_OTHERS` (8)

### Region

```python
from acled.models.enums import Region

# Use in filters
region = Region.WESTERN_AFRICA  # 1
```

- `WESTERN_AFRICA` (1)
- `MIDDLE_AFRICA` (2)
- `EASTERN_AFRICA` (3)
- `SOUTHERN_AFRICA` (4)
- `NOTHERN_AFRICA` (5)
- `SOUTH_ASIA` (7)
- `SOUTHEAST_ASIA` (9)
- `MIDDLE_EAST` (11)
- `EUROPE` (12)
- `CAUCASUS_AND_CENTRAL_ASIA` (13)
- `CENTRAL_AMERICA` (14)
- `SOUTH_AMERICA` (15)
- `CARIBBEAN` (16)
- `EAST_ASIA` (17)
- `NORTH_AMERICA` (18)
- `OCEANIA` (19)
- `ANTARCTICA` (20)

## Configuration Options

The library's behavior can be configured through environment variables:

- `ACLED_API_KEY`: Your ACLED API key
- `ACLED_EMAIL`: The email associated with your API key
- `ACLED_MAX_RETRIES`: Maximum number of retry attempts (default: 3)
- `ACLED_RETRY_BACKOFF_FACTOR`: Backoff factor for calculating wait time between retries (default: 0.5)
- `ACLED_REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)

## CLI Usage

The library includes a command-line interface for easy data access:

### Authentication

First, authenticate with your ACLED credentials:

```bash
acled auth login
```

This securely stores your API key and email for future use.

### Basic CLI Commands

```bash
# Get recent events from Syria
acled data --country Syria --year 2024 --limit 10

# Get data with table output
acled data --country Nigeria --format table

# Get data with specific filters
acled data --country Yemen --event-type Battles --limit 5 --format summary

# Save output to file
acled data --country Afghanistan --year 2024 --output events.json

# Get help for any command
acled data --help
```

### CLI Authentication Options

You can authenticate in three ways:

1. **Secure login** (recommended):
   ```bash
   acled auth login
   ```

2. **Command-line options**:
   ```bash
   acled data --api-key YOUR_API_KEY --email YOUR_EMAIL --country Syria
   ```

3. **Environment variables**:
   ```bash
   export ACLED_API_KEY="your_api_key"
   export ACLED_EMAIL="your_email"
   acled data --country Syria
   ```

## Important Notes

ACLED is an amazing service provided at no cost, so please be respectful and measured in your usage. Consider implementing caching in your application to reduce the number of API calls.

## References

- [ACLED Website](https://acleddata.com/)
- [ACLED API Documentation](https://acleddata.com/acleddatanew/wp-content/uploads/2020/10/ACLED_API-User-Guide_2020.pdf) (2020)

## Development and Contributing

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/blazeiburgess/acled.git
   cd acled
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=acled --cov-report=term-missing
```

## TODO

- Add client for deleted api, add method to access from main client
- Better document more advanced features (e.g. filter type changes = vs. > vs. < vs. LIKE). They should work now (partially tested), but are a little obscure.
