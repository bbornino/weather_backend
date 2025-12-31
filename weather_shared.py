# weather_shared.py
"""
Shared configuration, environment setup, domain models, and helpers
used across the Weather application.

This module contains:

1. Runtime environment setup
   - UTF-8 encoding
   - dotenv environment variables

2. Global configuration / defaults
   - HOME_CITY, HOME_LAT, HOME_LON

3. Core Data Objects
   - WeatherData: atomic weather conditions
   - WeatherReport: normalized per-source weather data
   - WeatherView: aggregated view for UI/CLI

4. Shared Functions
   - parse_location(location: str)
   - degrees_to_direction(deg: float)

5. Weather Code Map
   - WEATHER_CODE_MAP: WMO (World Meteorological Organization) codes
"""

# ==========================
# Runtime / Environment Setup
# ==========================
import os
import sys
import io
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

load_dotenv()
os.environ["PYTHONUTF8"] = "1"

# ==========================
# Global Configuration / Defaults
# ==========================
# Default home location (from environment)
HOME_CITY = os.getenv("HOME_CITY")
HOME_LAT = os.getenv("HOME_LATITUDE")
HOME_LON = os.getenv("HOME_LONGITUDE")


# ==========================
# Core Data Objects
# ==========================
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
        self.icon = None  # URL to NWS weather icon
        self.timestamp = None
        self.condition = None
        self.condition_str = None

    def __repr__(self):
        # Nicely formatted multi-line representation of all attributes
        # usage: print(WeatherData)
        attrs = "\n    ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"WeatherData(\n    {attrs}\n)"


class WeatherReport:
    """
    Represents a normalized weather report returned by a scraper.

    This object is API-agnostic and serves as the internal contract between
    weather scrapers and the rest of the application. Scrapers are responsible
    for translating raw API responses into this structure.

    A WeatherReport always contains current weather data, and may optionally
    contain hourly and/or daily forecast data depending on API support and
    request configuration.

    Attributes:
        source (str):
            Identifier for the data source (e.g. "open_meteo", "weatherapi", "nws").

        location (Location or dict):
            Normalized location information associated with this report.

        fetched_at (datetime):
            Timestamp indicating when the data was retrieved from the API.

        current (WeatherData):
            REQUIRED. Current weather conditions for the location.

        hourly (list[WeatherData] or None):
            OPTIONAL. Hourly forecast data. May be None if not requested or
            not supported by the API.

        daily (list[WeatherData] or None):
            OPTIONAL. Daily forecast data. May be None if not requested or
            not supported by the API.
    """

    def __init__(self):
        self.source = None
        self.location = None
        self.latitude = None
        self.longitude = None
        self.fetched_at = None
        self.current = None
        self.hourly = None
        self.daily = None
        self.astronomy = None
        self.alerts = None

    def __repr__(self):
        # Helper to recursively format attributes
        def format_attr(value, indent=1):
            space = "    " * indent
            if isinstance(value, list):
                return (
                    "[\n"
                    + ",\n".join(format_attr(v, indent + 1) for v in value)
                    + f"\n{space}]"
                )
            elif hasattr(value, "__repr__") and not isinstance(value, str):
                # Call repr() of nested object with extra indent
                nested = repr(value)
                nested_lines = nested.splitlines()
                indented_lines = [space + line for line in nested_lines]
                return "\n".join(indented_lines)
            else:
                return repr(value)

        attrs = "\n".join(f"    {k}={format_attr(v)}" for k, v in vars(self).items())
        return f"WeatherReport(\n{attrs}\n)"


class WeatherView:
    """
    Represents a presentation-ready view of weather data for the UI or CLI.

    This object aggregates one or more WeatherReport instances and enriches
    them with application-level metadata and display-specific information.
    It is not returned by scrapers and should only be constructed by the
    application or presentation layer.

    WeatherView owns configuration and rendering context such as units,
    timezone, and generation time, ensuring a single source of truth for
    how weather data is displayed.

    Attributes:
        app_name (str):
            Name of the application generating the output.

        app_version (str):
            Version of the application generating the output.

        units (str):
            Unit system used for display (e.g. "imperial", "metric").

        timezone (str):
            Timezone used for interpreting and displaying time-based data.

        generated_at (datetime):
            Timestamp indicating when this view was generated/rendered.

        summary (str):
            High-level, human-readable summary of the weather conditions.

        reports (list[WeatherReport]):
            One or more normalized weather reports to be displayed or grouped
            together in the UI or CLI.
    """

    def __init__(self):
        self.app_name = None
        self.app_version = None
        self.units = None
        self.generated_at = None
        self.timezone = None
        self.summary = None
        self.reports = None

    def __repr__(self):
        # Helper to recursively format attributes
        def format_attr(value, indent=1):
            space = "    " * indent
            if isinstance(value, list):
                return (
                    "[\n"
                    + ",\n".join(format_attr(v, indent + 1) for v in value)
                    + f"\n{space}]"
                )
            elif hasattr(value, "__repr__") and not isinstance(value, str):
                # Call repr() of nested object with extra indent
                nested = repr(value)
                nested_lines = nested.splitlines()
                indented_lines = [space + line for line in nested_lines]
                return "\n".join(indented_lines)
            else:
                return repr(value)

        attrs = "\n".join(f"    {k}={format_attr(v)}" for k, v in vars(self).items())
        return f"WeatherView(\n{attrs}\n)"


