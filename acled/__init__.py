"""ACLED API Wrapper.

A Python client for the Armed Conflict Location & Event Data Project (ACLED) API.
This package provides a convenient interface to access ACLED data and services.
"""

from acled.clients import AcledClient

try:
    from acled._version import version as __version__
except ImportError:
    __version__ = "0.1.7"  # fallback version
