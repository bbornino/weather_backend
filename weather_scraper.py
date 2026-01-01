"""
# weather_scraper.py
#
# Core weather scraping logic.
# Imports individual provider scrapers and aggregates data.
# Serves CLI, Lambda, and future front-ends.
#
"""

from datetime import datetime

from weather_objects import WeatherView
from weather_shared import parse_location
from accuweather.accuweather_scraper import get_accuweather_data
from weatherapi.weatherapi_scraper import get_weatherapi_data
from weatherbit.weatherbit_scraper import get_weatherbit_data
from open_meteo.open_meteo_scraper import get_open_meteo_data, geocode
from open_weather.open_weather_map_scraper import (
    get_open_weather_data,
    reverse_geocode,
)
from national_weather_service.nws_scraper import get_nws_data


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

    if config["display_info"]:
        print(
            f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] weather_scraper->get_weather()"
        )
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
    if config["display_info"]:
        print("Location: " + location)

    # Extract units
    units = config.get("units", "imperial")  # default to imperial if not provided
    if config["display_info"]:
        print("Units: " + units)

    # Extract fields to show
    show_fields = config.get("show", ["temp", "humidity"])  # default subset
    if config["display_info"]:
        print("Show Fields: ")
        print(show_fields)

    # Extract enabled APIs
    apis_config = config.get("apis", {})
    enabled_apis = [
        api for api, details in apis_config.items() if details.get("enabled")
    ]
    if config["display_info"]:
        print("Enabled APIs:")
        print(enabled_apis)
        print("\n")
    # Placeholder for results
    results = []

    # Each API call would go here later
    if "accuweather" in enabled_apis:
        if config["display_info"]:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Getting accuweather scraper... API key issue!",
                flush=True,
            )

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

        # NWS only supports a latitude and longitude
        loc = parse_location(location)
        if loc["city"] is not None and loc["state"] is not None:
            geocode_location = geocode(loc["city"], loc["state"])

            if geocode_location is None:
                # Graceful exit: we can't proceed without coordinates
                print(f"Could not geocode location: {loc['city']}, {loc['state']}")
                return None
            else:
                latitude = geocode_location.get("latitude")
                longitude = geocode_location.get("longitude")
        else:
            latitude = loc["lat"]
            longitude = loc["lon"]

        if config["display_info"]:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Getting national_weather_service...",
                flush=True,
            )
        results.append(get_nws_data(latitude, longitude, units))

    if "open_meteo" in enabled_apis:
        if config["display_info"]:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Getting open_meteo scraper...",
                flush=True,
            )
        results.append(get_open_meteo_data(location, units))

    if "open_weather" in enabled_apis:
        if config["display_info"]:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Getting open_weather scraper...",
                flush=True,
            )
        results.append(get_open_weather_data(location, units))

    if "weatherapi" in enabled_apis:
        if config["display_info"]:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Getting weatherapi scraper...",
                flush=True,
            )
        results.append(get_weatherapi_data(location, units))

    if "weatherbit" in enabled_apis:
        if config["display_info"]:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Getting weatherbit scraper... API key issue!",
                flush=True,
            )
        get_weatherbit_data(location, units)

    weather_view = WeatherView()
    weather_view.app_name = "Bornino Weather App"
    weather_view.app_version = 0.1
    weather_view.units = units
    weather_view.generated_at = datetime.now()
    weather_view.timezone = "America/Los_Angeles (GMT-8)"
    weather_view.reports = results

    return weather_view
