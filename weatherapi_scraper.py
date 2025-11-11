"""
weatherapi_scraper.py

Python script to fetch and display WeatherAPI.com data for a given location, including:
- Current weather
- Forecast (hourly + daily)
- Marine/ocean data (tides)
- Sun/moon rise and set times (astronomy)

Uses weatherapi_utils.py for configuration, API key, and human-readable printing.
"""

import json
import requests

from weatherapi_utils import (
    WEATHERAPI_KEY,
    URL_BASE,
    HOME_CITY,
    HOME_LAT,
    HOME_LON,
    print_weather_data,
)

# BASE_QUERY = {"key": WEATHERAPI_KEY, "q": f"{HOME_CITY}"}
BASE_QUERY = {"key": WEATHERAPI_KEY, "q": f"{HOME_LAT},{HOME_LON}"}

# Optional Parameters
days = 14  # Number of forcast days (1-14)
# hour=10     # Return only for a specific hour
dt = 2025 - 11 - 12  # For Specific Date (like history-lite)
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
print(json.dumps(data, indent=2))


# Marine/ocean data   marine.json
days = 10  # Number of forecast days.  Default: 1 Max: 10
# dt="2025-11-12" # Specific date for historial or forecast data.  Default: today
# hour=22         # Specific hour of the day (0-23) if you want hourly info
tide = "yes"  # Whether to include tide information "yes" or "no"
lang = "en"  # Localized for english
MARINE_BASE_QUERY = {"key": WEATHERAPI_KEY, "q": "San Francisco, CA"}

params = MARINE_BASE_QUERY.copy()
params.update({"lang": lang, "days": days, "tide": tide})

url = URL_BASE + "marine.json"
resp = requests.get(url, params=params, timeout=10)
data = resp.json()
print("\nCurrent Marine info for San Francisco")
print(json.dumps(data, indent=2))


# Sun/moon rise/set (optional)  astronomy.json
params = BASE_QUERY.copy()
params.update({"dt": "2025-11-12"})  # For specific date.  Default is today

url = URL_BASE + "astronomy.json"
resp = requests.get(url, params=params, timeout=10)
data = resp.json()
print(json.dumps(data, indent=2))
