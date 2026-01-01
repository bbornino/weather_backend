"""
weatherapi_utils.py

Configuration file for WeatherAPI.com integration.

Includes:
- API key
- Base URL
- Field mappings for current weather conditions
- Helper function to print weather data in a readable format

This file is imported by weatherapi_scraper.py and any other
modules that need WeatherAPI data.
"""

import os
from dotenv import load_dotenv

# import sys
# import io
from weather_objects import WeatherData


# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

load_dotenv()
os.environ["PYTHONUTF8"] = "1"
WEATHERAPI_KEY = os.getenv("WEATHERAPI_API_KEY")
URL_BASE = "https://api.weatherapi.com/v1/"

# Field mapping dictionary
WEATHERAPI_CONDITIONS_MAP = {
    # Core readings
    "temp_c": "Temperature (°C)",
    "temp_f": "Temperature (°F)",
    "feelslike_c": "Feels Like (°C)",
    "feelslike_f": "Feels Like (°F)",
    "humidity": "Relative Humidity (%)",
    "dewpoint_c": "Dew Point (°C)",
    "dewpoint_f": "Dew Point (°F)",
    "cloud": "Cloud Cover (%)",
    "precip_mm": "Precipitation (mm)",
    "precip_in": "Precipitation (in)",
    "pressure_mb": "Pressure (mb)",
    "pressure_in": "Pressure (in)",
    "vis_km": "Visibility (km)",
    "vis_miles": "Visibility (miles)",
    "uv": "UV Index",
    # Wind
    "wind_kph": "Wind Speed (kph)",
    "wind_mph": "Wind Speed (mph)",
    "gust_kph": "Wind Gust (kph)",
    "gust_mph": "Wind Gust (mph)",
    "wind_degree": "Wind Direction (°)",
    "wind_dir": "Wind Direction (Compass)",
    # Air quality
    "air_quality.co": "CO (ppm)",
    "air_quality.no2": "NO₂ (ppb)",
    "air_quality.o3": "O₃ (ppb)",
    "air_quality.so2": "SO₂ (ppb)",
    "air_quality.pm2_5": "PM2.5 (µg/m³)",
    "air_quality.pm10": "PM10 (µg/m³)",
    "air_quality.us-epa-index": "US EPA AQI Index",
    "air_quality.gb-defra-index": "UK DEFRA AQI Index",
    # Condition
    "condition.text": "Weather Description",
    "condition.icon": "Weather Icon URL",
    "condition.code": "Weather Condition Code",
    # Location metadata
    "lat": "Latitude",
    "lon": "Longitude",
    "name": "City",
    "region": "Region/State",
    "country": "Country",
    "tz_id": "Timezone",
    "localtime": "Local Date/Time",
    "localtime_epoch": "Local Time Epoch",
    # Timing
    "last_updated": "Last Updated",
    "last_updated_epoch": "Last Updated Epoch",
    "is_day": "Is Daytime (1 = day, 0 = night)",
    # Solar / radiation fields (optional if available)
    "short_rad": "Shortwave Radiation",
    "diff_rad": "Diffuse Radiation",
    "dni": "Direct Normal Irradiance",
    "gti": "Global Tilted Irradiance",
}


def parse_weatherapi_data(data, units) -> WeatherData:
    weather = WeatherData()
    if units == "imperial":
        weather.temperature = data["temp_f"]
        weather.feels_like = data["feelslike_f"]
        weather.wind_chill = data["windchill_f"]
        weather.heat_index = data["heatindex_f"]
        weather.dew_point = data["dewpoint_f"]

        weather.wind_speed = data["wind_mph"]
        weather.wind_degree = data["wind_degree"]
        weather.wind_direction = data["wind_dir"]
        weather.wind_gust = data["gust_mph"]

        weather.humidity = data["humidity"]
        weather.pressure = data["pressure_in"]
        weather.precipitation = data["precip_in"]
        weather.visibility = data["vis_miles"]
        weather.cloud_cover = data["cloud"]
        weather.uv = data["uv"]

        weather.timestamp = data["last_updated"]
        weather.condition = data["condition"]

    else:
        weather.temperature = data["temp_c"]
        weather.feels_like = data["feelslike_c"]
        weather.wind_chill = data["windchill_c"]
        weather.heat_index = data["heatindex_c"]
        weather.dew_point = data["dewpoint_c"]

        weather.wind_speed = data["wind_kph"]
        weather.wind_degree = data["wind_degree"]
        weather.wind_direction = data["wind_dir"]
        weather.wind_gust = data["gust_kph"]

        weather.humidity = data["humidity"]
        weather.pressure = data["pressure_mb"]
        weather.precipitation = data["precip_in"]
        weather.visibility = data["vis_km"]
        weather.cloud_cover = data["cloud"]
        weather.uv = data["uv"]

        weather.timestamp = data["last_updated"]
        weather.condition = data["condition"]

    return weather


def print_weather_data(data, mapping=None):
    """
    Print weather data dictionary in a human-readable format.
    Handles nested dictionaries, lists, and unmapped fields.
    """
    # import json
    if mapping is None:
        mapping = WEATHERAPI_CONDITIONS_MAP

    def flatten_key(d, parent_key=""):
        """
        Recursively flatten nested dict keys with dot notation for mapping.
        """
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(flatten_key(v, new_key))
            else:
                items[new_key] = v
        return items

    flat_data = flatten_key(data)

    for key, value in flat_data.items():
        # Remove 'current.' or 'location.' prefix if present
        stripped_key = ".".join(key.split(".")[1:]) if "." in key else key
        display_name = mapping.get(stripped_key, stripped_key.replace("_", " ").title())
        if isinstance(value, float):
            value = round(value, 2)
        print(f"{display_name} : {value}")
