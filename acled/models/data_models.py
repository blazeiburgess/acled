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
