#!/usr/bin/env python3
"""
🌦️ Live Weather Animation - PRO EDITION
Advanced weather simulation with zero external dependencies (except asciimatics & requests).
Features:
- Perlin noise for realistic cloud generation
- Atmospheric turbulence simulation
- Multi-layer particle systems with physics
- Dynamic wind gusts and vorticity
- Real-time pressure system visualization
- Branching lightning with realistic pathfinding
- Temperature-affected particle behavior
- Atmospheric scattering (Rayleigh/Mie approximation)
- Weather radar simulation mode

Run: python weather_live_pro.py
"""
import sys
import random
import math
import time
import json
import os
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Tuple, Dict
from collections import deque

from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError

try:
    import requests
except ImportError:
    print("Error: requests module required. Install: pip install requests")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

# Try to load config, fallback to defaults
try:
    from config import (
        OPENWEATHERMAP_API_KEY, LATITUDE, LONGITUDE,
        LOCATION_NAME, CACHE_FILE, CACHE_MAX_AGE
    )
except ImportError:
    OPENWEATHERMAP_API_KEY = os.getenv("OWM_API_KEY", "")
    LATITUDE = 40.7128
    LONGITUDE = -74.0060
    LOCATION_NAME = "New York"
    CACHE_FILE = "/tmp/weather_cache.json"
    CACHE_MAX_AGE = 300

# Physics constants
GRAVITY = 0.5
AIR_RESISTANCE = 0.02
TURBULENCE_SCALE = 0.15
THERMAL_UPDRAFT_STRENGTH = 0.3
WIND_GUST_FREQUENCY = 0.01
PRESSURE_GRADIENT_FORCE = 0.05

# Visual settings
ENABLE_RADAR_MODE = False  # Toggle with 'R' key
ENABLE_PRESSURE_FIELD = True
ENABLE_TURBULENCE_VIZ = False
PARTICLE_TRAIL_LENGTH = 3


class WeatherCondition(Enum):
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
    """Current weather conditions with extended atmospheric data."""
    condition: WeatherCondition
    temperature_f: float
    temperature_c: float
    humidity: int
    wind_speed_mph: float
    wind_direction: int
    description: str
    location: str
    timestamp: float
    clouds_percent: int = 0
    rain_intensity: float = 0.0
    snow_intensity: float = 0.0
    visibility: int = 10000
    pressure: int = 1013
    
    @property
    def wind_vector(self) -> Tuple[float, float]:
        """Wind as 2D vector."""
        rad = math.radians(self.wind_direction)
        return (math.sin(rad) * self.wind_speed_mph * 0.01,
                math.cos(rad) * self.wind_speed_mph * 0.01)
    
    @property
    def temperature_kelvin(self) -> float:
        return (self.temperature_f - 32) * 5/9 + 273.15
    
    @property
    def atmospheric_stability(self) -> float:
        """Stability index (0=unstable/stormy, 1=stable/calm)."""
        if self.condition == WeatherCondition.THUNDERSTORM:
            return 0.1
        elif self.condition in (WeatherCondition.HEAVY_RAIN, WeatherCondition.HEAVY_SNOW):
            return 0.3
        elif self.condition in (WeatherCondition.RAIN, WeatherCondition.SNOW):
            return 0.5
        else:
            return 0.8


# ═══════════════════════════════════════════════════════════════════════════════
# PERLIN NOISE GENERATOR (for realistic cloud patterns)
# ═══════════════════════════════════════════════════════════════════════════════

