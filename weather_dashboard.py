#!/usr/bin/env python3
"""
STORMY - Weather Oracle of the Terminal (Enhanced Edition)
"The sky speaks. I merely translate. With commentary. And now, forecasts."

A philosophical weather dashboard with the wisdom of ages,
the deadpan delivery of British comedy, references to lands
both wasteland and fantastical, PLUS forecasts, alerts, UV/AQI,
moon phases, achievements, and special effects.

Run: python weather_dashboard.py

New Features:
  - 7-day forecast with hourly breakdown
  - Weather alerts from NWS
  - UV Index & Air Quality monitoring  
  - Sunrise/sunset & moon phases
  - 30+ achievements with progress tracking
  - Special effects (aurora, rainbows, heat shimmer, etc.)
  - Enhanced keyboard controls

Press ? for help at any time.
"""
import sys
import os
import random
import math
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from asciimatics.event import KeyboardEvent

from lib.weather_api import get_weather, WeatherCondition, WeatherData, search_and_fetch_weather
from lib.mock_weather import get_demo_weather
from lib.particles import Particle, ParticleSystem
from collections import deque
from typing import List, Tuple, Optional, Dict, Any

# Global demo mode flag
DEMO_MODE = False
DEMO_SCENARIO = None

# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED MODULES - New integrated features
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from lib.weather_extended import (
        fetch_forecast, fetch_weather_alerts, fetch_astronomical_data,
        fetch_environmental_data, ForecastData, WeatherAlert, 
        AstronomicalData, EnvironmentalData, MoonPhase
    )
    EXTENDED_WEATHER_AVAILABLE = True
except ImportError:
    EXTENDED_WEATHER_AVAILABLE = False

try:
    from lib.achievements import AchievementManager, ACHIEVEMENTS
    ACHIEVEMENTS_AVAILABLE = True
except ImportError:
    ACHIEVEMENTS_AVAILABLE = False

try:
    from lib.interactive import (
        InputHandler, Action, HelpScreen, NotificationManager,
        DashboardState, ScreenshotCapture
    )
    INTERACTIVE_AVAILABLE = True
except ImportError:
    INTERACTIVE_AVAILABLE = False

try:
    from lib.dashboard_panels import (
        ForecastPanel, AlertBanner, AstronomicalPanel,
        EnvironmentalPanel, AchievementDisplay, HistoricalComparisonPanel
    )
    PANELS_AVAILABLE = True
except ImportError:
    PANELS_AVAILABLE = False

# Import creatures module
try:
    from engine.creatures import EasterEggManager, EASTER_EGG_CREATURES
    CREATURES_AVAILABLE = True
except ImportError:
    CREATURES_AVAILABLE = False
    EASTER_EGG_CREATURES = {}
    class EasterEggManager:
        def __init__(self, *a, **kw): pass
        def try_spawn(self, *a, **kw): return False
        def update(self): pass
        def draw(self, *a, **kw): pass

try:
    from engine.effects.special_effects import SpecialEffectsManager
    SPECIAL_EFFECTS_AVAILABLE = True
except ImportError:
    SPECIAL_EFFECTS_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL WEATHER ENGINE - Modular Architecture
# ═══════════════════════════════════════════════════════════════════════════════
from engine.physics.noise import PerlinNoise as EnginePerlinNoise, FractalNoise, SimplexNoise, DomainWarp
from engine.physics.particles import (
    Vector2, Particle as EngineParticle, ParticleSystem as EngineParticleSystem,
    PhysicsConfig, GravityForce, DragForce, WindForce, IntegrationType
)
from engine.physics.atmosphere import (
    AtmosphericModel, AtmosphericState, StabilityClass,
    calculate_wind_chill, calculate_heat_index
)
from engine.rendering.core import RenderStats, FrameBudget, RenderQueue, RenderCommand, RenderLayer
from engine.personality.core import PersonalityEngine, Mood, PersonalityConfig
from data.dialogue import (
    WEATHER_COMMENTS as DIALOGUE_COMMENTS, TEMP_COMMENTS, GREETINGS,
    ACHIEVEMENTS as DIALOGUE_ACHIEVEMENTS, QUIPS, WEATHER_TYPE_MAP, get_temp_category,
)
from data.art import BIG_DIGITS, WEATHER_MASCOT, STORMY_FACES, WEATHER_SCENES
from screens.achievements import draw_achievements_screen
from screens.search import location_search_screen
from screens.bestiary import draw_bestiary_screen

# Global performance monitoring
_render_stats = RenderStats()
_frame_budget = FrameBudget(target_fps=30)


# ═══════════════════════════════════════════════════════════════════════════════
# ADVANCED PHYSICS ENGINE - "Under the hood complexity"
# ═══════════════════════════════════════════════════════════════════════════════

# Physics constants (Stormy takes physics seriously, even if sarcastically)
GRAVITY = 0.5
AIR_RESISTANCE = 0.02
TURBULENCE_SCALE = 0.15
WIND_GUST_FREQUENCY = 0.01


