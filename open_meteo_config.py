"""
open_meteo_config.py

This module maps canonical weather metrics (from sys_config.yaml) to Open-Meteo API field names.
Only metrics supported by Open-Meteo are included in the dictionary. Unsupported metrics are
listed at the bottom for reference. This allows weather_scraper.py to always use consistent
canonical names across multiple APIs.
"""

import yaml

# -----------------------------
# Step 1: Load the master sys_config.yaml
# -----------------------------
with open("sys_config.yaml", "r") as f:
    sys_config = yaml.safe_load(f)

enabled_metrics = sys_config.get("metrics", {})
enabled_units = sys_config.get("units", "us")

# -----------------------------
# Step 2: Define Open-Meteo's supported fields
# -----------------------------
OPEN_METEO_FIELD_MAP = {
    "temperature_2m": "temperature",
    "apparent_temperature": "feels_like",
    "relative_humidity_2m": "humidity",
    "dewpoint_2m": "dew_point",
    "wind_chill": "wind_chill",  # optional, if API supports
    "heat_index": "heat_index",  # optional, if API supports
    "precipitation": "precipitation",
    "precipitation_probability": "precipitation_probability",
    "precipitation_type": "precipitation_type",
    "snowfall": "snowfall",
    "snow_depth": "snow_depth",
    "freezing_rain": "freezing_rain",  # optional
    "windspeed_10m": "wind_speed",
    "windgusts_10m": "wind_gusts",
    "winddirection_10m": "wind_direction",
    "wind_vector": "wind_vector",  # optional
    "cloudcover": "cloud_cover",
    "cloud_base": "cloud_base",  # optional
    "visibility": "visibility",
    "weathercode": "weather_code",
    "weather_description": "weather_description",  # optional
    "uv_index": "uv_index",
    "sunrise": "sunrise",
    "sunset": "sunset",
    "daylight_duration": "daylight_duration",  # optional
    "pressure_msl": "pressure",
    "pressure_trend": "pressure_trend",  # optional
    "altimeter": "altimeter",  # optional
    "feels_like_temperature": "feels_like_temperature",  # optional / derived
    "air_quality_index": "air_quality_index",  # optional
    "pollen_index": "pollen_index",  # optional
}


# -----------------------------
# Step 3: List unsupported terms for reference
# -----------------------------
"""
Unsupported metrics in Open-Meteo (these were in sys_config.yaml but have no corresponding Open-Meteo field):
- wind_chill
- heat_index
- freezing_rain
- wind_vector
- cloud_base
- weather_description
- daylight_duration
- pressure_trend
- altimeter
- feels_like_temperature
- air_quality_index
- pollen_index
"""

# -----------------------------
# Step 4: Filter dictionary by enabled metrics and Open-Meteo support
# -----------------------------
enabled_open_meteo_metrics = {
    canonical_name: api_field
    for api_field, canonical_name in OPEN_METEO_FIELD_MAP.items()
    if enabled_metrics.get(canonical_name, False)
}

# print(enabled_open_meteo_metrics)
