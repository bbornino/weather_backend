"""
weatherbit_scraper.py

Scraper for Weatherbit API that fetches:
- Current weather conditions
- Daily forecast
- Hourly forecast

Uses lat/lon coordinates and API key from weatherbit_utils.py.
Prints raw JSON and human-readable weather data using print_weather_data().

Notes / Current Issues:
- API key may be stale or invalid; requests may fail until a valid key is provided.
- Units support: "S" (Imperial / Fahrenheit, mph) and "M" (Metric / Celsius, kph).
- Error handling is included for HTTP failures and JSON decoding errors
"""

import json
import requests
from weatherbit.weatherbit_utils import API_KEY, URL_BASE, print_weather_data
from weather_shared import parse_location


def get_weatherbit_data(location, units):
    loc = parse_location(location)

    if loc["lat"] is not None:
        location_query = f"lat={loc['lat']}&lon={loc['lon']}"
    else:
        location_query = f"city={loc['city']},{loc['state']}"

    if units == "imperial":
        units_value = "S"  # Standard/Imperial, Fahrenheit , mph
    else:
        units_value = "M"  # Metric, Celcius

    # lang = "en"  # English for Descriptions

    url_suffix = f"?{location_query}&key={API_KEY}&units={units_value}"

    # Current Conditions
    weatherbit_current_conditions_url = URL_BASE + "current" + url_suffix
    print(f"weatherbit_current_conditions_url:{weatherbit_current_conditions_url}")

    try:
        response = requests.get(weatherbit_current_conditions_url, timeout=10)
        print(f"HTTP status: {response.status_code}")
        if response.status_code != 200:
            print("Weatherbit API request failed!")
            print(response.text)
            return None

        weatherbit_current_conditions_tmp = response.json()

        print("Full API response:")
        print(json.dumps(weatherbit_current_conditions_tmp, indent=2))

        weatherbit_current_conditions_data = weatherbit_current_conditions_tmp["data"][
            0
        ]
        print(json.dumps(weatherbit_current_conditions_data, indent=2))
        print_weather_data(weatherbit_current_conditions_data)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        weatherbit_current_conditions_data = None
    except ValueError as e:
        # JSON decoding failed
        print(f"Failed to parse JSON: {e}")
        weatherbit_current_conditions_data = None

    # # DAILY Forecast
    # weatherbit_daily_forecast_url = URL_BASE + "forecast/daily" + url_suffix
    # print(f"weatherbit_hourly_forecast_url:{weatherbit_daily_forecast_url}")
    # response = requests.get(weatherbit_daily_forecast_url, timeout=10)
    # weatherbit_daily_forecast_data = response.json()
    # print(f"weatherbit_daily_forecast_data:{weatherbit_daily_forecast_data}")

    # # HOURLY Forecast
    # weatherbit_hourly_forecast_url = URL_BASE + "forecast/hourly" + url_suffix
    # print(f"weatherbit_hourly_forecast_url:{weatherbit_hourly_forecast_url}")
    # response = requests.get(weatherbit_hourly_forecast_url, timeout=10)
    # weatherbit_hourly_forecast_data = response.json()
    # print(f"weatherbit_hourly_forecast_data:{weatherbit_hourly_forecast_data}")

    return "something"
