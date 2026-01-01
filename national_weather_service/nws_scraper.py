"""
nws_scraper.py

This module contains functions to fetch and process weather data from the
National Weather Service (NWS) API. It retrieves:

- Daily and hourly forecasts
- Current observations from nearby stations
- Active alerts for a given latitude and longitude

All data is normalized into WeatherData and WeatherReport objects for
consistent usage across the weather backend system.

Functions:
- get_nws_data(latitude, longitude, units): Fetches NWS weather data and
  returns a WeatherReport object containing current conditions, forecasts,
  and alerts.
"""

from datetime import datetime, timezone
from pathlib import Path

import urllib.request
import json

from weather_objects import WeatherData, WeatherReport
from weather_shared import degrees_to_direction
from national_weather_service.nws_config import (
    NATIONAL_WEATHER_SERVICE_BASE_URL,
    set_temp,
    set_speed,
    set_pressure,
    set_visibility,
    set_cloud_cover,
)

VERBOSE = False  # module-level verbosity switch
BASE_DIR = Path(__file__).resolve().parent


def get_nws_data(latitude, longitude, units):
    """
    Retrieve and process weather data from the National Weather Service (NWS).

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        units (str): Target units for conversion. Either "imperial" or "metric".

    Returns:
        WeatherReport: Contains current conditions, forecasts, and active alerts.
                       - current (WeatherData): Temperature, wind, humidity, etc.
                       - alerts (list of dict): Active NWS alerts for the location.
                       - latitude/longitude: Coordinates used for the request.
                       - fetched_at (datetime): UTC timestamp of when data was retrieved.

    Notes:
        - Temperature, wind speed, pressure, visibility, and cloud cover are
          converted to the requested units.
        - Expired alerts are automatically filtered out.
        - Saves raw JSON responses locally for debugging and inspection.
    """
    nws_endpoint_url = (
        NATIONAL_WEATHER_SERVICE_BASE_URL + f"points/{latitude},{longitude}"
    )

    # Given a specific latitutde and longitude, NWS will respond with the URLS to use:
    # "properties": {
    #       "forecast": "https://api.weather.gov/gridpoints/STO/47,69/forecast",
    #       "forecastHourly": "https://api.weather.gov/gridpoints/STO/47,69/forecast/hourly",
    #       "forecastGridData": "https://api.weather.gov/gridpoints/STO/47,69",
    #       "observationStations": "https://api.weather.gov/gridpoints/STO/47,69/stations",
    # Each of these urls will be queried to get the weather
    with urllib.request.urlopen(nws_endpoint_url) as nws_response:
        location_data = json.loads(nws_response.read().decode())

    if VERBOSE:
        print(nws_endpoint_url)
    #     print(location_data)

    # save the location_data to a file so that we can easily read the output
    location_file = BASE_DIR / "nws_location_data.json"
    with open(location_file, "w", encoding="utf-8") as json_file:
        json.dump(location_data, json_file, indent=4)

    #####################   Collect DAILY Forecast
    forecast_daily_url = location_data["properties"]["forecast"]
    with urllib.request.urlopen(forecast_daily_url) as forecast_response:
        forecast_daily_data = json.loads(forecast_response.read().decode())

    if VERBOSE:
        print(f"forecast_daily_url:{forecast_daily_url}")
    #     print("forecast_daily_data:")
    #     print(forecast_daily_data)

    # save the daily forcast data to a file so that we can easily read the output
    daily_forecast_file = BASE_DIR / "nws_forecast_daily.json"
    with open(daily_forecast_file, "w", encoding="utf-8") as daily_json:
        json.dump(forecast_daily_data, daily_json, indent=4)

    #####################   Collect HOURLY Forecast
    forecast_hourly_url = location_data["properties"]["forecastHourly"]

    with urllib.request.urlopen(forecast_hourly_url) as hourly_response:
        forecast_hourly_data = json.loads(hourly_response.read().decode())

    if VERBOSE:
        print(f"forecast_hourly_url:{forecast_hourly_url}")
        # print("forecast_hourly_data:")
        # print(forecast_hourly_data)

    # save the hourly forcast data to a file so that we can easily read the output
    hourly_forecast_file = BASE_DIR / "nws_forecast_hourly.json"
    with open(hourly_forecast_file, "w", encoding="utf-8") as hourly_json:
        json.dump(forecast_hourly_data, hourly_json, indent=4)

    #####################   Collect CURRENT Observation Stations
    current_observation_stations_url = location_data["properties"][
        "observationStations"
    ]

    with urllib.request.urlopen(current_observation_stations_url) as station_response:
        current_observation_stations_json = json.loads(station_response.read().decode())

    if VERBOSE:
        print(f"current_observation_stations_url:{current_observation_stations_url}")
        # print(f"current_observation_stations_json:{current_observation_stations_json}")
        # print(current_observation_stations_json["features"][0]["id"])

    # save the observation stations to a file so that we can easily read the output
    observation_stations_file = BASE_DIR / "nws_current_observation_stations_json.json"
    with open(observation_stations_file, "w", encoding="utf-8") as stations_json:
        json.dump(current_observation_stations_json, stations_json, indent=4)

    #####################   Collect CURRENT [Closest] Observation Station Data
    current_observation_station_url = (
        current_observation_stations_json["features"][0]["id"] + "/observations/latest"
    )

    with urllib.request.urlopen(current_observation_station_url) as response:
        current_observation_data_json = json.loads(response.read().decode())

    if VERBOSE:
        print(f"current_observation_station_url:{current_observation_station_url}")

    # too long: use a shorter name!
    current = current_observation_data_json["properties"]
    current_weather = WeatherData()

    current_weather.temperature = set_temp(
        current["temperature"]["value"], current["temperature"]["unitCode"], units
    )

    current_weather.wind_chill = set_temp(
        current["windChill"]["value"], current["windChill"]["unitCode"], units
    )
    current_weather.heat_index = set_temp(
        current["heatIndex"]["value"], current["heatIndex"]["unitCode"], units
    )
    current_weather.dew_point = set_temp(
        current["dewpoint"]["value"], current["dewpoint"]["unitCode"], units
    )

    current_weather.wind_speed = set_speed(
        current["windSpeed"]["value"], current["windSpeed"]["unitCode"], units
    )
    current_weather.wind_degree = current["windDirection"]["value"]
    current_weather.wind_direction = degrees_to_direction(
        current["windDirection"]["value"]
    )
    current_weather.wind_gust = set_speed(
        current["windGust"]["value"], current["windGust"]["unitCode"], units
    )

    current_weather.humidity = current["relativeHumidity"]["value"]
    current_weather.pressure = set_pressure(
        current["barometricPressure"]["value"],
        current["barometricPressure"]["unitCode"],
        units,
    )
    current_weather.visibility = set_visibility(
        current["visibility"]["value"], current["visibility"]["unitCode"], units
    )
    current_weather.cloud_cover = set_cloud_cover(current["cloudLayers"])

    current_weather.icon = current["icon"]
    current_weather.timestamp = current["timestamp"]
    current_weather.condition_str = current["textDescription"]

    # save the observation stations to a file so that we can easily read the output
    current_weather_file = BASE_DIR / "nws_current_weather.json"
    with open(current_weather_file, "w", encoding="utf-8") as current_weather_json:
        json.dump(current_observation_data_json, current_weather_json, indent=4)

    #####################   Collect Alerts
    alerts_url = (
        NATIONAL_WEATHER_SERVICE_BASE_URL + f"alerts?point={latitude},{longitude}"
    )
    with urllib.request.urlopen(alerts_url) as response:
        alert_data_json = json.loads(response.read().decode())

    if VERBOSE:
        print(f"alerts_url:{alerts_url}")
        # print("alert_data_json:")
        # print(alert_data_json)

    alerts = []
    now = datetime.now(timezone.utc)
    for feature in alert_data_json.get("features", []):
        props = feature["properties"]
        expires_str = props.get("expires")

        if expires_str:
            expires = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
            if expires < now:
                continue  # Skip expired alerts
        alerts.append(
            {
                "event": props["event"],
                "headline": props["headline"],
                "description": props.get("description", ""),
                "instruction": props.get("instruction", ""),
                "severity": props.get("severity"),
                "effective": props.get("effective"),
                "expires": props.get("expires"),
                "area": props.get("areaDesc"),
            }
        )

    if VERBOSE:
        print("NWS Alerts:")
        print(alerts)
    # save the observation stations to a file so that we can easily read the output
    alert_file = BASE_DIR / "nws_alert.json"
    with open(alert_file, "w", encoding="utf-8") as alert_json:
        json.dump(alert_data_json, alert_json, indent=4)

    nws_report = WeatherReport()

    nws_report.source = "nws"
    nws_report.latitude = latitude
    nws_report.longitude = longitude
    nws_report.fetched_at = datetime.now()
    nws_report.current = current_weather

    if VERBOSE:
        print("get_mws_data returning report:")
        print(nws_report)

    return nws_report
