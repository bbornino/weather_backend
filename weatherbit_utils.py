"""
weatherbit_utils.py

Configuration file for Weatherbit API integration.

Includes:
- API key
- Base URL
- Field mappings for current weather conditions
- Helper function to print weather data in a readable format

This file is imported by weatherbit_scraper.py and any other
modules that need Weatherbit data.
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHERBIT_API_KEY")
URL_BASE = "https://api.weatherbit.io/v2.0/"

# Field mapping dictionary
CURRENT_CONDITIONS_MAP = {
    # Core readings
    "temp": "Temperature (°F)",
    "app_temp": "Feels Like (°F)",
    "rh": "Relative Humidity (%)",
    "dewpt": "Dew Point (°F)",
    "clouds": "Cloud Cover (%)",
    "precip": "Precipitation (mm/hr)",
    "snow": "Snowfall (mm/hr)",
    "slp": "Sea Level Pressure (mb)",
    "pres": "Pressure (mb)",
    "vis": "Visibility (km)",
    "uv": "UV Index",
    "aqi": "Air Quality Index",
    # Wind
    "wind_spd": "Wind Speed (m/s)",
    "gust": "Wind Gust (m/s)",
    "wind_dir": "Wind Direction (°)",
    "wind_cdir": "Wind Direction (Compass)",
    "wind_cdir_full": "Wind Direction (Full Name)",
    # Solar radiation and angles
    "solar_rad": "Solar Radiation (W/m²)",
    "ghi": "Global Horizontal Irradiance (W/m²)",
    "dni": "Direct Normal Irradiance (W/m²)",
    "dhi": "Diffuse Horizontal Irradiance (W/m²)",
    "elev_angle": "Solar Elevation Angle (°)",
    "h_angle": "Solar Hour Angle (°)",
    # Location metadata
    "lat": "Latitude",
    "lon": "Longitude",
    "city_name": "City",
    "state_code": "State Code",
    "country_code": "Country Code",
    "timezone": "Timezone",
    "station": "Station ID",
    "sources": "Data Sources",
    # Timing and astronomical
    "ob_time": "Observation Time (UTC)",
    "datetime": "Local Date/Time",
    "pod": "Part of Day (d = day, n = night)",
    "sunrise": "Sunrise (Local Time)",
    "sunset": "Sunset (Local Time)",
    "ts": "Observation Timestamp (Unix)",
    # Weather summary
    "weather": "Weather Description",
}


def print_weather_data(data, mapping=CURRENT_CONDITIONS_MAP):
    """
    Print weather data dictionary in a human-readable format.
    Handles nested dictionaries, lists, and unmapped fields.
    """
    import json

    for key, value in data.items():
        display_name = mapping.get(key, key)

        if isinstance(value, dict):
            # For 'weather' or other nested dictionaries, pretty-print as JSON
            value = json.dumps(value, indent=2)
        elif isinstance(value, list):
            # Join list elements as string
            value = ", ".join(map(str, value))
        elif isinstance(value, float):
            # Round floats for readability
            value = round(value, 2)

        print(f"{display_name} : {value}")
