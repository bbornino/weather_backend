"""
weatherbit_scraper.py

Scraper for Weatherbit API that fetches:
- Current weather conditions
- Daily forecast
- Hourly forecast

Uses lat/lon coordinates and API key from weatherbit_utils.py.
Prints raw JSON and human-readable weather data using print_weather_data().
"""

import json
import requests
from weatherbit_utils import API_KEY, URL_BASE, print_weather_data

units = "M"  # Metric, Celcius
units = "I"  # Imperial, Fahrenheit
lang = "en"  # English for Descriptions

lat, lon = 38.605200, -121.342720  # For My House
# url_suffix = f"?city=Carmichael,CA&key={API_KEY}&units={units}"
url_suffix = f"?lat={lat}&lon={lon}&key={API_KEY}&units={units}"


# Current Conditions
weatherbit_current_conditions_url = URL_BASE + "current" + url_suffix
print(f"weatherbit_current_conditions_url:{weatherbit_current_conditions_url}")
response = requests.get(weatherbit_current_conditions_url, timeout=10)
weatherbit_current_conditions_tmp = response.json()
weatherbit_current_conditions_data = weatherbit_current_conditions_tmp["data"][0]
print(json.dumps(weatherbit_current_conditions_data, indent=2))
print_weather_data(weatherbit_current_conditions_data)


# DAILY Forecast
weatherbit_daily_forecast_url = URL_BASE + "forecast/daily" + url_suffix
print(f"weatherbit_hourly_forecast_url:{weatherbit_daily_forecast_url}")
response = requests.get(weatherbit_daily_forecast_url, timeout=10)
weatherbit_daily_forecast_data = response.json()
print(f"weatherbit_daily_forecast_data:{weatherbit_daily_forecast_data}")

# HOURLY Forecast
weatherbit_hourly_forecast_url = URL_BASE + "forecast/hourly" + url_suffix
print(f"weatherbit_hourly_forecast_url:{weatherbit_hourly_forecast_url}")
response = requests.get(weatherbit_hourly_forecast_url, timeout=10)
weatherbit_hourly_forecast_data = response.json()
print(f"weatherbit_hourly_forecast_data:{weatherbit_hourly_forecast_data}")
