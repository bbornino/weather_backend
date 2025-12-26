"""
weather_cli.py - Command-Line Interface (CLI) for the Weather Scraper project.

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

import argparse
import json
import os
import sys
from copy import deepcopy
from weather_scraper import get_weather


DEFAULT_SETTINGS_FILE = "weather_settings.json"
DEFAULTS = {
    "units": "imperial",
    "show": ["temp", "humidity"],
    "forecast": {"type": None, "count": 0},  # None | "hours" | "days"
    "apis": {},
    "locations": {},
    "default_location": None,
}

UNIT_DESCRIPTIONS = {
    "imperial": "Temperature: °F   Wind: mph",
    "metric": "Temperature: °C   Wind: km/h",
}

AVAILABLE_APIS = {
    "a": {
        "name": "accuweather",
        "description": "Detailed forecasts with alerts; strong US coverage; popular for hyper-local predictions",
        "status": "API KEY ISSUE",
    },
    "n": {
        "name": "national_weather_service",
        "description": "Official US government forecasts and warnings; US-only; reliable for alerts",
        "status": "TBD",
    },
    "o": {
        "name": "open_meteo",
        "description": "Free, no-auth global API; simple forecasts and historical data; lightweight",
        "status": "TBD",
    },
    "w": {
        "name": "open_weather",
        "description": "Global coverage, current weather and forecasts; widely supported; needs API key",
        "status": "OK",
    },
    "p": {
        "name": "weatherapi",
        "description": "Global forecasts including historical data; supports alerts and astronomy info",
        "status": "OK",
    },
    "b": {
        "name": "weatherbit",
        "description": "Global hourly/daily forecasts; good for developers needing JSON output",
        "status": "API KEY ISSUE",
    },
}


def load_settings(path):
    """Load settings from a JSON file, or return defaults if the file does not exist."""
    if not os.path.exists(path):
        return deepcopy(DEFAULTS)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings, path="weather_settings.json"):
    """Save the settings dictionary to a JSON file at the given path."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def merge_state(defaults, config, args):
    """Merge defaults, config, and CLI arguments into a single state dictionary."""
    state = deepcopy(defaults)
    state.update(config)

    for key, value in args.items():
        if value is not None:
            state[key] = value

    if isinstance(state.get("show"), str):
        state["show"] = [v.strip() for v in state["show"].split(",")]

    if state.get("forecast_days"):
        state["forecast"] = {"type": "days", "count": state["forecast_days"]}

    if state.get("forecast_hours"):
        state["forecast"] = {"type": "hours", "count": state["forecast_hours"]}

    return state


