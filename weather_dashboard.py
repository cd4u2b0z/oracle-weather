#!/usr/bin/env python3
"""
⚡ STORMY - Weather Oracle of the Terminal (Enhanced Edition)
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
from lib.particles import Particle, ParticleSystem
from collections import deque
from typing import List, Tuple, Optional, Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# 🆕 ENHANCED MODULES - New integrated features
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
# 🧠 PROFESSIONAL WEATHER ENGINE - Modular Architecture
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

# Global performance monitoring
_render_stats = RenderStats()
_frame_budget = FrameBudget(target_fps=30)


# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 ADVANCED PHYSICS ENGINE - "Under the hood complexity"
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
# 🎨 THEME & COLORS
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

class StormyPersonality:
    """The snarky AI that lives inside your terminal."""
    
    MOODS = ["philosophical", "deadpan", "wasteland", "bardic", "existential"]
    
    # Personality-driven weather comments - philosophical, deadpan, with wisdom
    COMMENTS = {
        WeatherCondition.CLEAR: [
            "The sun shines upon the land. It does not ask if you deserve it.",
            "Clear skies. The Divines are either pleased, or not paying attention.",
            "A fine day. Suspicious. The calm before some manner of nonsense.",
            "The sky is clear. Your path is not. But that's rather the point, isn't it.",
            "Cloudless. The ancestors smile upon you. Or they're just busy.",
            "Blue skies. The land remembers days like this. So should you.",
            "FATHER. The sun has emerged. It is... adequate.",
            "When the sky is clear, the wise man looks inward. The fool gets sunburnt.",
        ],
        WeatherCondition.PARTLY_CLOUDY: [
            "The clouds drift as we all drift. Neither here nor there. Profound, really.",
            "Partly cloudy. The sky commits to nothing. I respect that.",
            "Some clouds, some sun. The universe remains noncommittal on your plans.",
            "The clouds gather, then disperse. Much like my motivation.",
            "A Cherokee elder once said nothing about partly cloudy. It's just... partly cloudy.",
        ],
        WeatherCondition.CLOUDY: [
            "The grey sky hangs low. Like the weight of unfinished quests.",
            "Overcast. The sun has retreated. Wise, perhaps. It knows something.",
            "Grey skies. The color of deep thought. Or mild despair. Hard to tell.",
            "Clouds blanket the land. The earth prepares for what comes next.",
            "Overcast. I've seen this sky in the Reach. Nothing good follows.",
            "The clouds have come. So it goes. So it goes.",
        ],
        WeatherCondition.RAIN: [
            "Rain. War never changes, but the weather certainly does.",
            "The sky weeps. The earth drinks. The cycle continues, as cycles do.",
            "It's raining. The land needed this. Whether you did is... secondary.",
            "Rain falls on the just and unjust alike. I've checked.",
            "The water returns to the earth. You should probably stay inside.",
            "Precipitation. The Mojave makes you wish for this, actually.",
            "Rain. Good for the crops. Less good for whatever you had planned.",
            "The old ones say rain cleanses the spirit. It also cleanses your socks, if you're unprepared.",
        ],
        WeatherCondition.HEAVY_RAIN: [
            "HEAVY RAIN. Like the tears of Talos himself. Dramatic, really.",
            "The deluge comes. Somewhere, an ark is being hastily constructed.",
            "Torrential. The sky has opinions and it's expressing them... vigorously.",
            "Heavy rain. Even the Dragonborn would stay home for this.",
            "The heavens open. This is either cleansing or inconvenient. Often both.",
            "Rain, rain, rain. The Wasteland would kill for this. Literally.",
            "A great storm. The earth will drink deep. So will your basement.",
        ],
        WeatherCondition.DRIZZLE: [
            "A light drizzle. The sky's way of being passive-aggressive about commitment.",
            "Misting. Not quite rain. The weather equivalent of 'I'm fine.'",
            "Drizzle. The Nords would barely notice. You are not a Nord.",
            "A gentle rain. The earth whispers thanks. I whisper 'get an umbrella.'",
        ],
        WeatherCondition.SNOW: [
            "Snow falls. Skyrim belongs to... well, that's complicated actually.",
            "Winter arrives. The land sleeps. Your heating bill does not.",
            "Snow. The white silence descends. Beautiful. Treacherous. Cold.",
            "The frozen sky gives gifts. Whether you wanted them is irrelevant.",
            "Snow. Patrolling the Mojave makes you wish for a nuclear winter. Careful what you wish for.",
            "The snow comes. The old ones would read meaning in this. I read 'stay inside.'",
        ],
        WeatherCondition.HEAVY_SNOW: [
            "HEAVY SNOW. The Greybeards have SHOUTED and they're not happy.",
            "Blizzard conditions. This is fine. Everything is fine.",
            "The snow piles high. Much like my responsibilities. Both are ignored.",
            "Heavy snow. Somewhere, a courier is having a VERY bad day.",
            "The white death descends. Overdramatic? Perhaps. Accurate? Also yes.",
        ],
        WeatherCondition.THUNDERSTORM: [
            "STORM. The thunder rolls across the land like the drums of war. Magnificent.",
            "Lightning splits the sky. Thor is workshopping some ideas up there.",
            "A thunderstorm. The Divines are having a disagreement. Best not to get involved.",
            "The storm rages. There is wisdom in chaos. Also danger. Mostly danger.",
            "THUNDER. FATHER. I believe the sky is... shouting.",
            "Lightning illuminates the truth: you should be indoors.",
            "The storm speaks. It says 'stay inside and contemplate your existence.'",
            "Thunderstorm. Nature's light show. No ticket required. Survival not guaranteed.",
        ],
        WeatherCondition.FOG: [
            "Fog. The world fades to mystery. Watch your step. And your back.",
            "Mist rolls in. This is how quests begin. And sometimes end.",
            "The fog comes. What was hidden remains so. What was known... also questionable.",
            "Visibility: none. Navigation: vibes. Outcome: uncertain.",
            "Fog. The veil between worlds grows thin. Or it's just humidity. Hard to say.",
            "The mist gathers. Somewhere in it, a destiny awaits. Or a puddle. Probably a puddle.",
        ],
        WeatherCondition.FREEZING_RAIN: [
            "Freezing rain. The worst of both elements. A compromise pleasing no one.",
            "Ice falls from the sky. The Wasteland sends its regards.",
            "Freezing rain. Trust nothing. Especially the ground.",
        ],
    }
    
    # Temperature-based wisdom
    TEMP_COMMENTS = {
        "freezing": [  # Below 20°F
            "The cold seeps into bones. The old ones built fires. Do that.",
            "Freezing. Even the mammoths stayed home in this.",
            "Temperature: existentially concerning.",
            "This cold teaches humility. And frostbite. Mostly frostbite.",
        ],
        "cold": [  # 20-40°F
            "Cold enough to see your breath. Your spirit made visible. Briefly.",
            "Brisk. The Nords call this 'refreshing.' The Nords are insane.",
            "Cold. The land contracts. So do your ambitions.",
        ],
        "cool": [  # 40-60°F
            "Cool air. The earth breathes easy. A fine day for a quest. Or tea.",
            "Temperate. The Goldilocks zone. Not too hot. Not too cold. Merely existing.",
            "Pleasant, in a noncommittal sort of way.",
        ],
        "mild": [  # 60-75°F
            "Mild. The weather has achieved neutrality. Remarkable.",
            "Neither hot nor cold. The temperature equivalent of 'no strong opinions.'",
            "Room temperature. Outside. The simulation is well-calibrated today.",
        ],
        "warm": [  # 75-90°F
            "Warm. The sun reminds you it exists. Aggressively.",
            "Getting warm. Hydration becomes philosophy. Drink deep.",
            "Toasty. The desert wanderer in you awakens. The rest of you sweats.",
        ],
        "hot": [  # Above 90°F
            "HOT. Almost heaven. West Virginia. Except hotter. And you can't fast-travel.",
            "The heat bears down. Patrolling feels inadvisable.",
            "Temperature: punishing. Carry water. Question your choices.",
            "The sun is angry. What did you do? WHAT DID YOU DO.",
        ],
    }
    
    # Time-based greetings - philosophical and deadpan
    GREETINGS = {
        "morning": [
            "Ah. Morning. The world begins again. Whether it should is another matter.",
            "Dawn breaks. The land awakens. Your inbox fills. Such is existence.",
            "Morning. The ancestors faced each day with courage. You face it with coffee.",
        ],
        "afternoon": [
            "Afternoon. The day is half-spent. What have we learned? Nothing? Splendid.",
            "The sun is high. Your energy is not. This is the way of things.",
            "Afternoon. Time moves forward. It does not care about your schedule.",
        ],
        "evening": [
            "Evening falls. The day releases its grip. Tomorrow's problems can wait.",
            "Dusk approaches. A fine time for reflection. Or dinner. Both, perhaps.",
            "The evening comes. The wise prepare for rest. The foolish check weather apps.",
        ],
        "night": [
            "Night. Why are you still awake? The stars have questions.",
            "The dark hours. Either you're troubled, or curious. Both are valid.",
            "Night owl, are we? The moon sees you. It judges nothing. I judge slightly.",
        ],
    }
    
    # Achievement unlocks - philosophical and game-inspired
    ACHIEVEMENTS = {
        "first_check": ("📜 The Journey Begins", "Consulted the weather oracle for the first time"),
        "rain_lover": ("🌧️ Walks-In-Rain", "Witnessed 10 days of precipitation. The earth thanks you."),
        "snow_day": ("❄️ Winter's Herald", "The frozen sky has spoken. You listened."),
        "storm_chaser": ("⚡ Voice of Thunder", "Stood witness to the storm's fury. Unshaken."),
        "night_owl": ("🦉 Walker of Night", "Sought weather wisdom in the dark hours"),
        "early_bird": ("🌅 Dawn Watcher", "Rose with the sun to consult the skies"),
        "temp_extreme_hot": ("🔥 Forged in Fire", "Endured the sun's judgment at 100°F+"),
        "temp_extreme_cold": ("🥶 Heart of Winter", "Faced the bitter cold below 0°F"),
        "fog_master": ("👻 Mist Walker", "Navigated the veil between worlds"),
        "consistent": ("📅 The Dedicated", "Seven days of faithful observation. The sky notices."),
    }
    
    def __init__(self):
        self.mood = random.choice(self.MOODS)
        self.data_path = Path.home() / ".stormy_data.json"
        self.data = self._load_data()
        # Use the engine's PersonalityEngine for advanced mood/memory
        self.engine = PersonalityEngine(PersonalityConfig(name="Stormy"))
        self._use_engine = True  # Toggle to use engine vs inline comments
    
    def _load_data(self) -> dict:
        """Load persistent data for achievements."""
        if self.data_path.exists():
            try:
                return json.loads(self.data_path.read_text())
            except:
                pass
        return {
            "achievements": [],
            "check_count": 0,
            "rain_days": 0,
            "last_check_date": None,
            "streak": 0,
        }
    
    def _save_data(self):
        """Save persistent data."""
        try:
            self.data_path.write_text(json.dumps(self.data, indent=2))
        except:
            pass
    
    def get_greeting(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 17:
            period = "afternoon"  
        elif 17 <= hour < 21:
            period = "evening"
        else:
            period = "night"
        return random.choice(self.GREETINGS[period])
    
    def get_weather_comment(self, weather: WeatherData) -> str:
        """Get a snarky comment about the current weather."""
        if self._use_engine:
            # Map WeatherCondition to string for engine
            weather_map = {
                WeatherCondition.CLEAR: "clear",
                WeatherCondition.PARTLY_CLOUDY: "clear",
                WeatherCondition.CLOUDY: "clear",
                WeatherCondition.RAIN: "rain",
                WeatherCondition.HEAVY_RAIN: "rain",
                WeatherCondition.DRIZZLE: "rain",
                WeatherCondition.THUNDERSTORM: "storm",
                WeatherCondition.SNOW: "snow",
                WeatherCondition.HEAVY_SNOW: "snow",
                WeatherCondition.FOG: "fog",
                WeatherCondition.FREEZING_RAIN: "rain",
            }
            weather_type = weather_map.get(weather.condition, "clear")
            self.engine.update(weather_type)  # Update mood state machine
            return self.engine.get_weather_comment(weather_type)
        # Fallback to inline comments
        comments = self.COMMENTS.get(weather.condition, self.COMMENTS[WeatherCondition.CLOUDY])
        return random.choice(comments)
    
    def get_temp_comment(self, temp_f: float) -> str:
        """Get a comment based on temperature."""
        if temp_f < 20:
            category = "freezing"
        elif temp_f < 40:
            category = "cold"
        elif temp_f < 60:
            category = "cool"
        elif temp_f < 75:
            category = "mild"
        elif temp_f < 90:
            category = "warm"
        else:
            category = "hot"
        return random.choice(self.TEMP_COMMENTS[category])
    
    def check_achievements(self, weather: WeatherData) -> list:
        """Check and unlock achievements."""
        unlocked = []
        hour = datetime.now().hour
        today = datetime.now().strftime("%Y-%m-%d")
        
        # First check
        if "first_check" not in self.data["achievements"]:
            self.data["achievements"].append("first_check")
            unlocked.append(self.ACHIEVEMENTS["first_check"])
        
        # Update check count
        self.data["check_count"] += 1
        
        # Streak tracking
        if self.data["last_check_date"] != today:
            yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
            if self.data["last_check_date"] == yesterday:
                self.data["streak"] += 1
            else:
                self.data["streak"] = 1
            self.data["last_check_date"] = today
        
        # Weather-based achievements
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
        
        # Time-based achievements
        if hour >= 0 and hour < 5 and "night_owl" not in self.data["achievements"]:
            self.data["achievements"].append("night_owl")
            unlocked.append(self.ACHIEVEMENTS["night_owl"])
        
        if hour >= 5 and hour < 6 and "early_bird" not in self.data["achievements"]:
            self.data["achievements"].append("early_bird")
            unlocked.append(self.ACHIEVEMENTS["early_bird"])
        
        # Temperature achievements
        if weather.temperature_f >= 100 and "temp_extreme_hot" not in self.data["achievements"]:
            self.data["achievements"].append("temp_extreme_hot")
            unlocked.append(self.ACHIEVEMENTS["temp_extreme_hot"])
        
        if weather.temperature_f <= 0 and "temp_extreme_cold" not in self.data["achievements"]:
            self.data["achievements"].append("temp_extreme_cold")
            unlocked.append(self.ACHIEVEMENTS["temp_extreme_cold"])
        
        # Streak achievement
        if self.data["streak"] >= 7 and "consistent" not in self.data["achievements"]:
            self.data["achievements"].append("consistent")
            unlocked.append(self.ACHIEVEMENTS["consistent"])
        
        self._save_data()
        return unlocked
    
    def get_random_quip(self) -> str:
        """Get a random philosophical/deadpan quip."""
        quips = [
            "The clouds move as they will. We are all clouds, in a way. Drifting. Dissipating.",
            "Weather: the one thing that affects everyone equally. Democracy in its purest form.",
            "I've been contemplating the barometric pressure. It contemplates nothing back.",
            "The atmosphere is merely a thin shell protecting you from the void. You're welcome.",
            "A Lakota saying: 'The earth does not belong to us. We belong to the earth.' Also, it's raining.",
            "I've seen empires rise and fall. I've also seen partly cloudy. Both are temporary.",
            "The weather cares not for your meetings. This is both its cruelty and its wisdom.",
            "In the grand tapestry of existence, today's forecast is but a single thread. A damp thread.",
            "FATHER. I have consulted the clouds. They speak only of humidity.",
            "The Wasteland taught me many things. Chief among them: carry water. Always.",
            "A wizard is never late. He arrives precisely when he means to. The rain, however, does as it pleases.",
            "The Wheel weaves as the Wheel wills. The weather does whatever it wants.",
            "What is better: to be born dry, or to overcome your soggy nature through great effort?",
            "The earth speaks, if you listen. Right now it's saying 'bring a jacket.'",
            "I asked the universe for clarity. It gave me fog. The universe has a sense of humor.",
            "Time is a flat circle. So is this high-pressure system, coincidentally.",
            "The old gods are watching. They're not impressed with your umbrella choice.",
            "In Skyrim, they have a saying: 'The weather is the weather.' Profound. Absolutely profound.",
            "Dew point achieved. Somewhere, a meteorologist weeps with joy.",
            "The only constant is change. And also the fact that weather forecasts are merely suggestions.",
            # Physics-aware quips - Stormy knows what's running under the hood
            "I'm using Perlin noise to render these clouds. Ken Perlin would be proud. Or confused.",
            "Each raindrop follows Newton's laws. Gravity, drag, buoyancy. I take physics seriously.",
            "That lightning? Fractal branching via recursive pathfinding. Zeus was doing it wrong.",
            "The turbulence field uses multi-octave noise. The Nords called it 'wind'. I call it 'math'.",
            "Fun fact: I simulate air resistance using quadratic drag. Your umbrella is still useless.",
            "These particles have mass and buoyancy. More than can be said for most weather apps.",
            "I calculated 6t⁵ - 15t⁴ + 10t³ to make those clouds look smooth. You're welcome.",
            "The ancients read weather from bird flights. I use gradient noise. Same energy, better math.",
            "My wind gusts follow exponential decay curves. Nature approximates. I calculate.",
            "Each snowflake is a physics object with terminal velocity. Poetic AND scientifically accurate.",
        ]
        if self._use_engine:
            return self.engine.get_quip(meta_chance=0.4)
        return random.choice(quips)
    
    def get_mood(self) -> Mood:
        """Get current mood from engine."""
        return self.engine.current_mood
    
    def get_callback(self) -> str:
        """Attempt a memory callback."""
        return self.engine.get_callback()


# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 ASCII ART ASSETS
# ═══════════════════════════════════════════════════════════════════════════════

# Big temperature digits
BIG_DIGITS = {
    '0': ["┌─┐", "│ │", "└─┘"],
    '1': [" ┐ ", " │ ", " ┴ "],
    '2': ["┌─┐", "┌─┘", "└─┘"],
    '3': ["┌─┐", " ─┤", "└─┘"],
    '4': ["┐ ┐", "└─┤", "  ┘"],
    '5': ["┌─┐", "└─┐", "└─┘"],
    '6': ["┌─┐", "├─┐", "└─┘"],
    '7': ["┌─┐", "  │", "  ┘"],
    '8': ["┌─┐", "├─┤", "└─┘"],
    '9': ["┌─┐", "└─┤", "└─┘"],
    '-': ["   ", "───", "   "],
    '°': ["┌┐ ", "└┘ ", "   "],
    ' ': ["   ", "   ", "   "],
}

# Stormy's faces - wise and contemplative
# Cute weather mascot - changes expression based on conditions
WEATHER_MASCOT = {
    WeatherCondition.CLEAR: [
        "    \\  |  //    ",
        "      (◠‿◠)      ",
        "    //  |  \\    ",
    ],
    WeatherCondition.PARTLY_CLOUDY: [
        "    ~  ◠◠  ~    ",
        "      (◕‿◕)      ",
        "       ~~~       ",
    ],
    WeatherCondition.CLOUDY: [
        "     ~~~☁~~~     ",
        "      (◕ᴗ◕)      ",
        "       ~~~       ",
    ],
    WeatherCondition.FOG: [
        "    ≋≋≋≋≋≋≋≋    ",
        "      (◡_◡)      ",
        "    ≋≋≋≋≋≋≋≋    ",
    ],
    WeatherCondition.DRIZZLE: [
        "       ☁        ",
        "      (◕‿◕)      ",
        "      ⋮ ⋮ ⋮      ",
    ],
    WeatherCondition.RAIN: [
        "      ☁☁☁       ",
        "      (◕_◕)      ",
        "      ╏╏╏╏╏      ",
    ],
    WeatherCondition.HEAVY_RAIN: [
        "     ☁☁☁☁☁      ",
        "      (◕︵◕)      ",
        "     ╏╏╏╏╏╏╏     ",
    ],
    WeatherCondition.FREEZING_RAIN: [
        "      ☁❄☁       ",
        "      (◕﹏◕)      ",
        "      ╏*╏*╏      ",
    ],
    WeatherCondition.SNOW: [
        "     ❄  ❄  ❄     ",
        "      (◕ω◕)      ",
        "      * * *      ",
    ],
    WeatherCondition.HEAVY_SNOW: [
        "    ❄❄❄❄❄❄❄    ",
        "      (◕◡◕)      ",
        "     *******     ",
    ],
    WeatherCondition.THUNDERSTORM: [
        "     ⚡☁☁⚡      ",
        "      (◉_◉)      ",
        "       ⚡⚡       ",
    ],
    WeatherCondition.UNKNOWN: [
        "       ~?~       ",
        "      (◕_◕)      ",
        "       ~~~       ",
    ],
}

# Legacy faces for random variety
STORMY_FACES = {
    "happy": [
        "      (◠‿◠)      ",
    ],
}

# Weather scenes
WEATHER_SCENES = {
    WeatherCondition.CLEAR: [
        "        \\   |   /        ",
        "          .-'-.          ",
        "      ─  (     )  ─      ",
        "          `-.-'          ",
        "        /   |   \\        ",
        "                         ",
    ],
    WeatherCondition.RAIN: [
        "        ___               ",
        "      .(   ).             ",
        "     (___(____)           ",
        "      ' ' ' ' '           ",
        "     ' ' ' ' ' '          ",
        "      ' ' ' ' '           ",
    ],
    WeatherCondition.HEAVY_RAIN: [
        "        ___               ",
        "      .(   ).             ",
        "     (___(____)           ",
        "     | | | | | |          ",
        "     | | | | | | |        ",
        "     | | | | | |          ",
    ],
    WeatherCondition.THUNDERSTORM: [
        "        ___               ",
        "      .(   ).             ",
        "     (___(____)           ",
        "      /  | | \\           ",
        "        / \\              ",
        "       /   \\             ",
    ],
    WeatherCondition.SNOW: [
        "        ___               ",
        "      .(   ).             ",
        "     (___(____)           ",
        "      * * * * *           ",
        "     * * * * * *          ",
        "      * * * * *           ",
    ],
    WeatherCondition.FOG: [
        "  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋         ",
        " ░░▒░░░▒░░░░▒░░░░         ",
        "  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋         ",
        " ░░░░▒░░░░▒░░░▒░░         ",
        "  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋         ",
        " ░▒░░░░░▒░░░░▒░░░         ",
    ],
    WeatherCondition.PARTLY_CLOUDY: [
        "     \\  |  /    ___       ",
        "       .-'    .(   ).     ",
        "    ─ (    ) (___(____)   ",
        "       `-'               ",
        "     /  |  \\              ",
        "                          ",
    ],
    WeatherCondition.PARTLY_CLOUDY: [
        "     \\  |  /    ___       ",
        "       .-'    .(   ).     ",
        "    ─ (    ) (___(____)   ",
        "       `-'               ",
        "     /  |  \\              ",
        "                          ",
    ],
    WeatherCondition.CLOUDY: [
        "      ☁     ☁             ",
        "        ___               ",
        "      .(   ).    ☁        ",
        "     (___(____)           ",
        "   ☁          ☁           ",
        "      ☁    ☁              ",
    ],
}

# Fill in missing conditions
for cond in WeatherCondition:
    if cond not in WEATHER_SCENES:
        WEATHER_SCENES[cond] = WEATHER_SCENES.get(WeatherCondition.CLOUDY)




# ═══════════════════════════════════════════════════════════════════════════════
# 🌦️ DASHBOARD CLASS  
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
        
        # 🧠 ADVANCED PHYSICS SYSTEMS - "The brain behind the beauty"
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
        # 🌡️ ATMOSPHERIC MODEL (engine.physics.atmosphere)
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
        # ⚛️ ENGINE PARTICLE SYSTEM (engine.physics.particles)
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
        # 🆕 ENHANCED FEATURES INITIALIZATION
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
        self._fetch_extended_data()
        
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
        if key in (ord('l'), ord('L')):
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
        
        return None
    
    def _draw_help_overlay(self):
        """Draw a help overlay with available keyboard shortcuts."""
        screen = self.screen
        
        help_lines = [
            "═══════════ KEYBOARD SHORTCUTS ═══════════",
            "",
            "  Q       - Quit dashboard",
            "  R       - Refresh weather data",
            "  L       - Search new location",
            "  A       - View achievements",
            "  F       - Toggle forecast panel",
            "  U       - Toggle metric/imperial",
            "  ?       - Show/hide this help",
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

    def update(self):
        """Update animation state with advanced physics."""
        self.frame += 1
        
        # ═══════════════════════════════════════════════════════════════════
        # 🧠 UPDATE ADVANCED PHYSICS SYSTEMS
        # ═══════════════════════════════════════════════════════════════════
        self.turbulence.update()
        self.wind_gusts.update()
        self.cloud_time += 0.02
        
        # Get current wind (base + gusts)
        wind_x, wind_y = self.wind_gusts.get_wind()
        
        # ═══════════════════════════════════════════════════════════════════
        # ⚛️ UPDATE ENGINE PARTICLE SYSTEM (engine.physics.particles)
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
        # 🌩️ ADVANCED LIGHTNING SYSTEM (Branching fractals)
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
        
        # Easter egg creatures - try to spawn and update
        hour = datetime.now().hour
        self.easter_eggs.try_spawn(self.weather.condition, hour)
        self.easter_eggs.update()
        
        # ═══════════════════════════════════════════════════════════════════
        # 🆕 UPDATE ENHANCED FEATURES
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
        
        title = "⚡ LIVE" if self.weather.condition == WeatherCondition.THUNDERSTORM else "◉ LIVE"
        
        self._draw_box(ax, 0, aw, self.height - 1, title)
        
        # ═══════════════════════════════════════════════════════════════════
        # 🌫️ PERLIN NOISE CLOUD LAYER
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
        # 🌧️ PHYSICS-BASED PARTICLES (with trails)
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
            except:
                pass
        
        # Regular particles (for drifting effects)
        for p in self.particles.particles:
            try:
                px, py = int(p.x), int(p.y)
                if ax + 1 <= px < ax + aw - 1 and 2 <= py < self.height - 2:
                    colour = Theme.SUN if self.lightning_active and random.random() > 0.3 else p.colour
                    self.screen.print_at(p.char, px, py, colour=colour)
            except:
                pass
        
        # ═══════════════════════════════════════════════════════════════════
        # ⚡ BRANCHING LIGHTNING (Fractal pathfinding)
        # ═══════════════════════════════════════════════════════════════════
        for bolt in self.lightning_bolts:
            bolt.draw(self.screen, ax)
        
        # Old lightning fallback
        if self.lightning_active and not self.lightning_bolts:
            self._draw_lightning()
        
        # Easter egg creatures (rare visitors!)
        self.easter_eggs.draw(self.screen, self.lightning_active)
        
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
        footer = " [S]earch Location | [R]efresh | [A]chievements | [Q]uit "
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
# 🏆 ACHIEVEMENTS SCREEN
# ═══════════════════════════════════════════════════════════════════════════════

def draw_achievements_screen(screen: Screen, stormy: StormyPersonality):
    """Draw the achievements screen."""
    screen.clear()
    
    w, h = screen.width, screen.height
    
    # Title
    title = "STORMY'S HALL OF FAME"
    screen.print_at(title, (w - len(title)) // 2, 1, colour=Theme.SUN)
    
    subtitle = f"You've unlocked {len(stormy.data['achievements'])} of {len(stormy.ACHIEVEMENTS)} achievements!"
    screen.print_at(subtitle, (w - len(subtitle)) // 2, 3, colour=Theme.FROST)
    
    y = 5
    col_width = w // 2 - 2
    col = 0
    
    for key, (icon, name) in stormy.ACHIEVEMENTS.items():
        unlocked = key in stormy.data["achievements"]
        
        if unlocked:
            text = f"  {icon} {name}"
            colour = Theme.SUN
        else:
            text = f"  [?] ???"
            colour = Theme.MUTED
        
        x = 2 + col * col_width
        screen.print_at(text[:col_width-2], x, y, colour=colour)
        
        col += 1
        if col >= 2:
            col = 0
            y += 2
        
        if y >= h - 4:
            break
    
    # Stats
    stats = f"Total checks: {stormy.data['check_count']} | Current streak: {stormy.data['streak']} days"
    screen.print_at(stats, (w - len(stats)) // 2, h - 3, colour=Theme.SNOW)
    
    footer = "Press any key to return..."
    screen.print_at(footer, (w - len(footer)) // 2, h - 1, colour=Theme.FROST)
    
    screen.refresh()
    screen.wait_for_input(60)


def location_search_screen(screen: Screen) -> Optional[WeatherData]:
    """
    Interactive location search screen.
    Type a city name and press Enter to search.
    
    Examples:
        Summerville, SC
        New York, NY
        Moscow, Russia
        San Diego, CA
        Tokyo, Japan
    """
    screen.clear()
    w, h = screen.width, screen.height
    
    # Title
    title = "🌍 LOCATION SEARCH"
    screen.print_at(title, (w - len(title)) // 2, 2, colour=Theme.SUN)
    
    subtitle = "Type a city name and press Enter"
    screen.print_at(subtitle, (w - len(subtitle)) // 2, 4, colour=Theme.FROST)
    
    # Examples
    examples = [
        "Examples:  Summerville, SC  |  New York, NY  |  Moscow, Russia",
        "           Tokyo, Japan  |  London, UK  |  Paris, France"
    ]
    for i, ex in enumerate(examples):
        screen.print_at(ex, (w - len(ex)) // 2, 6 + i, colour=Theme.MUTED)
    
    # Input box
    box_y = 10
    box_width = min(60, w - 4)
    box_x = (w - box_width) // 2
    
    # Draw box
    screen.print_at("┌" + "─" * (box_width - 2) + "┐", box_x, box_y, colour=Theme.FROST)
    screen.print_at("│" + " " * (box_width - 2) + "│", box_x, box_y + 1, colour=Theme.FROST)
    screen.print_at("└" + "─" * (box_width - 2) + "┘", box_x, box_y + 2, colour=Theme.FROST)
    
    # Instructions
    instructions = "Enter = Search  |  Esc = Cancel  |  Backspace = Delete"
    screen.print_at(instructions, (w - len(instructions)) // 2, box_y + 4, colour=Theme.MUTED)
    
    screen.refresh()
    
    # Input loop
    query = ""
    cursor_x = box_x + 2
    
    while True:
        # Clear input area and redraw
        screen.print_at(" " * (box_width - 4), box_x + 2, box_y + 1)
        screen.print_at(query[-box_width+6:], box_x + 2, box_y + 1, colour=Theme.SUN)
        
        # Cursor
        cursor_pos = box_x + 2 + min(len(query), box_width - 6)
        screen.print_at("▌", cursor_pos, box_y + 1, colour=Theme.FROST)
        
        # Clear status line
        screen.print_at(" " * (w - 4), 2, box_y + 6)
        screen.refresh()
        
        ev = screen.get_key()
        
        if ev == Screen.KEY_ESCAPE or ev == ord('q'):
            return None
        
        if ev in (10, 13):  # Enter key
            if query.strip():
                # Show searching message
                msg = f"Searching for '{query}'..."
                screen.print_at(" " * (w - 4), 2, box_y + 6)
                screen.print_at(msg, (w - len(msg)) // 2, box_y + 6, colour=Theme.FROST)
                screen.refresh()
                
                # Search!
                weather = search_and_fetch_weather(query.strip())
                
                if weather:
                    success = f"✓ Found: {weather.location} - {weather.temperature_f:.0f}°F, {weather.description}"
                    screen.print_at(" " * (w - 4), 2, box_y + 6)
                    screen.print_at(success[:w-4], (w - min(len(success), w-4)) // 2, box_y + 6, colour=Theme.SUN)
                    screen.refresh()
                    time.sleep(1.5)
                    return weather
                else:
                    error = f"✗ Location not found: '{query}'"
                    screen.print_at(" " * (w - 4), 2, box_y + 6)
                    screen.print_at(error, (w - len(error)) // 2, box_y + 6, colour=Screen.COLOUR_RED)
                    screen.refresh()
                    time.sleep(1.5)
                    query = ""
        
        elif ev == Screen.KEY_BACK or ev == 127 or ev == 8:  # Backspace
            query = query[:-1]
        
        elif ev is not None and 32 <= ev < 127:  # Printable characters
            query += chr(ev)
        
        time.sleep(0.033)




# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN
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
        time.sleep(0.3)
    
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
            weather = get_weather(use_cache=False)
            if weather:
                dashboard = WeatherDashboard(screen, weather)
                last_fetch = time.time()
                if dashboard.notifications:
                    dashboard.notifications.add_success("Weather refreshed!")
        elif result == 'search':
            new_weather = location_search_screen(screen)
            if new_weather:
                weather = new_weather
                dashboard = WeatherDashboard(screen, weather)
                last_fetch = time.time()
        elif result == 'achievements':
            draw_achievements_screen(screen, dashboard.stormy)
            dashboard.draw()
        
        # Help toggle (? key)
        if ev == ord('?'):
            dashboard.show_help = not dashboard.show_help
        
        # F key now handled in handle_input for forecast toggle
        if ev in (ord('f'), ord('F')) and not dashboard.show_forecast:
            # Only trigger weather_live if forecast is disabled
            try:
                from weather_live import weather_live
                weather_live(screen)
            except:
                pass
            dashboard = WeatherDashboard(screen, weather)
        
        # Auto-refresh every 5 minutes
        if time.time() - last_fetch > 300:
            new_weather = get_weather(use_cache=False)
            if new_weather:
                weather = new_weather
                dashboard = WeatherDashboard(screen, weather)
                last_fetch = time.time()
        
        dashboard.update()
        dashboard.draw()
        
        # Draw help overlay if active
        if dashboard.show_help:
            dashboard._draw_help_overlay()
        
        screen.refresh()
        
        time.sleep(0.033)


def main():
    print("\033[2J\033[H")
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
