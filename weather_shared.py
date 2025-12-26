# weather_shared.py
"""
Shared configuration, environment setup, and domain models
used across the Weather application.

This module contains:
- Runtime environment setup (UTF-8, dotenv)
- Global home location constants
- Core data model: WeatherData
- Helper functions: parse_location, degrees_to_direction

"""

# -------------------------
# Runtime / environment setup
# -------------------------
import os
import sys
import io
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

load_dotenv()
os.environ["PYTHONUTF8"] = "1"

# -------------------------
# Global configuration / defaults
# -------------------------
# Default home location (from environment)
HOME_CITY = os.getenv("HOME_CITY")
HOME_LAT = os.getenv("HOME_LATITUDE")
HOME_LON = os.getenv("HOME_LONGITUDE")


# -------------------------
# Domain models
# -------------------------
class WeatherData:
    """
    Represents the weather conditions for a location at a point in time.

    Attributes:
        Temperature / feels:
            temperature (float)
            feels_like (float)
            wind_chill (float)
            heat_index (float)
            dew_point (float)

        Wind:
            wind_speed (float)
            wind_degree (float)
            wind_direction (str)
            wind_gust (float)

        Atmosphere:
            humidity (float)
            pressure (float)
            precipitation (float)
            visibility (float)
            cloud_cover (float)
            uv (float)

        Other:
            timestamp (datetime)
            condition (dict or list): structured weather description
    """

    def __init__(self):
        # Temperature / feels
        self.temperature = None
        self.feels_like = None
        self.wind_chill = None
        self.heat_index = None
        self.dew_point = None

        # Wind
        self.wind_speed = None
        self.wind_degree = None
        self.wind_direction = None
        self.wind_gust = None

        # Atmosphere
        self.humidity = None
        self.pressure = None
        self.precipitation = None
        self.visibility = None
        self.cloud_cover = None
        self.uv = None

        # Other
        self.timestamp = None
        self.condition = None

    def __repr__(self):
        # Nicely formatted multi-line representation of all attributes
        # usage: print(WeatherData)
        attrs = "\n    ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"WeatherData(\n    {attrs}\n)"


def parse_location(location: str):
    """
    Parse a location string and return a dict with keys: lat, lon, city, state.

    Acceptable input formats:
        - "lat,lon"      -> returns lat & lon as floats
        - "city,state"   -> returns city & state as strings

    Args:
        location (str): location string

    Returns:
        dict: {"lat": float or None, "lon": float or None, "city": str or None, "state": str or None}

    Raises:
        ValueError: if the string is not in an accepted format
    """
    parts = location.split(",")

    if len(parts) == 2:
        try:
            # Try parsing as lat/lon floats
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return {"lat": lat, "lon": lon, "city": None, "state": None}
        except ValueError:
            # Not floats → treat as city/state
            city = parts[0].strip()
            state = parts[1].strip()
            return {"lat": None, "lon": None, "city": city, "state": state}
    else:
        raise ValueError("Location string must be 'lat,lon' or 'city,state'")


def degrees_to_direction(deg: float) -> str:
    """
    Convert wind degree (0-360) into compass direction.
    Uses 16 cardinal directions.

    Args:
        deg (float): wind direction in degrees

    Returns:
        str: compass direction, e.g., 'N', 'NE', 'SW', etc.

    """
    if deg is None:
        return None

    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    idx = int((deg + 11.25) / 22.5) % 16
    return directions[idx]
