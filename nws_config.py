"""
nws_config.py

This module maps canonical weather metrics (from sys_config.yaml) to NWS API field names.
Only metrics supported by NWS are included in the dictionary. Unsupported metrics are
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
# Step 2: Define NWS-supported fields
# -----------------------------
NWS_FIELD_MAP = {
    "temperature_2m": "temperature",  # in F or C depending on request
    "apparent_temperature": "temperatureApparent",
    "relative_humidity_2m": "relativeHumidity",
    "dewpoint_2m": "dewpoint",
    "wind_chill": "windChill",  # optional, may need derivation
    "heat_index": "heatIndex",  # optional, may need derivation
    "precipitation": "probabilityOfPrecipitation",  # NWS returns probability & intensity separately
    "precipitation_probability": "probabilityOfPrecipitation",
    "precipitation_type": "quantitativePrecipitation",  # may need mapping
    "snowfall": "snowfallAmount",  # optional, from forecast properties
    "snow_depth": "snowDepth",  # optional
    "freezing_rain": "freezingRain",  # optional, rare
    "windspeed_10m": "windSpeed",  # NWS usually provides 'windSpeed' in mph or km/h
    "windgusts_10m": "windGust",
    "winddirection_10m": "windDirection",
    "wind_vector": None,  # NWS does not provide explicit vector
    "cloudcover": "cloudCover",
    "cloud_base": None,  # not directly provided
    "visibility": "visibility",
    "weathercode": "iconCode",  # NWS uses icons to summarize condition
    "weather_description": "shortForecast",  # optional text description
    "uv_index": "uvIndex",  # optional
    "sunrise": "sunriseTime",
    "sunset": "sunsetTime",
    "daylight_duration": None,  # can be derived from sunrise/sunset
    "pressure_msl": "barometricPressure",
    "pressure_trend": None,  # not directly provided
    "altimeter": None,  # not directly provided
    "feels_like_temperature": None,  # can be derived if needed
    "air_quality_index": None,  # NWS API separate AQI endpoint
    "pollen_index": None,  # not provided by NWS
}

# -----------------------------
# Step 3: List unsupported terms for reference
# -----------------------------
"""
Unsupported metrics in NWS (from sys_config.yaml but no direct NWS field):
- wind_vector
- cloud_base
- daylight_duration
- pressure_trend
- altimeter
- feels_like_temperature
- air_quality_index
- pollen_index
"""

# -----------------------------
# Step 4: Filter dictionary by enabled metrics and NWS support
# -----------------------------
enabled_nws_metrics = {
    canonical_name: api_field
    for canonical_name, api_field in NWS_FIELD_MAP.items()
    if api_field is not None and enabled_metrics.get(canonical_name, False)
}

# print(enabled_nws_metrics)
