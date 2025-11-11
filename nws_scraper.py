import urllib.request
import json
from nws_config import enabled_metrics, enabled_units

lat, lon = 38.605200, -121.342720  # For My House
nws_endpoint_url = f"https://api.weather.gov/points/{lat},{lon}"

with urllib.request.urlopen(nws_endpoint_url) as response:
    location_data = json.loads(response.read().decode())

print(nws_endpoint_url)
print(location_data)

with open("nws_location_data.json", "w") as f:
    json.dump(location_data, f, indent=4)

#####################   Collect DAILY Forecast

print(location_data["properties"]["forecast"])
forecast_daily_url = location_data["properties"]["forecast"]
print(f"forecast_daily_url:{forecast_daily_url}")


with urllib.request.urlopen(forecast_daily_url) as response:
    forecast_daily_data = json.loads(response.read().decode())

print("forecast_daily_data:")
print(forecast_daily_data)

with open("nws_forecast_daily.json", "w") as f:
    json.dump(forecast_daily_data, f, indent=4)

#####################   Collect HOURLY Forecast
print(location_data["properties"]["forecastHourly"])
forecast_hourly_url = location_data["properties"]["forecastHourly"]
print(f"forecast_hourly_url:{forecast_hourly_url}")

with urllib.request.urlopen(forecast_hourly_url) as response:
    forecast_hourly_data = json.loads(response.read().decode())

print("forecast_hourly_data:")
print(forecast_hourly_data)

with open("nws_forecast_hourly.json", "w") as f:
    json.dump(forecast_hourly_data, f, indent=4)


#####################   Collect CURRENT Observation Stations
current_observation_stations_url = location_data["properties"]["observationStations"]
print(f"current_observation_stations_url:{current_observation_stations_url}")

with urllib.request.urlopen(current_observation_stations_url) as response:
    current_observation_stations_json = json.loads(response.read().decode())

print(f"current_observation_stations_json:{current_observation_stations_json}")
print(current_observation_stations_json["features"][0]["id"])

with open("nws_current_observation_stations_json.json", "w") as f:
    json.dump(current_observation_stations_json, f, indent=4)


#####################   Collect CURRENT Closest Observation Station Data
current_closest_observation_station_url = (
    current_observation_stations_json["features"][0]["id"] + "/observations/latest"
)

with urllib.request.urlopen(current_closest_observation_station_url) as response:
    current_observation_data_json = json.loads(response.read().decode())

print(
    f"current_closest_observation_station_url:{current_closest_observation_station_url}"
)
print("current_observation_data_json:")
print(current_observation_data_json["properties"]["temperature"])
current_temperature_c = current_observation_data_json["properties"]["temperature"][
    "value"
]
current_temperature_f = 32 + current_temperature_c * 1.8
print(f"Current Temp: {current_temperature_c} degC or {current_temperature_f} degF")

with open("nws_current_observation_data.json", "w") as f:
    json.dump(current_observation_data_json, f, indent=4)
