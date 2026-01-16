"""
Enhanced Achievements System
============================
Expanded achievement tracking with more goals and progression.

Features:
- 30+ unique achievements
- Progress tracking for multi-step achievements
- Seasonal achievements
- Location-based achievements
- Weather streak tracking
- Rare event achievements
- Achievement categories and tiers

"Gamification of weather observation. 
The ancient meteorologists would be confused. 
But also probably into it." - Stormy
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import math


# ═══════════════════════════════════════════════════════════════════════════════
# 🏆 ACHIEVEMENT DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

class AchievementTier(Enum):
    """Achievement difficulty/prestige tier."""
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    LEGENDARY = "Legendary"


class AchievementCategory(Enum):
    """Achievement categories."""
    BASICS = "Getting Started"
    WEATHER = "Weather Watcher"
    TEMPERATURE = "Temperature Tales"
    TIME = "Time Keeper"
    EXPLORATION = "Explorer"
    DEDICATION = "Dedication"
    RARE = "Rare Events"
    SEASONAL = "Seasonal"
    SPECIAL = "Special"


@dataclass
class Achievement:
    """Single achievement definition."""
    id: str
    name: str
    description: str
    emoji: str
    category: AchievementCategory
    tier: AchievementTier
    secret: bool = False  # Hidden until unlocked
    progress_max: int = 1  # For multi-step achievements
    stormy_quote: str = ""  # Stormy's comment on unlocking
    
    def display_name(self) -> str:
        return f"{self.emoji} {self.name}"


# All achievements
ACHIEVEMENTS: Dict[str, Achievement] = {
    # ═══════════════════════════════════════════════════════════════════════════
    # 📜 BASICS - Getting Started
    # ═══════════════════════════════════════════════════════════════════════════
    "first_check": Achievement(
        id="first_check",
        name="The Journey Begins",
        description="Consulted the weather oracle for the first time",
        emoji="📜",
        category=AchievementCategory.BASICS,
        tier=AchievementTier.BRONZE,
        stormy_quote="Ah, a new seeker of atmospheric wisdom. Welcome."
    ),
    "help_reader": Achievement(
        id="help_reader",
        name="RTFM",
        description="Pressed '?' to view the help screen",
        emoji="📖",
        category=AchievementCategory.BASICS,
        tier=AchievementTier.BRONZE,
        stormy_quote="Reading the manual? A rare and admirable trait."
    ),
    "unit_switcher": Achievement(
        id="unit_switcher",
        name="Metric Convert",
        description="Switched between Fahrenheit and Celsius",
        emoji="🔄",
        category=AchievementCategory.BASICS,
        tier=AchievementTier.BRONZE,
        stormy_quote="The temperature is the same. Only the numbers change."
    ),
    "theme_explorer": Achievement(
        id="theme_explorer",
        name="Fashion Forward",
        description="Changed the color theme",
        emoji="🎨",
        category=AchievementCategory.BASICS,
        tier=AchievementTier.BRONZE,
        stormy_quote="Aesthetics matter. Even in weather apps."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🌦️ WEATHER - Weather Conditions
    # ═══════════════════════════════════════════════════════════════════════════
    "rain_witness": Achievement(
        id="rain_witness",
        name="First Rain",
        description="Witnessed your first rainy day",
        emoji="🌧️",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.BRONZE,
        stormy_quote="The sky weeps. The earth drinks. The cycle begins."
    ),
    "rain_lover": Achievement(
        id="rain_lover",
        name="Walks-In-Rain",
        description="Witnessed 10 days of precipitation",
        emoji="🌧️",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.SILVER,
        progress_max=10,
        stormy_quote="The earth thanks you for your patience."
    ),
    "rain_master": Achievement(
        id="rain_master",
        name="Pluviophile",
        description="Witnessed 50 days of precipitation",
        emoji="💧",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.GOLD,
        progress_max=50,
        stormy_quote="The rain knows you now. It considers you a friend."
    ),
    "snow_day": Achievement(
        id="snow_day",
        name="Winter's Herald",
        description="Witnessed snowfall",
        emoji="❄️",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.SILVER,
        stormy_quote="The frozen sky has spoken. You listened."
    ),
    "blizzard_survivor": Achievement(
        id="blizzard_survivor",
        name="Blizzard Walker",
        description="Witnessed heavy snow conditions",
        emoji="🌨️",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.GOLD,
        stormy_quote="The white death came. You observed. You survived."
    ),
    "storm_chaser": Achievement(
        id="storm_chaser",
        name="Voice of Thunder",
        description="Witnessed a thunderstorm",
        emoji="⚡",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.SILVER,
        stormy_quote="The sky roared. You stood witness. Respect."
    ),
    "storm_veteran": Achievement(
        id="storm_veteran",
        name="Storm Caller",
        description="Witnessed 10 thunderstorms",
        emoji="🌩️",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.GOLD,
        progress_max=10,
        stormy_quote="Thor himself nods in your direction."
    ),
    "fog_master": Achievement(
        id="fog_master",
        name="Mist Walker",
        description="Navigated through foggy conditions",
        emoji="🌫️",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.SILVER,
        stormy_quote="The veil parts for those who seek."
    ),
    "clear_streak": Achievement(
        id="clear_streak",
        name="Endless Blue",
        description="5 consecutive clear days",
        emoji="☀️",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.SILVER,
        progress_max=5,
        stormy_quote="The sun favors you. Suspicious, really."
    ),
    "rainbow_hunter": Achievement(
        id="rainbow_hunter",
        name="Rainbow Seeker",
        description="Witnessed clearing skies after rain",
        emoji="🌈",
        category=AchievementCategory.WEATHER,
        tier=AchievementTier.GOLD,
        stormy_quote="The light bends. The colors separate. Beautiful."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🌡️ TEMPERATURE - Extremes and Comfort
    # ═══════════════════════════════════════════════════════════════════════════
    "temp_extreme_hot": Achievement(
        id="temp_extreme_hot",
        name="Forged in Fire",
        description="Experienced 100°F+ temperatures",
        emoji="🔥",
        category=AchievementCategory.TEMPERATURE,
        tier=AchievementTier.GOLD,
        stormy_quote="The sun has chosen violence. You endured."
    ),
    "temp_extreme_cold": Achievement(
        id="temp_extreme_cold",
        name="Heart of Winter",
        description="Faced temperatures below 0°F",
        emoji="🥶",
        category=AchievementCategory.TEMPERATURE,
        tier=AchievementTier.GOLD,
        stormy_quote="The cold that breaks lesser spirits. Not yours."
    ),
    "perfect_day": Achievement(
        id="perfect_day",
        name="Perfect Day",
        description="Clear skies, 68-75°F, low humidity",
        emoji="✨",
        category=AchievementCategory.TEMPERATURE,
        tier=AchievementTier.GOLD,
        stormy_quote="Goldilocks weather. Not too hot. Not too cold. Just right."
    ),
    "temp_swing": Achievement(
        id="temp_swing",
        name="Whiplash",
        description="20°+ temperature change in 24 hours",
        emoji="🎢",
        category=AchievementCategory.TEMPERATURE,
        tier=AchievementTier.SILVER,
        stormy_quote="The atmosphere is indecisive today. Join the club."
    ),
    "freezing_rain_survivor": Achievement(
        id="freezing_rain_survivor",
        name="Ice Walker",
        description="Witnessed freezing rain conditions",
        emoji="🧊",
        category=AchievementCategory.TEMPERATURE,
        tier=AchievementTier.GOLD,
        stormy_quote="The worst of both worlds. You have my sympathy."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ⏰ TIME - When You Check
    # ═══════════════════════════════════════════════════════════════════════════
    "night_owl": Achievement(
        id="night_owl",
        name="Walker of Night",
        description="Checked weather between midnight and 5 AM",
        emoji="🦉",
        category=AchievementCategory.TIME,
        tier=AchievementTier.SILVER,
        stormy_quote="The night has questions. So do you, apparently."
    ),
    "early_bird": Achievement(
        id="early_bird",
        name="Dawn Watcher",
        description="Checked weather before 6 AM",
        emoji="🌅",
        category=AchievementCategory.TIME,
        tier=AchievementTier.SILVER,
        stormy_quote="You rise with the sun. The ancestors approve."
    ),
    "noon_check": Achievement(
        id="noon_check",
        name="High Noon",
        description="Checked weather at exactly 12:00 PM",
        emoji="🕛",
        category=AchievementCategory.TIME,
        tier=AchievementTier.BRONZE,
        secret=True,
        stormy_quote="The sun is highest. So is your dedication."
    ),
    "midnight_check": Achievement(
        id="midnight_check",
        name="Witching Hour",
        description="Checked weather at exactly midnight",
        emoji="🌙",
        category=AchievementCategory.TIME,
        tier=AchievementTier.SILVER,
        secret=True,
        stormy_quote="Between days. Between worlds. You checked the weather."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 📅 DEDICATION - Consistency
    # ═══════════════════════════════════════════════════════════════════════════
    "consistent": Achievement(
        id="consistent",
        name="The Dedicated",
        description="Checked weather 7 days in a row",
        emoji="📅",
        category=AchievementCategory.DEDICATION,
        tier=AchievementTier.SILVER,
        progress_max=7,
        stormy_quote="A week of faithful observation. The sky notices."
    ),
    "monthly_devotion": Achievement(
        id="monthly_devotion",
        name="Monthly Devotion",
        description="Checked weather 30 days in a row",
        emoji="🗓️",
        category=AchievementCategory.DEDICATION,
        tier=AchievementTier.GOLD,
        progress_max=30,
        stormy_quote="A month of dedication. You are truly one of us."
    ),
    "century_club": Achievement(
        id="century_club",
        name="Century Club",
        description="100 total weather checks",
        emoji="💯",
        category=AchievementCategory.DEDICATION,
        tier=AchievementTier.GOLD,
        progress_max=100,
        stormy_quote="One hundred consultations. Your wisdom grows."
    ),
    "thousand_checks": Achievement(
        id="thousand_checks",
        name="Weather Sage",
        description="1000 total weather checks",
        emoji="🏛️",
        category=AchievementCategory.DEDICATION,
        tier=AchievementTier.PLATINUM,
        progress_max=1000,
        stormy_quote="A thousand observations. You are become weather."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🌍 EXPLORATION - Locations
    # ═══════════════════════════════════════════════════════════════════════════
    "location_switch": Achievement(
        id="location_switch",
        name="Wanderer",
        description="Switched to a different location",
        emoji="🧭",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.BRONZE,
        stormy_quote="The weather changes with perspective. So do you."
    ),
    "globe_trotter": Achievement(
        id="globe_trotter",
        name="Globe Trotter",
        description="Checked weather in 5+ different locations",
        emoji="🌍",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.GOLD,
        progress_max=5,
        stormy_quote="The world is vast. Its weather, more so."
    ),
    "hemisphere_hopper": Achievement(
        id="hemisphere_hopper",
        name="Hemisphere Hopper",
        description="Checked weather in both Northern and Southern hemispheres",
        emoji="🌐",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.GOLD,
        stormy_quote="While one hemisphere freezes, another burns. You've seen both."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🍂 SEASONAL - Seasons
    # ═══════════════════════════════════════════════════════════════════════════
    "four_seasons": Achievement(
        id="four_seasons",
        name="Season Walker",
        description="Checked weather in all four seasons",
        emoji="🍂",
        category=AchievementCategory.SEASONAL,
        tier=AchievementTier.GOLD,
        progress_max=4,
        stormy_quote="Spring, summer, fall, winter. The wheel turns. You watched."
    ),
    "summer_solstice": Achievement(
        id="summer_solstice",
        name="Midsummer Witness",
        description="Checked weather on summer solstice",
        emoji="☀️",
        category=AchievementCategory.SEASONAL,
        tier=AchievementTier.SILVER,
        stormy_quote="The longest day. The sun lingers. As do you."
    ),
    "winter_solstice": Achievement(
        id="winter_solstice",
        name="Midwinter Witness",
        description="Checked weather on winter solstice",
        emoji="❄️",
        category=AchievementCategory.SEASONAL,
        tier=AchievementTier.SILVER,
        stormy_quote="The longest night. The sun retreats. You remain."
    ),
    "equinox_check": Achievement(
        id="equinox_check",
        name="Balance Seeker",
        description="Checked weather on an equinox",
        emoji="⚖️",
        category=AchievementCategory.SEASONAL,
        tier=AchievementTier.SILVER,
        stormy_quote="Day equals night. Balance achieved. Briefly."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ⚠️ RARE EVENTS
    # ═══════════════════════════════════════════════════════════════════════════
    "severe_alert": Achievement(
        id="severe_alert",
        name="Alert Observer",
        description="Witnessed an active severe weather alert",
        emoji="⚠️",
        category=AchievementCategory.RARE,
        tier=AchievementTier.SILVER,
        stormy_quote="The sky sends warnings. Wise to heed them."
    ),
    "tornado_watch": Achievement(
        id="tornado_watch",
        name="Tornado Aware",
        description="Experienced a tornado watch or warning",
        emoji="🌪️",
        category=AchievementCategory.RARE,
        tier=AchievementTier.GOLD,
        stormy_quote="The sky spirals. Respect its power."
    ),
    "hurricane_tracker": Achievement(
        id="hurricane_tracker",
        name="Hurricane Tracker",
        description="Tracked a hurricane or tropical storm",
        emoji="🌀",
        category=AchievementCategory.RARE,
        tier=AchievementTier.PLATINUM,
        stormy_quote="The great cyclone. Nature's fury manifest."
    ),
    "pressure_drop": Achievement(
        id="pressure_drop",
        name="Barometer Reader",
        description="Noticed a 10+ hPa pressure drop",
        emoji="📉",
        category=AchievementCategory.RARE,
        tier=AchievementTier.GOLD,
        stormy_quote="The air grows light. A storm approaches."
    ),
    "uv_extreme": Achievement(
        id="uv_extreme",
        name="Sun's Fury",
        description="Experienced UV index 11+",
        emoji="☀️",
        category=AchievementCategory.RARE,
        tier=AchievementTier.GOLD,
        stormy_quote="The sun shows no mercy today."
    ),
    "poor_air_quality": Achievement(
        id="poor_air_quality",
        name="Breath Watcher",
        description="Witnessed unhealthy air quality (AQI 150+)",
        emoji="😷",
        category=AchievementCategory.RARE,
        tier=AchievementTier.SILVER,
        stormy_quote="The air betrays us. Seek shelter."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🎭 SPECIAL - Easter Eggs
    # ═══════════════════════════════════════════════════════════════════════════
    "creature_sighting": Achievement(
        id="creature_sighting",
        name="Something in the Mist",
        description="Spotted a creature in the fog",
        emoji="👻",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.LEGENDARY,
        secret=True,
        stormy_quote="You saw it too? ...Interesting."
    ),
    "stormy_mood": Achievement(
        id="stormy_mood",
        name="Stormy's Mood Ring",
        description="Witnessed all of Stormy's moods",
        emoji="🎭",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.GOLD,
        progress_max=8,
        stormy_quote="You've seen all my faces. We are now... acquainted."
    ),
    "screenshot_master": Achievement(
        id="screenshot_master",
        name="Capture the Moment",
        description="Took 10 screenshots",
        emoji="📸",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.SILVER,
        progress_max=10,
        stormy_quote="Preserving moments for posterity. I approve."
    ),
    "data_exporter": Achievement(
        id="data_exporter",
        name="Data Archaeologist",
        description="Exported weather history",
        emoji="📊",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.SILVER,
        stormy_quote="Your data, preserved. Future generations thank you."
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 PROGRESS TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AchievementProgress:
    """Progress towards a single achievement."""
    achievement_id: str
    current: int = 0
    unlocked: bool = False
    unlock_time: Optional[float] = None
    
    @property
    def achievement(self) -> Achievement:
        return ACHIEVEMENTS.get(self.achievement_id)
    
    @property
    def progress_percent(self) -> float:
        if self.achievement and self.achievement.progress_max > 1:
            return (self.current / self.achievement.progress_max) * 100
        return 100.0 if self.unlocked else 0.0
    
    def increment(self, amount: int = 1) -> bool:
        """Increment progress. Returns True if achievement unlocked."""
        if self.unlocked:
            return False
        
        self.current += amount
        ach = self.achievement
        if ach and self.current >= ach.progress_max:
            self.unlocked = True
            self.unlock_time = time.time()
            return True
        return False
    
    def to_dict(self) -> dict:
        return {
            'achievement_id': self.achievement_id,
            'current': self.current,
            'unlocked': self.unlocked,
            'unlock_time': self.unlock_time,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AchievementProgress':
        return cls(**data)


# ═══════════════════════════════════════════════════════════════════════════════
# 🎮 ACHIEVEMENT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class AchievementManager:
    """
    Manages achievement tracking, unlocking, and persistence.
    """
    
    def __init__(self, data_path: str = None):
        self.data_path = Path(data_path) if data_path else Path.home() / ".stormy_achievements.json"
        self.progress: Dict[str, AchievementProgress] = {}
        self.stats: Dict[str, Any] = {
            'total_checks': 0,
            'streak': 0,
            'last_check_date': None,
            'rain_days': 0,
            'storm_days': 0,
            'locations_checked': [],
            'seasons_checked': [],
            'moods_seen': [],
            'screenshots_taken': 0,
            'last_pressure': None,
            'last_temp': None,
        }
        self._init_progress()
        self.load()
    
    def _init_progress(self):
        """Initialize progress for all achievements."""
        for ach_id in ACHIEVEMENTS:
            if ach_id not in self.progress:
                self.progress[ach_id] = AchievementProgress(achievement_id=ach_id)
    
    def load(self) -> bool:
        """Load progress from file."""
        if not self.data_path.exists():
            return False
        
        try:
            data = json.loads(self.data_path.read_text())
            
            # Load progress
            for ach_id, prog_data in data.get('progress', {}).items():
                self.progress[ach_id] = AchievementProgress.from_dict(prog_data)
            
            # Load stats
            self.stats.update(data.get('stats', {}))
            
            # Ensure all achievements have progress entries
            self._init_progress()
            
            return True
        except Exception as e:
            print(f"Error loading achievements: {e}")
            return False
    
    def save(self) -> bool:
        """Save progress to file."""
        try:
            data = {
                'progress': {
                    ach_id: prog.to_dict() 
                    for ach_id, prog in self.progress.items()
                },
                'stats': self.stats,
            }
            self.data_path.write_text(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving achievements: {e}")
            return False
    
    def unlock(self, achievement_id: str) -> Optional[Achievement]:
        """Unlock an achievement. Returns Achievement if newly unlocked."""
        if achievement_id not in ACHIEVEMENTS:
            return None
        
        prog = self.progress.get(achievement_id)
        if not prog:
            prog = AchievementProgress(achievement_id=achievement_id)
            self.progress[achievement_id] = prog
        
        if prog.unlocked:
            return None
        
        prog.unlocked = True
        prog.unlock_time = time.time()
        prog.current = ACHIEVEMENTS[achievement_id].progress_max
        self.save()
        
        return ACHIEVEMENTS[achievement_id]
    
    def increment(self, achievement_id: str, amount: int = 1) -> Optional[Achievement]:
        """Increment progress. Returns Achievement if unlocked."""
        if achievement_id not in ACHIEVEMENTS:
            return None
        
        prog = self.progress.get(achievement_id)
        if not prog:
            prog = AchievementProgress(achievement_id=achievement_id)
            self.progress[achievement_id] = prog
        
        if prog.increment(amount):
            self.save()
            return ACHIEVEMENTS[achievement_id]
        
        return None
    
    def check_weather(
        self,
        temperature_f: float,
        condition: str,
        humidity: int,
        pressure: int,
        uv_index: float = 0,
        aqi: int = 0,
        location: str = "",
        latitude: float = 0,
        alerts: List[str] = None,
        is_clearing: bool = False,
    ) -> List[Achievement]:
        """
        Check for achievements based on current weather.
        Returns list of newly unlocked achievements.
        """
        unlocked = []
        now = datetime.now()
        today = now.date().isoformat()
        
        # Update stats
        self.stats['total_checks'] += 1
        
        # Streak tracking
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        if self.stats['last_check_date'] == yesterday:
            self.stats['streak'] += 1
        elif self.stats['last_check_date'] != today:
            self.stats['streak'] = 1
        self.stats['last_check_date'] = today
        
        # ═══════════════════════════════════════════════════════════════════════
        # BASIC ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        # First check
        if result := self.unlock('first_check'):
            unlocked.append(result)
        
        # Check count milestones
        if result := self.increment('century_club'):
            unlocked.append(result)
        if result := self.increment('thousand_checks'):
            unlocked.append(result)
        
        # ═══════════════════════════════════════════════════════════════════════
        # WEATHER CONDITION ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        condition_lower = condition.lower()
        
        # Rain
        if 'rain' in condition_lower or 'drizzle' in condition_lower:
            if result := self.unlock('rain_witness'):
                unlocked.append(result)
            self.stats['rain_days'] += 1
            if result := self.increment('rain_lover'):
                unlocked.append(result)
            if result := self.increment('rain_master'):
                unlocked.append(result)
        
        # Snow
        if 'snow' in condition_lower:
            if result := self.unlock('snow_day'):
                unlocked.append(result)
            if 'heavy' in condition_lower:
                if result := self.unlock('blizzard_survivor'):
                    unlocked.append(result)
        
        # Thunderstorm
        if 'thunder' in condition_lower or 'storm' in condition_lower:
            if result := self.unlock('storm_chaser'):
                unlocked.append(result)
            self.stats['storm_days'] += 1
            if result := self.increment('storm_veteran'):
                unlocked.append(result)
        
        # Fog
        if 'fog' in condition_lower or 'mist' in condition_lower:
            if result := self.unlock('fog_master'):
                unlocked.append(result)
        
        # Freezing rain
        if 'freezing' in condition_lower:
            if result := self.unlock('freezing_rain_survivor'):
                unlocked.append(result)
        
        # Rainbow (clearing after rain)
        if is_clearing:
            if result := self.unlock('rainbow_hunter'):
                unlocked.append(result)
        
        # ═══════════════════════════════════════════════════════════════════════
        # TEMPERATURE ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        # Extreme heat
        if temperature_f >= 100:
            if result := self.unlock('temp_extreme_hot'):
                unlocked.append(result)
        
        # Extreme cold
        if temperature_f <= 0:
            if result := self.unlock('temp_extreme_cold'):
                unlocked.append(result)
        
        # Perfect day
        if (68 <= temperature_f <= 75 and 
            humidity < 60 and 
            'clear' in condition_lower):
            if result := self.unlock('perfect_day'):
                unlocked.append(result)
        
        # Temperature swing
        if self.stats['last_temp'] is not None:
            temp_diff = abs(temperature_f - self.stats['last_temp'])
            if temp_diff >= 20:
                if result := self.unlock('temp_swing'):
                    unlocked.append(result)
        self.stats['last_temp'] = temperature_f
        
        # ═══════════════════════════════════════════════════════════════════════
        # TIME-BASED ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        hour = now.hour
        minute = now.minute
        
        # Night owl (midnight - 5am)
        if 0 <= hour < 5:
            if result := self.unlock('night_owl'):
                unlocked.append(result)
        
        # Early bird (5-6am)
        if 5 <= hour < 6:
            if result := self.unlock('early_bird'):
                unlocked.append(result)
        
        # High noon
        if hour == 12 and minute == 0:
            if result := self.unlock('noon_check'):
                unlocked.append(result)
        
        # Midnight
        if hour == 0 and minute == 0:
            if result := self.unlock('midnight_check'):
                unlocked.append(result)
        
        # ═══════════════════════════════════════════════════════════════════════
        # STREAK ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        if self.stats['streak'] >= 7:
            if result := self.unlock('consistent'):
                unlocked.append(result)
        
        if self.stats['streak'] >= 30:
            if result := self.unlock('monthly_devotion'):
                unlocked.append(result)
        
        # ═══════════════════════════════════════════════════════════════════════
        # LOCATION ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        if location and location not in self.stats['locations_checked']:
            self.stats['locations_checked'].append(location)
            
            if len(self.stats['locations_checked']) > 1:
                if result := self.unlock('location_switch'):
                    unlocked.append(result)
            
            if result := self.increment('globe_trotter'):
                unlocked.append(result)
        
        # Hemisphere tracking
        if latitude != 0:
            hemisphere = 'north' if latitude > 0 else 'south'
            if hemisphere not in self.stats.get('hemispheres', []):
                if 'hemispheres' not in self.stats:
                    self.stats['hemispheres'] = []
                self.stats['hemispheres'].append(hemisphere)
                if len(self.stats['hemispheres']) >= 2:
                    if result := self.unlock('hemisphere_hopper'):
                        unlocked.append(result)
        
        # ═══════════════════════════════════════════════════════════════════════
        # SEASONAL ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        month = now.month
        day = now.day
        
        # Determine season (Northern Hemisphere default)
        if month in (12, 1, 2):
            season = 'winter'
        elif month in (3, 4, 5):
            season = 'spring'
        elif month in (6, 7, 8):
            season = 'summer'
        else:
            season = 'fall'
        
        if season not in self.stats['seasons_checked']:
            self.stats['seasons_checked'].append(season)
            if result := self.increment('four_seasons'):
                unlocked.append(result)
        
        # Solstices and equinoxes (approximate dates)
        if (month == 6 and 20 <= day <= 22) or (month == 12 and 20 <= day <= 22):
            if month == 6:
                if result := self.unlock('summer_solstice'):
                    unlocked.append(result)
            else:
                if result := self.unlock('winter_solstice'):
                    unlocked.append(result)
        
        if (month == 3 and 19 <= day <= 21) or (month == 9 and 21 <= day <= 24):
            if result := self.unlock('equinox_check'):
                unlocked.append(result)
        
        # ═══════════════════════════════════════════════════════════════════════
        # ENVIRONMENTAL ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        # UV extreme
        if uv_index >= 11:
            if result := self.unlock('uv_extreme'):
                unlocked.append(result)
        
        # Poor air quality
        if aqi >= 150:
            if result := self.unlock('poor_air_quality'):
                unlocked.append(result)
        
        # Pressure drop
        if self.stats['last_pressure'] is not None:
            pressure_diff = self.stats['last_pressure'] - pressure
            if pressure_diff >= 10:
                if result := self.unlock('pressure_drop'):
                    unlocked.append(result)
        self.stats['last_pressure'] = pressure
        
        # ═══════════════════════════════════════════════════════════════════════
        # ALERT ACHIEVEMENTS
        # ═══════════════════════════════════════════════════════════════════════
        
        if alerts:
            if result := self.unlock('severe_alert'):
                unlocked.append(result)
            
            for alert in alerts:
                alert_lower = alert.lower()
                if 'tornado' in alert_lower:
                    if result := self.unlock('tornado_watch'):
                        unlocked.append(result)
                if 'hurricane' in alert_lower or 'tropical' in alert_lower:
                    if result := self.unlock('hurricane_tracker'):
                        unlocked.append(result)
        
        self.save()
        return unlocked
    
    def record_action(self, action: str) -> Optional[Achievement]:
        """Record a user action that might trigger achievements."""
        unlocked = None
        
        if action == 'help':
            unlocked = self.unlock('help_reader')
        elif action == 'unit_switch':
            unlocked = self.unlock('unit_switcher')
        elif action == 'theme_change':
            unlocked = self.unlock('theme_explorer')
        elif action == 'screenshot':
            self.stats['screenshots_taken'] = self.stats.get('screenshots_taken', 0) + 1
            unlocked = self.increment('screenshot_master')
        elif action == 'export':
            unlocked = self.unlock('data_exporter')
        elif action == 'creature_spotted':
            unlocked = self.unlock('creature_sighting')
        elif action.startswith('mood_'):
            mood = action.replace('mood_', '')
            if mood not in self.stats.get('moods_seen', []):
                if 'moods_seen' not in self.stats:
                    self.stats['moods_seen'] = []
                self.stats['moods_seen'].append(mood)
                unlocked = self.increment('stormy_mood')
        
        if unlocked:
            self.save()
        return unlocked
    
    def get_unlocked(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [
            ACHIEVEMENTS[prog.achievement_id]
            for prog in self.progress.values()
            if prog.unlocked and prog.achievement_id in ACHIEVEMENTS
        ]
    
    def get_in_progress(self) -> List[Tuple[Achievement, AchievementProgress]]:
        """Get achievements in progress (not yet unlocked but started)."""
        results = []
        for prog in self.progress.values():
            if not prog.unlocked and prog.current > 0:
                ach = ACHIEVEMENTS.get(prog.achievement_id)
                if ach:
                    results.append((ach, prog))
        return results
    
    def get_locked(self, include_secret: bool = False) -> List[Achievement]:
        """Get all locked achievements."""
        locked = []
        for ach_id, ach in ACHIEVEMENTS.items():
            prog = self.progress.get(ach_id)
            if not prog or not prog.unlocked:
                if include_secret or not ach.secret:
                    locked.append(ach)
        return locked
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        total = len(ACHIEVEMENTS)
        unlocked = len(self.get_unlocked())
        
        by_tier = {tier: 0 for tier in AchievementTier}
        by_category = {cat: 0 for cat in AchievementCategory}
        
        for ach in self.get_unlocked():
            by_tier[ach.tier] += 1
            by_category[ach.category] += 1
        
        return {
            'total': total,
            'unlocked': unlocked,
            'percent': (unlocked / total) * 100 if total > 0 else 0,
            'by_tier': {t.value: c for t, c in by_tier.items()},
            'by_category': {c.value: n for c, n in by_category.items()},
            'streak': self.stats.get('streak', 0),
            'total_checks': self.stats.get('total_checks', 0),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🏆 Achievement System Test\n")
    
    manager = AchievementManager()
    
    # Simulate some weather checks
    print("Simulating weather checks...")
    
    # First check
    unlocked = manager.check_weather(
        temperature_f=72,
        condition="Clear",
        humidity=45,
        pressure=1015,
        location="Test City",
    )
    print(f"First check unlocked: {[a.name for a in unlocked]}")
    
    # Rainy day
    unlocked = manager.check_weather(
        temperature_f=55,
        condition="Rain",
        humidity=85,
        pressure=1008,
        location="Test City",
    )
    print(f"Rain check unlocked: {[a.name for a in unlocked]}")
    
    # Show stats
    stats = manager.get_stats_summary()
    print(f"\n📊 Stats:")
    print(f"  Unlocked: {stats['unlocked']}/{stats['total']} ({stats['percent']:.0f}%)")
    print(f"  Streak: {stats['streak']} days")
    print(f"  Total checks: {stats['total_checks']}")