class PerlinNoise:
    """
    2D Perlin noise for realistic cloud and fog patterns.
    "The ancient mathematicians called it 'gradient noise'. I call it 'making
    clouds look less like a 5-year-old drew them.'" - Stormy
    """
    
    def __init__(self, seed: int = None):
        # Now uses engine module internally!
        self._engine = EnginePerlinNoise(seed=seed or int(time.time()))
        self._fractal = FractalNoise(self._engine)
        # Legacy compat
        self.seed = seed or int(time.time())
        random.seed(self.seed)
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm
    
    @staticmethod
    def fade(t: float) -> float:
        """Quintic interpolation: 6t^5 - 15t^4 + 10t^3"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    @staticmethod
    def lerp(t: float, a: float, b: float) -> float:
        return a + t * (b - a)
    
    @staticmethod
    def grad(hash_val: int, x: float, y: float) -> float:
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def noise(self, x: float, y: float) -> float:
        """Generate 2D Perlin noise value at (x, y)."""
        xi, yi = int(x) & 255, int(y) & 255
        xf, yf = x - int(x), y - int(y)
        u, v = self.fade(xf), self.fade(yf)
        
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        
        x1 = self.lerp(u, self.grad(aa, xf, yf), self.grad(ba, xf - 1, yf))
        x2 = self.lerp(u, self.grad(ab, xf, yf - 1), self.grad(bb, xf - 1, yf - 1))
        return self.lerp(v, x1, x2)
    
    def octave_noise(self, x: float, y: float, octaves: int = 4,
                     persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """Multi-octave fractal noise for natural-looking patterns."""
        total, frequency, amplitude, max_value = 0, 1, 1, 0
        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        return total / max_value


class TurbulenceField:
    """
    Dynamic atmospheric turbulence using Perlin noise.
    "Wind doesn't just blow in a straight line. It swirls, it eddies,
    it makes your umbrella useless. This simulates that chaos." - Stormy
    """
    
    def __init__(self, seed: int = None):
        self.noise = PerlinNoise(seed)
        self.time_offset = 0
    
    def update(self):
        self.time_offset += 0.01
    
    def get_turbulence(self, x: float, y: float) -> Tuple[float, float]:
        tx = self.noise.octave_noise(x * 0.02 + self.time_offset, y * 0.02, octaves=3)
        ty = self.noise.octave_noise(x * 0.02, y * 0.02 + self.time_offset + 100, octaves=3)
        return tx * TURBULENCE_SCALE, ty * TURBULENCE_SCALE


class WindGustSystem:
    """
    Dynamic wind gusts with realistic decay.
    "The Nords call sudden gusts 'Kyne's Breath'. I call them 'hat thieves.'" - Stormy
    """
    
    def __init__(self, base_wind_x: float, base_wind_y: float):
        self.base_wind_x = base_wind_x
        self.base_wind_y = base_wind_y
        self.gust_strength = 0
        self.gust_angle = 0
        self.gust_timer = 0
    
    def update(self):
        if self.gust_timer > 0:
            self.gust_timer -= 1
            self.gust_strength *= 0.95
        elif random.random() < WIND_GUST_FREQUENCY:
            self.gust_strength = random.uniform(0.5, 2.0)
            self.gust_angle = random.uniform(0, 2 * math.pi)
            self.gust_timer = random.randint(30, 120)
    
    def get_wind(self) -> Tuple[float, float]:
        gust_x = math.cos(self.gust_angle) * self.gust_strength
        gust_y = math.sin(self.gust_angle) * self.gust_strength
        return self.base_wind_x + gust_x, self.base_wind_y + gust_y


class LightningBolt:
    """
    Procedurally generated branching lightning using recursive fractal patterns.
    "Zeus's anger, rendered in Unicode. The ancient Greeks would be impressed.
    Or terrified. Probably terrified." - Stormy
    """
    
    def __init__(self, start_x: int, start_y: int, end_y: int, width: int):
        self.segments: List[Tuple[int, int, int, int]] = []
        self.lifetime = random.randint(3, 8)
        self.age = 0
        self.brightness = 1.0
        self.width = width
        self._generate(start_x, start_y, end_y)
    
    def _generate(self, x: int, y: int, target_y: int, depth: int = 0):
        current_x, current_y = x, y
        while current_y < target_y:
            next_x = max(0, min(self.width - 1, current_x + random.randint(-3, 3)))
            next_y = current_y + random.randint(2, 5)
            self.segments.append((current_x, current_y, next_x, next_y))
            
            # Branching with decreasing probability at depth
            if depth < 2 and random.random() < (0.3 - depth * 0.1):
                branch_len = random.randint(3, 6)
                self._generate_branch(next_x, next_y, branch_len, depth + 1)
            
            current_x, current_y = next_x, next_y
    
    def _generate_branch(self, x: int, y: int, length: int, depth: int):
        direction = random.choice([-1, 1])
        current_x, current_y = x, y
        for _ in range(length):
            next_x = max(0, min(self.width - 1, current_x + random.randint(1, 3) * direction))
            next_y = current_y + random.randint(1, 3)
            self.segments.append((current_x, current_y, next_x, next_y))
            current_x, current_y = next_x, next_y
            if random.random() < 0.15:
                break
    
    def update(self):
        self.age += 1
        self.brightness = max(0, 1.0 - (self.age / self.lifetime))
    
    def is_expired(self) -> bool:
        return self.age >= self.lifetime
    
    def draw(self, screen, x_offset: int = 0):
        if self.brightness <= 0:
            return
        
        if self.brightness > 0.7:
            colour, char = Screen.COLOUR_WHITE, "█"
        elif self.brightness > 0.4:
            colour, char = Screen.COLOUR_YELLOW, "▓"
        else:
            colour, char = Screen.COLOUR_CYAN, "│"
        
        for x1, y1, x2, y2 in self.segments:
            self._draw_line(screen, x1 + x_offset, y1, x2 + x_offset, y2, char, colour)
    
    @staticmethod
    def _draw_line(screen, x1: int, y1: int, x2: int, y2: int, char: str, colour: int):
        """Bresenham line algorithm for smooth lightning."""
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx, sy = (1 if x1 < x2 else -1), (1 if y1 < y2 else -1)
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


class PhysicsParticle:
    """
    Advanced particle with realistic physics: mass, buoyancy, drag, and trails.
    "Newton's laws, applied to raindrops. He'd be proud. Or confused by the
    terminal. Probably confused." - Stormy
    """
    
    def __init__(self, x: float, y: float, char: str, colour: int,
                 vx: float = 0, vy: float = 0, mass: float = 1.0,
                 lifetime: int = -1, buoyancy: float = 0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.char, self.colour = char, colour
        self.mass = mass
        self.lifetime = lifetime
        self.age = 0
        self.buoyancy = buoyancy
        self.trail: deque = deque(maxlen=3)
        self.collided = False
    
    def update(self, wind_x: float, wind_y: float, turb_x: float, turb_y: float):
        self.trail.append((int(self.x), int(self.y)))
        
        # Wind and turbulence
        self.vx += wind_x + turb_x
        self.vy += wind_y + turb_y
        
        # Gravity and buoyancy
        self.vy += (GRAVITY - self.buoyancy) / self.mass
        
        # Air resistance (quadratic drag)
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > 0:
            drag = AIR_RESISTANCE * speed * speed / self.mass
            self.vx -= drag * self.vx / speed
            self.vy -= drag * self.vy / speed
        
        self.x += self.vx
        self.y += self.vy
        self.age += 1
    
    def is_expired(self, width: int, height: int) -> bool:
        if self.lifetime > 0 and self.age >= self.lifetime:
            return True
        return self.x < -5 or self.x >= width + 5 or self.y >= height + 5


# ═══════════════════════════════════════════════════════════════════════════════
# THEME & COLORS
# ═══════════════════════════════════════════════════════════════════════════════

class Theme:
    FROST = Screen.COLOUR_CYAN
    SNOW = Screen.COLOUR_WHITE  
    SUN = Screen.COLOUR_YELLOW
    DANGER = Screen.COLOUR_RED
    NATURE = Screen.COLOUR_GREEN
    MAGIC = Screen.COLOUR_MAGENTA
    MUTED = Screen.COLOUR_BLUE


# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 STORMY'S PERSONALITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════
# STORMY - Thin wrapper around PersonalityEngine + persistence
# ═══════════════════════════════════════════════════════════════════════════════
# Inspired by: Carrot Weather, Fallout, Elder Scrolls, Monty Python
# Musical mood: The Ink Spots, Frank Sinatra, Bing Crosby, The Mills Brothers
# "I don't want to set the world on fire... I just want to tell you it's raining."

class StormyPersonality:
    """Thin wrapper: persistence + achievements. All dialogue lives in data/dialogue.py,
    all mood/memory logic lives in engine/personality/core.py."""

    ACHIEVEMENTS = DIALOGUE_ACHIEVEMENTS

    def __init__(self):
        self.data_path = Path.home() / ".stormy_data.json"
        self.data = self._load_data()
        self.engine = PersonalityEngine(PersonalityConfig(name="Stormy"))

    def _load_data(self) -> dict:
        if self.data_path.exists():
            try:
                return json.loads(self.data_path.read_text())
            except Exception:
                pass
        return {
            "achievements": [],
            "check_count": 0,
            "rain_days": 0,
            "last_check_date": None,
            "streak": 0,
            "checks_today": 0,
            "weekend_checks": 0,
        }

    def _save_data(self):
        try:
            self.data_path.write_text(json.dumps(self.data, indent=2))
        except Exception:
            pass

    def get_greeting(self) -> str:
        return self.engine.get_greeting()

    def get_weather_comment(self, weather: WeatherData) -> str:
        weather_type = WEATHER_TYPE_MAP.get(weather.condition, "clear")
        self.engine.update(weather_type)
        return self.engine.get_weather_comment_by_condition(weather.condition)

    def get_temp_comment(self, temp_f: float) -> str:
        return self.engine.get_temp_comment(temp_f)

    def check_achievements(self, weather: WeatherData) -> list:
        unlocked = []
        hour = datetime.now().hour
        today = datetime.now().strftime("%Y-%m-%d")

        if "first_check" not in self.data["achievements"]:
            self.data["achievements"].append("first_check")
            unlocked.append(self.ACHIEVEMENTS["first_check"])

        self.data["check_count"] += 1

        if self.data["check_count"] >= 100 and "century_club" not in self.data["achievements"]:
            self.data["achievements"].append("century_club")
            unlocked.append(self.ACHIEVEMENTS["century_club"])

        if self.data.get("last_check_date") == today:
            self.data["checks_today"] = self.data.get("checks_today", 0) + 1
        else:
            self.data["checks_today"] = 1

        if self.data["checks_today"] >= 10 and "marathon_watcher" not in self.data["achievements"]:
            self.data["achievements"].append("marathon_watcher")
            unlocked.append(self.ACHIEVEMENTS["marathon_watcher"])

        if self.data["last_check_date"] != today:
            yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
            if self.data["last_check_date"] == yesterday:
                self.data["streak"] += 1
            else:
                self.data["streak"] = 1
            self.data["last_check_date"] = today

        if weather.condition == WeatherCondition.THUNDERSTORM and "storm_chaser" not in self.data["achievements"]:
            self.data["achievements"].append("storm_chaser")
            unlocked.append(self.ACHIEVEMENTS["storm_chaser"])

        if weather.condition in (WeatherCondition.SNOW, WeatherCondition.HEAVY_SNOW) and "snow_day" not in self.data["achievements"]:
            self.data["achievements"].append("snow_day")
            unlocked.append(self.ACHIEVEMENTS["snow_day"])

        if weather.condition == WeatherCondition.FOG and "fog_master" not in self.data["achievements"]:
            self.data["achievements"].append("fog_master")
            unlocked.append(self.ACHIEVEMENTS["fog_master"])

        if weather.condition in (WeatherCondition.RAIN, WeatherCondition.HEAVY_RAIN, WeatherCondition.DRIZZLE):
            self.data["rain_days"] += 1
            if self.data["rain_days"] >= 10 and "rain_lover" not in self.data["achievements"]:
                self.data["achievements"].append("rain_lover")
                unlocked.append(self.ACHIEVEMENTS["rain_lover"])
            if hour >= 21 or hour < 5:
                if "noir_night" not in self.data["achievements"]:
                    self.data["achievements"].append("noir_night")
                    unlocked.append(self.ACHIEVEMENTS["noir_night"])

        if 0 <= hour < 5 and "night_owl" not in self.data["achievements"]:
            self.data["achievements"].append("night_owl")
            unlocked.append(self.ACHIEVEMENTS["night_owl"])

        if 5 <= hour < 6 and "early_bird" not in self.data["achievements"]:
            self.data["achievements"].append("early_bird")
            unlocked.append(self.ACHIEVEMENTS["early_bird"])

        if hour == 0 and datetime.now().minute < 5 and "midnight_oracle" not in self.data["achievements"]:
            self.data["achievements"].append("midnight_oracle")
            unlocked.append(self.ACHIEVEMENTS["midnight_oracle"])

        if weather.temperature_f >= 100 and "temp_extreme_hot" not in self.data["achievements"]:
            self.data["achievements"].append("temp_extreme_hot")
            unlocked.append(self.ACHIEVEMENTS["temp_extreme_hot"])

        if weather.temperature_f <= 0 and "temp_extreme_cold" not in self.data["achievements"]:
            self.data["achievements"].append("temp_extreme_cold")
            unlocked.append(self.ACHIEVEMENTS["temp_extreme_cold"])

        if 76.5 <= weather.temperature_f <= 77.5 and "lucky_seven" not in self.data["achievements"]:
            self.data["achievements"].append("lucky_seven")
            unlocked.append(self.ACHIEVEMENTS["lucky_seven"])

        if (71 <= weather.temperature_f <= 73 and
            weather.condition == WeatherCondition.CLEAR and
            getattr(weather, 'humidity', 100) < 60 and
            "perfect_day" not in self.data["achievements"]):
            self.data["achievements"].append("perfect_day")
            unlocked.append(self.ACHIEVEMENTS["perfect_day"])

        if getattr(weather, 'humidity', 0) > 90 and "humidity_hero" not in self.data["achievements"]:
            self.data["achievements"].append("humidity_hero")
            unlocked.append(self.ACHIEVEMENTS["humidity_hero"])

        if getattr(weather, 'wind_speed', 0) > 30 and "wind_warrior" not in self.data["achievements"]:
            self.data["achievements"].append("wind_warrior")
            unlocked.append(self.ACHIEVEMENTS["wind_warrior"])

        if self.data["streak"] >= 7 and "consistent" not in self.data["achievements"]:
            self.data["achievements"].append("consistent")
            unlocked.append(self.ACHIEVEMENTS["consistent"])

        self._save_data()
        return unlocked

    def log_creature_sighting(self, name: str):
        """Record a creature sighting in persistent data."""
        sightings = self.data.setdefault("creature_sightings", {})
        sightings[name] = sightings.get(name, 0) + 1
        self._save_data()

    def get_creature_sightings(self) -> dict:
        return self.data.get("creature_sightings", {})

    def get_random_quip(self) -> str:
        return self.engine.get_quip(meta_chance=0.4)

    def get_mood(self) -> Mood:
        return self.engine.current_mood

    def get_callback(self) -> str:
        return self.engine.get_callback()


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class WeatherDashboard:
    """The main Stormy weather dashboard."""
    
    def __init__(self, screen: Screen, weather: WeatherData):
        self.screen = screen
        self.weather = weather
        self.width = screen.width
        self.height = screen.height
        self.frame = 0
        
        # Personality engine
        self.stormy = StormyPersonality()
        self.current_comment = self.stormy.get_weather_comment(weather)
        self.greeting = self.stormy.get_greeting()
        self.new_achievements = self.stormy.check_achievements(weather)
        self.achievement_display_timer = 120 if self.new_achievements else 0
        
        # Mood-based face - wise and contemplative
        hour = datetime.now().hour
        if weather.condition == WeatherCondition.THUNDERSTORM:
            self.face = "concerned"
        elif weather.condition == WeatherCondition.CLEAR:
            self.face = "knowing" if random.random() > 0.5 else "amused"
        elif weather.condition == WeatherCondition.FOG:
            self.face = "contemplative"
        elif weather.condition in (WeatherCondition.RAIN, WeatherCondition.HEAVY_RAIN):
            self.face = "wise"
        elif hour < 6 or hour > 22:
            self.face = "contemplative"
        else:
            self.face = random.choice(list(STORMY_FACES.keys()))
        
        # Layout
        self.sidebar_width = min(50, max(42, self.width // 3))
        self.animation_start_x = self.sidebar_width + 1
        self.animation_width = self.width - self.sidebar_width - 2
        
        # Animation
        self.particles = ParticleSystem()
        self.lightning_active = False
        self.lightning_timer = 0
        self.comment_timer = 0
        self.quip_mode = False
        
        # ADVANCED PHYSICS SYSTEMS - "The brain behind the beauty"
        # Initialize turbulence field for realistic wind patterns
        self.turbulence = TurbulenceField()
        
        # Wind gust system with base wind from actual weather
        wind_rad = math.radians(self.weather.wind_direction)
        base_wind_x = math.sin(wind_rad) * self.weather.wind_speed_mph * 0.01
        base_wind_y = math.cos(wind_rad) * self.weather.wind_speed_mph * 0.005
        self.wind_gusts = WindGustSystem(base_wind_x, base_wind_y)
        
        # Perlin noise for cloud generation
        self.cloud_noise = PerlinNoise()
        self.cloud_time = 0
        
        # ═══════════════════════════════════════════════════════════════════
        # ATMOSPHERIC MODEL (engine.physics.atmosphere)
        # Real barometric formula: P(h) = P₀ × exp(-Mgh/RT)
        # ═══════════════════════════════════════════════════════════════════
        cloud_cover = {
            WeatherCondition.CLEAR: 0, WeatherCondition.PARTLY_CLOUDY: 40,
            WeatherCondition.CLOUDY: 80, WeatherCondition.FOG: 100,
            WeatherCondition.RAIN: 70, WeatherCondition.HEAVY_RAIN: 90,
            WeatherCondition.THUNDERSTORM: 100, WeatherCondition.SNOW: 80,
        }.get(self.weather.condition, 50)
        
        self.atmo_state = AtmosphericState(
            temperature_c=self.weather.temperature_c,
            pressure_hpa=getattr(self.weather, 'pressure_mb', 1013.25),
            humidity_percent=self.weather.humidity,
            wind_speed_ms=self.weather.wind_speed_mph * 0.44704,
            cloud_cover_percent=cloud_cover
        )
        self.atmo_model = AtmosphericModel(self.atmo_state)
        self.stability_class = self.atmo_model.classify_stability()
        
        # Calculate "feels like" using REAL atmospheric equations
        if self.weather.temperature_c < 10 and self.weather.wind_speed_mph > 3:
            self.feels_like_c = calculate_wind_chill(
                self.weather.temperature_c, self.weather.wind_speed_mph * 0.44704
            )
        elif self.weather.temperature_c > 27 and self.weather.humidity > 40:
            self.feels_like_c = calculate_heat_index(
                self.weather.temperature_c, self.weather.humidity
            )
        else:
            self.feels_like_c = self.weather.temperature_c
        
        # ═══════════════════════════════════════════════════════════════════
        # ENGINE PARTICLE SYSTEM (engine.physics.particles)
        # Full physics: Vector2, forces, Semi-implicit Euler integration
        # ═══════════════════════════════════════════════════════════════════
        self.engine_physics_config = PhysicsConfig(
            gravity=GRAVITY,
            air_resistance=AIR_RESISTANCE,
            integration=IntegrationType.SEMI_IMPLICIT,
            max_velocity=10.0
        )
        self.engine_particle_system = EngineParticleSystem(
            self.engine_physics_config,
            bounds=(self.animation_start_x, 0, self.width, self.height)
        )
        self.engine_particle_system.add_force_generator(GravityForce(GRAVITY))
        self.engine_particle_system.add_force_generator(DragForce(AIR_RESISTANCE))
        self.engine_wind_force = WindForce(
            base_velocity=Vector2(base_wind_x, base_wind_y),
            turbulence_func=lambda x, y: self.turbulence.get_turbulence(x, y)
        )
        self.engine_particle_system.add_force_generator(self.engine_wind_force)
        
        # ═══════════════════════════════════════════════════════════════════
        # 📊 PERFORMANCE MONITORING (engine.rendering.core)
        # ═══════════════════════════════════════════════════════════════════
        self.render_stats = _render_stats
        self.frame_budget = _frame_budget
        self.render_queue = RenderQueue()  # Layered rendering queue
        # Advanced noise generators for organic effects
        self.simplex_noise = SimplexNoise(seed=int(time.time()))
        self.domain_warp = DomainWarp(FractalNoise(), warp_strength=4.0)  # For warped cloud shapes
        
        # Advanced lightning bolts (branching fractals)
        self.lightning_bolts: List[LightningBolt] = []
        self.flash_intensity = 0
        
        # Physics-based particles (separate from simple particle system)
        self.physics_particles: List[PhysicsParticle] = []
        
        # Ground accumulation (rain puddles / snow drifts)
        self.ground_accumulation = [0] * self.animation_width
        
        # Easter egg creatures - rare supernatural visitors!
        self.easter_eggs = EasterEggManager(
            self.animation_start_x, 
            self.animation_width, 
            self.height
        )
        
        # ═══════════════════════════════════════════════════════════════════
        # ENHANCED FEATURES INITIALIZATION
        # ═══════════════════════════════════════════════════════════════════
        
        # Dashboard state for UI toggles
        self.show_forecast = True
        self.show_alerts = True
        self.show_sidebar_extras = True
        self.use_metric = False
        self.show_help = False
        
        # Notification system
        if INTERACTIVE_AVAILABLE:
            self.notifications = NotificationManager()
            self.input_handler = InputHandler()
            self.screenshot_capture = ScreenshotCapture()
        else:
            self.notifications = None
            self.input_handler = None
        
        # Forecast data (fetched asynchronously-ish)
        self.forecast_data: Optional[ForecastData] = None
        self.alerts: List[WeatherAlert] = []
        self.astro_data: Optional[AstronomicalData] = None
        self.env_data: Optional[EnvironmentalData] = None
        self._extended_data_fetched = False  # Lazy load on first draw
        
        # Special effects manager
        if SPECIAL_EFFECTS_AVAILABLE:
            self.special_effects = SpecialEffectsManager(
                self.animation_width,
                self.height - 6
            )
            # Determine which special effects to enable based on conditions
            self._setup_special_effects()
        else:
            self.special_effects = None
        
        # Enhanced achievement manager
        if ACHIEVEMENTS_AVAILABLE:
            self.achievement_manager = AchievementManager()
            self._check_enhanced_achievements()
        else:
            self.achievement_manager = None
        
        # Weather history database + sparklines
        try:
            from lib.weather_extended import WeatherDatabase
            from lib.sparkline import sparkline_with_range
            self.weather_db = WeatherDatabase()
            self.weather_db.log_weather(weather, self.env_data)
            self._sparkline_renderer = sparkline_with_range
        except Exception:
            self.weather_db = None
            self._sparkline_renderer = None

        # UI Panels
        if PANELS_AVAILABLE:
            self.forecast_panel = ForecastPanel(screen, self.use_metric)
            self.alert_banner = AlertBanner(screen)
            self.astro_panel = AstronomicalPanel(screen)
            self.env_panel = EnvironmentalPanel(screen)
            self.achievement_display = AchievementDisplay(screen)
        else:
            self.forecast_panel = None
            self.alert_banner = None
        
        self._setup_animation()
    
    def _fetch_extended_data(self):
        """Fetch extended weather data (forecast, alerts, astronomical, environmental)."""
        if not EXTENDED_WEATHER_AVAILABLE:
            return
        
        lat = getattr(self.weather, 'lat', 33.0185)
        lon = getattr(self.weather, 'lon', -80.1756)
        
        try:
            # Fetch 7-day forecast
            self.forecast_data = fetch_forecast(lat, lon)
        except Exception as e:
            self.forecast_data = None
        
        try:
            # Fetch weather alerts (US only via NWS)
            self.alerts = fetch_weather_alerts(lat, lon)
        except Exception:
            self.alerts = []
        
        try:
            # Fetch astronomical data (sunrise, sunset, moon phase)
            self.astro_data = fetch_astronomical_data(lat, lon)
        except Exception:
            self.astro_data = None
        
        try:
            # Fetch environmental data (UV, AQI)
            self.env_data = fetch_environmental_data(lat, lon)
        except Exception:
            self.env_data = None
    
    def _setup_special_effects(self):
        """Configure special effects based on weather conditions."""
        if not self.special_effects:
            return
        
        c = self.weather.condition
        hour = datetime.now().hour
        is_night = hour < 6 or hour >= 20
        
        # Map condition enum to string
        condition_map = {
            WeatherCondition.CLEAR: 'clear',
            WeatherCondition.PARTLY_CLOUDY: 'partly_cloudy',
            WeatherCondition.CLOUDY: 'cloudy',
            WeatherCondition.RAIN: 'rain',
            WeatherCondition.HEAVY_RAIN: 'heavy_rain',
            WeatherCondition.THUNDERSTORM: 'thunderstorm',
            WeatherCondition.SNOW: 'snow',
            WeatherCondition.HEAVY_SNOW: 'heavy_snow',
            WeatherCondition.FOG: 'fog',
        }
        condition_str = condition_map.get(c, 'clear')
        
        # Use the manager's update_for_conditions method
        lat = getattr(self.weather, 'lat', 33.0185)
        self.special_effects.update_for_conditions(
            temperature_f=self.weather.temperature_f,
            condition=condition_str,
            is_night=is_night,
            latitude=lat,
            humidity=self.weather.humidity,
            wind_speed=self.weather.wind_speed_mph,
        )

    def _check_enhanced_achievements(self):
        """Check for new achievements with enhanced system."""
        if not self.achievement_manager:
            return
        
        # Call check_weather with appropriate parameters
        newly_unlocked = self.achievement_manager.check_weather(
            temperature_f=self.weather.temperature_f,
            condition=self.weather.condition.name.lower(),
            humidity=self.weather.humidity,
            pressure=getattr(self.weather, 'pressure', 1013),
            uv_index=getattr(self.env_data, 'uv_index', 0) if self.env_data else 0,
            aqi=getattr(self.env_data, 'aqi', 0) if self.env_data else 0,
            location=getattr(self.weather, 'location', ''),
            latitude=getattr(self.weather, 'lat', 0),
            alerts=[a.title for a in self.alerts] if self.alerts else [],
        )
        
        # Queue achievement notifications
        if newly_unlocked and self.notifications:
            for achievement in newly_unlocked:
                self.notifications.add_achievement(
                    achievement.name,
                    achievement.emoji
                )

    def handle_input(self, key):
        """Handle keyboard input with enhanced controls."""
        if key is None:
            return None
        
        # Q to quit
        if key in (ord('q'), ord('Q')):
            return True
        
        # R to refresh
        if key in (ord('r'), ord('R')):
            return 'refresh'
        
        # L to search location
        if key in (ord('s'), ord('S'), ord('l'), ord('L')):
            return 'search'
        
        # A to show achievements
        if key in (ord('a'), ord('A')):
            return 'achievements'
        
        # ? to toggle help
        if key == ord('?'):
            self.show_help = not self.show_help
            return 'help'
        
        # F to toggle forecast panel
        if key in (ord('f'), ord('F')):
            if hasattr(self, 'show_forecast'):
                self.show_forecast = not self.show_forecast
            return 'forecast'
        
        # U to toggle metric/imperial
        if key in (ord('u'), ord('U')):
            if hasattr(self, 'use_metric'):
                self.use_metric = not self.use_metric
                if self.notifications:
                    unit = "metric" if self.use_metric else "imperial"
                    self.notifications.add_info(f"Switched to {unit} units")
            return None
        
        
        # B to show bestiary
        if key in (ord('b'), ord('B')):
            return 'bestiary'

        # Space to toggle quips
        if key == ord(" "):
            self.quip_mode = not self.quip_mode
            if self.quip_mode:
                self.current_comment = self.stormy.get_random_quip()
            else:
                self.current_comment = self.stormy.get_weather_comment(self.weather)
            return None
        return None
    
    def _draw_help_overlay(self):
        """Draw a help overlay with available keyboard shortcuts."""
        screen = self.screen
        
        help_lines = [
            "═══════════ KEYBOARD SHORTCUTS ═══════════",
            "",
            "  Q       - Quit dashboard",
            "  R       - Refresh weather data",
            "  S/L     - Search new location",
            "  A       - View achievements",
            "  B       - Creature bestiary",
            "  F       - Toggle forecast panel",
            "  U       - Toggle metric/imperial",
            "  ?       - Show/hide this help",
            "  Space   - Toggle Stormy quips",
            "",
            "════════════════════════════════════════════",
            "       Press any key to dismiss",
        ]
        
        # Calculate overlay position
        max_width = max(len(line) for line in help_lines)
        box_width = max_width + 4
        box_height = len(help_lines) + 2
        start_x = (screen.width - box_width) // 2
        start_y = (screen.height - box_height) // 2
        
        # Draw background box
        for dy in range(box_height):
            screen.print_at(" " * box_width, start_x, start_y + dy, 
                          colour=7, bg=0)
        
        # Draw help text
        for i, line in enumerate(help_lines):
            screen.print_at(line.center(max_width), start_x + 2, start_y + 1 + i,
                          colour=7, bg=0)


    def _setup_animation(self):
        """Configure particles based on weather - EVERY condition has effects."""
        c = self.weather.condition
        
        # Rain variants
        if c in (WeatherCondition.RAIN, WeatherCondition.HEAVY_RAIN, WeatherCondition.DRIZZLE):
            self.particles.gravity = 0.05
            self.particles.wind = self.weather.wind_speed_mph / 80
            if c == WeatherCondition.HEAVY_RAIN:
                self.particle_chars = ["|", "|", ":"]
                self.spawn_rate = 20
            elif c == WeatherCondition.RAIN:
                self.particle_chars = ["|", ":", "."]
                self.spawn_rate = 12
            else:  # Drizzle
                self.particle_chars = [".", ".", "'"]
                self.spawn_rate = 5
            self.particle_colour = Theme.FROST
        
        # Snow variants    
        elif c in (WeatherCondition.SNOW, WeatherCondition.HEAVY_SNOW):
            self.particles.gravity = 0.01
            self.particles.wind = self.weather.wind_speed_mph / 100
            self.particle_chars = ["*", "+", ".", "o", "'"]
            self.particle_colour = Theme.SNOW
            self.spawn_rate = 15 if c == WeatherCondition.HEAVY_SNOW else 8
        
        # Freezing rain - ice pellets
        elif c == WeatherCondition.FREEZING_RAIN:
            self.particles.gravity = 0.06
            self.particles.wind = self.weather.wind_speed_mph / 60
            self.particle_chars = ["'", ".", "*", "o"]
            self.particle_colour = Theme.FROST
            self.spawn_rate = 10
        
        # Thunderstorm
        elif c == WeatherCondition.THUNDERSTORM:
            self.particles.gravity = 0.08
            self.particles.wind = self.weather.wind_speed_mph / 40
            self.particle_chars = ["|", "|", ":"]
            self.particle_colour = Theme.FROST
            self.spawn_rate = 18
        
        # Fog - thick drifting mist layers
        elif c == WeatherCondition.FOG:
            self.particles.gravity = 0
            self.particles.wind = 0.015  # Slow, creeping mist
            self.particle_chars = ["░", "▒", "≋", "~", "▓"]  # Dense mist chars
            self.particle_colour = Theme.MUTED
            self.spawn_rate = 8  # Dense fog
        
        # CLOUDY - drifting cloud wisps
        elif c == WeatherCondition.CLOUDY:
            self.particles.gravity = 0
            self.particles.wind = 0.04 + (self.weather.wind_speed_mph / 200)
            self.particle_chars = ["=", "~", "-", "."]
            self.particle_colour = Theme.MUTED
            self.spawn_rate = 3
        
        # PARTLY CLOUDY - sun glints with occasional cloud wisps
        elif c == WeatherCondition.PARTLY_CLOUDY:
            self.particles.gravity = 0
            self.particles.wind = 0.05 + (self.weather.wind_speed_mph / 200)
            self.particle_chars = ["·", "✦", ".", "☁", "*"]  # Mix of sun sparkles and wisps
            self.particle_colour = Theme.SUN  # Golden sun color
            self.spawn_rate = 3
        
        # CLEAR - twinkling stars/dust motes/sun sparkles
        elif c == WeatherCondition.CLEAR:
            self.particles.gravity = 0
            self.particles.wind = 0.01
            self.particle_chars = [".", "*", "+", "'"]
            self.particle_colour = Theme.SUN
            self.spawn_rate = 2
        
        # UNKNOWN / fallback - ambient particles
        else:
            self.particles.gravity = 0
            self.particles.wind = 0.02
            self.particle_chars = [".", "'"]
            self.particle_colour = Theme.MUTED
            self.spawn_rate = 1

    def transition_to(self, new_weather: WeatherData):
        """Crossfade to new weather: decay old particles, ramp in new ones."""
        self._transition_frames = 0
        self._transition_total = 60  # ~2 seconds at 30fps
        self._old_spawn_rate = self.spawn_rate
        self._old_particle_chars = self.particle_chars
        self._old_particle_colour = self.particle_colour

        # Update core weather state
        self.weather = new_weather
        self.current_comment = self.stormy.get_weather_comment(new_weather)
        self.greeting = self.stormy.get_greeting()
        self.new_achievements = self.stormy.check_achievements(new_weather)
        if self.new_achievements:
            self.achievement_display_timer = 120

        # Configure new particle settings (saved for ramp-in)
        self._setup_animation()
        self._new_spawn_rate = self.spawn_rate
        self.spawn_rate = 0  # Start at zero, ramp up

        # Log to history db
        if self.weather_db:
            try:
                self.weather_db.log_weather(new_weather, self.env_data)
            except Exception:
                pass

        # Re-fetch extended data
        self._extended_data_fetched = False

    def _update_transition(self):
        """Handle crossfade interpolation during weather transitions."""
        if not hasattr(self, '_transition_frames'):
            return
        self._transition_frames += 1
        t = self._transition_frames / self._transition_total
        if t >= 1.0:
            self.spawn_rate = self._new_spawn_rate
            del self._transition_frames
            return
        # Ease-in: new particles ramp up using smoothstep
        smooth = t * t * (3 - 2 * t)
        self.spawn_rate = int(self._new_spawn_rate * smooth)

    def update(self):
        """Update animation state with advanced physics."""
        self.frame += 1
        self._update_transition()
        
        # Lazy fetch extended data on first update
        if not self._extended_data_fetched:
            self._extended_data_fetched = True
            import threading
            threading.Thread(target=self._fetch_extended_data, daemon=True).start()
        # ═══════════════════════════════════════════════════════════════════
        # UPDATE ADVANCED PHYSICS SYSTEMS
        # ═══════════════════════════════════════════════════════════════════
        self.turbulence.update()
        self.wind_gusts.update()
        self.cloud_time += 0.02
        
        # Get current wind (base + gusts)
        wind_x, wind_y = self.wind_gusts.get_wind()
        
        # ═══════════════════════════════════════════════════════════════════
        # UPDATE ENGINE PARTICLE SYSTEM (engine.physics.particles)
        # ═══════════════════════════════════════════════════════════════════
        self.frame_budget.begin_frame()
        self.engine_particle_system.update(1.0)  # Uses Vector2, forces, integrators
        frame_ms = self.frame_budget.end_frame()
        self.render_stats.record_frame(frame_ms / 1000.0, self.engine_particle_system.active_particle_count)
        
        # Update legacy physics particles (kept for compatibility)
        for p in self.physics_particles:
            turb_x, turb_y = self.turbulence.get_turbulence(p.x, p.y)
            p.update(wind_x, wind_y, turb_x, turb_y)
            
            # Ground accumulation for rain/snow
            if p.y >= self.height - 3 and not p.collided:
                idx = int(p.x - self.animation_start_x) % self.animation_width
                if 0 <= idx < len(self.ground_accumulation):
                    self.ground_accumulation[idx] = min(5, self.ground_accumulation[idx] + 0.5)
                    p.collided = True
        
        # Remove expired physics particles
        self.physics_particles = [
            p for p in self.physics_particles 
            if not p.is_expired(self.width, self.height)
        ]
        
        # Update lightning bolts (branching fractals)
        for bolt in self.lightning_bolts:
            bolt.update()
        self.lightning_bolts = [b for b in self.lightning_bolts if not b.is_expired()]
        
        # Flash intensity decay
        if self.flash_intensity > 0:
            self.flash_intensity *= 0.7
        
        # Ground accumulation evaporation
        for i in range(len(self.ground_accumulation)):
            if random.random() < 0.005:
                self.ground_accumulation[i] = max(0, self.ground_accumulation[i] - 0.1)
        
        # ═══════════════════════════════════════════════════════════════════
        # STORMY'S PERSONALITY UPDATES
        # ═══════════════════════════════════════════════════════════════════
        self.comment_timer += 1
        if self.comment_timer > 300:
            self.comment_timer = 0
            if random.random() > 0.6:
                self.quip_mode = not self.quip_mode
                if self.quip_mode:
                    self.current_comment = self.stormy.get_random_quip()
                else:
                    self.current_comment = self.stormy.get_weather_comment(self.weather)
        
        if self.achievement_display_timer > 0:
            self.achievement_display_timer -= 1
        
        # ═══════════════════════════════════════════════════════════════════
        # SPAWN PARTICLES (Using physics-based system for precipitation)
        # ═══════════════════════════════════════════════════════════════════
        drifters = (WeatherCondition.CLOUDY, WeatherCondition.PARTLY_CLOUDY, 
                   WeatherCondition.CLEAR, WeatherCondition.FOG)
        is_drifter = self.weather.condition in drifters
        is_precipitation = self.weather.condition in (
            WeatherCondition.RAIN, WeatherCondition.HEAVY_RAIN, WeatherCondition.DRIZZLE,
            WeatherCondition.SNOW, WeatherCondition.HEAVY_SNOW, WeatherCondition.THUNDERSTORM
        )
        
        # Spawn physics-based particles for precipitation
        if is_precipitation and self.frame % 2 == 0:
            for _ in range(self.spawn_rate // 2):
                x = random.uniform(self.animation_start_x + 2, self.width - 3)
                char = random.choice(self.particle_chars) if self.particle_chars else "."
                
                if self.weather.condition in (WeatherCondition.SNOW, WeatherCondition.HEAVY_SNOW):
                    # Light, floaty snow
                    p = PhysicsParticle(x, 3, char, Theme.SNOW,
                                       vx=random.uniform(-0.2, 0.2),
                                       vy=random.uniform(0.1, 0.4),
                                       mass=0.2, buoyancy=0.3)
                else:
                    # Heavier rain
                    p = PhysicsParticle(x, 3, char, Theme.FROST,
                                       vx=random.uniform(-0.3, 0.3),
                                       vy=random.uniform(1.0, 2.5),
                                       mass=0.6)
                self.physics_particles.append(p)
        
        # Regular particles for drifting effects
        for _ in range(self.spawn_rate):
            if self.particle_chars:
                if is_drifter:
                    p = Particle(
                        x=self.animation_start_x + 2,
                        y=random.uniform(4, self.height - 6),
                        vx=random.uniform(0.3, 0.8),
                        vy=random.uniform(-0.05, 0.05),
                        char=random.choice(self.particle_chars),
                        colour=self.particle_colour
                    )
                    p._horiz = True
                else:
                    p = Particle(
                        x=random.uniform(self.animation_start_x + 2, self.width - 3),
                        y=random.uniform(2, 5),
                        vx=self.particles.wind * 3 + random.uniform(-0.15, 0.15),
                        vy=random.uniform(0.4, 1.4),
                        char=random.choice(self.particle_chars),
                        colour=self.particle_colour
                    )
                    p._horiz = False
                    if self.weather.condition in (WeatherCondition.SNOW, WeatherCondition.HEAVY_SNOW):
                        p._drift = random.uniform(0, 6.28)
                self.particles.spawn(p)
        
        for p in self.particles.particles:
            if hasattr(p, '_drift'):
                p.x += 0.3 * math.sin(p.age * 0.07 + p._drift)
            if getattr(p, '_horiz', False):
                p.x += p.vx
                p.y += p.vy
                p.age += 1
            else:
                p.update(self.particles.gravity, self.particles.wind, 0)
        
        self.particles.particles = [
            p for p in self.particles.particles
            if 3 <= p.y < self.height - 2 and self.animation_start_x < p.x < self.width - 1
        ]
        
        # ═══════════════════════════════════════════════════════════════════
        # ADVANCED LIGHTNING SYSTEM (Branching fractals)
        # ═══════════════════════════════════════════════════════════════════
        if self.weather.condition == WeatherCondition.THUNDERSTORM:
            if self.lightning_timer > 0:
                self.lightning_timer -= 1
            elif random.random() < 0.02:
                # Spawn a new branching lightning bolt!
                bolt_x = random.randint(self.animation_start_x + 10, self.width - 10)
                bolt = LightningBolt(
                    bolt_x - self.animation_start_x, 
                    3, 
                    random.randint(self.height // 2, self.height - 5),
                    self.animation_width
                )
                self.lightning_bolts.append(bolt)
                self.lightning_active = True
                self.lightning_timer = random.randint(3, 6)
                self.flash_intensity = 1.0  # Screen flash
            else:
                self.lightning_active = len(self.lightning_bolts) > 0
        
        # Easter egg creatures - try to spawn, track sightings, update
        hour = datetime.now().hour
        was_active = self.easter_eggs.is_active
        spawned = self.easter_eggs.try_spawn(self.weather.condition, hour)
        if spawned and self.easter_eggs.current_creature_name:
            self.stormy.log_creature_sighting(self.easter_eggs.current_creature_name)
        self.easter_eggs.update()
        
        # ═══════════════════════════════════════════════════════════════════
        # UPDATE ENHANCED FEATURES
        # ═══════════════════════════════════════════════════════════════════
        
        # Update special effects
        if self.special_effects:
            self.special_effects.update()
        
        # Update notifications
        if self.notifications:
            self.notifications.update()

    def draw(self):
        """Draw the dashboard with layer-timed rendering."""
        import time as _time
        
        # Clear render queue for this frame
        self.render_queue.clear()
        
        # Background flash based on lightning intensity
        if self.flash_intensity > 0.7:
            bg = Screen.COLOUR_WHITE
        elif self.flash_intensity > 0.3:
            bg = Theme.SUN
        elif self.lightning_active:
            bg = Theme.SUN
        else:
            bg = Screen.COLOUR_BLACK
        self.screen.clear_buffer(bg, Screen.A_NORMAL, bg)
        
        # Layer 1: UI Background (sidebar)
        _t0 = _time.perf_counter()
        self._draw_sidebar()
        self.render_stats.record_layer("sidebar", _time.perf_counter() - _t0)
        
        # Layer 2: Animation (particles, weather, etc)
        _t0 = _time.perf_counter()
        self._draw_animation()
        self.render_stats.record_layer("animation", _time.perf_counter() - _t0)
        
        # Layer 3: UI Foreground (footer)
        _t0 = _time.perf_counter()
        self._draw_footer()
        self.render_stats.record_layer("footer", _time.perf_counter() - _t0)
        
        # Achievement popup
        if self.achievement_display_timer > 0 and self.new_achievements:
            self._draw_achievement_popup()
    
    def _draw_box(self, x: int, y: int, w: int, h: int, title: str = "", colour=Theme.FROST):
        """Draw a box with optional title."""
        self.screen.print_at("+" + "-" * (w - 2) + "+", x, y, colour=colour)
        for row in range(1, h - 1):
            self.screen.print_at("|", x, y + row, colour=colour)
            self.screen.print_at("|", x + w - 1, y + row, colour=colour)
        self.screen.print_at("+" + "-" * (w - 2) + "+", x, y + h - 1, colour=colour)
        
        if title:
            t = f" {title} "
            tx = x + (w - len(t)) // 2
            self.screen.print_at(t, tx, y, colour=Theme.SUN)
    
    def _draw_sidebar(self):
        """Draw the info sidebar."""
        sw = self.sidebar_width
        
        # Main box
        self._draw_box(0, 0, sw, self.height - 1, "STORMY")
        
        y = 2
        
        # Weather mascot - cute face that changes with weather
        mascot = WEATHER_MASCOT.get(self.weather.condition, WEATHER_MASCOT[WeatherCondition.UNKNOWN])
        for line in mascot:
            fx = max(2, (sw - len(line)) // 2)
            self.screen.print_at(line, fx, y, colour=Theme.MAGIC)
            y += 1
        y += 1
        
        # Greeting (wrapped if needed)
        greeting_words = self.greeting.split()
        greeting_lines = []
        greeting_line = ""
        max_greeting_width = sw - 8  # More conservative width for proper wrapping
        for word in greeting_words:
            # Truncate very long words
            if len(word) > max_greeting_width:
                word = word[:max_greeting_width-2] + ".."
            if len(greeting_line) + len(word) + 1 <= max_greeting_width:
                greeting_line += (" " if greeting_line else "") + word
            else:
                if greeting_line:
                    greeting_lines.append(greeting_line)
                greeting_line = word
        if greeting_line:
            greeting_lines.append(greeting_line)
        
        for gl in greeting_lines[:4]:  # Max 4 lines for greeting
            gl = gl[:sw-4]  # Ensure line fits within sidebar
            gx = max(2, (sw - len(gl)) // 2)
            self.screen.print_at(gl, gx, y, colour=Theme.FROST)
            y += 1
        y += 1
        
        # Big temperature
        temp_val = int(round(self.weather.temperature_f))
        temp_str = f"{temp_val}"
        big_lines = ["", "", ""]
        for char in temp_str:
            d = BIG_DIGITS.get(char, BIG_DIGITS[' '])
            for i in range(3):
                big_lines[i] += d[i]
        # Add degree symbol
        for i in range(3):
            big_lines[i] += BIG_DIGITS['°'][i]
        
        temp_width = len(big_lines[0])
        tx = max(2, (sw - temp_width) // 2)
        
        # Color based on temp
        if temp_val < 32:
            temp_colour = Theme.FROST
        elif temp_val > 85:
            temp_colour = Theme.DANGER
        else:
            temp_colour = Theme.SUN
        
        for i, line in enumerate(big_lines):
            self.screen.print_at(line, tx, y + i, colour=temp_colour)
        y += 4
        
        # Feels like / Celsius
        feels = f"Feels: {int(round(self.weather.temperature_f))}F | {int(round(self.weather.temperature_c))}C"
        feels_centered = feels.center(sw - 4)[:sw-4]
        self.screen.print_at(feels_centered, 2, y, colour=Theme.MUTED)
        y += 2
        
        # Weather scene art
        scene = WEATHER_SCENES.get(self.weather.condition, WEATHER_SCENES[WeatherCondition.CLOUDY])
        for line in scene:
            if y < self.height - 12:
                self.screen.print_at(line[:sw-4], 2, y, colour=Theme.SNOW)
                y += 1
        y += 1
        
        # Condition
        desc = self.weather.description.title()
        if len(desc) > sw - 4:
            desc = desc[:sw-7] + "..."
        dx = max(2, (sw - len(desc)) // 2)
        self.screen.print_at(desc, dx, y, colour=Theme.SNOW)
        y += 2
        
        # Divider
        self.screen.print_at("+" + "-" * (sw - 2) + "+", 0, y, colour=Theme.FROST)
        y += 1
        
        # Snarky comment (wrapped)
        comment = self.current_comment
        words = comment.split()
        lines = []
        current_line = ""
        max_text_width = sw - 8  # Leave room for: 2 spaces + quote + text + quote + margin
        for word in words:
            if len(current_line) + len(word) + 1 <= max_text_width:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
                # Handle very long words by truncating
                if len(current_line) > max_text_width:
                    current_line = current_line[:max_text_width-3] + "..."
        if current_line:
            lines.append(current_line)
        
        for line in lines[:4]:  # Max 4 lines for longer comments
            formatted = f"  \"{line}\""
            self.screen.print_at(formatted[:sw-2], 1, y, colour=Theme.MAGIC)
            y += 1
        y += 1
        
        # Stats
        if y < self.height - 6:
            stats = [
                f"  Wind: {int(self.weather.wind_speed_mph)} mph {self.weather.wind_strength}",
                f"  Humidity: {self.weather.humidity}%",
                f"  Clouds: {self.weather.clouds_percent}%",
            ]
            for stat in stats:
                if y < self.height - 4:
                    self.screen.print_at(stat[:sw-3], 1, y, colour=Theme.SNOW)
                    y += 1
        
        # Sparkline trends (24h history)
        if self.weather_db and self._sparkline_renderer and y < self.height - 8:
            try:
                trend = self.weather_db.get_trend_data(hours=24)
                spark_width = sw - 16  # leave room for label + range
                if trend["temp"] and len(trend["temp"]) >= 2:
                    y += 1
                    self.screen.print_at("+" + "-" * (sw - 2) + "+", 0, y, colour=Theme.FROST)
                    y += 1
                    spark = self._sparkline_renderer(trend["temp"], "Temp", width=spark_width)
                    self.screen.print_at(f"  {spark}"[:sw-2], 1, y, colour=Theme.SUN)
                    y += 1
                if trend["humidity"] and len(trend["humidity"]) >= 2:
                    spark = self._sparkline_renderer(trend["humidity"], "Hum%", width=spark_width)
                    self.screen.print_at(f"  {spark}"[:sw-2], 1, y, colour=Theme.FROST)
                    y += 1
                if trend["wind"] and len(trend["wind"]) >= 2:
                    spark = self._sparkline_renderer(trend["wind"], "Wind", width=spark_width)
                    self.screen.print_at(f"  {spark}"[:sw-2], 1, y, colour=Theme.SNOW)
                    y += 1
            except Exception:
                pass

        # Time and achievements at bottom
        self.screen.print_at("+" + "-" * (sw - 2) + "+", 0, self.height - 4, colour=Theme.FROST)
        
        now = datetime.now().strftime("%I:%M %p")
        achievements_count = len(self.stormy.data.get("achievements", []))
        streak = self.stormy.data.get("streak", 0)
        
        self.screen.print_at(f"  {now}", 1, self.height - 3, colour=Theme.SNOW)
        self.screen.print_at(f"  {achievements_count} achievements | {streak} day streak", 1, self.height - 2, colour=Theme.SUN)
    
    def _draw_animation(self):
        """Draw the animation area with advanced physics visualization."""
        ax = self.animation_start_x
        aw = self.animation_width
        
        title = "󱐋 LIVE" if self.weather.condition == WeatherCondition.THUNDERSTORM else "◉ LIVE"
        
        self._draw_box(ax, 0, aw, self.height - 1, title)
        
        # ═══════════════════════════════════════════════════════════════════
        # PERLIN NOISE CLOUD LAYER
        # ═══════════════════════════════════════════════════════════════════
        if self.weather.condition in (
            WeatherCondition.RAIN, WeatherCondition.HEAVY_RAIN,
            WeatherCondition.THUNDERSTORM, WeatherCondition.SNOW,
            WeatherCondition.HEAVY_SNOW, WeatherCondition.CLOUDY,
            WeatherCondition.FOG
        ):
            cloud_chars = ["█", "▓", "▒", "░"]
            for y in range(2, 6):
                for x in range(ax + 2, ax + aw - 2):
                    # Use domain warping for more organic cloud shapes
                    # Domain warp samples create swirling, flowing cloud patterns
                    base_x = (x - ax) * 0.15 + self.cloud_time
                    base_y = y * 0.3
                    
                    # Add warped displacement for organic feel
                    warp_offset = self.domain_warp.sample(base_x * 0.5, base_y * 0.5) * 0.5
                    
                    noise_val = self.cloud_noise.octave_noise(
                        base_x + warp_offset,
                        base_y + warp_offset * 0.3,
                        octaves=3
                    )
                    
                    # Threshold based on weather intensity
                    threshold = -0.3 if self.weather.condition in (
                        WeatherCondition.THUNDERSTORM, WeatherCondition.HEAVY_RAIN
                    ) else 0.0
                    
                    if noise_val > threshold:
                        char_idx = min(3, max(0, int((noise_val + 0.5) * 3)))
                        char = cloud_chars[char_idx]
                        
                        # Flash colour during lightning
                        if self.flash_intensity > 0.5:
                            colour = Screen.COLOUR_WHITE
                        elif self.lightning_active:
                            colour = Theme.SUN
                        else:
                            colour = Theme.MUTED if self.weather.condition == WeatherCondition.THUNDERSTORM else Screen.COLOUR_WHITE
                        
                        self.screen.print_at(char, x, y, colour=colour)
        
        # ═══════════════════════════════════════════════════════════════════
        # PHYSICS-BASED PARTICLES (with trails)
        # ═══════════════════════════════════════════════════════════════════
        for p in self.physics_particles:
            try:
                px, py = int(p.x), int(p.y)
                if ax + 1 <= px < ax + aw - 1 and 2 <= py < self.height - 2:
                    colour = Theme.SUN if self.lightning_active and random.random() > 0.3 else p.colour
                    self.screen.print_at(p.char, px, py, colour=colour)
                    
                    # Draw faint trail for motion blur effect
                    for i, (tx, ty) in enumerate(p.trail):
                        if ax + 1 <= tx < ax + aw - 1 and 2 <= ty < self.height - 2:
                            trail_colour = Screen.COLOUR_BLUE if i == 0 else Screen.COLOUR_BLACK
                            self.screen.print_at("·", tx, ty, colour=trail_colour)
            except Exception:
                pass
        
        # Regular particles (for drifting effects)
        for p in self.particles.particles:
            try:
                px, py = int(p.x), int(p.y)
                if ax + 1 <= px < ax + aw - 1 and 2 <= py < self.height - 2:
                    colour = Theme.SUN if self.lightning_active and random.random() > 0.3 else p.colour
                    self.screen.print_at(p.char, px, py, colour=colour)
            except Exception:
                pass
        
        # ═══════════════════════════════════════════════════════════════════
        # BRANCHING LIGHTNING (Fractal pathfinding)
        # ═══════════════════════════════════════════════════════════════════
        for bolt in self.lightning_bolts:
            bolt.draw(self.screen, ax)
        
        # Old lightning fallback
        if self.lightning_active and not self.lightning_bolts:
            self._draw_lightning()
        
        # Easter egg creatures (rare visitors!)
        colour_map = {"FROST": Theme.FROST, "SNOW": Theme.SNOW, "SUN": Theme.SUN, "DANGER": Theme.DANGER, "NATURE": Theme.NATURE, "MAGIC": Theme.MAGIC, "MUTED": Theme.MUTED}
        self.easter_eggs.draw(self.screen, colour_map, self.lightning_active)
        
        # ═══════════════════════════════════════════════════════════════════
        # 🌊 GROUND ACCUMULATION (Puddles / Snow drifts)
        # ═══════════════════════════════════════════════════════════════════
        ground_char = "▓" if self.lightning_active else "▒"
        for i, x in enumerate(range(ax + 1, ax + aw - 1)):
            self.screen.print_at(ground_char, x, self.height - 2, colour=Theme.MUTED)
            
            # Show accumulation
            if i < len(self.ground_accumulation):
                level = int(self.ground_accumulation[i])
                if level > 0:
                    if self.weather.condition in (WeatherCondition.SNOW, WeatherCondition.HEAVY_SNOW):
                        # Snow drifts
                        acc_chars = ["·", "░", "▒", "▓", "█"]
                        acc_char = acc_chars[min(level, 4)]
                        self.screen.print_at(acc_char, x, self.height - 3, colour=Theme.SNOW)
                    else:
                        # Rain puddles
                        acc_chars = ["·", "~", "≈", "∿", "≋"]
                        acc_char = acc_chars[min(level, 4)]
                        self.screen.print_at(acc_char, x, self.height - 3, colour=Theme.FROST)
        
        # Location label in animation area
        loc = f"{self.weather.location}"
        self.screen.print_at(loc[:aw-4], ax + 3, self.height - 4, colour=Theme.SNOW)
    
    def _draw_lightning(self):
        """Draw lightning bolt."""
        ax = self.animation_start_x
        aw = self.animation_width
        
        x = random.randint(ax + aw // 4, ax + 3 * aw // 4)
        y = 5
        
        while y < self.height - 5:
            self.screen.print_at(random.choice(["#", "|", "/"]), x, y, colour=Theme.SUN)
            y += 1
            x += random.choice([-1, 0, 0, 1])
            x = max(ax + 3, min(ax + aw - 4, x))
    
    def _draw_achievement_popup(self):
        """Draw achievement unlock popup."""
        if not self.new_achievements:
            return
        
        icon, name = self.new_achievements[0]
        
        popup_w = max(len(name) + 10, 30)
        popup_h = 5
        px = (self.width - popup_w) // 2
        py = (self.height - popup_h) // 2
        
        # Background
        for row in range(popup_h):
            self.screen.print_at(" " * popup_w, px, py + row, bg=Theme.MAGIC)
        
        # Border
        self._draw_box(px, py, popup_w, popup_h, "ACHIEVEMENT UNLOCKED!", colour=Theme.SUN)
        
        # Content
        text = f"{icon}  {name}"
        tx = px + (popup_w - len(text)) // 2
        self.screen.print_at(text, tx, py + 2, colour=Theme.SNOW, bg=Theme.MAGIC)
    
    def _draw_footer(self):
        """Draw footer bar."""
        footer = " [S]earch | [R]efresh | [A]chievements | [F]orecast | [?]Help | [Q]uit "
        fx = max(0, (self.width - len(footer)) // 2)
        
        # Background bar
        self.screen.print_at(" " * self.width, 0, self.height - 1, bg=Theme.FROST)
        self.screen.print_at(footer[:self.width], fx, self.height - 1, 
                            colour=Screen.COLOUR_BLACK, bg=Theme.FROST)
        
        # Watermark
        watermark = "Dr. Baklava"
        self.screen.print_at(watermark, self.width - len(watermark) - 1, self.height - 1,
                            colour=Theme.MUTED, bg=Theme.FROST)



# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def dashboard_main(screen: Screen):
    """Main dashboard loop."""
    
    # Loading screen with personality
    screen.clear()
    loading_msgs = [
        "Consulting the ancient meteorological texts...",
        "Communing with the clouds...",
        "The wind speaks... listening...",
        "Fetching weather data...",
    ]
    
    ly = screen.height // 2
    for i, msg in enumerate(loading_msgs):
        screen.print_at(" " * 40, (screen.width - 40) // 2, ly, colour=Theme.FROST)
        screen.print_at(msg, (screen.width - len(msg)) // 2, ly, colour=Theme.FROST)
        screen.refresh()
        time.sleep(0.1)
    
    if DEMO_MODE:
        from lib.mock_weather import get_demo_weather
        weather = get_demo_weather(DEMO_SCENARIO)
    else:
        weather = get_weather()
    
    if not weather:
        screen.clear()
        err = "The weather servers remain silent. As do the gods, sometimes."
        screen.print_at(err, (screen.width - len(err)) // 2, screen.height // 2, colour=Theme.DANGER)
        sass = "(Perhaps they're contemplating existence. Give them a moment.)"
        screen.print_at(sass, (screen.width - len(sass)) // 2, screen.height // 2 + 2, colour=Theme.MAGIC)
        hint = "Press any key to retry or Q to quit."
        screen.print_at(hint, (screen.width - len(hint)) // 2, screen.height // 2 + 4, colour=Theme.SNOW)
        screen.refresh()
        ev = screen.wait_for_input(30)
        if ev == ord('q') or ev == ord('Q'):
            return
        return dashboard_main(screen)
    
    dashboard = WeatherDashboard(screen, weather)
    last_fetch = time.time()
    
    while True:
        ev = screen.get_key()
        
        # Use enhanced input handler if available
        result = dashboard.handle_input(ev)
        
        if result == True:
            return  # Quit
        elif result == 'refresh':
            new_weather = get_weather(use_cache=False)
            if new_weather:
                weather = new_weather
                dashboard.transition_to(weather)
                last_fetch = time.time()
                if dashboard.notifications:
                    dashboard.notifications.add_success("Weather refreshed!")
        elif result == 'search':
            new_weather = location_search_screen(screen, Theme)
            if new_weather:
                weather = new_weather
                dashboard = WeatherDashboard(screen, weather)
                last_fetch = time.time()
        elif result == 'achievements':
            draw_achievements_screen(screen, dashboard.stormy, Theme)
            dashboard.draw()
        elif result == 'bestiary':
            draw_bestiary_screen(screen, dashboard.stormy, Theme)
            dashboard.draw()
        
        # F key now handled in handle_input for forecast toggle
        if ev in (ord('f'), ord('F')) and not dashboard.show_forecast:
            # Only trigger weather_live if forecast is disabled
            try:
                from weather_live import weather_live
                weather_live(screen)
            except Exception:
                pass
            dashboard = WeatherDashboard(screen, weather)
        
        # Auto-refresh every 5 minutes
        if time.time() - last_fetch > 300:
            new_weather = get_weather(use_cache=False)
            if new_weather:
                weather = new_weather
                dashboard.transition_to(weather)
                last_fetch = time.time()
        
        dashboard.update()
        dashboard.draw()
        
        # Draw help overlay if active
        if dashboard.show_help:
            dashboard._draw_help_overlay()
        
        screen.refresh()
        
        time.sleep(0.033)


def main():
    global DEMO_MODE, DEMO_SCENARIO
    
    import argparse
    parser = argparse.ArgumentParser(
        description="STORMY - Weather Oracle of the Terminal",
        epilog="Try it without an API key: python weather_dashboard.py --demo"
    )
    parser.add_argument(
        "--demo", 
        action="store_true",
        help="Run in demo mode with mock weather data (no API key needed)"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        choices=["clear", "rain", "thunderstorm", "snow", "fog", "cloudy", "drizzle"],
        help="Demo scenario to display (requires --demo)"
    )
    args = parser.parse_args()
    
    DEMO_MODE = args.demo
    DEMO_SCENARIO = args.scenario
    
    print("[2J[H")
    if DEMO_MODE:
        print("STORMY - Weather Oracle of the Terminal [DEMO MODE]")
        print("   Experience the weather without an API key...")
    else:
        print("STORMY - Weather Oracle of the Terminal")
        print("   The sky has wisdom to share...")
    
    while True:
        try:
            Screen.wrapper(dashboard_main)
            break
        except ResizeScreenError:
            pass
    
    print("\nStormy speaks: \"The path continues. The weather changes. You remain. Until next time.\"\n")
if __name__ == "__main__":
    main()
