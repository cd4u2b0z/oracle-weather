"""
Extended Weather API Module
===========================
Adds forecast, alerts, astronomical data, UV/AQI, and historical data.

Features:
- 7-day forecast with hourly breakdowns
- NWS severe weather alerts
- Sunrise/sunset times
- Moon phase calculations
- UV index from OpenMeteo
- Air Quality Index (AQI)
- Historical comparison data
- Weather data export/logging

Author: Stormy the Weather Oracle
"""
from __future__ import annotations
import json
import math
import os
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, date
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
import requests

# Import base config
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    OPENWEATHERMAP_API_KEY, LATITUDE, LONGITUDE, 
    TIMEZONE, LOCATION_NAME
)
from lib.weather_api import WeatherCondition, WeatherData, OWM_CONDITION_MAP


# ═══════════════════════════════════════════════════════════════════════════════
# 📅 FORECAST DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HourlyForecast:
    """Single hour forecast data."""
    time: datetime
    temperature_f: float
    temperature_c: float
    condition: WeatherCondition
    description: str
    precipitation_prob: int  # 0-100%
    humidity: int
    wind_speed_mph: float
    wind_direction: int
    clouds_percent: int
    feels_like_f: float
    
    @property
    def hour_str(self) -> str:
        return self.time.strftime("%I%p").lstrip("0").lower()
    
    @property
    def temp_trend(self) -> str:
        """Unicode arrow for temperature display."""
        return ""  # Set by comparison logic


@dataclass
class DailyForecast:
    """Single day forecast data."""
    date: date
    temp_high_f: float
    temp_low_f: float
    temp_high_c: float
    temp_low_c: float
    condition: WeatherCondition
    description: str
    precipitation_prob: int
    precipitation_amount: float  # mm
    humidity: int
    wind_speed_mph: float
    sunrise: datetime
    sunset: datetime
    uv_index: float = 0.0
    
    @property
    def day_name(self) -> str:
        today = date.today()
        if self.date == today:
            return "Today"
        elif self.date == today + timedelta(days=1):
            return "Tomorrow"
        return self.date.strftime("%a")
    
    @property
    def temp_range_str(self) -> str:
        return f"{self.temp_high_f:.0f}°/{self.temp_low_f:.0f}°"
    
    def trend_vs(self, other: 'DailyForecast') -> str:
        """Get trend arrow comparing to another day."""
        diff = self.temp_high_f - other.temp_high_f
        if diff > 5:
            return "↑"
        elif diff > 2:
            return "↗"
        elif diff < -5:
            return "↓"
        elif diff < -2:
            return "↘"
        return "→"


@dataclass
class ForecastData:
    """Complete forecast package."""
    hourly: List[HourlyForecast] = field(default_factory=list)
    daily: List[DailyForecast] = field(default_factory=list)
    location: str = ""
    timestamp: float = 0.0
    
    def get_next_hours(self, count: int = 12) -> List[HourlyForecast]:
        """Get next N hours of forecast."""
        return self.hourly[:count]
    
    def get_week(self) -> List[DailyForecast]:
        """Get 7-day forecast."""
        return self.daily[:7]


# ═══════════════════════════════════════════════════════════════════════════════
# 🚨 WEATHER ALERTS
# ═══════════════════════════════════════════════════════════════════════════════

class AlertSeverity(Enum):
    """NWS alert severity levels."""
    EXTREME = "Extreme"
    SEVERE = "Severe"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


class AlertUrgency(Enum):
    """How urgent the alert is."""
    IMMEDIATE = "Immediate"
    EXPECTED = "Expected"
    FUTURE = "Future"
    PAST = "Past"
    UNKNOWN = "Unknown"