def parse_args():
    """Parse command-line arguments and return them as a dictionary."""
    parser = argparse.ArgumentParser(description="Weather comparison CLI")

    parser.add_argument(
        "--config", default=DEFAULT_SETTINGS_FILE, help="Path to settings JSON file"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument(
        "--no-interactive", action="store_true", help="Disable interactive prompts"
    )

    parser.add_argument("location", nargs="?", help="Named location alias")

    parser.add_argument("--apis", help="Comma-separated API list")
    parser.add_argument("--only", help="Use only specified APIs")

    parser.add_argument("--units", choices=["imperial", "metric"])
    parser.add_argument("--show", help="Comma-separated fields")

    parser.add_argument("--forecast-days", type=int)
    parser.add_argument("--forecast-hours", type=int)

    parser.add_argument("--no-config", action="store_true")

    return vars(parser.parse_args())


def should_use_interactive(args):
    """Return True if the CLI should run in interactive mode."""
    if args["interactive"]:
        return True

    if args["no_interactive"]:
        return False

    # sys.argv always includes the script name as argv[0]
    # If length == 1, user passed no CLI args
    return len(sys.argv) == 1


def manage_locations(state):
    """Interactively set the locations in the state."""
    locations = state.get("locations", {})
    default_loc = state.get("default_location")
    active_loc = state.get("active_location", default_loc)

    while True:
        print("\nLocations:")
        if locations:
            for alias, loc in locations.items():
                marks = []
                if alias == default_loc:
                    marks.append("default")
                if alias == active_loc:
                    marks.append("active")
                mark_str = f" ({', '.join(marks)})" if marks else ""
                print(f" - {alias}: {loc}{mark_str}")
        else:
            print(" No locations defined.")

        print("\nOptions:")
        print("a) Add location")
        print("r) Remove location")
        print("s) Set default location")
        print("c) Set active location for this session")
        print("d) Done")

        choice = input("Choose an option: ").strip().lower()

        if choice == "a":
            alias = input("Enter alias (e.g., home, work): ").strip()
            val = input("Enter location (City, State OR Zip OR lat,lon): ").strip()
            locations[alias] = val
            if not default_loc:
                state["default_location"] = alias
            print(f"Added location '{alias}'")
        elif choice == "r":
            alias = input("Enter alias to remove: ").strip()
            if alias in locations:
                del locations[alias]
                if state.get("default_location") == alias:
                    state["default_location"] = None
                print(f"Removed location '{alias}'")
            else:
                print("Alias not found.")
        elif choice == "s":
            alias = input("Enter alias to set as default: ").strip()
            if alias in locations:
                state["default_location"] = alias
                print(f"Default location set to '{alias}'")
            else:
                print("Alias not found.")
        elif choice == "c":
            alias = input("Enter alias to set as active: ").strip()
            if alias in locations:
                state["active_location"] = alias
                active_loc = alias
                state["location"] = locations[alias]
                print(f"Active location set to '{alias}': '{state["location"]}'")
            else:
                print("Alias not found.")
        elif choice == "d":
            state["locations"] = locations
            return  # done
        else:
            print("Invalid choice, try again.")


def manage_apis(state):
    """Interactively set the APIs in the state using single-character selection."""
    apis = state.get("apis", {})

    while True:
        print("\nAPIs (toggle by letter):\n")
        if apis:
            for key, info in AVAILABLE_APIS.items():
                name = info["name"]
                enabled = apis.get(name, {}).get("enabled", False)
                status = "ON" if enabled else "OFF"
                api_status = info["status"]
                print(f"[{key}] {name:<28} [{status}] ({api_status})")
            print("\n[?] View API descriptions")
            print("\n[d] Done")
        else:
            print(" No APIs defined.")

        choice = input("Choose an API to toggle or 'd' when done: ").strip().lower()

        if choice in AVAILABLE_APIS:
            api_name = AVAILABLE_APIS[choice]["name"]
            if api_name not in apis:
                apis[api_name] = {"enabled": True}
                print(f"Added API '{api_name}' (enabled)")
            else:
                apis[api_name]["enabled"] = not apis[api_name].get("enabled", False)
                status = "enabled" if apis[api_name]["enabled"] else "disabled"
                print(f"API '{api_name}' is now {status}")
        elif choice == "?":
            print("\nAPI Details:\n")
            for info in AVAILABLE_APIS.values():
                print(f"{info['name']}")
                print(f"  {info['description']}\n")
            input("Press Enter to return to the API list...")
        elif choice == "d":
            state["apis"] = apis
            return
        else:
            print("Invalid choice, try again.")


def set_units(state):
    """Interactively set the units in the state."""
    current = state.get("units", "imperial")
    print(f"\nCurrent units: {current}")
    print("Options:")
    print("i) imperial")
    print("m) metric")
    print("c) Cancel")

    choice = input("Choose units: ").strip().lower()
    if choice == "i":
        state["units"] = "imperial"
        print("Units set to imperial")
    elif choice == "m":
        state["units"] = "metric"
        print("Units set to metric")
    elif choice == "c":
        print("Units unchanged")
    else:
        print("Invalid choice, units unchanged")


def set_fields(state):
    """Interactively set the fields in the state."""
    current = state.get("show", ["temp", "humidity"])
    available = [
        "temp",
        "humidity",
        "wind",
        "pressure",
        "clouds",
        "uv",
    ]  # extend as needed

    while True:
        print("\nCurrent fields to display: " + ", ".join(current))
        print("Available fields: " + ", ".join(available))
        print("Options:")
        print("a) Add a field")
        print("r) Remove a field")
        print("d) Reset to defaults")
        print("c) Cancel")

        choice = input("Choose an option: ").strip().lower()
        if choice == "a":
            field = input("Enter field to add: ").strip()
            if field in available and field not in current:
                current.append(field)
                print(f"Added field '{field}'")
            else:
                print("Invalid field or already present")
        elif choice == "r":
            field = input("Enter field to remove: ").strip()
            if field in current:
                current.remove(field)
                print(f"Removed field '{field}'")
            else:
                print("Field not in current selection")
        elif choice == "d":
            current = ["temp", "humidity"]
            print("Reset to default fields")
        elif choice == "c":
            state["show"] = current
            return
        else:
            print("Invalid choice, try again")


def set_forecast(state):
    """Interactively set the forcast type (days vs hours) in the state."""
    forecast = state.get("forecast", {"type": None, "count": 0})
    current_type = forecast.get("type", None)
    current_count = forecast.get("count", 0)

    print(f"\nCurrent forecast: {current_type or 'None'} ({current_count})")
    print("Options:")
    print("h) Set forecast in hours")
    print("d) Set forecast in days")
    print("n) Disable forecast")
    print("c) Cancel")

    choice = input("Choose an option: ").strip().lower()
    if choice == "h":
        count = input("Enter number of hours: ").strip()
        if count.isdigit():
            state["forecast"] = {"type": "hours", "count": int(count)}
            print(f"Forecast set to {count} hours")
        else:
            print("Invalid input")
    elif choice == "d":
        count = input("Enter number of days: ").strip()
        if count.isdigit():
            state["forecast"] = {"type": "days", "count": int(count)}
            print(f"Forecast set to {count} days")
        else:
            print("Invalid input")
    elif choice == "n":
        state["forecast"] = {"type": None, "count": 0}
        print("Forecast disabled")
    elif choice == "c":
        print("Forecast unchanged")
    else:
        print("Invalid choice, forecast unchanged")


def interactive_menu(state, config_path):
    """Display the interactive menu."""
    while True:
        print("\nWeather CLI - Interactive Mode\n")
        print(f"Settings file - {config_path}")

        default_alias = state.get("default_location")
        active_alias = state.get("active_location", default_alias)
        locations = state.get("locations", {})

        default_loc = locations.get(default_alias, "None")
        active_loc = locations.get(active_alias, "None")

        print(f"Selected location - {active_alias}: {active_loc}")
        print(f"Default location - {default_alias}: {default_loc}")

        current_units = state.get("units", "imperial")
        print(f"Units - {UNIT_DESCRIPTIONS.get(current_units, current_units)}")
        print(f"Fields to show - {', '.join(state.get('show', []))}")
        print(
            f"Forecast - {state['forecast'].get('type', 'None')} ({state['forecast'].get('count', 0)})"
        )
        enabled_apis = [k for k, v in state.get("apis", {}).items() if v.get("enabled")]
        print(f"Enabled APIs - {', '.join(enabled_apis) if enabled_apis else 'None'}\n")

        print("Menu:")
        print("L) Select location")
        print("A) Select APIs")
        print("U) Units")
        print("F) Fields to display")
        print("O) Forecast options")
        print("R) Run weather comparison")
        print("X) Exit")

        choice = input("\nChoose an option: ").strip().lower()

        if choice == "l":
            manage_locations(state)
        elif choice == "a":
            manage_apis(state)
        elif choice == "u":
            set_units(state)
        elif choice == "f":
            set_fields(state)
        elif choice == "o":
            set_forecast(state)
        elif choice == "r":
            print("actual run not implemented... yet")
            weather_results = get_weather(state)
            print("\n\nReceived this weather:")
            print(weather_results)
            break
        elif choice == "x":
            break
        else:
            print("Invalid choice, try again.")


def main():
    """
    Entry point for the Weather CLI.

    - Parses command-line arguments
    - Loads and merges settings
    - Runs either interactive or non-interactive mode
    - Saves updated settings to disk
    """
    args = parse_args()
    interactive = should_use_interactive(args)

    config_path = args["config"]
    config = {} if args.get("no_config") else load_settings(config_path)

    state = merge_state(DEFAULTS, config, args)

    if interactive:
        print("[Interactive mode]\n")
        interactive_menu(state, config_path)
        save_settings(state, config_path)
    else:
        print("[Non-interactive mode]\n")

    print("goodbye!")


if __name__ == "__main__":
    main()
