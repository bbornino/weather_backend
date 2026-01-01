"""
open_weather_map_scraper.py

Scraper for OpenWeatherMap API.

Features:
- Fetch current weather conditions for a specific location
- Fetch forecast data for the same location
- Supports both imperial (°F, mph) and metric (°C, kph) units
- Human-readable output using print_weather_data
- Designed for personal use or small projects

Configuration:
- API key is stored in environment variables (OPEN_WEATHER_MAP_API_KEY)
- Location can be specified via HOME_CITY or HOME_LAT/HOME_LON
- Units are set via the UNITS variable ("imperial" or "metric")

Notes:
- OpenWeatherMap requires proper API key
- Some endpoints may have subscription limits
- Optional 'exclude' parameter available for One Call API to reduce payload
"""

from datetime import datetime
import json
import requests
from open_weather.open_weather_map_utils import (
    OPEN_WEATHER_MAP_API_KEY,
    URL_BASE,
    # print_weather_data,
    parse_open_weather_map_data,
)
from weather_objects import WeatherReport
from weather_shared import parse_location

VERBOSE = False  # module-level verbosity switch


def get_open_weather_data(location, units):
    loc = parse_location(location)

    # UNITS = "imperial"
    # UNITS = "metric"
    # LOCATION = f"lat={HOME_LAT}&lon={HOME_LON}"
    # LOCATION = f"q={HOME_CITY}"

    owm_query = {
        "appid": OPEN_WEATHER_MAP_API_KEY,
        "units": units,
    }

    # Append location info dynamically
    if loc["lat"] is not None and loc["lon"] is not None:
        owm_query.update({"lat": loc["lat"], "lon": loc["lon"]})
    else:
        owm_query.update({"q": f"{loc['city']},{loc['state']}"})

    # #################  'exclude' parameter
    #
    # One Call API 'exclude' parameter:
    # - Optional; allows skipping sections of the response to reduce payload size.
    # - Possible values: 'current', 'minutely', 'hourly', 'daily', 'alerts'.
    # - Example: exclude='minutely,hourly' would return only current, daily, and alerts.
    # - By default, if you omit 'exclude', the API returns all available data.
    # - Including everything increases JSON size, especially with hourly and daily forecasts.
    # - Useful for personal projects: you can usually take all data without issues.
    # - Consider using 'exclude' only if you need to reduce API usage or response size.
    #
    # Sample usages of One Call API 'exclude' parameter:

    # 1) Exclude a single section: skip minutely forecast
    # EXCLUDE = "minutely"  #  → returns current, hourly, daily, alerts

    # 2) Exclude multiple sections: skip minutely and hourly forecasts
    # EXCLUDE = "minutely,hourly"  # → returns current, daily, alerts

    # 3) Exclude three sections: skip minutely, hourly, and alerts
    # EXCLUDE = "minutely,hourly,alerts"  # → returns only current and daily

    # URL_SUFFIX += f"&exclude={EXCLUDE}"

    #  Current Weather Conditions
    current_conditions_url = URL_BASE + "weather"

    current_conditions_response = requests.get(
        current_conditions_url, params=owm_query, timeout=10
    )
    current_conditions_data = current_conditions_response.json()

    if VERBOSE:
        print("Open Weather Map Current Raw Data")
        print(current_conditions_data)
        print(json.dumps(current_conditions_data, indent=2))

    current_weather = parse_open_weather_map_data(current_conditions_data, units)

    if VERBOSE:
        print("Open Weather Map Current Formatted WeatherData")
        print(current_conditions_url)
        print(current_weather)

    #  Current Forecast
    # CURRENT_CONDITIONS_URL = URL_BASE + "forecast"
    # print(CURRENT_CONDITIONS_URL)
    # response = requests.get(CURRENT_CONDITIONS_URL, params=owm_query, timeout=10)
    # data = response.json()

    open_weather_map_report = WeatherReport()
    open_weather_map_report.source = "open_weather"
    if loc.get("city") and loc.get("state"):
        open_weather_map_report.location = f"{loc['city']}, {loc['state']}"
    else:
        open_weather_map_report.location = f"{current_conditions_data['lat']['lat']},{current_conditions_data['lon']['lat']}"

    open_weather_map_report.latitude = current_conditions_data["coord"]["lat"]
    open_weather_map_report.longitude = current_conditions_data["coord"]["lon"]
    open_weather_map_report.fetched_at = datetime.now()
    open_weather_map_report.current = current_weather
    open_weather_map_report.hourly = None  # TO DO
    open_weather_map_report.daily = None  # TO DO

    return open_weather_map_report


def reverse_geocode(lat, lon):
    """
    Reverse-geocode latitude/longitude to city and state using OpenWeatherMap.

    Returns:
        dict with keys: city, state, country
        or None if lookup fails
    """
    url = URL_BASE.replace("/data/2.5/", "/geo/1.0/reverse")

    params = {
        "lat": lat,
        "lon": lon,
        "limit": 1,
        "appid": OPEN_WEATHER_MAP_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"OpenWeather reverse geocode failed: {e}")
        return None

    if not data:
        return None

    entry = data[0]

    return {
        "city": entry.get("name"),
        "state": entry.get("state"),
        "country": entry.get("country"),
    }
