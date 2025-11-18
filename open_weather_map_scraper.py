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

import json
import requests
from open_weather_map_utils import (
    OPEN_WEATHER_MAP_API_KEY,
    URL_BASE,
    HOME_CITY,
    HOME_LAT,
    HOME_LON,
    print_weather_data,
)

UNITS = "imperial"
# UNITS = "metric"
LOCATION = f"lat={HOME_LAT}&lon={HOME_LON}"
# LOCATION = f"q={HOME_CITY}"

OWM_BASE_QUERY = {
    "appid": OPEN_WEATHER_MAP_API_KEY,
    "units": UNITS,
    # "q":        HOME_CITY,
    "lat": HOME_LAT,
    "lon": HOME_LON,
}


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
CURRENT_CONDITIONS_URL = URL_BASE + "weather"
print(CURRENT_CONDITIONS_URL)
current_conditions_response = requests.get(
    CURRENT_CONDITIONS_URL, params=OWM_BASE_QUERY, timeout=10
)
current_conditions_data = current_conditions_response.json()
# print(data)
# print(json.dumps(current_conditions_data, indent=2))
print_weather_data(current_conditions_data)

#  Current Forecast
CURRENT_CONDITIONS_URL = URL_BASE + "forecast"
print(CURRENT_CONDITIONS_URL)
response = requests.get(CURRENT_CONDITIONS_URL, params=OWM_BASE_QUERY, timeout=10)
data = response.json()
# print(data)
# print(json.dumps(data, indent=2))
