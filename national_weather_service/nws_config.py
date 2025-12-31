"""
nws_config.py

This module provides National Weather Service (NWS)-specific configuration
and unit conversion functions for the weather backend system. It provides helper functions to
convert values from NWS-provided units to standardized metric or imperial units.

Key Features:
- Provides conversion utilities for:
    - Temperature (set_temp)
    - Wind speed (set_speed)
    - Atmospheric pressure (set_pressure)
    - Visibility (set_visibility)
    - Cloud cover percentage (set_cloud_cover)
- Handles missing values (None) gracefully.
- Ensures consistent, rounded values for integration into WeatherData and
  WeatherReport objects.

Constants:
- NATIONAL_WEATHER_SERVICE_BASE_URL (str): Base URL for the NWS API.

"""

NATIONAL_WEATHER_SERVICE_BASE_URL = "https://api.weather.gov/"


def set_temp(temperature_value, temperature_units, target_units):
    """
    Convert a temperature value from its source units to the target units.

    Args:
        temperature_value (float): The numeric temperature.
        temperature_units (str): The units of the input value, e.g., "wmoUnit:degC" or "wmoUnit:degF".
        target_units (str): The units you want, either "imperial" or "metric".

    Returns:
        float: The temperature in the target units.
    """
    if temperature_value is None:
        return None

    if target_units == "imperial" and temperature_units == "wmoUnit:degC":
        return round(32 + temperature_value * 1.8, 1)
    elif target_units == "metric" and temperature_units == "wmoUnit:degF":
        return round((temperature_value - 32) / 1.8, 1)
    else:
        return round(temperature_value, 1)


def set_speed(speed_value, speed_units, target_units):
    """
    Convert a wind speed value from its source units to the target units.

    Args:
        speed_value (float): The numeric speed.
        speed_units (str): The units of the input value, e.g., "wmoUnit:m_s-1", "wmoUnit:km_h-1", or "wmoUnit:mph".
        target_units (str): The units you want, either "imperial" or "metric".

    Returns:
        float: The speed in the target units.
    """
    if speed_value is None:
        return None

    if target_units == "imperial" and speed_units == "wmoUnit:m_s-1":
        return round(speed_value * 2.23694, 1)  # m/s → mph
    elif target_units == "imperial" and speed_units == "wmoUnit:km_h-1":
        return round(speed_value * 0.621371, 1)  # km/h → mph
    elif target_units == "metric" and speed_units == "wmoUnit:mph":
        return round(speed_value * 1.60934, 1)  # mph → km/h
    elif target_units == "metric" and speed_units == "wmoUnit:m_s-1":
        return speed_value  # already m/s, metric-compatible
    else:
        return speed_value  # fallback if units unknown


def set_pressure(pressure_value, pressure_units, target_units):
    """
    Convert a pressure value from its source units to the target units.

    Args:
        pressure_value (float): The numeric pressure.
        pressure_units (str): The units of the input value, e.g., "wmoUnit:Pa" or "wmoUnit:hPa".
        target_units (str): The units you want, either "imperial" or "metric".

    Returns:
        float: The pressure in the target units (hPa for metric, inHg for imperial).
    """
    if pressure_value is None:
        return None  # handle nulls

    # Convert to inches of mercury if target is imperial
    if target_units == "imperial":
        if pressure_units == "wmoUnit:Pa":
            return round(pressure_value * 0.0002953, 2)  # Pa → inHg
        elif pressure_units == "wmoUnit:hPa":
            return round(pressure_value * 0.02953, 2)  # hPa → inHg
        elif pressure_units == "wmoUnit:inHg":
            return pressure_value  # already in inHg
        else:
            return pressure_value  # unknown unit fallback

    # Convert to hPa if target is metric
    elif target_units == "metric":
        if pressure_units == "wmoUnit:Pa":
            return round(pressure_value / 100.0, 1)  # Pa → hPa
        elif pressure_units == "wmoUnit:hPa":
            return pressure_value  # already hPa
        elif pressure_units == "wmoUnit:inHg":
            return round(pressure_value / 0.02953, 2)  # inHg → hPa
        else:
            return pressure_value  # unknown unit fallback

    # fallback if target_units is not recognized
    else:
        return pressure_value


def set_visibility(visibility_value, visibility_units, target_units):
    """
    Convert visibility to target units.

    Args:
        visibility_value (float): The visibility value.
        visibility_units (str): The units of the input, e.g., "wmoUnit:m".
        target_units (str): Desired units, "metric" (meters) or "imperial" (miles).

    Returns:
        float: Visibility in target units.
    """
    if visibility_value is None:
        return None  # handle missing data

    # Metric output: meters
    if target_units == "metric":
        if visibility_units == "wmoUnit:m":
            return visibility_value
        elif visibility_units == "wmoUnit:mi":
            return round(visibility_value * 1609.34, 2)  # miles → meters
        else:
            return visibility_value  # fallback

    # Imperial output: miles
    elif target_units == "imperial":
        if visibility_units == "wmoUnit:m":
            return round(visibility_value / 1609.34, 2)  # meters → miles
        elif visibility_units == "wmoUnit:mi":
            return visibility_value
        else:
            return visibility_value  # fallback

    # fallback if target_units is invalid
    else:
        return visibility_value


def set_cloud_cover(cloud_layers):
    coverage_map = {"SKC": 0, "CLR": 0, "FEW": 12.5, "SCT": 37.5, "BKN": 75, "OVC": 100}
    if not cloud_layers:
        return None

    percents = []
    for layer in cloud_layers:
        amount = layer.get("amount")
        if amount:
            perc = coverage_map.get(amount.upper())
            if perc is not None:
                percents.append(perc)

    return max(percents) if percents else None
