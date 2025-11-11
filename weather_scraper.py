# weather_scraper.py
# ------------------
# This script gets the current weather for your city using the Open-Meteo API.
# It uses only Python's built-in libraries (no installs needed).

import urllib.request
import json
from weather_code_map import WEATHER_CODE_MAP

# STEP 1: Define the city you want the weather for.
# For now, let's use Carmichael, California.
latitude = 38.6171
longitude = -121.3283

# STEP 2: Create the URL to ask Open-Meteo for the current weather.
# We request temperature, windspeed, and weather code.
url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={latitude}&longitude={longitude}"
    "&current_weather=true"
)

# STEP 3: Send the request and read the response
print(f"Fetching current weather for Carmichael, CA...\n")
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())

# STEP 4: Extract the weather information
current = data["current_weather"]
temperature = current["temperature"]
windspeed = current["windspeed"]
code = current["weathercode"]

print(data)

# STEP 5: Display the results nicely
print(f"Temperature: {temperature}°C")
print(f"Wind speed: {windspeed} km/h")
print(f"Weather code: {code} - {WEATHER_CODE_MAP.get(code)}")
