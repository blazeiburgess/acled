# ACLED API Wrapper

A Python library that wraps the ACLED API.

## Installation

Use [Poetry](https://python-poetry.org/) to install the package:

```bash
poetry add acled
```

Or install via `pip` (after building):

```bash
pip install acled
```

## Usage

You can set the required API key and Email variables with environment variables or pass them in directly. The relevant variables naames are:

- ACLED_API_KEY
- ACLED_EMAIL

### Example where env variables are set

```python
from acled import AcledClient

# Initialize the client
client = AcledClient()

# Fetch data with optional filters
filters = {
    'limit': 10,
    'event_date': '2023-01-01|2023-01-31'
}

events = client.acled_data_client.get_data(params=filters)

# Iterate over events
for event in events:
    print(event['event_id_cnty'], event['event_date'], event['notes'])

```

### Example passing in credentials

```python
from acled import AcledClient
# assuming you are using a local.py file
from .local import api_key, email

# Initialize the client
client = AcledClient(api_key=api_key, email=email)

# Fetch data with optional filters
filters = {
    'limit': 10,
    'event_date': '2023-01-01|2023-01-31'
}

events = client.acled_data_client.get_data(params=filters)

# Iterate over events
for event in events:
    print(event['event_id_cnty'], event['event_date'], event['notes'])
```

## Configuration

All requests require a valid API key and the email that is registered to that API key.

ACLED is an amazing service provided at no cost so please be respectful and measured in your usage.

## Reference

[Here's the original API documentation](https://acleddata.com/acleddatanew/wp-content/uploads/2020/10/ACLED_API-User-Guide_2020.pdf) (2020)