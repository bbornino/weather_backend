# accuweather_client.py
# ---------------------
# A Python client for interacting with the AccuWeather API.
# Provides methods to:
#   - Fetch and cache location keys by friendly name or lat/lon
#   - Retrieve current conditions
#   - Retrieve hourly (up to 12-hour) forecasts
#   - Retrieve daily (up to 5-day) forecasts
# Cache is persisted in a JSON file to minimize API calls and stay within free-tier limits.

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env immediately
load_dotenv()


class AccuWeatherClient:
    def __init__(
        self,
        cache_file="accuweather_location_cache.json",
        api_key=None,
        timeout=(5, 10),
    ):
        """
        Initialize AccuWeatherClient
        :param cache_file: Path to JSON file storing cached location keys
        :param api_key: AccuWeather API key
        :param timeout: Tuple of (connect_timeout, read_timeout)
        """
        self.API_KEY = api_key or os.getenv("ACCUWEATHER_API_KEY")
        self.cache_file = cache_file
        self.timeout = timeout

        # Load existing cache if exists, else start empty
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                try:
                    self.cached_keys = json.load(f)
                except json.JSONDecodeError:
                    self.cached_keys = []
        else:
            self.cached_keys = []

    def get_location_key(self, friendly_name=None, lat=None, lon=None):
        """
        Return the AccuWeather location key for the given friendly name or lat/lon
        """
        # Try to find in cache
        cached_key = self.find_cached_key(friendly_name, lat, lon)
        if cached_key:
            return cached_key

        # Not found in cache → call API
        if lat is not None and lon is not None:
            # Geoposition search
            url = "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
            params = {"apikey": self.API_KEY, "q": f"{lat},{lon}"}
            data = self._get_json_or_raise(url, params)
            location_key = data["Key"]
            # Store the lat/lon from response (use the returned coordinates, more accurate)
            lat_resp = data["GeoPosition"]["Latitude"]
            lon_resp = data["GeoPosition"]["Longitude"]

        elif friendly_name:
            # City name search
            url = "https://dataservice.accuweather.com/locations/v1/cities/search"
            params = {"apikey": self.API_KEY, "q": friendly_name}
            data_list = self._get_json_or_raise(url, params)
            if not data_list:
                raise RuntimeError(f"No results returned for city '{friendly_name}'")
            data = data_list[0]

            location_key = data["Key"]
            lat_resp = data["GeoPosition"]["Latitude"]
            lon_resp = data["GeoPosition"]["Longitude"]

        else:
            raise ValueError("Must provide either friendly_name or lat/lon")

        # Save to cache
        self.cached_keys.append(
            {
                "friendly_name": friendly_name,
                "key": location_key,
                "lat": lat_resp,
                "lon": lon_resp,
            }
        )
        self._save_cache()

        return location_key

    def _get_json_or_raise(self, url, params):
        """
        Wrapper for requests.get that raises RuntimeError with API message
        if the key is expired or any other error occurs.
        """
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            # First, try to parse JSON regardless of status code
            try:
                data = resp.json()
            except Exception:
                data = {}

            # Handle API-specific 403 with expired key
            if resp.status_code == 403:
                detail = data.get("detail") or data.get("title") or "Forbidden"
                raise RuntimeError(f"AccuWeather API Key problem: {detail}")

            # Raise for any other HTTP errors
            resp.raise_for_status()
            return data

        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

    def find_cached_key(self, friendly_name=None, lat=None, lon=None):
        """
        Search the cache for a matching friendly_name or lat/lon.
        Uses small tolerance for float comparison.
        """
        for entry in self.cached_keys:
            # Match by friendly_name first
            if friendly_name and entry.get("friendly_name") == friendly_name:
                return entry["key"]
            # Match by lat/lon if provided
            if lat is not None and lon is not None:
                if (
                    abs(entry["lat"] - lat) < 0.0001
                    and abs(entry["lon"] - lon) < 0.0001
                ):
                    return entry["key"]
        return None

    def get_api_key(self):
        return self.API_KEY

    def _save_cache(self):
        """Private method to persist cache to disk"""
        print("AccuWeatherClint wrote to file")
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cached_keys, f, indent=2)

    def get_current_conditions(self, location_key):
        """
        Fetch current conditions for a given location key.
        Returns the JSON response from AccuWeather.
        """
        url = f"https://dataservice.accuweather.com/currentconditions/v1/{location_key}"
        params = {"apikey": self.API_KEY}
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch current conditions: {e}")

    def get_hourly_forecast(self, location_key, hours=12):
        """
        Fetch hourly forecast for the next 'hours' hours (free tier: 12 hours max)
        Returns a list of hourly forecast dicts.
        """
        if hours > 12:
            hours = 12  # free tier limit
        url = f"https://dataservice.accuweather.com/forecasts/v1/hourly/{hours}hour/{location_key}"
        params = {"apikey": self.API_KEY}

        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()  # list of hourly forecast dicts
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch hourly forecast: {e}")

    def get_daily_forecast(self, location_key, days=5):
        """
        Fetch daily forecast for the next 'days' days (free tier: 5 days max)
        Returns the DailyForecasts array from the API response.
        """
        if days > 5:
            days = 5  # free tier limit
        url = f"https://dataservice.accuweather.com/forecasts/v1/daily/{days}day/{location_key}"
        params = {"apikey": self.API_KEY}

        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("DailyForecasts", [])  # list of daily forecast dicts
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch daily forecast: {e}")
