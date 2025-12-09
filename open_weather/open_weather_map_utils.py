"""
open_weather_map_utils.py

Configuration file for OpenWeatherMap.Org integration.

Includes:
- API key
- Base URL
- Field mappings for current weather conditions
- Helper function to print weather data in a readable format

This file is imported by open_weather_map_scraper.py and any other
modules that need OpenWeatherMap data.
"""

import os
from dotenv import load_dotenv

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()
os.environ["PYTHONUTF8"] = "1"
HOME_CITY = os.getenv("HOME_CITY")
HOME_LAT = os.getenv("HOME_LATITUDE")
HOME_LON = os.getenv("HOME_LONGITUDE")
OPEN_WEATHER_MAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
URL_BASE = "https://api.openweathermap.org/data/2.5/"


def build_conditions_map(units="imperial"):
    """
    Returns a mapping dictionary for OpenWeatherMap fields
    with units adjusted dynamically.

    units: "imperial", "metric", or "standard" (Kelvin)
    """
    if units == "imperial":
        temp_unit = "°F"
        wind_unit = "mph"
        visibility_unit = "m"
    elif units == "metric":
        temp_unit = "°C"
        wind_unit = "m/s"
        visibility_unit = "m"
    else:  # standard
        temp_unit = "K"
        wind_unit = "m/s"
        visibility_unit = "m"

    return {
        "temp": f"Temperature ({temp_unit})",
        "feels_like": f"Feels Like ({temp_unit})",
        "temp_min": f"Min Temperature ({temp_unit})",
        "temp_max": f"Max Temperature ({temp_unit})",
        "pressure": "Pressure (hPa)",
        "humidity": "Relative Humidity (%)",
        "visibility": f"Visibility ({visibility_unit})",
        "wind.speed": f"Wind Speed ({wind_unit})",
        "wind.deg": "Wind Direction (°)",
        "weather.0.main": "Main Weather",
        "weather.0.description": "Description",
        "weather.0.icon": "Icon URL",
        "sys.country": "Country",
        "sys.sunrise": "Sunrise",
        "sys.sunset": "Sunset",
        "name": "City Name",
        "timezone": "Timezone Offset (s)",
    }


def print_weather_data(data, units="imperial", mapping=None):
    """
    Print OpenWeatherMap data dictionary in a human-readable format.
    Handles nested dictionaries, lists, and unmapped fields.
    """
    if mapping is None:
        mapping = build_conditions_map(units)

    def flatten_key(d, parent_key=""):
        """
        Recursively flatten nested dict keys with dot notation for mapping.
        Handles lists by index notation (e.g., weather.0.description).
        """
        items = {}
        if isinstance(d, dict):
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.update(flatten_key(v, new_key))
                elif isinstance(v, list):
                    for idx, elem in enumerate(v):
                        list_key = f"{new_key}.{idx}"
                        if isinstance(elem, dict):
                            items.update(flatten_key(elem, list_key))
                        else:
                            items[list_key] = elem
                else:
                    items[new_key] = v
        return items

    flat_data = flatten_key(data)

    for key, value in flat_data.items():
        # Remove top-level prefix if present (coord, main, wind, etc.)
        stripped_key = ".".join(key.split(".")[1:]) if "." in key else key
        display_name = mapping.get(stripped_key, stripped_key.replace("_", " ").title())
        if isinstance(value, float):
            value = round(value, 2)
        print(f"{display_name} : {value}")
