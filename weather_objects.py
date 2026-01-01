"""
weather_scraper.py

Shared configuration, environment setup, domain models, and helpers
used across the Weather application.

This module contains Core Data Objects:
   - WeatherData: atomic weather conditions
   - WeatherReport: normalized per-source weather data
   - WeatherView: aggregated view for UI/CLI


"""


class WeatherData:
    """
    Represents the weather conditions for a location at a point in time.

    Attributes:
        Temperature / feels:
            temperature (float)
            feels_like (float)
            wind_chill (float)
            heat_index (float)
            dew_point (float)

        Wind:
            wind_speed (float)
            wind_degree (float)
            wind_direction (str)
            wind_gust (float)

        Atmosphere:
            humidity (float)
            pressure (float)
            precipitation (float)
            visibility (float)
            cloud_cover (float)
            uv (float)

        Other:
            timestamp (datetime)
            condition (dict or list): structured weather description
    """

    def __init__(self):
        # Temperature / feels
        self.temperature = None
        self.feels_like = None
        self.wind_chill = None
        self.heat_index = None
        self.dew_point = None

        # Wind
        self.wind_speed = None
        self.wind_degree = None
        self.wind_direction = None
        self.wind_gust = None

        # Atmosphere
        self.humidity = None
        self.pressure = None
        self.precipitation = None
        self.visibility = None
        self.cloud_cover = None
        self.uv = None

        # Other
        self.icon = None  # URL to NWS weather icon
        self.timestamp = None
        self.condition = None
        self.condition_str = None

    def __repr__(self):
        # Nicely formatted multi-line representation of all attributes
        # usage: print(WeatherData)
        attrs = "\n    ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"WeatherData(\n    {attrs}\n)"


class WeatherReport:
    """
    Represents a normalized weather report returned by a scraper.

    This object is API-agnostic and serves as the internal contract between
    weather scrapers and the rest of the application. Scrapers are responsible
    for translating raw API responses into this structure.

    A WeatherReport always contains current weather data, and may optionally
    contain hourly and/or daily forecast data depending on API support and
    request configuration.

    Attributes:
        source (str):
            Identifier for the data source (e.g. "open_meteo", "weatherapi", "nws").

        location (Location or dict):
            Normalized location information associated with this report.

        fetched_at (datetime):
            Timestamp indicating when the data was retrieved from the API.

        current (WeatherData):
            REQUIRED. Current weather conditions for the location.

        hourly (list[WeatherData] or None):
            OPTIONAL. Hourly forecast data. May be None if not requested or
            not supported by the API.

        daily (list[WeatherData] or None):
            OPTIONAL. Daily forecast data. May be None if not requested or
            not supported by the API.
    """

    def __init__(self):
        self.source = None
        self.location = None
        self.latitude = None
        self.longitude = None
        self.fetched_at = None
        self.current = None
        self.hourly = None
        self.daily = None
        self.astronomy = None
        self.alerts = None

    def __repr__(self):
        # Helper to recursively format attributes
        def format_attr(value, indent=1):
            space = "    " * indent
            if isinstance(value, list):
                return (
                    "[\n"
                    + ",\n".join(format_attr(v, indent + 1) for v in value)
                    + f"\n{space}]"
                )
            elif hasattr(value, "__repr__") and not isinstance(value, str):
                # Call repr() of nested object with extra indent
                nested = repr(value)
                nested_lines = nested.splitlines()
                indented_lines = [space + line for line in nested_lines]
                return "\n".join(indented_lines)
            else:
                return repr(value)

        attrs = "\n".join(f"    {k}={format_attr(v)}" for k, v in vars(self).items())
        return f"WeatherReport(\n{attrs}\n)"


class WeatherView:
    """
    Represents a presentation-ready view of weather data for the UI or CLI.

    This object aggregates one or more WeatherReport instances and enriches
    them with application-level metadata and display-specific information.
    It is not returned by scrapers and should only be constructed by the
    application or presentation layer.

    WeatherView owns configuration and rendering context such as units,
    timezone, and generation time, ensuring a single source of truth for
    how weather data is displayed.

    Attributes:
        app_name (str):
            Name of the application generating the output.

        app_version (str):
            Version of the application generating the output.

        units (str):
            Unit system used for display (e.g. "imperial", "metric").

        timezone (str):
            Timezone used for interpreting and displaying time-based data.

        generated_at (datetime):
            Timestamp indicating when this view was generated/rendered.

        summary (str):
            High-level, human-readable summary of the weather conditions.

        reports (list[WeatherReport]):
            One or more normalized weather reports to be displayed or grouped
            together in the UI or CLI.
    """

    def __init__(self):
        self.app_name = None
        self.app_version = None
        self.units = None
        self.generated_at = None
        self.timezone = None
        self.summary = None
        self.reports = None

    def __repr__(self):
        # Helper to recursively format attributes
        def format_attr(value, indent=1):
            space = "    " * indent
            if isinstance(value, list):
                return (
                    "[\n"
                    + ",\n".join(format_attr(v, indent + 1) for v in value)
                    + f"\n{space}]"
                )
            elif hasattr(value, "__repr__") and not isinstance(value, str):
                # Call repr() of nested object with extra indent
                nested = repr(value)
                nested_lines = nested.splitlines()
                indented_lines = [space + line for line in nested_lines]
                return "\n".join(indented_lines)
            else:
                return repr(value)

        attrs = "\n".join(f"    {k}={format_attr(v)}" for k, v in vars(self).items())
        return f"WeatherView(\n{attrs}\n)"