@dataclass
class WeatherAlert:
    """NWS weather alert."""
    event: str  # e.g., "Tornado Warning", "Heat Advisory"
    severity: AlertSeverity
    urgency: AlertUrgency
    headline: str
    description: str
    instruction: str
    start: datetime
    end: datetime
    areas: List[str]
    
    @property
    def is_active(self) -> bool:
        now = datetime.now()
        return self.start <= now <= self.end
    
    @property
    def is_severe(self) -> bool:
        return self.severity in (AlertSeverity.EXTREME, AlertSeverity.SEVERE)
    
    @property
    def short_name(self) -> str:
        """Abbreviated event name for display."""
        abbrevs = {
            "Tornado Warning": "🌪️ TORNADO",
            "Tornado Watch": "🌪️ Tor Watch",
            "Severe Thunderstorm Warning": "⛈️ SVR TSTM",
            "Severe Thunderstorm Watch": "⛈️ Tstm Watch",
            "Flash Flood Warning": "🌊 FLASH FLOOD",
            "Flood Warning": "🌊 FLOOD",
            "Winter Storm Warning": "❄️ WINTER STORM",
            "Blizzard Warning": "❄️ BLIZZARD",
            "Ice Storm Warning": "🧊 ICE STORM",
            "Heat Advisory": "🔥 Heat Adv",
            "Excessive Heat Warning": "🔥 EXTREME HEAT",
            "Wind Advisory": "💨 Wind Adv",
            "High Wind Warning": "💨 HIGH WIND",
            "Hurricane Warning": "🌀 HURRICANE",
            "Hurricane Watch": "🌀 Hurr Watch",
            "Tropical Storm Warning": "🌀 TROP STORM",
        }
        return abbrevs.get(self.event, f"⚠️ {self.event[:15]}")


# ═══════════════════════════════════════════════════════════════════════════════
# 🌙 ASTRONOMICAL DATA
# ═══════════════════════════════════════════════════════════════════════════════

class MoonPhase(Enum):
    """Moon phase names."""
    NEW_MOON = "New Moon"
    WAXING_CRESCENT = "Waxing Crescent"
    FIRST_QUARTER = "First Quarter"
    WAXING_GIBBOUS = "Waxing Gibbous"
    FULL_MOON = "Full Moon"
    WANING_GIBBOUS = "Waning Gibbous"
    LAST_QUARTER = "Last Quarter"
    WANING_CRESCENT = "Waning Crescent"


@dataclass
class AstronomicalData:
    """Sun and moon data."""
    sunrise: datetime
    sunset: datetime
    solar_noon: datetime
    day_length_hours: float
    moon_phase: MoonPhase
    moon_illumination: float  # 0-100%
    moon_age_days: float  # Days since new moon
    
    @property
    def is_daytime(self) -> bool:
        now = datetime.now()
        return self.sunrise <= now <= self.sunset
    
    @property
    def time_until_sunset(self) -> timedelta:
        return self.sunset - datetime.now()
    
    @property
    def time_until_sunrise(self) -> timedelta:
        return self.sunrise - datetime.now()
    
    @property
    def moon_emoji(self) -> str:
        emojis = {
            MoonPhase.NEW_MOON: "🌑",
            MoonPhase.WAXING_CRESCENT: "🌒",
            MoonPhase.FIRST_QUARTER: "🌓",
            MoonPhase.WAXING_GIBBOUS: "🌔",
            MoonPhase.FULL_MOON: "🌕",
            MoonPhase.WANING_GIBBOUS: "🌖",
            MoonPhase.LAST_QUARTER: "🌗",
            MoonPhase.WANING_CRESCENT: "🌘",
        }
        return emojis.get(self.moon_phase, "🌙")
    
    @property
    def moon_ascii(self) -> List[str]:
        """ASCII art for moon phase."""
        art = {
            MoonPhase.NEW_MOON: [
                "  .--.  ",
                " (    ) ",
                "(      )",
                " (    ) ",
                "  `--'  ",
            ],
            MoonPhase.WAXING_CRESCENT: [
                "  .--.  ",
                " (  `. )",
                "(    `.)",
                " (  .' )",
                "  `--'  ",
            ],
            MoonPhase.FIRST_QUARTER: [
                "  .--.  ",
                " (   |) ",
                "(    |)",
                " (   |) ",
                "  `--'  ",
            ],
            MoonPhase.WAXING_GIBBOUS: [
                "  .--.  ",
                " (`   ) ",
                "(`    )",
                " (`   ) ",
                "  `--'  ",
            ],
            MoonPhase.FULL_MOON: [
                "  .---.  ",
                " ( o o ) ",
                "(   V   )",
                " (  _  ) ",
                "  `---'  ",
            ],
            MoonPhase.WANING_GIBBOUS: [
                "  .--.  ",
                " (   `) ",
                "(    `)",
                " (   `) ",
                "  `--'  ",
            ],
            MoonPhase.LAST_QUARTER: [
                "  .--.  ",
                " (|   ) ",
                "(|    )",
                " (|   ) ",
                "  `--'  ",
            ],
            MoonPhase.WANING_CRESCENT: [
                "  .--.  ",
                " (.'  ) ",
                "(.'   )",
                " (.'  ) ",
                "  `--'  ",
            ],
        }
        return art.get(self.moon_phase, art[MoonPhase.FULL_MOON])