# ==========================
# Shared Helper Functions
# ==========================


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


# -------------------------
# Maps
# -------------------------
"""
The WEATHER_CODE_MAP provides a complete mapping of WMO (World Meteorological Organization)
international weather condition codes to human-readable descriptions. These codes are
used by major weather data providers (including Open-Meteo, Meteostat, and others)
to standardize weather condition reporting. This map allows all weather scrapers
and data processors in the project to share a common reference.
"""

WEATHER_CODE_MAP = {
    0: "Cloud development not observed or not observable",
    1: "Clouds generally dissolving or becoming less developed",
    2: "State of sky on the whole unchanged",
    3: "Clouds generally forming or developing",
    4: "Visibility reduced by smoke, e.g. veldt or forest fires, industrial smoke or volcanic ashes",
    5: "Haze",
    6: "Widespread dust in suspension in the air, not raised by wind at or near the station at the time of observation",
    7: "Dust or sand raised by wind at or near the station, but no well-developed dust whirl(s) or sand whirl(s), and no duststorm or sandstorm seen",
    8: "Well-developed dust or sand whirl(s) seen at or near the station during the preceding hour or at the time of observation, but no duststorm or sandstorm",
    9: "Duststorm or sandstorm within sight at the time of observation, or at the station during the preceding hour",
    10: "Mist",
    11: "Patches of shallow fog or ice fog at the station, whether on land or sea, not deeper than about 2 m on land or 10 m at sea",
    12: "More or less continuous shallow fog or ice fog at the station, whether on land or sea, not deeper than about 2 m on land or 10 m at sea",
    13: "Lightning visible, no thunder heard",
    14: "Precipitation within sight, not reaching the ground or the surface of the sea",
    15: "Precipitation within sight, reaching the ground or the surface of the sea, but distant (i.e. estimated to be more than 5 km from the station)",
    16: "Precipitation within sight, reaching the ground or surface, near to but not at the station",
    17: "Thunderstorm, but no precipitation at the time of observation",
    18: "Squalls at or within sight of the station during the preceding hour or at the time of observation",
    19: "Funnel cloud(s) (tornado cloud or waterspout) at or within sight of the station during the preceding hour or at the time of observation",
    20: "Drizzle (not freezing) or snow grains, not falling as shower(s)",
    21: "Rain (not freezing) not falling as shower(s)",
    22: "Snow not falling as shower(s)",
    23: "Rain and snow or ice pellets, type (a) not falling as shower(s)",
    24: "Freezing drizzle or freezing rain not falling as shower(s)",
    25: "Shower(s) of rain",
    26: "Shower(s) of snow, or of rain and snow",
    27: "Shower(s) of hail*, or of rain and hail*",
    28: "Fog or ice fog at the station during the preceding hour but not at time of observation",
    29: "Thunderstorm (with or without precipitation) at the station during the preceding hour but not at time of observation",
    30: "Slight or moderate duststorm or sandstorm — has decreased during the preceding hour",
    31: "Slight or moderate duststorm or sandstorm — no appreciable change during the preceding hour",
    32: "Slight or moderate duststorm or sandstorm — has begun or has increased during the preceding hour",
    33: "Severe duststorm or sandstorm — has decreased during the preceding hour",
    34: "Severe duststorm or sandstorm — no appreciable change during the preceding hour",
    35: "Severe duststorm or sandstorm — has begun or has increased during the preceding hour",
    36: "Slight or moderate blowing snow generally low (below eye level)",
    37: "Heavy drifting snow generally low (below eye level)",
    38: "Slight or moderate blowing snow generally high (above eye level)",
    39: "Heavy drifting snow generally high (above eye level)",
    40: "Fog or ice fog at a distance at the time of observation, but not at the station during the preceding hour, the fog or ice fog extending to a level above that of the observer",
    41: "Fog or ice fog in patches",
    42: "Fog or ice fog, sky visible has become thinner during the preceding hour",
    43: "Fog or ice fog, sky invisible preceding hour",
    44: "Fog or ice fog, sky visible — no appreciable change during the preceding hour",
    45: "Fog or ice fog, sky invisible — no appreciable change during the preceding hour",
    46: "Fog or ice fog, sky visible has begun or become thicker during the preceding hour",
    47: "Fog or ice fog, sky invisible has begun or become thicker during the preceding hour",
    48: "Fog, depositing rime, sky visible",
    49: "Fog, depositing rime, sky invisible",
    50: "Drizzle, not freezing, intermittent slight at time of observation",
    51: "Drizzle, not freezing, continuous slight at time of observation",
    52: "Drizzle, not freezing, intermittent moderate at time of observation",
    53: "Drizzle, not freezing, continuous moderate at time of observation",
    54: "Drizzle, not freezing, intermittent heavy (dense) at time of observation",
    55: "Drizzle, not freezing, continuous heavy (dense) at time of observation",
    56: "Drizzle, freezing, slight",
    57: "Drizzle, freezing, moderate or heavy (dense)",
    58: "Drizzle and rain, slight",
    59: "Drizzle and rain, moderate or heavy",
    60: "Rain, not freezing, intermittent slight at time of observation",
    61: "Rain, not freezing, continuous slight at time of observation",
    62: "Rain, not freezing, intermittent moderate at time of observation",
    63: "Rain, not freezing, continuous moderate at time of observation",
    64: "Rain, not freezing, intermittent heavy at time of observation",
    65: "Rain, not freezing, continuous heavy at time of observation",
    66: "Rain, freezing, slight",
    67: "Rain, freezing, moderate or heavy (dense)",
    68: "Rain or drizzle and snow, slight",
    69: "Rain or drizzle and snow, moderate or heavy",
    70: "Intermittent fall of snowflakes slight at time of observation",
    71: "Continuous fall of snowflakes",
    72: "Intermittent fall of snowflakes moderate at time of observation",
    73: "Continuous fall of snowflakes moderate at time of observation",
    74: "Intermittent fall of snowflakes heavy at time of observation",
    75: "Continuous fall of snowflakes heavy at time of observation",
    76: "Diamond dust (with or without fog)",
    77: "Snow grains (with or without fog)",
    78: "Isolated star-like snow crystals (with or without fog)",
    79: "Ice pellets, type (a)",
    80: "Rain shower(s), slight",
    81: "Rain shower(s), moderate or heavy",
    82: "Rain shower(s), violent",
    83: "Shower(s) of rain and snow mixed, slight",
    84: "Shower(s) of rain and snow mixed, moderate or heavy",
    85: "Snow shower(s), slight",
    86: "Snow shower(s), moderate or heavy",
    87: "Shower(s) of snow pellets or ice pellets, type (b), with or without rain or rain and snow mixed — slight",
    88: "Shower(s) of snow pellets or ice pellets, type (b), with or without rain or rain and snow mixed — moderate or heavy",
    89: "Shower(s) of hail*, with or without rain or rain and snow mixed, not associated with thunder — slight",
    90: "Shower(s) of hail*, with or without rain or rain and snow mixed, not associated with thunder — moderate or heavy",
    91: "Slight rain at time of observation — thunderstorm during preceding hour but not at time of observation",
    92: "Moderate or heavy rain at time of observation — thunderstorm during preceding hour but not at time of observation",
    93: "Slight snow, or rain and snow mixed or hail** at time of observation — thunderstorm during preceding hour but not at time of observation",
    94: "Moderate or heavy snow, or rain and snow mixed or hail** at time of observation — thunderstorm during preceding hour but not at time of observation",
    95: "Thunderstorm, slight or moderate, without hail**, but with rain and/or snow at time of observation — thunderstorm at time of observation",
    96: "Thunderstorm, slight or moderate, with hail** at time of observation — thunderstorm at time of observation",
    97: "Thunderstorm, heavy, without hail**, but with rain and/or snow at time of observation — thunderstorm at time of observation",
    98: "Thunderstorm combined with duststorm or sandstorm at time of observation",
    99: "Thunderstorm, heavy, with hail** at time of observation — thunderstorm at time of observation",
}
