import urllib.request
import json
from open_meteo_config import enabled_open_meteo_metrics, enabled_units

base_url = "https://api.open-meteo.com/v1/forecast"
lat, lon = 38.605200, -121.342720  # For My House
query = f"?latitude={lat}&longitude={lon}&current_weather=true"

# for canonical_name, api_field in enabled_open_meteo_metrics.items():
#     query += f"&{api_field}=true"

hourly_fields = []
daily_fields = []

for canonical_name, api_field in enabled_open_meteo_metrics.items():
    if api_field in [
        "temperature_2m",
        "apparent_temperature",
        "windspeed_10m",
        "winddirection_10m",
        "weathercode",
    ]:
        continue  # already in current_weather
    elif api_field in [
        "relative_humidity_2m",
        "dewpoint_2m",
        "precipitation_probability",
        "uv_index",
    ]:
        hourly_fields.append(api_field)
    elif api_field in ["uv_index_max", "precipitation_sum"]:
        daily_fields.append(api_field)

if hourly_fields:
    query += "&hourly=" + ",".join(hourly_fields)

if daily_fields:
    query += "&daily=" + ",".join(daily_fields)

if enabled_units == "us":
    query += "&temperature_unit=fahrenheit"
    query += "&windspeed_unit=mph"
    query += "&precipitation_unit=inch"
    query += "&timezone=America/Los_Angeles"


full_url = base_url + query


with urllib.request.urlopen(full_url) as response:
    data = json.loads(response.read().decode())

print(full_url)
print(data)