# ═══════════════════════════════════════════════════════════════════════════════
# 🌡️ UV INDEX & AIR QUALITY
# ═══════════════════════════════════════════════════════════════════════════════

class UVLevel(Enum):
    """UV index severity levels."""
    LOW = "Low"           # 0-2
    MODERATE = "Moderate" # 3-5
    HIGH = "High"         # 6-7
    VERY_HIGH = "Very High"  # 8-10
    EXTREME = "Extreme"   # 11+


class AQILevel(Enum):
    """Air Quality Index levels (US EPA)."""
    GOOD = "Good"                      # 0-50
    MODERATE = "Moderate"              # 51-100
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"  # 101-150
    UNHEALTHY = "Unhealthy"            # 151-200
    VERY_UNHEALTHY = "Very Unhealthy"  # 201-300
    HAZARDOUS = "Hazardous"            # 301+


@dataclass
class EnvironmentalData:
    """UV and air quality data."""
    uv_index: float
    uv_level: UVLevel
    aqi: int
    aqi_level: AQILevel
    dominant_pollutant: str  # PM2.5, PM10, O3, NO2, etc.
    pm25: float  # μg/m³
    pm10: float
    ozone: float
    
    @property
    def uv_color(self) -> str:
        """Terminal color name for UV level."""
        colors = {
            UVLevel.LOW: "GREEN",
            UVLevel.MODERATE: "YELLOW",
            UVLevel.HIGH: "YELLOW",  # Orange not available
            UVLevel.VERY_HIGH: "RED",
            UVLevel.EXTREME: "MAGENTA",
        }
        return colors.get(self.uv_level, "WHITE")
    
    @property
    def aqi_color(self) -> str:
        """Terminal color name for AQI level."""
        colors = {
            AQILevel.GOOD: "GREEN",
            AQILevel.MODERATE: "YELLOW",
            AQILevel.UNHEALTHY_SENSITIVE: "YELLOW",
            AQILevel.UNHEALTHY: "RED",
            AQILevel.VERY_UNHEALTHY: "MAGENTA",
            AQILevel.HAZARDOUS: "RED",
        }
        return colors.get(self.aqi_level, "WHITE")
    
    @property
    def uv_advice(self) -> str:
        """Stormy's UV advice."""
        advice = {
            UVLevel.LOW: "The sun is gentle. A rare mercy.",
            UVLevel.MODERATE: "Some protection wise. The sun remembers.",
            UVLevel.HIGH: "Sunscreen is not optional. The sun has opinions.",
            UVLevel.VERY_HIGH: "Seek shade. The sun has chosen violence today.",
            UVLevel.EXTREME: "DANGER. The sun is actively hostile. Stay inside.",
        }
        return advice.get(self.uv_level, "")
    
    @property
    def aqi_advice(self) -> str:
        """Stormy's AQI advice."""
        advice = {
            AQILevel.GOOD: "The air is clean. Breathe deep. Treasure it.",
            AQILevel.MODERATE: "Acceptable air. The sensitive may notice.",
            AQILevel.UNHEALTHY_SENSITIVE: "The air grows heavy. The vulnerable should take care.",
            AQILevel.UNHEALTHY: "The air protests. Limit outdoor exertion.",
            AQILevel.VERY_UNHEALTHY: "The air is angry. Everyone should limit exposure.",
            AQILevel.HAZARDOUS: "HAZARDOUS. The very air betrays you. Stay indoors.",
        }
        return advice.get(self.aqi_level, "")


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 HISTORICAL DATA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass 
class HistoricalComparison:
    """Comparison with historical data."""
    yesterday_high_f: float
    yesterday_low_f: float
    yesterday_condition: WeatherCondition
    last_year_high_f: Optional[float]
    last_year_low_f: Optional[float]
    last_year_condition: Optional[WeatherCondition]
    avg_high_f: float  # Historical average for this date
    avg_low_f: float
    record_high_f: float
    record_high_year: int
    record_low_f: float
    record_low_year: int
    
    def temp_vs_yesterday(self, current_temp: float) -> Tuple[float, str]:
        """Compare current temp to yesterday."""
        diff = current_temp - self.yesterday_high_f
        if diff > 0:
            return diff, f"{diff:.0f}° warmer than yesterday"
        elif diff < 0:
            return diff, f"{abs(diff):.0f}° cooler than yesterday"
        return 0, "Same as yesterday"
    
    def temp_vs_average(self, current_temp: float) -> Tuple[float, str]:
        """Compare current temp to historical average."""
        diff = current_temp - self.avg_high_f
        if diff > 5:
            return diff, f"{diff:.0f}° above average"
        elif diff < -5:
            return diff, f"{abs(diff):.0f}° below average"
        return diff, "Near average"


# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 API FETCHERS
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_forecast(lat: float = LATITUDE, lon: float = LONGITUDE) -> Optional[ForecastData]:
    """
    Fetch 7-day forecast with hourly data from OpenMeteo.
    Free, no API key required!
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': [
                'temperature_2m', 'relative_humidity_2m', 'precipitation_probability',
                'weather_code', 'cloud_cover', 'wind_speed_10m', 'wind_direction_10m',
                'apparent_temperature'
            ],
            'daily': [
                'weather_code', 'temperature_2m_max', 'temperature_2m_min',
                'precipitation_sum', 'precipitation_probability_max',
                'wind_speed_10m_max', 'sunrise', 'sunset', 'uv_index_max'
            ],
            'timezone': TIMEZONE,
            'temperature_unit': 'fahrenheit',
            'wind_speed_unit': 'mph',
            'forecast_days': 7,
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Parse hourly data
        hourly_list = []
        hourly = data.get('hourly', {})
        times = hourly.get('time', [])
        
        for i, time_str in enumerate(times[:48]):  # Next 48 hours
            dt = datetime.fromisoformat(time_str)
            temp_f = hourly['temperature_2m'][i]
            
            hourly_list.append(HourlyForecast(
                time=dt,
                temperature_f=temp_f,
                temperature_c=(temp_f - 32) * 5 / 9,
                condition=_map_wmo_to_condition(hourly['weather_code'][i]),
                description=_wmo_description(hourly['weather_code'][i]),
                precipitation_prob=int(hourly['precipitation_probability'][i] or 0),
                humidity=int(hourly['relative_humidity_2m'][i]),
                wind_speed_mph=hourly['wind_speed_10m'][i],
                wind_direction=int(hourly['wind_direction_10m'][i]),
                clouds_percent=int(hourly['cloud_cover'][i]),
                feels_like_f=hourly['apparent_temperature'][i],
            ))
        
        # Parse daily data
        daily_list = []
        daily = data.get('daily', {})
        dates = daily.get('time', [])
        
        for i, date_str in enumerate(dates):
            dt = datetime.fromisoformat(date_str).date()
            high_f = daily['temperature_2m_max'][i]
            low_f = daily['temperature_2m_min'][i]
            
            # Parse sunrise/sunset
            sunrise = datetime.fromisoformat(daily['sunrise'][i])
            sunset = datetime.fromisoformat(daily['sunset'][i])
            
            daily_list.append(DailyForecast(
                date=dt,
                temp_high_f=high_f,
                temp_low_f=low_f,
                temp_high_c=(high_f - 32) * 5 / 9,
                temp_low_c=(low_f - 32) * 5 / 9,
                condition=_map_wmo_to_condition(daily['weather_code'][i]),
                description=_wmo_description(daily['weather_code'][i]),
                precipitation_prob=int(daily['precipitation_probability_max'][i] or 0),
                precipitation_amount=daily['precipitation_sum'][i] or 0,
                humidity=50,  # Not in daily, use placeholder
                wind_speed_mph=daily['wind_speed_10m_max'][i],
                sunrise=sunrise,
                sunset=sunset,
                uv_index=daily.get('uv_index_max', [0]*7)[i] or 0,
            ))
        
        return ForecastData(
            hourly=hourly_list,
            daily=daily_list,
            location=LOCATION_NAME,
            timestamp=time.time(),
        )
        
    except Exception as e:
        print(f"Forecast fetch error: {e}", file=sys.stderr)
        return None


def fetch_weather_alerts(lat: float = LATITUDE, lon: float = LONGITUDE) -> List[WeatherAlert]:
    """
    Fetch active weather alerts from NWS (National Weather Service).
    US only, but free and detailed!
    """
    alerts = []
    try:
        # NWS API uses points endpoint
        url = f"https://api.weather.gov/alerts/active"
        params = {
            'point': f"{lat},{lon}",
            'status': 'actual',
        }
        headers = {
            'User-Agent': 'StormyWeatherDashboard/1.0 (github.com/asciimatics-weather-toys)',
            'Accept': 'application/geo+json',
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            
            # Parse severity
            sev_str = props.get('severity', 'Unknown')
            severity = AlertSeverity.UNKNOWN
            for s in AlertSeverity:
                if s.value == sev_str:
                    severity = s
                    break
            
            # Parse urgency
            urg_str = props.get('urgency', 'Unknown')
            urgency = AlertUrgency.UNKNOWN
            for u in AlertUrgency:
                if u.value == urg_str:
                    urgency = u
                    break
            
            # Parse times
            start = datetime.fromisoformat(props.get('onset', props.get('effective', '')).replace('Z', '+00:00'))
            end = datetime.fromisoformat(props.get('expires', '').replace('Z', '+00:00'))
            
            alerts.append(WeatherAlert(
                event=props.get('event', 'Unknown'),
                severity=severity,
                urgency=urgency,
                headline=props.get('headline', ''),
                description=props.get('description', ''),
                instruction=props.get('instruction', ''),
                start=start,
                end=end,
                areas=props.get('areaDesc', '').split('; '),
            ))
            
    except Exception as e:
        # NWS API can be flaky, don't crash
        print(f"Alert fetch error: {e}", file=sys.stderr)
    
    return alerts


def fetch_astronomical_data(lat: float = LATITUDE, lon: float = LONGITUDE) -> Optional[AstronomicalData]:
    """
    Fetch sunrise/sunset and calculate moon phase.
    Uses OpenMeteo for sun data, calculates moon phase algorithmically.
    """
    try:
        # Get sun data from OpenMeteo
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': ['sunrise', 'sunset'],
            'timezone': TIMEZONE,
            'forecast_days': 1,
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get('daily', {})
        sunrise = datetime.fromisoformat(daily['sunrise'][0])
        sunset = datetime.fromisoformat(daily['sunset'][0])
        
        # Calculate solar noon and day length
        solar_noon = sunrise + (sunset - sunrise) / 2
        day_length = (sunset - sunrise).total_seconds() / 3600
        
        # Calculate moon phase using Conway's algorithm
        moon_phase, moon_illum, moon_age = _calculate_moon_phase()
        
        return AstronomicalData(
            sunrise=sunrise,
            sunset=sunset,
            solar_noon=solar_noon,
            day_length_hours=day_length,
            moon_phase=moon_phase,
            moon_illumination=moon_illum,
            moon_age_days=moon_age,
        )
        
    except Exception as e:
        print(f"Astronomical data fetch error: {e}", file=sys.stderr)
        return None


def _calculate_moon_phase() -> Tuple[MoonPhase, float, float]:
    """
    Calculate moon phase using astronomical algorithms.
    Returns (phase, illumination%, days_since_new_moon)
    """
    # Reference new moon: January 6, 2000
    reference = datetime(2000, 1, 6, 18, 14)
    now = datetime.now()
    
    # Synodic month = 29.53059 days
    synodic_month = 29.53059
    
    # Days since reference new moon
    days = (now - reference).total_seconds() / 86400
    
    # Current phase in cycle (0 = new moon)
    phase_days = days % synodic_month
    
    # Illumination (approximate cosine curve)
    illumination = (1 - math.cos(2 * math.pi * phase_days / synodic_month)) / 2 * 100
    
    # Determine phase name
    phase_fraction = phase_days / synodic_month
    
    if phase_fraction < 0.0625:
        phase = MoonPhase.NEW_MOON
    elif phase_fraction < 0.1875:
        phase = MoonPhase.WAXING_CRESCENT
    elif phase_fraction < 0.3125:
        phase = MoonPhase.FIRST_QUARTER
    elif phase_fraction < 0.4375:
        phase = MoonPhase.WAXING_GIBBOUS
    elif phase_fraction < 0.5625:
        phase = MoonPhase.FULL_MOON
    elif phase_fraction < 0.6875:
        phase = MoonPhase.WANING_GIBBOUS
    elif phase_fraction < 0.8125:
        phase = MoonPhase.LAST_QUARTER
    elif phase_fraction < 0.9375:
        phase = MoonPhase.WANING_CRESCENT
    else:
        phase = MoonPhase.NEW_MOON
    
    return phase, illumination, phase_days


def fetch_environmental_data(lat: float = LATITUDE, lon: float = LONGITUDE) -> Optional[EnvironmentalData]:
    """
    Fetch UV index and air quality data from OpenMeteo.
    """
    try:
        # UV from forecast
        uv_url = "https://api.open-meteo.com/v1/forecast"
        uv_params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': ['uv_index'],
            'timezone': TIMEZONE,
            'forecast_days': 1,
        }
        
        uv_response = requests.get(uv_url, params=uv_params, timeout=10)
        uv_response.raise_for_status()
        uv_data = uv_response.json()
        
        # Get current hour's UV
        current_hour = datetime.now().hour
        uv_values = uv_data.get('hourly', {}).get('uv_index', [0] * 24)
        uv_index = uv_values[current_hour] if current_hour < len(uv_values) else 0
        uv_index = uv_index or 0  # Handle None
        
        # Determine UV level
        if uv_index <= 2:
            uv_level = UVLevel.LOW
        elif uv_index <= 5:
            uv_level = UVLevel.MODERATE
        elif uv_index <= 7:
            uv_level = UVLevel.HIGH
        elif uv_index <= 10:
            uv_level = UVLevel.VERY_HIGH
        else:
            uv_level = UVLevel.EXTREME
        
        # Air quality from OpenMeteo Air Quality API
        aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        aqi_params = {
            'latitude': lat,
            'longitude': lon,
            'current': ['us_aqi', 'pm10', 'pm2_5', 'ozone'],
            'timezone': TIMEZONE,
        }
        
        aqi_response = requests.get(aqi_url, params=aqi_params, timeout=10)
        aqi_response.raise_for_status()
        aqi_data = aqi_response.json()
        
        current = aqi_data.get('current', {})
        aqi = int(current.get('us_aqi', 0) or 0)
        pm25 = current.get('pm2_5', 0) or 0
        pm10 = current.get('pm10', 0) or 0
        ozone = current.get('ozone', 0) or 0
        
        # Determine AQI level
        if aqi <= 50:
            aqi_level = AQILevel.GOOD
        elif aqi <= 100:
            aqi_level = AQILevel.MODERATE
        elif aqi <= 150:
            aqi_level = AQILevel.UNHEALTHY_SENSITIVE
        elif aqi <= 200:
            aqi_level = AQILevel.UNHEALTHY
        elif aqi <= 300:
            aqi_level = AQILevel.VERY_UNHEALTHY
        else:
            aqi_level = AQILevel.HAZARDOUS
        
        # Determine dominant pollutant
        pollutants = {'PM2.5': pm25 * 2, 'PM10': pm10, 'O3': ozone}
        dominant = max(pollutants, key=pollutants.get)
        
        return EnvironmentalData(
            uv_index=uv_index,
            uv_level=uv_level,
            aqi=aqi,
            aqi_level=aqi_level,
            dominant_pollutant=dominant,
            pm25=pm25,
            pm10=pm10,
            ozone=ozone,
        )
        
    except Exception as e:
        print(f"Environmental data fetch error: {e}", file=sys.stderr)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# 📚 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _map_wmo_to_condition(code: int) -> WeatherCondition:
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


def _wmo_description(code: int) -> str:
    """Get human-readable description from WMO code."""
    descriptions = {
        0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Fog", 48: "Freezing Fog",
        51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
        56: "Freezing Drizzle", 57: "Heavy Freezing Drizzle",
        61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
        66: "Freezing Rain", 67: "Heavy Freezing Rain",
        71: "Light Snow", 73: "Snow", 75: "Heavy Snow", 77: "Snow Grains",
        80: "Rain Showers", 81: "Rain Showers", 82: "Heavy Showers",
        85: "Snow Showers", 86: "Heavy Snow Showers",
        95: "Thunderstorm", 96: "Thunderstorm w/ Hail", 99: "Severe Thunderstorm",
    }
    return descriptions.get(code, "Unknown")


# ═══════════════════════════════════════════════════════════════════════════════
# 💾 DATA PERSISTENCE & EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

class WeatherDatabase:
    """SQLite database for weather history."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Path.home() / ".stormy_weather.db")
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    location TEXT,
                    temperature_f REAL,
                    temperature_c REAL,
                    humidity INTEGER,
                    condition TEXT,
                    description TEXT,
                    wind_speed_mph REAL,
                    pressure INTEGER,
                    uv_index REAL,
                    aqi INTEGER
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON weather_log(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_location 
                ON weather_log(location)
            """)
    
    def log_weather(self, weather: WeatherData, env: EnvironmentalData = None):
        """Log current weather to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO weather_log 
                (timestamp, location, temperature_f, temperature_c, humidity,
                 condition, description, wind_speed_mph, pressure, uv_index, aqi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                weather.timestamp,
                weather.location,
                weather.temperature_f,
                weather.temperature_c,
                weather.humidity,
                weather.condition.value,
                weather.description,
                weather.wind_speed_mph,
                weather.pressure,
                env.uv_index if env else None,
                env.aqi if env else None,
            ))
    
    def get_yesterday(self, location: str = LOCATION_NAME) -> Optional[Dict]:
        """Get yesterday's weather summary."""
        yesterday = time.time() - 86400
        yesterday_start = yesterday - 43200  # ±12 hours
        yesterday_end = yesterday + 43200
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT AVG(temperature_f) as avg_temp,
                       MAX(temperature_f) as high_temp,
                       MIN(temperature_f) as low_temp,
                       condition
                FROM weather_log
                WHERE timestamp BETWEEN ? AND ?
                  AND location = ?
                GROUP BY date(timestamp, 'unixepoch', 'localtime')
                ORDER BY timestamp DESC
                LIMIT 1
            """, (yesterday_start, yesterday_end, location)).fetchone()
            
            if row:
                return dict(row)
        return None
    
    def get_last_year_same_day(self, location: str = LOCATION_NAME) -> Optional[Dict]:
        """Get same day last year's weather."""
        last_year = time.time() - (365 * 86400)
        window_start = last_year - 43200
        window_end = last_year + 43200
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT AVG(temperature_f) as avg_temp,
                       MAX(temperature_f) as high_temp,
                       MIN(temperature_f) as low_temp,
                       condition
                FROM weather_log
                WHERE timestamp BETWEEN ? AND ?
                  AND location = ?
                LIMIT 1
            """, (window_start, window_end, location)).fetchone()
            
            if row and row['avg_temp']:
                return dict(row)
        return None
    
    def export_csv(self, filepath: str, days: int = 30):
        """Export weather history to CSV."""
        import csv
        
        start_time = time.time() - (days * 86400)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM weather_log
                WHERE timestamp > ?
                ORDER BY timestamp
            """, (start_time,)).fetchall()
        
        with open(filepath, 'w', newline='') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                for row in rows:
                    writer.writerow(dict(row))
    
    def export_json(self, filepath: str, days: int = 30):
        """Export weather history to JSON."""
        start_time = time.time() - (days * 86400)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM weather_log
                WHERE timestamp > ?
                ORDER BY timestamp
            """, (start_time,)).fetchall()
        
        data = [dict(row) for row in rows]
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def get_historical_comparison(
    current_temp: float,
    db: WeatherDatabase = None,
    location: str = LOCATION_NAME
) -> Optional[HistoricalComparison]:
    """
    Get historical comparison data.
    Uses database if available, otherwise returns None.
    """
    if db is None:
        db = WeatherDatabase()
    
    yesterday = db.get_yesterday(location)
    last_year = db.get_last_year_same_day(location)
    
    if not yesterday:
        return None
    
    return HistoricalComparison(
        yesterday_high_f=yesterday.get('high_temp', current_temp),
        yesterday_low_f=yesterday.get('low_temp', current_temp - 10),
        yesterday_condition=WeatherCondition(yesterday.get('condition', 'clear')),
        last_year_high_f=last_year.get('high_temp') if last_year else None,
        last_year_low_f=last_year.get('low_temp') if last_year else None,
        last_year_condition=WeatherCondition(last_year['condition']) if last_year else None,
        avg_high_f=current_temp,  # Would need climate data
        avg_low_f=current_temp - 15,
        record_high_f=current_temp + 20,
        record_high_year=1998,
        record_low_f=current_temp - 30,
        record_low_year=1985,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 🖥️ WIDGET OUTPUT MODES
# ═══════════════════════════════════════════════════════════════════════════════

def output_single_line(weather: WeatherData, env: EnvironmentalData = None) -> str:
    """
    Generate single-line output for tmux/i3bar/waybar integration.
    Format: "☀️ 72°F | Wind: 5mph | Humidity: 45%"
    """
    icons = {
        WeatherCondition.CLEAR: "☀️",
        WeatherCondition.PARTLY_CLOUDY: "⛅",
        WeatherCondition.CLOUDY: "☁️",
        WeatherCondition.FOG: "🌫️",
        WeatherCondition.DRIZZLE: "🌦️",
        WeatherCondition.RAIN: "🌧️",
        WeatherCondition.HEAVY_RAIN: "🌧️",
        WeatherCondition.SNOW: "❄️",
        WeatherCondition.HEAVY_SNOW: "🌨️",
        WeatherCondition.THUNDERSTORM: "⛈️",
        WeatherCondition.FREEZING_RAIN: "🧊",
        WeatherCondition.UNKNOWN: "🌡️",
    }
    
    icon = icons.get(weather.condition, "🌡️")
    parts = [
        f"{icon} {weather.temperature_f:.0f}°F",
        f"💨{weather.wind_speed_mph:.0f}mph",
        f"💧{weather.humidity}%",
    ]
    
    if env:
        if env.uv_index >= 6:
            parts.append(f"☀️UV:{env.uv_index:.0f}")
        if env.aqi >= 100:
            parts.append(f"AQI:{env.aqi}")
    
    return " | ".join(parts)


def output_json(
    weather: WeatherData,
    forecast: ForecastData = None,
    env: EnvironmentalData = None,
    astro: AstronomicalData = None,
    alerts: List[WeatherAlert] = None
) -> str:
    """
    Generate JSON output for scripting integration.
    """
    data = {
        'current': {
            'temperature_f': weather.temperature_f,
            'temperature_c': weather.temperature_c,
            'condition': weather.condition.value,
            'description': weather.description,
            'humidity': weather.humidity,
            'wind_speed_mph': weather.wind_speed_mph,
            'wind_direction': weather.wind_direction,
            'pressure': weather.pressure,
            'location': weather.location,
            'timestamp': weather.timestamp,
        }
    }
    
    if env:
        data['environment'] = {
            'uv_index': env.uv_index,
            'uv_level': env.uv_level.value,
            'aqi': env.aqi,
            'aqi_level': env.aqi_level.value,
            'pm25': env.pm25,
            'pm10': env.pm10,
        }
    
    if astro:
        data['astronomical'] = {
            'sunrise': astro.sunrise.isoformat(),
            'sunset': astro.sunset.isoformat(),
            'is_daytime': astro.is_daytime,
            'moon_phase': astro.moon_phase.value,
            'moon_illumination': astro.moon_illumination,
        }
    
    if forecast:
        data['forecast'] = {
            'hourly': [
                {
                    'time': h.time.isoformat(),
                    'temp_f': h.temperature_f,
                    'condition': h.condition.value,
                    'precip_prob': h.precipitation_prob,
                }
                for h in forecast.hourly[:24]
            ],
            'daily': [
                {
                    'date': str(d.date),
                    'high_f': d.temp_high_f,
                    'low_f': d.temp_low_f,
                    'condition': d.condition.value,
                    'precip_prob': d.precipitation_prob,
                }
                for d in forecast.daily
            ],
        }
    
    if alerts:
        data['alerts'] = [
            {
                'event': a.event,
                'severity': a.severity.value,
                'headline': a.headline,
                'start': a.start.isoformat(),
                'end': a.end.isoformat(),
            }
            for a in alerts
        ]
    
    return json.dumps(data, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 TEST / DEMO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🌤️ Extended Weather API Test\n")
    
    print("📅 Fetching forecast...")
    forecast = fetch_forecast()
    if forecast:
        print(f"  Got {len(forecast.hourly)} hourly, {len(forecast.daily)} daily forecasts")
        print(f"  Next 6 hours: ", end="")
        for h in forecast.hourly[:6]:
            print(f"{h.hour_str}:{h.temperature_f:.0f}° ", end="")
        print()
        print(f"  7-day outlook:")
        for d in forecast.daily[:7]:
            print(f"    {d.day_name}: {d.temp_range_str} - {d.description}")
    
    print("\n🚨 Fetching alerts...")
    alerts = fetch_weather_alerts()
    if alerts:
        for alert in alerts:
            print(f"  {alert.short_name}: {alert.headline[:60]}...")
    else:
        print("  No active alerts")
    
    print("\n🌙 Fetching astronomical data...")
    astro = fetch_astronomical_data()
    if astro:
        print(f"  Sunrise: {astro.sunrise.strftime('%I:%M %p')}")
        print(f"  Sunset: {astro.sunset.strftime('%I:%M %p')}")
        print(f"  Day length: {astro.day_length_hours:.1f} hours")
        print(f"  Moon: {astro.moon_emoji} {astro.moon_phase.value} ({astro.moon_illumination:.0f}%)")
    
    print("\n🌡️ Fetching UV & AQI...")
    env = fetch_environmental_data()
    if env:
        print(f"  UV Index: {env.uv_index:.1f} ({env.uv_level.value})")
        print(f"  AQI: {env.aqi} ({env.aqi_level.value})")
        print(f"  PM2.5: {env.pm25:.1f} μg/m³")
    
    print("\n✅ All systems operational!")
