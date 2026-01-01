"""
weatherapi_scraper.py

Python script to fetch and display WeatherAPI.com data for a given location, including:
- Current weather
- Forecast (hourly + daily)
- Marine/ocean data (tides)
- Sun/moon rise and set times (astronomy)

Uses weatherapi_utils.py for configuration, API key, and human-readable printing.
"""

from datetime import datetime
import json
import requests

from weatherapi.weatherapi_utils import (
    WEATHERAPI_KEY,
    URL_BASE,
    # print_weather_data,
    parse_weatherapi_data,
)

from weather_objects import WeatherReport
from weather_shared import parse_location

VERBOSE = False  # module-level verbosity switch


def get_weatherapi_data(location, units):
    loc = parse_location(location)

    if loc["lat"] is not None:
        location_query = f"{loc['lat']},{loc['lon']}"
    else:
        location_query = f"city={loc['city']},{loc['state']}"

    BASE_QUERY = {"key": WEATHERAPI_KEY, "q": location_query}

    # Optional Parameters
    days = 14  # Number of forcast days (1-14)
    # hour=10     # Return only for a specific hour
    # dt = 2025 - 11 - 12  # For Specific Date (like history-lite)
    lang = "en"  # Localized for english
    aqi = "yes"  #  air quality
    alerts = "yes"  # Include Weather Alerts

    # Current Weather
    # Use /current.json only if you literally only need the “now” snapshot.
    # params = BASE_QUERY.copy()
    # params.update({"lang": lang, "aqi": aqi, "alerts": alerts})

    # url = URL_BASE + "current.json"
    # resp = requests.get(url, params=params, timeout=10)
    # data = resp.json()
    # # print(json.dumps(data, indent=2))
    # print_weather_data(data)

    # Forecast
    # Use /forecast.json if you want hourly + daily + current.
    params = BASE_QUERY.copy()
    params.update({"lang": lang, "aqi": aqi, "alerts": alerts, "days": days})

    url = URL_BASE + "forecast.json"
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    # print(json.dumps(data, indent=2))

    if VERBOSE:
        print("Weather API Current Temp:")
        print(data["current"])
        print(json.dumps(data["current"], indent=2))

    current_weather = parse_weatherapi_data(data["current"], units)

    if VERBOSE:
        print("weatherapi generated WeatherData")
        print(current_weather)

    # Marine/ocean data   marine.json
    # days = 10  # Number of forecast days.  Default: 1 Max: 10
    # # dt="2025-11-12" # Specific date for historial or forecast data.  Default: today
    # # hour=22         # Specific hour of the day (0-23) if you want hourly info
    # tide = "yes"  # Whether to include tide information "yes" or "no"
    # lang = "en"  # Localized for english
    # MARINE_BASE_QUERY = {"key": WEATHERAPI_KEY, "q": "San Francisco, CA"}

    # params = MARINE_BASE_QUERY.copy()
    # params.update({"lang": lang, "days": days, "tide": tide})

    # url = URL_BASE + "marine.json"
    # resp = requests.get(url, params=params, timeout=10)
    # data = resp.json()
    # print("\nCurrent Marine info for San Francisco")
    # print(json.dumps(data, indent=2))

    # # Sun/moon rise/set (optional)  astronomy.json
    params = BASE_QUERY.copy()
    params.update({"dt": "2025-11-12"})  # For specific date.  Default is today

    url = URL_BASE + "astronomy.json"
    resp = requests.get(url, params=params, timeout=10)
    astronomy_data = resp.json()
    if VERBOSE:
        print("weatherapi Sunrise, sunset, moon rise, moonset:")
        print(json.dumps(astronomy_data, indent=2))

    weatherapi_report = WeatherReport()
    weatherapi_report.source = "WeatherApi"
    if loc.get("city") and loc.get("state"):
        weatherapi_report.location = f"{loc['city']}, {loc['state']}"
    else:
        weatherapi_report.location = f"{data['latitude']},{data['longitude']}"

    weatherapi_report.latitude = data["location"]["lat"]
    weatherapi_report.longitude = data["location"]["lon"]
    weatherapi_report.fetched_at = datetime.now()
    weatherapi_report.current = current_weather
    weatherapi_report.hourly = None  # TO DO
    weatherapi_report.daily = None  # TO DO
    weatherapi_report.astronomy = astronomy_data

    if VERBOSE:
        print("get_weatherapi_data returning report:")
        print(weatherapi_report)

    return weatherapi_report
