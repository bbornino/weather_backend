"""
# weather_scraper.py
#
# Core weather scraping logic.
# Imports individual provider scrapers and aggregates data.
# Serves CLI, Lambda, and future front-ends.
#
"""

from datetime import datetime

from weather_shared import parse_location, WeatherView
from accuweather.accuweather_scraper import get_accuweather_data
from weatherapi.weatherapi_scraper import get_weatherapi_data
from weatherbit.weatherbit_scraper import get_weatherbit_data
from open_meteo.open_meteo_scraper import get_open_meteo_data
from open_weather.open_weather_map_scraper import (
    get_open_weather_data,
    reverse_geocode,
)


def get_weather(config):
    """
    Main entry point for weather data.
    Can be called by CLI, Lambda, Django, etc.

    Args:
        location (str or tuple): city name or (lat, lon)
        apis (list[str]): list of API names to call, defaults to all
        fields (list[str]): optional subset of fields to return

    Returns:
        dict: JSON-compatible dict with all API results
    """
    # placeholder for now
    print("\nweather_scraper->get_weather()")
    # print(config)

    # Determine which location to use
    location = config.get("location")
    if not location:
        # fallback: use default_location key to look up in locations dict
        default_key = config.get("default_location")
        locations = config.get("locations", {})
        location = locations.get(default_key) if default_key else None

    if not location:
        raise ValueError("No location provided or found in config")
    print("Location: " + location)

    # Extract units
    units = config.get("units", "imperial")  # default to imperial if not provided
    print("Units: " + units)

    # Extract fields to show
    show_fields = config.get("show", ["temp", "humidity"])  # default subset
    print("Show Fields: ")
    print(show_fields)

    # Extract enabled APIs
    apis_config = config.get("apis", {})
    enabled_apis = [
        api for api, details in apis_config.items() if details.get("enabled")
    ]
    print("Enabled APIs:")
    print(enabled_apis)
    print("\n")
    # Placeholder for results
    results = []

    # Each API call would go here later
    if "accuweather" in enabled_apis:
        print("calling accuweather scraper... API key issue!")

        # Some Accuweather plans only allow a City, St, not lat and lon
        loc = parse_location(location)
        if loc["lat"] is not None and loc["lon"] is not None:
            loc = reverse_geocode(lat=loc["lat"], lon=loc["lon"])
        city_state = f"{loc['city']}, {loc['state']}"

        try:
            get_accuweather_data(city_state)
        except RuntimeError as e:
            print(f"!!!  Weather fetch failed: {e}")

    if "national_weather_service" in enabled_apis:
        print("national_weather_service is NOT enabled yet")

    if "open_meteo" in enabled_apis:
        print("Calling open_meteo scraper...")
        results.append(get_open_meteo_data(location, units))

    if "open_weather" in enabled_apis:
        print("calling open_weather scraper...")
        results.append(get_open_weather_data(location, units))

    if "weatherapi" in enabled_apis:
        print("calling weatherapi scraper...")
        results.append(get_weatherapi_data(location, units))

    if "weatherbit" in enabled_apis:
        print("calling weatherbit scraper... API key issue!")
        get_weatherbit_data(location, units)
        # print(wb_results)

    weather_view = WeatherView()
    weather_view.app_name = "Bornino Weather App"
    weather_view.app_version = 0.1
    weather_view.units = units
    weather_view.generated_at = datetime.now()
    weather_view.timezone = "America/Los_Angeles (GMT-8)"
    weather_view.reports = results

    return weather_view
