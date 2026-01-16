"""
Configuration Manager
=====================
Enhanced configuration system with YAML support, themes, and multiple locations.

Features:
- YAML configuration file (human-readable)
- Multiple saved locations
- Color themes (Nord, Dracula, Solarized, etc.)
- Unit preferences (°F/°C, mph/km/h)
- Display customization
- Keyboard shortcuts

Usage:
    from config_manager import Config
    config = Config()
    config.load()
    print(config.current_location)
    config.switch_location("Tokyo")
"""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

# Try YAML, fall back to JSON
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 COLOR THEMES
# ═══════════════════════════════════════════════════════════════════════════════

class ThemeName(Enum):
    """Available color themes."""
    DEFAULT = "default"
    NORD = "nord"
    DRACULA = "dracula"
    SOLARIZED_DARK = "solarized_dark"
    SOLARIZED_LIGHT = "solarized_light"
    GRUVBOX = "gruvbox"
    MONOKAI = "monokai"
    CYBERPUNK = "cyberpunk"
    RETRO = "retro"


@dataclass
class ColorTheme:
    """Color theme definition using terminal color indices."""
    name: str
    # Primary colors (0-7 standard terminal colors)
    frost: int = 6       # Cyan - cold/ice
    snow: int = 7        # White - snow/clean
    sun: int = 3         # Yellow - sun/warm
    danger: int = 1      # Red - alerts/hot
    nature: int = 2      # Green - nature/good
    magic: int = 5       # Magenta - special effects
    muted: int = 4       # Blue - clouds/calm
    text: int = 7        # White - default text
    
    # Semantic colors
    primary: int = 6     # Main accent
    secondary: int = 4   # Secondary accent
    accent: int = 5      # Highlights
    background: int = 0  # Background (for reference)
    
    # Weather-specific
    rain: int = 4        # Blue
    lightning: int = 3   # Yellow
    fog: int = 4         # Dim blue
    clear_day: int = 3   # Yellow
    clear_night: int = 4 # Blue
    cloud: int = 7       # White/gray


