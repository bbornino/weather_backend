"""
# weather_scraper.py
#
# Core weather scraping logic.
# Imports individual provider scrapers and aggregates data.
# Serves CLI, Lambda, and future front-ends.
#
"""

import urllib.request
import json
from weather_code_map import WEATHER_CODE_MAP
