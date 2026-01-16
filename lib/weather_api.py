"""
Weather API client - fetches real weather data from OpenWeatherMap and OpenMeteo.
Mirrors your Waybar weather configuration.
"""
import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import requests

# Import config
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    OPENWEATHERMAP_API_KEY, OPENWEATHERMAP_CITY_ID,
    LATITUDE, LONGITUDE, TIMEZONE, LOCATION_NAME,
    CACHE_FILE, CACHE_MAX_AGE
)


class WeatherCondition(Enum):
    """Weather conditions that map to animations."""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    FOG = "fog"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    FREEZING_RAIN = "freezing_rain"
    SNOW = "snow"
    HEAVY_SNOW = "heavy_snow"
    THUNDERSTORM = "thunderstorm"
    UNKNOWN = "unknown"


@dataclass
class WeatherData:
    """Current weather conditions."""
    condition: WeatherCondition
    temperature_f: float
    temperature_c: float
    humidity: int
    wind_speed_mph: float
    wind_direction: int  # degrees
    description: str
    location: str
    timestamp: float
    
    # Additional data for animations
    clouds_percent: int = 0
    rain_intensity: float = 0.0  # mm/h
    snow_intensity: float = 0.0  # mm/h
    visibility: int = 10000  # meters
    pressure: int = 1013  # hPa
    
    @property
    def wind_strength(self) -> str:
        """Human-readable wind strength."""
        if self.wind_speed_mph < 5:
            return "calm"
        elif self.wind_speed_mph < 15:
            return "light"
        elif self.wind_speed_mph < 25:
            return "moderate"
        elif self.wind_speed_mph < 40:
            return "strong"
        else:
            return "severe"
    
    @property
    def is_stormy(self) -> bool:
        return self.condition in (WeatherCondition.THUNDERSTORM, WeatherCondition.HEAVY_RAIN)
    
    @property
    def is_precipitation(self) -> bool:
        return self.condition in (
            WeatherCondition.DRIZZLE, WeatherCondition.RAIN, WeatherCondition.HEAVY_RAIN,
            WeatherCondition.SNOW, WeatherCondition.HEAVY_SNOW, WeatherCondition.FREEZING_RAIN
        )


# OpenWeatherMap condition code to our condition mapping
OWM_CONDITION_MAP = {
    # Thunderstorm group (2xx)
    200: WeatherCondition.THUNDERSTORM, 201: WeatherCondition.THUNDERSTORM,
    202: WeatherCondition.THUNDERSTORM, 210: WeatherCondition.THUNDERSTORM,
    211: WeatherCondition.THUNDERSTORM, 212: WeatherCondition.THUNDERSTORM,
    221: WeatherCondition.THUNDERSTORM, 230: WeatherCondition.THUNDERSTORM,
    231: WeatherCondition.THUNDERSTORM, 232: WeatherCondition.THUNDERSTORM,
    # Drizzle group (3xx)
    300: WeatherCondition.DRIZZLE, 301: WeatherCondition.DRIZZLE,
    302: WeatherCondition.DRIZZLE, 310: WeatherCondition.DRIZZLE,
    311: WeatherCondition.DRIZZLE, 312: WeatherCondition.DRIZZLE,
    313: WeatherCondition.DRIZZLE, 314: WeatherCondition.DRIZZLE,
    321: WeatherCondition.DRIZZLE,
    # Rain group (5xx)
    500: WeatherCondition.RAIN, 501: WeatherCondition.RAIN,
    502: WeatherCondition.HEAVY_RAIN, 503: WeatherCondition.HEAVY_RAIN,
    504: WeatherCondition.HEAVY_RAIN, 511: WeatherCondition.FREEZING_RAIN,
    520: WeatherCondition.RAIN, 521: WeatherCondition.RAIN,
    522: WeatherCondition.HEAVY_RAIN, 531: WeatherCondition.RAIN,
    # Snow group (6xx)
    600: WeatherCondition.SNOW, 601: WeatherCondition.SNOW,
    602: WeatherCondition.HEAVY_SNOW, 611: WeatherCondition.FREEZING_RAIN,
    612: WeatherCondition.FREEZING_RAIN, 613: WeatherCondition.FREEZING_RAIN,
    615: WeatherCondition.SNOW, 616: WeatherCondition.SNOW,
    620: WeatherCondition.SNOW, 621: WeatherCondition.SNOW,
    622: WeatherCondition.HEAVY_SNOW,
    # Atmosphere group (7xx)
    701: WeatherCondition.FOG, 711: WeatherCondition.FOG,
    721: WeatherCondition.FOG, 731: WeatherCondition.FOG,
    741: WeatherCondition.FOG, 751: WeatherCondition.FOG,
    761: WeatherCondition.FOG, 762: WeatherCondition.FOG,
    771: WeatherCondition.THUNDERSTORM, 781: WeatherCondition.THUNDERSTORM,
    # Clear (800)
    800: WeatherCondition.CLEAR,
    # Clouds (80x)
    801: WeatherCondition.PARTLY_CLOUDY, 802: WeatherCondition.PARTLY_CLOUDY,
    803: WeatherCondition.CLOUDY, 804: WeatherCondition.CLOUDY,
}