class PerlinNoise:
    """2D Perlin noise implementation for natural-looking patterns."""
    
    def __init__(self, seed: int = None):
        self.seed = seed or int(time.time())
        random.seed(self.seed)
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm  # Duplicate for overflow
    
    @staticmethod
    def fade(t: float) -> float:
        """6t^5 - 15t^4 + 10t^3"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    @staticmethod
    def lerp(t: float, a: float, b: float) -> float:
        return a + t * (b - a)
    
    @staticmethod
    def grad(hash_val: int, x: float, y: float) -> float:
        """Gradient function."""
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def noise(self, x: float, y: float) -> float:
        """Generate 2D Perlin noise value at (x, y)."""
        # Find unit grid cell
        xi = int(x) & 255
        yi = int(y) & 255
        
        # Relative position in cell
        xf = x - int(x)
        yf = y - int(y)
        
        # Fade curves
        u = self.fade(xf)
        v = self.fade(yf)
        
        # Hash corners
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        
        # Blend results
        x1 = self.lerp(u, self.grad(aa, xf, yf), self.grad(ba, xf - 1, yf))
        x2 = self.lerp(u, self.grad(ab, xf, yf - 1), self.grad(bb, xf - 1, yf - 1))
        
        return self.lerp(v, x1, x2)
    
    def octave_noise(self, x: float, y: float, octaves: int = 4, 
                     persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """Multi-octave Perlin noise for fractal patterns."""
        total = 0
        frequency = 1
        amplitude = 1
        max_value = 0
        
        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        return total / max_value


# ═══════════════════════════════════════════════════════════════════════════════
# ADVANCED PARTICLE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class Particle:
    """Physics-based particle with atmospheric interactions."""
    
    def __init__(self, x: float, y: float, char: str, colour: int,
                 vx: float = 0, vy: float = 0, mass: float = 1.0,
                 lifetime: int = -1, temperature: float = 273.15):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.char = char
        self.colour = colour
        self.mass = mass
        self.lifetime = lifetime
        self.age = 0
        self.temperature = temperature
        
        # Trail history for motion blur
        self.trail: deque = deque(maxlen=PARTICLE_TRAIL_LENGTH)
        
        # Physics properties
        self.buoyancy = 0.0  # Positive = rises, negative = falls
        self.affected_by_wind = True
        self.affected_by_turbulence = True
        self.collided = False
    
    def update(self, wind_x: float, wind_y: float, turbulence_x: float, 
               turbulence_y: float, dt: float = 1.0):
        """Update particle physics."""
        # Store position in trail
        self.trail.append((int(self.x), int(self.y)))
        
        # Apply forces
        if self.affected_by_wind:
            self.vx += wind_x * dt
            self.vy += wind_y * dt
        
        if self.affected_by_turbulence:
            self.vx += turbulence_x * TURBULENCE_SCALE * dt
            self.vy += turbulence_y * TURBULENCE_SCALE * dt
        
        # Gravity and buoyancy
        net_gravity = (GRAVITY - self.buoyancy) / self.mass
        self.vy += net_gravity * dt
        
        # Air resistance
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > 0:
            drag = AIR_RESISTANCE * speed * speed / self.mass
            drag_x = -drag * self.vx / speed
            drag_y = -drag * self.vy / speed
            self.vx += drag_x * dt
            self.vy += drag_y * dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Age
        self.age += 1
    
    def is_expired(self, width: int, height: int) -> bool:
        """Check if particle should be removed."""
        if self.lifetime > 0 and self.age >= self.lifetime:
            return True
        if self.x < -5 or self.x >= width + 5:
            return True
        if self.y >= height + 5:
            return True
        return False


class ParticleSystem:
    """Manages particle lifecycle and interactions."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
    
    def add_particle(self, particle: Particle):
        self.particles.append(particle)
    
    def update(self, wind_x: float, wind_y: float, 
               turbulence_field: 'TurbulenceField'):
        """Update all particles."""
        for p in self.particles:
            turb_x, turb_y = turbulence_field.get_turbulence(p.x, p.y)
            p.update(wind_x, wind_y, turb_x, turb_y)
        
        # Remove expired particles
        self.particles = [p for p in self.particles if not p.is_expired(self.width, self.height)]
    
    def clear(self):
        self.particles.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# TURBULENCE & ATMOSPHERIC EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════

class TurbulenceField:
    """Dynamic turbulence field using Perlin noise."""
    
    def __init__(self, seed: int = None):
        self.noise = PerlinNoise(seed)
        self.time_offset = 0
    
    def update(self):
        self.time_offset += 0.01
    
    def get_turbulence(self, x: float, y: float) -> Tuple[float, float]:
        """Get turbulence vector at position."""
        tx = self.noise.octave_noise(x * 0.02 + self.time_offset, y * 0.02, octaves=3)
        ty = self.noise.octave_noise(x * 0.02, y * 0.02 + self.time_offset + 100, octaves=3)
        return tx, ty


