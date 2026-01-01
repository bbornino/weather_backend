# Weather Backend README.md

This project provides a unified backend for fetching and normalizing weather data from multiple APIs, starting with OpenMeteo, WeatherAPI, NWS, and OpenWeather. It defines core data objects, standardizes returned data, and prepares it for display in a CLI or UI.

---

## Project Info

- **Repository**: [GitHub link placeholder](https://github.com/bbornino/weather_backend)
- **Website / Live Demo**: Coming soon
- **Documentation**: Will be available in ~1 week
- **Author / Maintainer**: Brian Bornino
- **License**: MIT / TBD

---

## Getting Started

These instructions help you set up the Weather Backend locally and try a simple CLI example.

### Prerequisites

- Python 3.11+ installed
- pip (Python package manager)
- Environment variables:
  - `HOME_CITY`, `HOME_LATITUDE`, `HOME_LONGITUDE` (for default location)
  - `OPENWEATHERMAP_API_KEY` (for OpenWeather integration)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/bbornino/weather_backend.git
cd weather_backend

2. Set up environment variables (example .env file):

HOME_CITY=[your city, state]
HOME_LATITUDE=[your latitude]
HOME_LONGITUDE=[your longitude]
OPENWEATHERMAP_API_KEY=your_api_key_here

Example CLI Usage
python weather_cli.py --location "Carmichael, CA" --units imperial --show temp,humidity


Expected output (abbreviated):

Temperature      57.2°F
Humidity         94%
Wind Speed       11.4mph
---

## Release History

- **v0.1 (2026-01-01)**  
  - Core backend implementation
  - Unified data objects (`WeatherData`, `WeatherReport`, `WeatherView`)
  - CLI-ready display for current weather
  - Initial integration with Open-Meteo API


- **v0.2 (TBD)**  
  - Integrate hourly and daily forecasts  
  


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
├── `app_name`: str # Application name
├── `app_version`: str # Application version
├── `units`: str # "imperial" or "metric"
├── `generated_at`: datetime # Timestamp of render
├── `timezone`: str # Timezone string
├── `summary`: str # Human-readable summary of weather
└── `reports`: list[WeatherReport]


### WeatherReport
Represents normalized data from a single weather source. Returned by scrapers.

WeatherReport
├── `source`: str # e.g., "open_meteo"
├── `location`: str # City/state or lat/lon
├── `latitude`: str 
├── `longitude`: str 
├── `fetched_at`: datetime # When data was retrieved
├── `current`: WeatherData # REQUIRED: current weather
├── `hourly`: list[WeatherData] or None # Optional hourly forecast
├── `daily`: list[WeatherData] or None # Optional hourly forecast
├── `astronomy`: obj or None  # Optional info
└── `alerts`: obj or None  # Optional info


### WeatherData
Represents the weather conditions at a specific point in time.
WeatherData
├── `temperature`: float
├── `feels_like`: float
├── `wind_chill`: float
├── `heat_index`: float
├── `dew_point`: float
├── `wind_speed`: float
├── `wind_degree`: float
├── `wind_direction`: str
├── `wind_gust`: float
├── `humidity`: float
├── `pressure`: float
├── `precipitation`: float
├── `visibility`: float
├── `cloud_cover`: float
├── `uv`: float
├── `icon`: str #  URL to NWS weather icon
├── `timestamp`: datetime
├── `condition`: dict or list
└── `condition_str`: str # Human-readable description



---

## Helper Functions

- `parse_location(location: str) -> dict`: Converts a location string to latitude/longitude or city/state.
- `degrees_to_direction(deg: float) -> str`: Converts wind degrees to compass direction.
- `format_unit_description_full(location: str)`
- `UNIT_MAP`: Maps data types to display units (°F/°C, mph/kph, etc.)
- `WEATHER_CODE_MAP`: Maps WMO weather codes to descriptions

---

## API Integration

- OpenMeteo, WeatherAPI, NWS, and OpenWeather: Fully integrated. Returns a `WeatherReport` object.
- Additional APIs can be integrated by writing scraper functions that normalize to `WeatherReport`.

---


## Notes

- `hourly` and `daily` forecasts are optional and may be `None` for some APIs.
- All `WeatherData` fields default to `None` unless the API provides them.
- Time-related fields (`fetched_at`, `generated_at`, `timestamp`) are stored as `datetime` objects for internal consistency. Format to strings only when displaying.
- `WEATHER_CODE_MAP` maps WMO weather codes to human-readable descriptions.