def _load_cache() -> Optional[WeatherData]:
    """Load weather data from cache if valid."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
            
            # Check cache age
            if time.time() - data.get('timestamp', 0) < CACHE_MAX_AGE:
                return WeatherData(
                    condition=WeatherCondition(data['condition']),
                    temperature_f=data['temperature_f'],
                    temperature_c=data['temperature_c'],
                    humidity=data['humidity'],
                    wind_speed_mph=data['wind_speed_mph'],
                    wind_direction=data['wind_direction'],
                    description=data['description'],
                    location=data['location'],
                    timestamp=data['timestamp'],
                    clouds_percent=data.get('clouds_percent', 0),
                    rain_intensity=data.get('rain_intensity', 0.0),
                    snow_intensity=data.get('snow_intensity', 0.0),
                    visibility=data.get('visibility', 10000),
                    pressure=data.get('pressure', 1013),
                )
    except Exception:
        pass
    return None


def _save_cache(weather: WeatherData):
    """Save weather data to cache."""
    try:
        data = {
            'condition': weather.condition.value,
            'temperature_f': weather.temperature_f,
            'temperature_c': weather.temperature_c,
            'humidity': weather.humidity,
            'wind_speed_mph': weather.wind_speed_mph,
            'wind_direction': weather.wind_direction,
            'description': weather.description,
            'location': weather.location,
            'timestamp': weather.timestamp,
            'clouds_percent': weather.clouds_percent,
            'rain_intensity': weather.rain_intensity,
            'snow_intensity': weather.snow_intensity,
            'visibility': weather.visibility,
            'pressure': weather.pressure,
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


def fetch_openweathermap() -> Optional[WeatherData]:
    """Fetch weather from OpenWeatherMap API (same as your Waybar script)."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'id': OPENWEATHERMAP_CITY_ID,
            'appid': OPENWEATHERMAP_API_KEY,
            'units': 'imperial'  # Fahrenheit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse response
        weather_id = data['weather'][0]['id']
        condition = OWM_CONDITION_MAP.get(weather_id, WeatherCondition.UNKNOWN)
        
        temp_f = data['main']['temp']
        temp_c = (temp_f - 32) * 5 / 9
        
        # Get rain/snow intensity if present
        rain_intensity = 0.0
        snow_intensity = 0.0
        if 'rain' in data:
            rain_intensity = data['rain'].get('1h', data['rain'].get('3h', 0)) / 3
        if 'snow' in data:
            snow_intensity = data['snow'].get('1h', data['snow'].get('3h', 0)) / 3
        
        return WeatherData(
            condition=condition,
            temperature_f=temp_f,
            temperature_c=temp_c,
            humidity=data['main']['humidity'],
            wind_speed_mph=data['wind']['speed'],
            wind_direction=data['wind'].get('deg', 0),
            description=data['weather'][0]['description'].title(),
            location=LOCATION_NAME,
            timestamp=time.time(),
            clouds_percent=data['clouds']['all'],
            rain_intensity=rain_intensity,
            snow_intensity=snow_intensity,
            visibility=data.get('visibility', 10000),
            pressure=data['main']['pressure'],
        )
    except Exception as e:
        print(f"OpenWeatherMap error: {e}", file=sys.stderr)
        return None


