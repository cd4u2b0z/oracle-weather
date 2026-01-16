"""
Weather API Configuration for asciimatics-weather-toys
Uses the same APIs as your Waybar weather module.
"""

# OpenWeatherMap API (same as your bulletproof-weather.sh)
OPENWEATHERMAP_API_KEY = "69def8ba31d3be7da6226b6d51b2b655"
OPENWEATHERMAP_CITY_ID = "4597040"  # Summerville, SC
OPENWEATHERMAP_ZIP = "29465"

# OpenMeteo (no API key required - same as your weather.py)
LATITUDE = 32.4840
LONGITUDE = -80.1756
TIMEZONE = "America/New_York"

# Location display name
LOCATION_NAME = "Summerville, SC"

# Cache settings
CACHE_FILE = "/tmp/asciimatics_weather_cache.json"
CACHE_MAX_AGE = 300  # 5 minutes

# Animation settings
DEFAULT_TERMINAL_FPS = 30