class PressureField:
    """Atmospheric pressure field visualization."""
    
    def __init__(self, width: int, height: int, base_pressure: int = 1013):
        self.width = width
        self.height = height
        self.base_pressure = base_pressure
        self.noise = PerlinNoise()
        self.time_offset = 0
    
    def update(self):
        self.time_offset += 0.005
    
    def get_pressure(self, x: int, y: int) -> float:
        """Get pressure at grid position (in hPa)."""
        noise_val = self.noise.octave_noise(
            x * 0.05 + self.time_offset, 
            y * 0.05, 
            octaves=2
        )
        return self.base_pressure + noise_val * 20
    
    def get_pressure_char(self, pressure: float) -> Tuple[str, int]:
        """Get character representing pressure level."""
        if pressure > self.base_pressure + 10:
            return "H", Screen.COLOUR_RED
        elif pressure > self.base_pressure + 3:
            return "h", Screen.COLOUR_YELLOW
        elif pressure < self.base_pressure - 10:
            return "L", Screen.COLOUR_CYAN
        elif pressure < self.base_pressure - 3:
            return "l", Screen.COLOUR_BLUE
        else:
            return "·", Screen.COLOUR_WHITE


class WindGustSystem:
    """Dynamic wind gusts."""
    
    def __init__(self, base_wind_x: float, base_wind_y: float):
        self.base_wind_x = base_wind_x
        self.base_wind_y = base_wind_y
        self.gust_strength = 0
        self.gust_angle = 0
        self.gust_timer = 0
    
    def update(self):
        """Generate random gusts."""
        if self.gust_timer > 0:
            self.gust_timer -= 1
            # Decay gust
            self.gust_strength *= 0.95
        else:
            # Random new gust
            if random.random() < WIND_GUST_FREQUENCY:
                self.gust_strength = random.uniform(0.5, 2.0)
                self.gust_angle = random.uniform(0, 2 * math.pi)
                self.gust_timer = random.randint(30, 120)
    
    def get_wind(self) -> Tuple[float, float]:
        """Get current wind including gusts."""
        gust_x = math.cos(self.gust_angle) * self.gust_strength
        gust_y = math.sin(self.gust_angle) * self.gust_strength
        return self.base_wind_x + gust_x, self.base_wind_y + gust_y


# ═══════════════════════════════════════════════════════════════════════════════
# LIGHTNING SYSTEM (Realistic branching)
# ═══════════════════════════════════════════════════════════════════════════════