# Predefined themes
THEMES: Dict[ThemeName, ColorTheme] = {
    ThemeName.DEFAULT: ColorTheme(
        name="Default",
        frost=6, snow=7, sun=3, danger=1, nature=2, magic=5, muted=4,
    ),
    ThemeName.NORD: ColorTheme(
        name="Nord",
        frost=6, snow=7, sun=3, danger=1, nature=2, magic=5, muted=4,
        primary=6, secondary=4, accent=5,
        rain=4, lightning=3, clear_day=3, clear_night=4,
    ),
    ThemeName.DRACULA: ColorTheme(
        name="Dracula",
        frost=6, snow=7, sun=3, danger=1, nature=2, magic=5, muted=4,
        primary=5, secondary=6, accent=1,
        rain=5, lightning=3, clear_day=3, clear_night=5,
    ),
    ThemeName.SOLARIZED_DARK: ColorTheme(
        name="Solarized Dark",
        frost=6, snow=7, sun=3, danger=1, nature=2, magic=5, muted=4,
        primary=4, secondary=6, accent=3,
    ),
    ThemeName.SOLARIZED_LIGHT: ColorTheme(
        name="Solarized Light",
        frost=6, snow=0, sun=3, danger=1, nature=2, magic=5, muted=4,
        text=0,  # Dark text on light
    ),
    ThemeName.GRUVBOX: ColorTheme(
        name="Gruvbox",
        frost=6, snow=7, sun=3, danger=1, nature=2, magic=5, muted=4,
        primary=3, secondary=2, accent=1,
    ),
    ThemeName.MONOKAI: ColorTheme(
        name="Monokai",
        frost=6, snow=7, sun=3, danger=1, nature=2, magic=5, muted=4,
        primary=5, secondary=2, accent=3,
    ),
    ThemeName.CYBERPUNK: ColorTheme(
        name="Cyberpunk",
        frost=6, snow=7, sun=3, danger=1, nature=6, magic=5, muted=4,
        primary=5, secondary=6, accent=1,
        lightning=5, clear_night=5,
    ),
    ThemeName.RETRO: ColorTheme(
        name="Retro",
        frost=6, snow=7, sun=3, danger=1, nature=2, magic=5, muted=4,
        primary=2, secondary=3, accent=6,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# 📍 LOCATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Location:
    """Saved location with coordinates."""
    name: str
    display_name: str
    latitude: float
    longitude: float
    timezone: str = "America/New_York"
    country: str = ""
    state: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        return cls(**data)
    
    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION DATACLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class TemperatureUnit(Enum):
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"


class SpeedUnit(Enum):
    MPH = "mph"
    KMH = "km/h"
    MS = "m/s"
    KNOTS = "knots"


class PressureUnit(Enum):
    HPA = "hPa"
    INHG = "inHg"
    MB = "mb"


@dataclass
class DisplaySettings:
    """Display customization options."""
    show_forecast: bool = True
    show_hourly: bool = True
    forecast_days: int = 7
    forecast_hours: int = 12
    show_uv_index: bool = True
    show_aqi: bool = True
    show_moon_phase: bool = True
    show_sunrise_sunset: bool = True
    show_alerts: bool = True
    show_historical: bool = True
    show_mascot: bool = True
    show_particles: bool = True
    particle_density: float = 1.0  # Multiplier
    animation_fps: int = 30
    compact_mode: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DisplaySettings':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UnitSettings:
    """Unit preferences."""
    temperature: TemperatureUnit = TemperatureUnit.FAHRENHEIT
    speed: SpeedUnit = SpeedUnit.MPH
    pressure: PressureUnit = PressureUnit.HPA
    time_24h: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UnitSettings':
        return cls(
            temperature=TemperatureUnit(data.get('temperature', 'fahrenheit')),
            speed=SpeedUnit(data.get('speed', 'mph')),
            pressure=PressureUnit(data.get('pressure', 'hPa')),
            time_24h=data.get('time_24h', False),
        )
    
    def to_dict(self) -> dict:
        return {
            'temperature': self.temperature.value,
            'speed': self.speed.value,
            'pressure': self.pressure.value,
            'time_24h': self.time_24h,
        }


@dataclass
class KeyBindings:
    """Keyboard shortcut configuration."""
    quit: str = 'q'
    refresh: str = 'r'
    toggle_units: str = 'u'
    switch_location: str = 'l'
    next_location: str = 'n'
    prev_location: str = 'p'
    toggle_forecast: str = 'f'
    toggle_compact: str = 'c'
    screenshot: str = 's'
    help: str = '?'
    toggle_particles: str = 'a'  # Animation
    cycle_theme: str = 't'
    export_data: str = 'e'
    
    @classmethod
    def from_dict(cls, data: dict) -> 'KeyBindings':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class APISettings:
    """API configuration."""
    openweathermap_key: str = ""
    openweathermap_city_id: str = ""
    cache_max_age: int = 300  # seconds
    cache_file: str = "/tmp/asciimatics_weather_cache.json"
    request_timeout: int = 10
    
    @classmethod
    def from_dict(cls, data: dict) -> 'APISettings':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass 
class PersonalitySettings:
    """Stormy's personality configuration."""
    enabled: bool = True
    snark_level: float = 0.7  # 0-1
    wisdom_level: float = 0.6
    reference_frequency: float = 0.8  # Pop culture references
    meta_comments: bool = True  # Comments about the code/physics
    achievements_enabled: bool = True
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PersonalitySettings':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
# 🎛️ MAIN CONFIGURATION CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Config:
    """
    Main configuration manager.
    
    Handles loading, saving, and accessing all configuration.
    Supports both YAML and JSON formats.
    """
    
    DEFAULT_CONFIG_PATH = Path.home() / ".config" / "stormy" / "config.yaml"
    FALLBACK_CONFIG_PATH = Path.home() / ".stormy_config.json"
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else self._find_config_path()
        
        # Initialize with defaults
        self.locations: List[Location] = [
            Location(
                name="default",
                display_name="Summerville, SC",
                latitude=32.4840,
                longitude=-80.1756,
                timezone="America/New_York",
                country="US",
                state="South Carolina",
            )
        ]
        self.current_location_index: int = 0
        self.theme: ThemeName = ThemeName.DEFAULT
        self.display: DisplaySettings = DisplaySettings()
        self.units: UnitSettings = UnitSettings()
        self.keybindings: KeyBindings = KeyBindings()
        self.api: APISettings = APISettings()
        self.personality: PersonalitySettings = PersonalitySettings()
        
        # Load existing API key from old config if present
        self._load_legacy_config()
    
    def _find_config_path(self) -> Path:
        """Find existing config or return default path."""
        if self.DEFAULT_CONFIG_PATH.exists():
            return self.DEFAULT_CONFIG_PATH
        if self.FALLBACK_CONFIG_PATH.exists():
            return self.FALLBACK_CONFIG_PATH
        return self.DEFAULT_CONFIG_PATH
    
    def _load_legacy_config(self):
        """Load API keys from legacy config.py if present."""
        try:
            # Import from old config
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from config import (
                OPENWEATHERMAP_API_KEY, OPENWEATHERMAP_CITY_ID,
                LATITUDE, LONGITUDE, TIMEZONE, LOCATION_NAME,
                CACHE_FILE, CACHE_MAX_AGE
            )
            
            self.api.openweathermap_key = OPENWEATHERMAP_API_KEY
            self.api.openweathermap_city_id = OPENWEATHERMAP_CITY_ID
            self.api.cache_file = CACHE_FILE
            self.api.cache_max_age = CACHE_MAX_AGE
            
            # Update default location
            self.locations[0] = Location(
                name="default",
                display_name=LOCATION_NAME,
                latitude=LATITUDE,
                longitude=LONGITUDE,
                timezone=TIMEZONE,
            )
        except ImportError:
            pass
    
    @property
    def current_location(self) -> Location:
        """Get currently selected location."""
        return self.locations[self.current_location_index]
    
    @property
    def current_theme(self) -> ColorTheme:
        """Get current color theme."""
        return THEMES.get(self.theme, THEMES[ThemeName.DEFAULT])
    
    def switch_location(self, name_or_index) -> bool:
        """Switch to a different location by name or index."""
        if isinstance(name_or_index, int):
            if 0 <= name_or_index < len(self.locations):
                self.current_location_index = name_or_index
                return True
        else:
            for i, loc in enumerate(self.locations):
                if loc.name.lower() == name_or_index.lower():
                    self.current_location_index = i
                    return True
                if loc.display_name.lower() == name_or_index.lower():
                    self.current_location_index = i
                    return True
        return False
    
    def next_location(self):
        """Switch to next location in list."""
        self.current_location_index = (self.current_location_index + 1) % len(self.locations)
    
    def prev_location(self):
        """Switch to previous location in list."""
        self.current_location_index = (self.current_location_index - 1) % len(self.locations)
    
    def add_location(self, location: Location):
        """Add a new saved location."""
        # Check for duplicates
        for existing in self.locations:
            if existing.name == location.name:
                return False
        self.locations.append(location)
        return True
    
    def remove_location(self, name: str) -> bool:
        """Remove a saved location."""
        if len(self.locations) <= 1:
            return False  # Keep at least one location
        
        for i, loc in enumerate(self.locations):
            if loc.name == name:
                self.locations.pop(i)
                if self.current_location_index >= len(self.locations):
                    self.current_location_index = len(self.locations) - 1
                return True
        return False
    
    def cycle_theme(self):
        """Cycle to next theme."""
        themes = list(ThemeName)
        current_index = themes.index(self.theme)
        self.theme = themes[(current_index + 1) % len(themes)]
    
    def toggle_units(self):
        """Toggle between Fahrenheit and Celsius."""
        if self.units.temperature == TemperatureUnit.FAHRENHEIT:
            self.units.temperature = TemperatureUnit.CELSIUS
            self.units.speed = SpeedUnit.KMH
        else:
            self.units.temperature = TemperatureUnit.FAHRENHEIT
            self.units.speed = SpeedUnit.MPH
    
    def load(self) -> bool:
        """Load configuration from file."""
        if not self.config_path.exists():
            return False
        
        try:
            content = self.config_path.read_text()
            
            if HAS_YAML and self.config_path.suffix in ('.yaml', '.yml'):
                data = yaml.safe_load(content)
            else:
                data = json.loads(content)
            
            if not data:
                return False
            
            # Load locations
            if 'locations' in data:
                self.locations = [Location.from_dict(loc) for loc in data['locations']]
            
            self.current_location_index = data.get('current_location_index', 0)
            
            if 'theme' in data:
                try:
                    self.theme = ThemeName(data['theme'])
                except ValueError:
                    self.theme = ThemeName.DEFAULT
            
            if 'display' in data:
                self.display = DisplaySettings.from_dict(data['display'])
            
            if 'units' in data:
                self.units = UnitSettings.from_dict(data['units'])
            
            if 'keybindings' in data:
                self.keybindings = KeyBindings.from_dict(data['keybindings'])
            
            if 'api' in data:
                self.api = APISettings.from_dict(data['api'])
            
            if 'personality' in data:
                self.personality = PersonalitySettings.from_dict(data['personality'])
            
            return True
            
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return False
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'locations': [loc.to_dict() for loc in self.locations],
                'current_location_index': self.current_location_index,
                'theme': self.theme.value,
                'display': self.display.to_dict(),
                'units': self.units.to_dict(),
                'keybindings': self.keybindings.to_dict(),
                'api': self.api.to_dict(),
                'personality': self.personality.to_dict(),
            }
            
            if HAS_YAML and self.config_path.suffix in ('.yaml', '.yml'):
                content = yaml.dump(data, default_flow_style=False, sort_keys=False)
            else:
                content = json.dumps(data, indent=2)
            
            self.config_path.write_text(content)
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}", file=sys.stderr)
            return False
    
    def to_dict(self) -> dict:
        """Export full config as dictionary."""
        return {
            'locations': [loc.to_dict() for loc in self.locations],
            'current_location_index': self.current_location_index,
            'theme': self.theme.value,
            'display': self.display.to_dict(),
            'units': self.units.to_dict(),
            'keybindings': self.keybindings.to_dict(),
            'api': self.api.to_dict(),
            'personality': self.personality.to_dict(),
        }
    
    def generate_default_config(self) -> str:
        """Generate a default config file content."""
        template = """# Stormy Weather Dashboard Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# 📍 Saved Locations
# Add as many locations as you like - switch between them with 'n'/'p' keys
locations:
  - name: home
    display_name: "Summerville, SC"
    latitude: 32.4840
    longitude: -80.1756
    timezone: "America/New_York"
    country: "US"
    state: "South Carolina"
    
  # Example additional locations (uncomment to use):
  # - name: work
  #   display_name: "New York, NY"
  #   latitude: 40.7128
  #   longitude: -74.0060
  #   timezone: "America/New_York"
  #   country: "US"
  #   state: "New York"
  #
  # - name: vacation
  #   display_name: "Tokyo, Japan"
  #   latitude: 35.6762
  #   longitude: 139.6503
  #   timezone: "Asia/Tokyo"
  #   country: "JP"

current_location_index: 0

# 🎨 Color Theme
# Options: default, nord, dracula, solarized_dark, solarized_light, 
#          gruvbox, monokai, cyberpunk, retro
theme: default

# 📺 Display Settings
display:
  show_forecast: true
  show_hourly: true
  forecast_days: 7
  forecast_hours: 12
  show_uv_index: true
  show_aqi: true
  show_moon_phase: true
  show_sunrise_sunset: true
  show_alerts: true
  show_historical: true
  show_mascot: true
  show_particles: true
  particle_density: 1.0      # 0.5 = half, 2.0 = double
  animation_fps: 30
  compact_mode: false

# 📏 Units
units:
  temperature: fahrenheit    # fahrenheit or celsius
  speed: mph                 # mph, km/h, m/s, knots
  pressure: hPa              # hPa, inHg, mb
  time_24h: false

# ⌨️ Keyboard Shortcuts
keybindings:
  quit: q
  refresh: r
  toggle_units: u
  switch_location: l
  next_location: n
  prev_location: p
  toggle_forecast: f
  toggle_compact: c
  screenshot: s
  help: "?"
  toggle_particles: a
  cycle_theme: t
  export_data: e

# 🔑 API Settings
api:
  openweathermap_key: "YOUR_API_KEY_HERE"
  openweathermap_city_id: ""
  cache_max_age: 300         # seconds
  cache_file: "/tmp/asciimatics_weather_cache.json"
  request_timeout: 10

# 🧠 Stormy's Personality
personality:
  enabled: true
  snark_level: 0.7           # 0.0 = polite, 1.0 = maximum snark
  wisdom_level: 0.6          # Philosophical depth
  reference_frequency: 0.8   # Pop culture/game references
  meta_comments: true        # Comments about the physics engine
  achievements_enabled: true
"""
        return template


# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def convert_temperature(temp_f: float, to_unit: TemperatureUnit) -> float:
    """Convert temperature from Fahrenheit to desired unit."""
    if to_unit == TemperatureUnit.CELSIUS:
        return (temp_f - 32) * 5 / 9
    return temp_f


def format_temperature(temp_f: float, unit: TemperatureUnit) -> str:
    """Format temperature with unit symbol."""
    if unit == TemperatureUnit.CELSIUS:
        return f"{(temp_f - 32) * 5 / 9:.0f}°C"
    return f"{temp_f:.0f}°F"


def convert_speed(speed_mph: float, to_unit: SpeedUnit) -> float:
    """Convert speed from MPH to desired unit."""
    conversions = {
        SpeedUnit.MPH: 1.0,
        SpeedUnit.KMH: 1.60934,
        SpeedUnit.MS: 0.44704,
        SpeedUnit.KNOTS: 0.868976,
    }
    return speed_mph * conversions.get(to_unit, 1.0)


def format_speed(speed_mph: float, unit: SpeedUnit) -> str:
    """Format speed with unit."""
    converted = convert_speed(speed_mph, unit)
    return f"{converted:.0f} {unit.value}"


def format_time(dt, use_24h: bool = False) -> str:
    """Format time according to preference."""
    if use_24h:
        return dt.strftime("%H:%M")
    return dt.strftime("%I:%M %p").lstrip("0")


# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI for config management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stormy Weather Configuration Manager")
    parser.add_argument('--init', action='store_true', help="Create default config file")
    parser.add_argument('--show', action='store_true', help="Show current config")
    parser.add_argument('--path', help="Config file path")
    parser.add_argument('--add-location', nargs=2, metavar=('NAME', 'QUERY'),
                        help="Add location by search query")
    
    args = parser.parse_args()
    
    config = Config(args.path)
    config.load()
    
    if args.init:
        config.config_path.parent.mkdir(parents=True, exist_ok=True)
        config.config_path.write_text(config.generate_default_config())
        print(f"✅ Created config file: {config.config_path}")
        return
    
    if args.show:
        print(f"📁 Config path: {config.config_path}")
        print(f"📍 Current location: {config.current_location.display_name}")
        print(f"🎨 Theme: {config.theme.value}")
        print(f"🌡️ Units: {config.units.temperature.value}")
        print(f"📍 Saved locations ({len(config.locations)}):")
        for i, loc in enumerate(config.locations):
            marker = "→" if i == config.current_location_index else " "
            print(f"  {marker} {loc.name}: {loc.display_name}")
        return
    
    if args.add_location:
        name, query = args.add_location
        # Would need to import geocoder
        print(f"Adding location '{name}' by searching '{query}'...")
        print("(Use the dashboard's 'l' key for interactive location search)")
        return
    
    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