def fetch_openmeteo() -> Optional[WeatherData]:
    """Fetch weather from OpenMeteo API (fallback, no API key needed)."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': LATITUDE,
            'longitude': LONGITUDE,
            'current': [
                'temperature_2m', 'relative_humidity_2m', 'weather_code',
                'wind_speed_10m', 'wind_direction_10m', 'cloud_cover',
                'precipitation', 'rain', 'snowfall', 'visibility',
                'surface_pressure'
            ],
            'timezone': TIMEZONE,
            'temperature_unit': 'fahrenheit',
            'wind_speed_unit': 'mph',
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        
        # Map OpenMeteo weather codes
        wmo_code = current['weather_code']
        condition = _map_wmo_code(wmo_code)
        
        temp_f = current['temperature_2m']
        temp_c = (temp_f - 32) * 5 / 9
        
        return WeatherData(
            condition=condition,
            temperature_f=temp_f,
            temperature_c=temp_c,
            humidity=current['relative_humidity_2m'],
            wind_speed_mph=current['wind_speed_10m'],
            wind_direction=int(current['wind_direction_10m']),
            description=_get_description(wmo_code),
            location=LOCATION_NAME,
            timestamp=time.time(),
            clouds_percent=int(current.get('cloud_cover', 0)),
            rain_intensity=current.get('rain', 0.0),
            snow_intensity=current.get('snowfall', 0.0),
            visibility=int(current.get('visibility', 10000)),
            pressure=int(current.get('surface_pressure', 1013)),
        )
    except Exception as e:
        print(f"OpenMeteo error: {e}", file=sys.stderr)
        return None


def _map_wmo_code(code: int) -> WeatherCondition:
    """Map WMO weather codes to our conditions."""
    if code == 0:
        return WeatherCondition.CLEAR
    elif code in (1, 2):
        return WeatherCondition.PARTLY_CLOUDY
    elif code == 3:
        return WeatherCondition.CLOUDY
    elif code in (45, 48):
        return WeatherCondition.FOG
    elif code in (51, 53, 55):
        return WeatherCondition.DRIZZLE
    elif code in (56, 57, 66, 67):
        return WeatherCondition.FREEZING_RAIN
    elif code in (61, 63, 80, 81):
        return WeatherCondition.RAIN
    elif code in (65, 82):
        return WeatherCondition.HEAVY_RAIN
    elif code in (71, 73, 77, 85):
        return WeatherCondition.SNOW
    elif code in (75, 86):
        return WeatherCondition.HEAVY_SNOW
    elif code in (95, 96, 99):
        return WeatherCondition.THUNDERSTORM
    return WeatherCondition.UNKNOWN


def _get_description(code: int) -> str:
    """Get human-readable description from WMO code."""
    descriptions = {
        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing Rime Fog",
        51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
        56: "Light Freezing Drizzle", 57: "Dense Freezing Drizzle",
        61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        66: "Light Freezing Rain", 67: "Heavy Freezing Rain",
        71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow", 77: "Snow Grains",
        80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
        85: "Slight Snow Showers", 86: "Heavy Snow Showers",
        95: "Thunderstorm", 96: "Thunderstorm with Slight Hail", 99: "Thunderstorm with Heavy Hail",
    }
    return descriptions.get(code, "Unknown")


def get_weather(use_cache: bool = True) -> Optional[WeatherData]:
    """
    Get current weather data.
    Tries cache first, then OpenWeatherMap, then OpenMeteo.
    """
    # Try cache first
    if use_cache:
        cached = _load_cache()
        if cached:
            return cached
    
    # Try OpenWeatherMap (primary - same as your Waybar)
    weather = fetch_openweathermap()
    if weather:
        _save_cache(weather)
        return weather
    
    # Fallback to OpenMeteo
    weather = fetch_openmeteo()
    if weather:
        _save_cache(weather)
        return weather
    
    return None


# Quick test
if __name__ == "__main__":
    print("Fetching weather data...")
    weather = get_weather(use_cache=False)
    if weather:
        print(f"\n📍 {weather.location}")
        print(f"🌡️  {weather.temperature_f:.0f}°F ({weather.temperature_c:.0f}°C)")
        print(f"☁️  {weather.description}")
        print(f"💨 Wind: {weather.wind_speed_mph:.0f} mph ({weather.wind_strength})")
        print(f"💧 Humidity: {weather.humidity}%")
        print(f"👁️  Visibility: {weather.visibility}m")
        print(f"🎬 Animation: {weather.condition.value}")
    else:
        print("Failed to fetch weather data")


# ═══════════════════════════════════════════════════════════════════════════════
# 🌍 LOCATION SEARCH - Search any city worldwide
# ═══════════════════════════════════════════════════════════════════════════════

def geocode_location(query: str) -> Optional[dict]:
    """
    Geocode a location query using OpenWeatherMap's Geocoding API.
    Returns dict with lat, lon, name, country or None if not found.
    
    Tries multiple query variations for better matching:
    - Original query
    - With ", US" appended for US cities
    - City name only (first part before comma)
    
    Examples:
        geocode_location("Summerville, SC")
        geocode_location("New York, NY")
        geocode_location("Moscow, Russia")
        geocode_location("San Diego, CA")
    """
    # State abbreviation to full name mapping for better API matching
    US_STATES = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    
    def try_query(q: str, prefer_country: str = None) -> Optional[dict]:
        try:
            url = "https://api.openweathermap.org/geo/1.0/direct"
            # Get multiple results so we can prefer the right country
            params = {'q': q, 'limit': 5, 'appid': OPENWEATHERMAP_API_KEY}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                # If we prefer a country, try to find it first
                if prefer_country:
                    for result in data:
                        if result['country'] == prefer_country:
                            return {
                                'lat': result['lat'],
                                'lon': result['lon'],
                                'name': result['name'],
                                'state': result.get('state', ''),
                                'country': result['country'],
                            }
                # Fall back to first result
                result = data[0]
                return {
                    'lat': result['lat'],
                    'lon': result['lon'],
                    'name': result['name'],
                    'state': result.get('state', ''),
                    'country': result['country'],
                }
        except:
            pass
        return None
    
    # Build list of query variations to try
    queries_to_try = [query]
    
    # If query has a US state abbreviation, expand it
    parts = [p.strip() for p in query.split(',')]
    if len(parts) >= 2:
        state_abbr = parts[-1].upper().strip()
        if state_abbr in US_STATES:
            # Try: "City, Full State Name"
            city = parts[0]
            queries_to_try.append(f"{city}, {US_STATES[state_abbr]}")
            # Try: "City, State, US"  
            queries_to_try.append(f"{query}, US")
    
    # Try just the city name
    city_only = parts[0].strip()
    if city_only not in queries_to_try:
        queries_to_try.append(city_only)
    
    # Determine if we should prefer US results
    prefer_us = False
    if len(parts) >= 2:
        state_part = parts[-1].strip()
        state_abbr = state_part.upper()
        # Check abbreviation OR full state name
        if state_abbr in US_STATES or state_part.title() in US_STATES.values():
            prefer_us = True
    
    # Try each variation
    for q in queries_to_try:
        result = try_query(q, prefer_country='US' if prefer_us else None)
        if result:
            return result
    
    return None


def fetch_weather_by_coords(lat: float, lon: float, location_name: str = None) -> Optional[WeatherData]:
    """
    Fetch weather for any coordinates using OpenWeatherMap API.
    Uses the same API key as your Waybar config.
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': OPENWEATHERMAP_API_KEY,
            'units': 'imperial'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse response
        weather_id = data['weather'][0]['id']
        condition = OWM_CONDITION_MAP.get(weather_id, WeatherCondition.UNKNOWN)
        
        temp_f = data['main']['temp']
        temp_c = (temp_f - 32) * 5 / 9
        
        # Get rain/snow intensity if present
        rain_intensity = 0.0
        snow_intensity = 0.0
        if 'rain' in data:
            rain_intensity = data['rain'].get('1h', data['rain'].get('3h', 0)) / 3
        if 'snow' in data:
            snow_intensity = data['snow'].get('1h', data['snow'].get('3h', 0)) / 3
        
        # Use provided name or get from API
        loc_name = location_name or data.get('name', f"{lat:.2f}, {lon:.2f}")
        
        return WeatherData(
            condition=condition,
            temperature_f=temp_f,
            temperature_c=temp_c,
            humidity=data['main']['humidity'],
            wind_speed_mph=data['wind']['speed'],
            wind_direction=data['wind'].get('deg', 0),
            description=data['weather'][0]['description'].title(),
            location=loc_name,
            timestamp=time.time(),
            clouds_percent=data['clouds']['all'],
            rain_intensity=rain_intensity,
            snow_intensity=snow_intensity,
            visibility=data.get('visibility', 10000),
            pressure=data['main']['pressure'],
        )
    except Exception as e:
        print(f"Weather fetch error: {e}", file=sys.stderr)
        return None


def search_and_fetch_weather(query: str, retries: int = 2) -> Optional[WeatherData]:
    """
    Search for a location and fetch its weather in one call.
    Includes retry logic for rate-limited APIs.
    
    Usage:
        weather = search_and_fetch_weather("San Diego, CA")
        weather = search_and_fetch_weather("Tokyo, Japan")
        weather = search_and_fetch_weather("Paris, France")
    """
    for attempt in range(retries + 1):
        location = geocode_location(query)
        if location:
            break
        if attempt < retries:
            time.sleep(0.5)  # Brief pause before retry
    
    if not location:
        return None
    
    # Build nice location name
    if location['state']:
        loc_name = f"{location['name']}, {location['state']}, {location['country']}"
    else:
        loc_name = f"{location['name']}, {location['country']}"
    
    return fetch_weather_by_coords(location['lat'], location['lon'], loc_name)
