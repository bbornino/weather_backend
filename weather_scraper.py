"""
# weather_scraper.py
#
# Core weather scraping logic.
# Imports individual provider scrapers and aggregates data.
# Serves CLI, Lambda, and future front-ends.
#
"""

import urllib.request
import json
from weather_code_map import WEATHER_CODE_MAP


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
    print("weather_scraper->get_weather()")
    print(config)

    # Determine which location to use
    location = config.get("location")
    if not location:
        # fallback: use default_location key to look up in locations dict
        default_key = config.get("default_location")
        locations = config.get("locations", {})
        location = locations.get(default_key) if default_key else None

    if not location:
        raise ValueError("No location provided or found in config")

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

    # Placeholder for results
    results = []

    # Each API call would go here later
    for api_name in enabled_apis:
        # For now, return dummy data
        dummy_data = {}
        if "temp" in show_fields:
            dummy_data["temperature"] = 72
        if "humidity" in show_fields:
            dummy_data["humidity"] = 50

        results.append({"api_name": api_name, "success": True, "data": dummy_data})

    return {"location": location, "units": units, "results": results}
