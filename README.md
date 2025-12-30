# Weather Backend README.md

This project provides a unified backend for fetching and normalizing weather data from multiple APIs, starting with Open-Meteo. It defines core data objects, standardizes returned data, and prepares it for display in a CLI or UI.

---

## Project Info

- **Repository**: [GitHub link placeholder](#)
- **Website / Live Demo**: [Website link placeholder](#)
- **Documentation**: [Documentation link placeholder](#)
- **Author / Maintainer**: Brian Bornino
- **License**: MIT / TBD

---

## Release History

- **v0.1 (2025-12-30)**  
  - Initial backend implementation  
  - Integrated Open-Meteo API  
  - Added core objects: `WeatherData`, `WeatherReport`, `WeatherView`  
  - Basic CLI / Python usage example included  

- **v0.2 (TBD)**  
  - Add support for additional APIs  
  - Integrate hourly and daily forecasts  
  - Refine `WeatherView` formatting for display  
  - Add web UI / notifications


---

## Planned Features

- Support additional weather APIs (WeatherAPI, NWS, WeatherBit)
- Hourly and daily forecasts fully integrated
- CLI and Web UI for rendering `WeatherView`
- Alerts / notifications for severe weather



---

## Core Objects

### WeatherView
Represents a presentation-ready view of weather data, aggregating one or more WeatherReport instances. Holds app-level metadata and display context.


WeatherView
├── app_name: str # Application name
├── app_version: str # Application version
├── units: str # "imperial" or "metric"
├── generated_at: datetime # Timestamp of render
├── timezone: str # Timezone string
├── summary: str # Human-readable summary of weather
└── reports: list[WeatherReport]


### WeatherReport
Represents normalized data from a single weather source. Returned by scrapers.

WeatherReport
├── source: str # e.g., "open_meteo"
├── location: str # City/state or lat/lon
├── latitude: str 
├── longitude: str 
├── fetched_at: datetime # When data was retrieved
├── current: WeatherData # REQUIRED: current weather
├── hourly: list[WeatherData] or None # Optional hourly forecast
└── daily: list[WeatherData] or None # Optional daily forecast


### WeatherData
Represents the weather conditions at a specific point in time.
WeatherData
├── temperature: float
├── feels_like: float
├── wind_chill: float
├── heat_index: float
├── dew_point: float
├── wind_speed: float
├── wind_degree: float
├── wind_direction: str
├── wind_gust: float
├── humidity: float
├── pressure: float
├── precipitation: float
├── visibility: float
├── cloud_cover: float
├── uv: float
├── timestamp: datetime
├── condition: dict or list
└── condition_str: str # Human-readable description



---

## Helper Functions

- `parse_location(location: str) -> dict`: Converts a location string to latitude/longitude or city/state.
- `degrees_to_direction(deg: float) -> str`: Converts wind degrees to compass direction.

---

## API Integration

- **Open-Meteo**: Fully integrated. Returns a `WeatherReport` object.
- Additional APIs can be integrated by writing scraper functions that normalize to `WeatherReport`.

---

## Usage

```python
from weather_shared import WeatherView, WeatherReport
from weather_scraper import get_open_meteo_data

report = get_open_meteo_data("San Francisco, CA", units="imperial")

view = WeatherView()
view.app_name = "Bornino Weather App"
view.app_version = "0.1"
view.units = "imperial"
view.generated_at = datetime.now()
view.timezone = "America/Los_Angeles"
view.reports = [report]

print(view)


---

## Notes

- `hourly` and `daily` forecasts are optional and may be `None` for some APIs.
- All `WeatherData` fields default to `None` unless the API provides them.
- Time-related fields (`fetched_at`, `generated_at`, `timestamp`) are stored as `datetime` objects for internal consistency. Format to strings only when displaying.
- `WEATHER_CODE_MAP` maps WMO weather codes to human-readable descriptions.
