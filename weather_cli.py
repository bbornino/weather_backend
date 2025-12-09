# weather_cli.py
"""
Command-Line Interface (CLI) for the Weather Scraper project.

Purpose:
    - Provides a local interface to fetch weather data from multiple providers
    - Calls the core weather scraping logic in weather_scraper.py
    - Supports toggling which APIs and which data fields to retrieve
    - Designed for local testing, exploration, and development

Usage:
    python weather_cli.py [options]

Notes:
    - The CLI is a thin layer over the core logic.
    - Environment variables are loaded centrally in weather_scraper.py.
    - Future expansion could include additional CLI arguments or modes.
"""
