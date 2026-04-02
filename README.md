# Unofficial ACLED API Wrapper

A Python library that unofficially wraps the ACLED (Armed Conflict Location & Event Data) API. This library provides a convenient interface for accessing and analyzing conflict and protest data from around the world.

[ACLED (Armed Conflict Location & Event Data Project)](https://acleddata.com/) is a disaggregated data collection, analysis, and crisis mapping project that tracks political violence and protest events across the world.

## Installation

Install via `pip`:

```bash
pip install acled
```

## Authentication

ACLED requires authentication for all API requests. Register on the [ACLED website](https://acleddata.com/register/) to get credentials.

The library supports multiple authentication methods:

### Modern Authentication (Recommended)

Use your ACLED username/email and password:

```python
from acled import AcledClient

# Auto-detect best method (OAuth or Cookie)
client = AcledClient(username="your_email", password="your_password")

# Or use environment variables
# export ACLED_USERNAME="your_email"  (or ACLED_EMAIL)
# export ACLED_PASSWORD="your_password"
client = AcledClient()  # Auto-detects from environment
```

### Legacy Authentication (API Key)

Still supported in the code, but seems broken in the API. Will be removed soon once confirmed:

```python
client = AcledClient(api_key="your_api_key", email="your_email")

# Or use environment variables
# export ACLED_API_KEY="your_api_key"
# export ACLED_EMAIL="your_email"
```

## Basic Usage

```python
from acled import AcledClient
from acled.models import AcledEvent
from typing import List

client = AcledClient()

# Fetch event data with filters
events: List[AcledEvent] = client.get_data(
    country='Yemen',
    year=2024,
    limit=10
)

for event in events:
    print(f"{event['event_date']}: {event['event_type']} - {event['country']}")
```

## Advanced Usage

### Filtering Data

```python
from acled import AcledClient

client = AcledClient()

# Fetch data with multiple filters
events = client.get_data(
    country='Yemen',
    year=2023,
    event_type='Battles',
    fatalities=5,
    limit=5,
)

for event in events:
    print(f"{event['country']} - {event['event_date']} - {event['fatalities']} fatalities")
```

### Using Filter Operators

Use `_where` suffixes via the `query_params` dictionary to change the default filter operator:

```python
client = AcledClient()

# Filter events with more than 5 fatalities
events = client.get_data(
    country='Yemen',
    fatalities=5,
    limit=10,
    query_params={'fatalities_where': '>'},
)

# Filter events with event_type containing "Violence"
events = client.get_data(
    limit=10,
    query_params={
        'event_type': 'Violence',
        'event_type_where': 'LIKE',
    }
)
```

Available operators:
- `=` (default): Exact match
- `>`, `<`, `>=`, `<=`: Comparison operators
- `LIKE`: Partial match (case-insensitive)
- `BETWEEN`: Range filter (use pipe `|` to separate values)

### Date Range Filtering

Use `BETWEEN` with pipe-separated dates:

```python
events = client.get_data(
    event_date='2023-01-01|2023-12-31',
    query_params={'event_date_where': 'BETWEEN'},
    limit=50,
)
```

### Dyadic vs Monadic Export

The ACLED endpoint supports two data structure formats via `export_type`:

```python
# Dyadic (default): one row per event, with actor1/actor2 columns
events = client.get_data(country='Yemen', limit=10)

# Monadic: one row per actor-event, same event may appear twice
events = client.get_data(country='Yemen', limit=10, export_type='monadic')
```

### Field Selection

Limit which fields are returned using pipe-separated field names:

```python
events = client.get_data(
    country='Yemen',
    fields='country|event_date|event_type|fatalities',
    limit=10,
)
```

## Available Endpoints

The library provides access to all ACLED API endpoints:

### 1. Event Data

The main endpoint for conflict and protest events.

```python
events = client.get_data(
    country='Yemen',
    year=2024,
    event_type='Battles',
    limit=10,
)

for event in events:
    print(f"{event['event_date']} | {event['event_type']} | fatalities: {event['fatalities']}")
```

### 2. CAST Forecast Data

Conflict Alert System forecasts — predicted and observed event counts by region and month.

```python
forecasts = client.get_cast_data(
    country='Somalia',
    year=2025,
    limit=5,
)

for f in forecasts:
    print(f"{f['country']} | {f['admin1']} | {f['month']}/{f['year']}"
          f" | forecast: {f['total_forecast']} | observed: {f['total_observed']}")
```

### 3. Deleted Events

Event IDs removed from the dataset (duplicates or out-of-scope).

```python
deleted = client.get_deleted_data(limit=5)

for d in deleted:
    print(f"{d['event_id_cnty']} | deleted_timestamp: {d['deleted_timestamp']}")
```

### 4. Actor Data

```python
actors = client.get_actor_data(limit=5)

for actor in actors:
    print(f"[{actor.get('mal_actor_id')}] {actor.get('label')}")
```

### 5. Actor Type Data

```python
actor_types = client.get_actor_type_data(limit=5)

for at in actor_types:
    print(at['actor_type_name'])
```

### 6. Country Data

```python
countries = client.get_country_data(limit=5)

for c in countries:
    print(f"{c.get('nicename')} | iso: {c.get('iso')} | iso3: {c.get('iso3')}")
```

### 7. Region Data

```python
regions = client.get_region_data(limit=5)

for r in regions:
    print(r['region_name'])
```

## Data Models

The library provides TypedDict models for type-checked API responses. All fields use `total=False` so missing fields don't raise errors (useful with the `fields` parameter).

### AcledEvent

Core event record with fields including:
- `event_id_cnty`: Unique event identifier
- `event_date`: Date of the event (`datetime.date`)
- `year`, `time_precision`: Temporal metadata
- `disorder_type`, `event_type`, `sub_event_type`: Event classification
- `actor1`, `actor2`, `assoc_actor_1`, `assoc_actor_2`: Actors involved
- `inter1`, `inter2`, `interaction`: Actor type codes
- `country`, `admin1`, `admin2`, `admin3`, `location`: Location hierarchy
- `latitude`, `longitude`, `geo_precision`: Coordinates
- `fatalities`: Reported death count
- `notes`, `tags`, `source`, `source_scale`: Descriptive metadata
- `timestamp`: Upload timestamp (`datetime.datetime`, UTC)

### CastForecast

CAST conflict forecast with fields including:
- `country`, `admin1`: Location
- `month`, `year`: Time period
- `total_forecast`, `battles_forecast`, `erv_forecast`, `vac_forecast`: Predicted event counts
- `total_observed`, `battles_observed`, `erv_observed`, `vac_observed`: Actual event counts (populated after month ends)

### DeletedEvent

Removed event record:
- `event_id_cnty`: Event identifier
- `deleted_timestamp`: Unix timestamp of deletion

### Actor, Country, Region, ActorType

Metadata models for actors, countries, regions, and actor type categories. Field availability varies by endpoint — use `.get()` for safe access.

## Enums and Constants

### TimePrecision

```python
from acled.models.enums import TimePrecision

TimePrecision.EXACT_DATE       # 1
TimePrecision.APPROXIMATE_DATE # 2
TimePrecision.ESTIMATED_DATE   # 3
```

### DisorderType

```python
from acled.models.enums import DisorderType

DisorderType.POLITICAL_VIOLENCE     # "Political violence"
DisorderType.DEMONSTRATIONS         # "Demonstrations"
DisorderType.STRATEGIC_DEVELOPMENTS # "Strategic developments"
```

### Actor

Actor type codes for `inter1`/`inter2` filters:

```python
from acled.models.enums import Actor

Actor.STATE_FORCES            # 1
Actor.REBEL_FORCES            # 2
Actor.MILITIA_GROUPS          # 3
Actor.COMMUNAL_IDENTITY_GROUPS # 4
Actor.RIOTERS                 # 5
Actor.PROTESTERS              # 6
Actor.CIVILIANS               # 7
Actor.FOREIGN_OTHERS          # 8
```

### Region

```python
from acled.models.enums import Region

Region.WESTERN_AFRICA           # 1
Region.MIDDLE_AFRICA            # 2
Region.EASTERN_AFRICA           # 3
Region.SOUTHERN_AFRICA          # 4
Region.NOTHERN_AFRICA           # 5
Region.SOUTH_ASIA               # 7
Region.SOUTHEAST_ASIA           # 9
Region.MIDDLE_EAST              # 11
Region.EUROPE                   # 12
Region.CAUCASUS_AND_CENTRAL_ASIA # 13
Region.CENTRAL_AMERICA          # 14
Region.SOUTH_AMERICA            # 15
Region.CARIBBEAN                # 16
Region.EAST_ASIA                # 17
Region.NORTH_AMERICA            # 18
Region.OCEANIA                  # 19
Region.ANTARCTICA               # 20
```

## Configuration

Environment variables for customizing library behavior:

**Authentication:**
- `ACLED_USERNAME` or `ACLED_EMAIL`: Username/email for modern auth
- `ACLED_PASSWORD`: Password for modern auth
- `ACLED_API_KEY`: API key for legacy auth
- `ACLED_EMAIL`: Email for legacy auth

**Connection:**
- `ACLED_MAX_RETRIES`: Maximum retry attempts (default: 3)
- `ACLED_RETRY_BACKOFF_FACTOR`: Backoff multiplier between retries (default: 0.5)
- `ACLED_REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)

## CLI Usage

The library includes a command-line interface:

### Authentication

```bash
# Auto-detect best method (recommended)
acled auth login

# Specify a method
acled auth login --method oauth
acled auth login --method cookie
acled auth login --method legacy
```

### Querying Data

```bash
# Get recent events from Syria
acled data --country Syria --year 2024 --limit 10

# Filter by event type and fatalities
acled data --country Yemen --event-type Battles --fatalities 5

# Date range query
acled data --start-date 2024-01-01 --end-date 2024-06-30

# Control output display format (global flag)
acled --format table data --country Nigeria --limit 10
acled --format csv data --country Syria --year 2024

# Save to file
acled data --country Afghanistan --year 2024 --output events.json
```

### CLI Authentication Options

1. **Secure login** (recommended):
   ```bash
   acled auth login  # Prompts for credentials
   ```

2. **Environment variables**:
   ```bash
   export ACLED_USERNAME="your_email"
   export ACLED_PASSWORD="your_password"
   acled data --country Syria
   ```

3. **Command-line options** (legacy only):
   ```bash
   acled data --api-key YOUR_API_KEY --email YOUR_EMAIL --country Syria
   ```

## Important Notes

- The library defaults `limit` to 50 for safety. The API default is 5000. Increase the limit and use `page` for bulk data retrieval.
- All API responses are parsed as JSON. The library does not support CSV/XML response formats directly.
- ACLED is an amazing service provided at no cost. Please be respectful and measured in your usage. Consider caching results to reduce API calls.

## References

- [ACLED Website](https://acleddata.com/)
- [ACLED API Documentation](https://acleddata.com/api-documentation)
- [Getting Started](https://acleddata.com/api-documentation/getting-started)
- [ACLED Endpoint](https://acleddata.com/api-documentation/acled-endpoint)
- [CAST Endpoint](https://acleddata.com/api-documentation/cast-endpoint)
- [Deleted Endpoint](https://acleddata.com/api-documentation/deleted-endpoint)
- [Elements of API Calls](https://acleddata.com/api-documentation/elements-acleds-api)

## Development

### Setup

```bash
git clone https://github.com/blazeiburgess/acled.git
cd acled
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Tests

```bash
pytest
pytest --cov=acled --cov-report=term-missing
```
