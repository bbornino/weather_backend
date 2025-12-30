from datetime import datetime
import requests
from open_meteo.open_meteo_config import (
    OPEN_METEO_BASE_URL,
    GEOCODE_BASE_URL,
    OPEN_METEO_HOURLY_FIELDS,
    OPEN_METEO_DAILY_FIELDS,
    parse_open_meteo_data,
)
from weather_shared import WeatherData, parse_location, WeatherReport

VERBOSE = False  # module-level verbosity switch


def get_open_meteo_data(location, units):
    loc = parse_location(location)

    latitude = None
    longitude = None
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

    open_meteo_query = {
        "current_weather": "true",
        "latitude": latitude,
        "longitude": longitude,
    }

    base_url = OPEN_METEO_BASE_URL + "forecast"

    if units == "imperial":
        open_meteo_query.update(
            {
                "temperature_unit": "fahrenheit",
                "windspeed_unit": "mph",
                "precipitation_unit": "inch",
                "timezone": "America/Los_Angeles",
            }
        )
    else:  # metric
        open_meteo_query.update(
            {
                "temperature_unit": "celsius",
                "windspeed_unit": "kmh",
                "precipitation_unit": "mm",
                "timezone": "America/Los_Angeles",
            }
        )

    # Display and Add the hourly and daily fields requested into the query
    if VERBOSE:
        print("hourly_fields:", OPEN_METEO_HOURLY_FIELDS)
        print("\ndaily_fields:", OPEN_METEO_DAILY_FIELDS)
    if OPEN_METEO_HOURLY_FIELDS:
        open_meteo_query.update({"hourly": ",".join(OPEN_METEO_HOURLY_FIELDS)})
    if OPEN_METEO_DAILY_FIELDS:
        open_meteo_query.update({"daily": ",".join(OPEN_METEO_DAILY_FIELDS)})

    # This block will get JUST the current weather as a tiny amount of data.
    # Main call does not use the current_weather
    # Left commented out for potential use later.
    # open_meteo_current_weather_query = {
    #     "current_weather": "true",
    #     "latitude": latitude,
    #     "longitude": longitude,
    # }
    # current_weather_response = requests.get(
    #     base_url, params=open_meteo_current_weather_query, timeout=10
    # )

    response = requests.get(base_url, params=open_meteo_query, timeout=10)

    data = response.json()

    current_open_meteo_weather = parse_open_meteo_data(data["current_weather"], units)
    if VERBOSE:
        print("\nReturned Data:")
        print(data)
        print("current_open_meteo_weather:")
        print(current_open_meteo_weather)

    open_meteo_report = WeatherReport()
    open_meteo_report.source = "open_meteo"
    if loc.get("city") and loc.get("state"):
        open_meteo_report.location = f"{loc['city']}, {loc['state']}"
    else:
        open_meteo_report.location = f"{data['latitude']},{data['longitude']}"

    open_meteo_report.latitude = data["latitude"]
    open_meteo_report.longitude = data["longitude"]
    open_meteo_report.fetched_at = datetime.now()
    open_meteo_report.current = current_open_meteo_weather
    open_meteo_report.hourly = None  # TO DO
    open_meteo_report.daily = None  # TO DO

    if VERBOSE:
        print("get_open_meteo_data returning report:")
        print(open_meteo_report)

    return open_meteo_report


def geocode(city, state, country="US"):
    """
    Query the Open-Meteo geocoding API for a city and return the
    best-matching populated place for the given state and country.

    This function is intentionally conservative:
    - It filters results instead of trusting API ordering
    - It only accepts populated places (feature_code == 'PPL')
    - It assumes the caller has already provided a valid state
    """
    # print(f"Open Meteo Geocode City: {city}  State:{state}")
    params = {"name": city, "admin1": state, "country": country}

    try:
        # Perform the HTTP request with a timeout to avoid hanging
        resp = requests.get(GEOCODE_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        # Any network, timeout, or HTTP error ends geocoding cleanly
        print(f"Open Meteo geocode failed: {e}")
        return None

    # Defensive guard: API returned no JSON or unexpected structure
    if not data:
        return None

    results = data["results"]
    filtered_results = []

    # Apply our definition of a "correct" location:
    # - Same country
    # - Same state (spelled out, no abbreviations)
    # - A populated place (not a landmark or geographic feature)
    for r in results:
        if r.get("country_code") != country:
            continue
        if r.get("admin1") != state:
            continue
        if r.get("feature_code") != "PPL":
            continue

        filtered_results.append(r)

    # At this stage, results are already filtered down to valid
    # candidates. Returning the first match is acceptable because:
    # - The list is small
    # - All entries meet our correctness criteria
    # - Ordering is no longer critical to correctness
    return filtered_results[0] if filtered_results else None