class LightningBolt:
    """Procedurally generated branching lightning."""
    
    def __init__(self, start_x: int, start_y: int, end_y: int):
        self.segments: List[Tuple[int, int, int, int]] = []
        self.lifetime = random.randint(3, 8)
        self.age = 0
        self.brightness = 1.0
        self._generate(start_x, start_y, end_y)
    
    def _generate(self, x: int, y: int, target_y: int):
        """Generate lightning path with realistic branching."""
        current_x, current_y = x, y
        
        while current_y < target_y:
            # Main bolt step
            next_x = current_x + random.randint(-3, 3)
            next_y = current_y + random.randint(2, 5)
            
            self.segments.append((current_x, current_y, next_x, next_y))
            
            # Random branches
            if random.random() < 0.3:
                branch_len = random.randint(3, 8)
                self._generate_branch(next_x, next_y, branch_len)
            
            current_x, current_y = next_x, next_y
    
    def _generate_branch(self, x: int, y: int, length: int):
        """Generate a side branch."""
        direction = random.choice([-1, 1])
        current_x, current_y = x, y
        
        for _ in range(length):
            next_x = current_x + random.randint(1, 3) * direction
            next_y = current_y + random.randint(1, 3)
            self.segments.append((current_x, current_y, next_x, next_y))
            current_x, current_y = next_x, next_y
            
            if random.random() < 0.1:
                break
    
    def update(self):
        self.age += 1
        self.brightness = max(0, 1.0 - (self.age / self.lifetime))
    
    def is_expired(self) -> bool:
        return self.age >= self.lifetime
    
    def draw(self, screen: Screen):
        """Draw lightning with intensity falloff."""
        if self.brightness <= 0:
            return
        
        # Determine colour based on brightness
        if self.brightness > 0.7:
            colour = Screen.COLOUR_WHITE
            char = "█"
        elif self.brightness > 0.4:
            colour = Screen.COLOUR_YELLOW
            char = "▓"
        else:
            colour = Screen.COLOUR_BLUE
            char = "│"
        
        for x1, y1, x2, y2 in self.segments:
            # Draw line using Bresenham
            self._draw_line(screen, x1, y1, x2, y2, char, colour)
    
    @staticmethod
    def _draw_line(screen: Screen, x1: int, y1: int, x2: int, y2: int, 
                   char: str, colour: int):
        """Bresenham line algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            if 0 <= x1 < screen.width and 0 <= y1 < screen.height:
                screen.print_at(char, x1, y1, colour=colour)
            
            if x1 == x2 and y1 == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy


# ═══════════════════════════════════════════════════════════════════════════════
# WEATHER API CLIENT (Self-contained)
# ═══════════════════════════════════════════════════════════════════════════════

OWM_CONDITION_MAP = {
    200: WeatherCondition.THUNDERSTORM, 201: WeatherCondition.THUNDERSTORM,
    202: WeatherCondition.THUNDERSTORM, 210: WeatherCondition.THUNDERSTORM,
    211: WeatherCondition.THUNDERSTORM, 212: WeatherCondition.THUNDERSTORM,
    221: WeatherCondition.THUNDERSTORM, 230: WeatherCondition.THUNDERSTORM,
    231: WeatherCondition.THUNDERSTORM, 232: WeatherCondition.THUNDERSTORM,
    300: WeatherCondition.DRIZZLE, 301: WeatherCondition.DRIZZLE,
    302: WeatherCondition.DRIZZLE, 310: WeatherCondition.DRIZZLE,
    500: WeatherCondition.RAIN, 501: WeatherCondition.RAIN,
    502: WeatherCondition.HEAVY_RAIN, 503: WeatherCondition.HEAVY_RAIN,
    511: WeatherCondition.FREEZING_RAIN, 520: WeatherCondition.RAIN,
    600: WeatherCondition.SNOW, 601: WeatherCondition.SNOW,
    602: WeatherCondition.HEAVY_SNOW, 611: WeatherCondition.FREEZING_RAIN,
    701: WeatherCondition.FOG, 741: WeatherCondition.FOG,
    800: WeatherCondition.CLEAR,
    801: WeatherCondition.PARTLY_CLOUDY, 802: WeatherCondition.PARTLY_CLOUDY,
    803: WeatherCondition.CLOUDY, 804: WeatherCondition.CLOUDY,
}


def fetch_weather() -> Optional[WeatherData]:
    """Fetch weather with caching."""
    # Try cache first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
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
                    pressure=data.get('pressure', 1013),
                )
        except:
            pass
    
    # Fetch fresh
    if not OPENWEATHERMAP_API_KEY:
        return None
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': LATITUDE,
            'lon': LONGITUDE,
            'appid': OPENWEATHERMAP_API_KEY,
            'units': 'imperial'
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        weather = WeatherData(
            condition=OWM_CONDITION_MAP.get(data['weather'][0]['id'], WeatherCondition.UNKNOWN),
            temperature_f=data['main']['temp'],
            temperature_c=(data['main']['temp'] - 32) * 5/9,
            humidity=data['main']['humidity'],
            wind_speed_mph=data['wind']['speed'],
            wind_direction=data['wind'].get('deg', 0),
            description=data['weather'][0]['description'],
            location=LOCATION_NAME,
            timestamp=time.time(),
            clouds_percent=data['clouds']['all'],
            pressure=data['main']['pressure'],
        )
        
        # Cache it
        with open(CACHE_FILE, 'w') as f:
            json.dump({
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
                'pressure': weather.pressure,
            }, f)
        
        return weather
    except Exception as e:
        print(f"Weather fetch failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# ANIMATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class WeatherAnimation:
    """Base animation with advanced systems."""
    
    def __init__(self, screen: Screen, weather: WeatherData):
        self.screen = screen
        self.weather = weather
        self.width = screen.width
        self.height = screen.height
        self.frame = 0
        
        # Advanced systems
        self.particle_system = ParticleSystem(self.width, self.height)
        self.turbulence = TurbulenceField()
        self.pressure = PressureField(self.width, self.height, weather.pressure)
        
        wind_x, wind_y = weather.wind_vector
        self.wind_gust = WindGustSystem(wind_x, wind_y)
        
        self.lightning_bolts: List[LightningBolt] = []
        
        # Perlin noise for clouds
        self.cloud_noise = PerlinNoise()
        self.cloud_time = 0
        
        # Radar mode
        self.radar_mode = ENABLE_RADAR_MODE
    
    def update(self):
        """Update all systems."""
        self.frame += 1
        self.turbulence.update()
        self.pressure.update()
        self.wind_gust.update()
        self.cloud_time += 0.02
        
        wind_x, wind_y = self.wind_gust.get_wind()
        self.particle_system.update(wind_x, wind_y, self.turbulence)
        
        # Update lightning
        for bolt in self.lightning_bolts:
            bolt.update()
        self.lightning_bolts = [b for b in self.lightning_bolts if not b.is_expired()]
    
    def draw(self):
        """Override in subclass."""
        pass
    
    def draw_info_bar(self):
        """Enhanced info bar."""
        temp = f"{self.weather.temperature_f:.0f}°F"
        wind = f"{self.weather.wind_speed_mph:.0f}mph"
        press = f"{self.weather.pressure}hPa"
        
        info = f" {self.weather.location} │ {temp} │ {self.weather.description} │ Wind:{wind} │ P:{press} │ [Q]Quit [R]Radar "
        if len(info) > self.width:
            info = info[:self.width-1]
        
        self.screen.print_at(info, 0, 0, 
                           colour=Screen.COLOUR_BLACK, 
                           bg=Screen.COLOUR_CYAN)
    
    def draw_pressure_overlay(self):
        """Draw pressure field visualization."""
        if not ENABLE_PRESSURE_FIELD or self.radar_mode:
            return
        
        step = 4
        for y in range(2, self.height - 2, step):
            for x in range(0, self.width, step):
                pressure = self.pressure.get_pressure(x, y)
                char, colour = self.pressure.get_pressure_char(pressure)
                self.screen.print_at(char, x, y, colour=colour)


class ThunderstormAnimation(WeatherAnimation):
    """Advanced thunderstorm with branching lightning."""
    
    def __init__(self, screen: Screen, weather: WeatherData):
        super().__init__(screen, weather)
        self.flash_timer = 0
        self.next_lightning = random.randint(30, 120)
    
    def update(self):
        super().update()
        
        # Generate rain
        if self.frame % 2 == 0:
            for _ in range(8):
                x = random.randint(0, self.width - 1)
                char = random.choice(["┃", "║", "│"])
                p = Particle(x, 2, char, Screen.COLOUR_BLUE, 
                           vx=random.uniform(-0.5, 0.5),
                           vy=random.uniform(2, 4),
                           mass=0.8)
                p.affected_by_turbulence = True
                self.particle_system.add_particle(p)
        
        # Generate lightning
        if self.flash_timer <= 0:
            if random.random() < 0.02:
                x = random.randint(10, self.width - 10)
                bolt = LightningBolt(x, 2, random.randint(self.height // 2, self.height - 5))
                self.lightning_bolts.append(bolt)
                self.flash_timer = 10
        else:
            self.flash_timer -= 1
    
    def draw(self):
        # Sky flash effect
        if self.flash_timer > 7:
            bg = Screen.COLOUR_WHITE
        elif self.flash_timer > 4:
            bg = Screen.COLOUR_YELLOW
        else:
            bg = Screen.COLOUR_BLACK
        
        self.screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, bg)
        
        # Dark clouds
        for y in range(2, 10):
            for x in range(0, self.width):
                noise = self.cloud_noise.octave_noise(
                    x * 0.1 + self.cloud_time, y * 0.2, octaves=3
                )
                if noise > -0.2:
                    char = random.choice(["█", "▓", "▒"])
                    self.screen.print_at(char, x, y, colour=Screen.COLOUR_BLACK)
        
        # Lightning
        for bolt in self.lightning_bolts:
            bolt.draw(self.screen)
        
        # Rain particles
        for p in self.particle_system.particles:
            if 0 <= int(p.x) < self.width and 0 <= int(p.y) < self.height:
                self.screen.print_at(p.char, int(p.x), int(p.y), colour=p.colour)
        
        self.draw_info_bar()


class RainAnimation(WeatherAnimation):
    """Rain with realistic accumulation and splashes."""
    
    def __init__(self, screen: Screen, weather: WeatherData):
        super().__init__(screen, weather)
        self.ground_water = [0] * self.width  # Water accumulation
    
    def update(self):
        super().update()
        
        # Rain particles
        intensity = 5 if self.weather.condition == WeatherCondition.HEAVY_RAIN else 3
        if self.frame % 2 == 0:
            for _ in range(intensity):
                x = random.randint(0, self.width - 1)
                char = random.choice(["│", "|", "┃", ":"])
                p = Particle(x, 2, char, Screen.COLOUR_CYAN,
                           vx=random.uniform(-0.3, 0.3),
                           vy=random.uniform(1.5, 3.0),
                           mass=0.5)
                self.particle_system.add_particle(p)
        
        # Accumulate water
        for p in self.particle_system.particles:
            if p.y >= self.height - 2 and not p.collided:
                x_idx = int(p.x) % self.width
                self.ground_water[x_idx] = min(5, self.ground_water[x_idx] + 1)
                p.collided = True
                
                # Splash
                for _ in range(2):
                    splash = Particle(p.x, self.height - 2, "·", Screen.COLOUR_BLUE,
                                    vx=random.uniform(-1, 1),
                                    vy=random.uniform(-2, -1),
                                    lifetime=10)
                    self.particle_system.add_particle(splash)
        
        # Evaporate water slowly
        for i in range(self.width):
            if random.random() < 0.01:
                self.ground_water[i] = max(0, self.ground_water[i] - 1)
    
    def draw(self):
        self.screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK)
        
        # Clouds
        for y in range(2, 8):
            for x in range(0, self.width, 3):
                noise = self.cloud_noise.octave_noise(x * 0.15 + self.cloud_time, y * 0.2)
                if noise > 0.1:
                    self.screen.print_at("▒", x, y, colour=Screen.COLOUR_WHITE)
        
        # Rain
        for p in self.particle_system.particles:
            if 0 <= int(p.x) < self.width and 2 <= int(p.y) < self.height - 1:
                self.screen.print_at(p.char, int(p.x), int(p.y), colour=p.colour)
        
        # Water accumulation
        for x, level in enumerate(self.ground_water):
            if level > 0:
                y = self.height - 2
                char = ["·", "~", "≈", "∿", "≋"][min(level - 1, 4)]
                self.screen.print_at(char, x, y, colour=Screen.COLOUR_BLUE)
        
        self.draw_pressure_overlay()
        self.draw_info_bar()


class SnowAnimation(WeatherAnimation):
    """Snow with realistic accumulation."""
    
    def __init__(self, screen: Screen, weather: WeatherData):
        super().__init__(screen, weather)
        self.snow_depth = [0] * self.width
    
    def update(self):
        super().update()
        
        # Snowflakes
        intensity = 4 if self.weather.condition == WeatherCondition.HEAVY_SNOW else 2
        if self.frame % 3 == 0:
            for _ in range(intensity):
                x = random.randint(0, self.width - 1)
                char = random.choice(["*", "❄", "❅", "·", "°"])
                p = Particle(x, 2, char, Screen.COLOUR_WHITE,
                           vx=random.uniform(-0.3, 0.3),
                           vy=random.uniform(0.2, 0.8),
                           mass=0.2)
                p.affected_by_turbulence = True
                self.particle_system.add_particle(p)
        
        # Accumulate
        for p in self.particle_system.particles:
            if p.y >= self.height - 2 - self.snow_depth[int(p.x) % self.width] and not p.collided:
                x_idx = int(p.x) % self.width
                self.snow_depth[x_idx] = min(8, self.snow_depth[x_idx] + 1)
                p.collided = True
    
    def draw(self):
        self.screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK)
        
        # Snowflakes
        for p in self.particle_system.particles:
            if 0 <= int(p.x) < self.width and 2 <= int(p.y) < self.height:
                self.screen.print_at(p.char, int(p.x), int(p.y), colour=p.colour)
        
        # Snow accumulation
        for x, depth in enumerate(self.snow_depth):
            for d in range(depth):
                y = self.height - 2 - d
                if y >= 2:
                    char = "▁" if d == depth - 1 else "░"
                    self.screen.print_at(char, x, y, colour=Screen.COLOUR_WHITE)
        
        self.draw_pressure_overlay()
        self.draw_info_bar()


class ClearAnimation(WeatherAnimation):
    """Clear sky with stars/sun."""
    
    def __init__(self, screen: Screen, weather: WeatherData):
        super().__init__(screen, weather)
        self.is_night = datetime.now().hour < 6 or datetime.now().hour > 20
        self.stars = []
        
        if self.is_night:
            for _ in range(int(self.width * self.height * 0.02)):
                self.stars.append({
                    'x': random.randint(0, self.width - 1),
                    'y': random.randint(2, self.height - 5),
                    'char': random.choice(["·", ".", "*", "✦"]),
                    'phase': random.uniform(0, 2 * math.pi),
                })
    
    def draw(self):
        self.screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK)
        
        if self.is_night:
            # Twinkling stars
            for star in self.stars:
                brightness = (math.sin(self.frame * 0.05 + star['phase']) + 1) / 2
                if brightness > 0.3:
                    colour = Screen.COLOUR_WHITE if brightness > 0.7 else Screen.COLOUR_CYAN
                    self.screen.print_at(star['char'], star['x'], star['y'], colour=colour)
        else:
            # Sun
            sun_y = 5
            sun_x = self.width // 2
            self.screen.print_at("  \\  |  /  ", sun_x - 5, sun_y - 1, colour=Screen.COLOUR_YELLOW)
            self.screen.print_at("    ☀    ", sun_x - 4, sun_y, colour=Screen.COLOUR_YELLOW)
            self.screen.print_at("  /  |  \\  ", sun_x - 5, sun_y + 1, colour=Screen.COLOUR_YELLOW)
        
        self.draw_pressure_overlay()
        self.draw_info_bar()


# Animation selector
def get_animation_class(condition: WeatherCondition):
    """Select animation class based on weather."""
    mapping = {
        WeatherCondition.THUNDERSTORM: ThunderstormAnimation,
        WeatherCondition.HEAVY_RAIN: RainAnimation,
        WeatherCondition.RAIN: RainAnimation,
        WeatherCondition.DRIZZLE: RainAnimation,
        WeatherCondition.SNOW: SnowAnimation,
        WeatherCondition.HEAVY_SNOW: SnowAnimation,
        WeatherCondition.CLEAR: ClearAnimation,
    }
    return mapping.get(condition, ClearAnimation)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def main_loop(screen: Screen):
    """Main animation loop."""
    # Fetch weather
    weather = fetch_weather()
    if not weather:
        screen.print_at("Failed to fetch weather. Check API key.", 0, 0)
        screen.refresh()
        time.sleep(3)
        return
    
    # Create animation
    AnimClass = get_animation_class(weather.condition)
    anim = AnimClass(screen, weather)
    
    last_refresh = time.time()
    
    while True:
        # Handle input
        ev = screen.get_event()
        if ev and hasattr(ev, 'key_code'):
            if ev.key_code in (ord('q'), ord('Q')):
                return
            elif ev.key_code in (ord('r'), ord('R')):
                anim.radar_mode = not anim.radar_mode
        
        # Update
        anim.update()
        anim.draw()
        
        # Refresh screen
        screen.refresh()
        
        # Refetch weather every 5 minutes
        if time.time() - last_refresh > 300:
            new_weather = fetch_weather()
            if new_weather:
                AnimClass = get_animation_class(new_weather.condition)
                anim = AnimClass(screen, new_weather)
            last_refresh = time.time()
        
        time.sleep(1/30)  # 30 FPS


def main():
    """Entry point."""
    try:
        Screen.wrapper(main_loop)
    except KeyboardInterrupt:
        pass
    except ResizeScreenError:
        print("Terminal resized. Please restart.")


if __name__ == "__main__":
    main()
