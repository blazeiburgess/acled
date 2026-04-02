"""Data model classes for the ACLED API.

This module defines TypedDict classes that represent the structure of data
returned by the ACLED API, including events, actors, countries, regions, and
actor types.
"""

from typing import Optional, TypedDict
import datetime


class AcledEvent(TypedDict, total=False):
    """TypedDict representing an ACLED event.

    Contains all fields that describe an event in the ACLED database, including
    its identifiers, date, location, actors involved, and other attributes.
    """
    event_id_cnty: str
    event_date: datetime.date
    year: int
    time_precision: int
    disorder_type: str
    event_type: str
    sub_event_type: str
    actor1: str
    assoc_actor_1: Optional[str]
    inter1: int
    actor2: Optional[str]
    assoc_actor_2: Optional[str]
    inter2: Optional[int]
    interaction: int
    civilian_targeting: Optional[str]
    iso: int
    region: str
    country: str
    admin1: Optional[str]
    admin2: Optional[str]
    admin3: Optional[str]
    location: str
    latitude: float
    longitude: float
    geo_precision: int
    source: str
    source_scale: str
    notes: str
    fatalities: int
    tags: Optional[str]
    timestamp: datetime.datetime


class Actor(TypedDict, total=False):
    """TypedDict representing an actor in the ACLED database.

    Contains information about an actor involved in ACLED events, including
    their name and event statistics.
    """
    actor_name: str
    first_event_date: datetime.date
    last_event_date: datetime.date
    event_count: int

class Country(TypedDict, total=False):
    """TypedDict representing a country in the ACLED database.

    Contains information about a country where ACLED events have occurred,
    including its name, ISO codes, and event statistics.
    """
    country: str
    iso: int
    iso3: str
    first_event_date: datetime.date
    last_event_date: datetime.date
    event_count: int

class Region(TypedDict, total=False):
    """TypedDict representing a geographical region in the ACLED database.

    Contains information about a region where ACLED events have occurred,
    including its ID, name, and event statistics.
    """
    region: int
    region_name: str
    first_event_date: datetime.date
    last_event_date: datetime.date
    event_count: int

class CastForecast(TypedDict, total=False):
    """TypedDict representing a CAST (Conflict Alert System) forecast.

    Contains forecast and observed event counts for a given country/admin1
    region and time period, broken down by event type (battles, explosions/
    remote violence, violence against civilians).
    """
    country: str
    admin1: str
    month: str
    year: int
    total_forecast: int
    battles_forecast: int
    erv_forecast: int
    vac_forecast: int
    total_observed: int
    battles_observed: int
    erv_observed: int
    vac_observed: int
    timestamp: int


class DeletedEvent(TypedDict, total=False):
    """TypedDict representing a deleted event record from the ACLED database.

    Contains the identifier of an event that has been removed from the dataset,
    along with the timestamp of its deletion.
    """
    event_id_cnty: str
    deleted_timestamp: int


class ActorType(TypedDict, total=False):
    """TypedDict representing a type of actor in the ACLED database.

    Contains information about a category of actors involved in ACLED events,
    including its ID, name, and event statistics.
    """
    actor_type_id: int
    actor_type_name: str
    first_event_date: datetime.date
    last_event_date: datetime.date
    event_count: int
