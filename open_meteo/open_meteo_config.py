"""
open_meteo_config.py

This module maps canonical weather metrics (from sys_config.yaml) to Open-Meteo API field names.
Only metrics supported by Open-Meteo are included in the dictionary. Unsupported metrics are
listed at the bottom for reference. This allows weather_scraper.py to always use consistent
canonical names across multiple APIs.
"""

from weather_shared import WeatherData, degrees_to_direction, WEATHER_CODE_MAP


OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/"
GEOCODE_BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"

# -----------------------------
# Open-Meteo's supported fields
# -----------------------------
OPEN_METEO_HOURLY_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "dewpoint_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "weathercode",
    "cloudcover",
    "cloudcover_low",
    "cloudcover_mid",
    "cloudcover_high",
    "visibility",
    "windspeed_10m",
    "winddirection_10m",
    "windgusts_10m",
]


OPEN_METEO_DAILY_FIELDS = [
    "temperature_2m_max",
    "temperature_2m_mean",
    "temperature_2m_min",
    "precipitation_sum",
    "rain_sum",
    "showers_sum",
    "snowfall_sum",
    "windspeed_10m_max",
    "winddirection_10m_dominant",
    "windgusts_10m_max",
    "precipitation_hours",
    "precipitation_probability_max",
    "precipitation_probability_mean",
    "precipitation_probability_min",
    "sunrise",
    "sunset",
    "sunshine_duration",
    "weathercode",
]


def parse_open_meteo_data(data, units) -> WeatherData:
    # print(f"parse_open_meteo_data units: {units}")
    # print(data)

    weather = WeatherData()
    if units == "imperial":
        weather.temperature = data["temperature"]
        weather.wind_speed = data["windspeed"]
        weather.wind_degree = data["winddirection"]
        weather.wind_direction = degrees_to_direction(data["winddirection"])
        weather.condition_str = WEATHER_CODE_MAP[data["weathercode"]]

    return weather
