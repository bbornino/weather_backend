# accuweather_scraper.py
# ----------------------
# Simple script to fetch and display AccuWeather data for a given location.
# Currently retrieves only current conditions; hourly and daily forecasts
# are included but commented out to avoid excessive API calls and rate limits.
# Provides optional JSON save functionality for caching purposes during development.

from accuweather_client import AccuWeatherClient


def get_accuweather_data(location, units):
    client = AccuWeatherClient()
    location_key = client.get_location_key("Home")

    current_conditions_data = client.get_current_conditions(location_key)
    # hourly_forecast_data = client.get_hourly_forecast(location_key)
    # daily_forecast_data = client.get_daily_forecast(location_key)

    print(current_conditions_data)
    # print(hourly_forecast_data)
    # print(daily_forecast_data)

    # with open("accuweather_current_conditions_data.json", "w", encoding="utf-8") as f:
    #     json.dump(current_conditions_data, f, indent=4)

    # with open("accuweather_hourly_forecast_data.json", "w", encoding="utf-8") as f:
    #     json.dump(hourly_forecast_data, f, indent=4)

    # with open("accuweather_daily_forecast_data.json", "w", encoding="utf-8") as f:
    #     json.dump(current_conditions_data, f, indent=4)
