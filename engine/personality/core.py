"""
Personality Engine Module
=========================
AI personality system with mood states, memory, and contextual responses.

Design Pattern: State Machine + Factory + Observer
Inspiration: Dwarf Fortress personality, Destiny ghost dialogue, Dark Souls item descriptions

Now powered by the unified dialogue pool in data/dialogue.py — all 200+ lines
of noir/wasteland/prophet/crooner/absurdist writing, no longer dead code.
"""
from __future__ import annotations
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod

from data.dialogue import (
    WEATHER_COMMENTS, TEMP_COMMENTS, GREETINGS, QUIPS,
    WEATHER_TYPE_MAP, get_temp_category,
)


class Mood(Enum):
    """Personality mood states."""
    PHILOSOPHICAL = auto()   # Deep thoughts, cosmic scale
    DEADPAN = auto()        # Dry humor, understated
    BARDIC = auto()         # References, literary
    EXISTENTIAL = auto()    # Questioning, melancholic
    SARDONIC = auto()       # Sharp wit, irony
    CONTEMPLATIVE = auto()  # Quiet wisdom
    AMUSED = auto()         # Finding humor in situation
    CONCERNED = auto()      # Worried, warning


class PersonalityTrait(Enum):
    """Configurable personality traits."""
    WIT = auto()           # Clever remarks frequency
    WISDOM = auto()        # Philosophical depth
    REFERENCES = auto()    # Pop culture/literary references
    SNARK = auto()         # Sarcasm level
    WARMTH = auto()        # Friendliness
    MYSTERY = auto()       # Cryptic messages


@dataclass
class MemoryEntry:
    """Single memory entry with decay."""
    content: str
    timestamp: float
    importance: float = 0.5  # [0, 1] affects recall probability
    category: str = "general"

    def age(self) -> float:
        """Time since memory creation in seconds."""
        return time.time() - self.timestamp

    def recall_probability(self) -> float:
        """Probability of recalling this memory (decays over time)."""
        decay = 0.99 ** (self.age() / 60)  # Decay per minute
        return self.importance * decay


@dataclass
class PersonalityConfig:
    """Configuration for personality behavior."""
    name: str = "Stormy"
    traits: Dict[PersonalityTrait, float] = field(default_factory=lambda: {
        PersonalityTrait.WIT: 0.8,
        PersonalityTrait.WISDOM: 0.7,
        PersonalityTrait.REFERENCES: 0.9,
        PersonalityTrait.SNARK: 0.6,
        PersonalityTrait.WARMTH: 0.4,
        PersonalityTrait.MYSTERY: 0.5,
    })
    mood_change_rate: float = 0.1  # Probability of mood shift
    memory_capacity: int = 50
    callback_chance: float = 0.15  # Chance to reference past events


class DialogueBank:
    """
    Repository of dialogue organized by weather and context.

    Pulls from the unified data/dialogue.py pool which contains all
    200+ lines of rich noir/wasteland/prophet/crooner/absurdist dialogue
    merged with engine-original content. No more dead code.
    """

    # Expose the unified pools directly
    WEATHER_COMMENTS = WEATHER_COMMENTS
    TEMP_COMMENTS = TEMP_COMMENTS
    GREETINGS = GREETINGS
    QUIPS = QUIPS

    # Meta quips get pulled from the QUIPS pool — filter for physics/meta lines
    META_QUIPS: List[str] = [q for q in QUIPS if any(kw in q.lower() for kw in
        ["perlin", "physics", "particle", "newton", "fractal", "turbulence",
         "drag", "terminal velocity", "atmospheric", "calculated", "simulate",
         "render", "noise", "buoyancy", "dew point", "barometric"])]

    # Philosophical subset for fallback
    PHILOSOPHICAL_QUIPS: List[str] = [q for q in QUIPS if q not in
        [mq for mq in QUIPS if any(kw in q.lower() for kw in
        ["perlin", "physics", "particle", "newton", "fractal", "turbulence",
         "drag", "terminal velocity", "atmospheric", "calculated", "simulate",
         "render", "noise", "buoyancy"])]]


class MoodStateMachine:
    """
    Finite state machine for mood transitions.

    Transitions based on:
    - Weather conditions
    - Time of day
    - Random variation
    - User interaction
    """

    # Transition probabilities: (from_mood, to_mood) -> probability
    TRANSITIONS = {
        (Mood.PHILOSOPHICAL, Mood.DEADPAN): 0.3,
        (Mood.PHILOSOPHICAL, Mood.CONTEMPLATIVE): 0.2,
        (Mood.DEADPAN, Mood.SARDONIC): 0.3,
        (Mood.DEADPAN, Mood.AMUSED): 0.2,
        (Mood.SARDONIC, Mood.DEADPAN): 0.4,
        (Mood.CONTEMPLATIVE, Mood.PHILOSOPHICAL): 0.3,
        (Mood.AMUSED, Mood.DEADPAN): 0.4,
        (Mood.CONCERNED, Mood.PHILOSOPHICAL): 0.3,
        (Mood.BARDIC, Mood.PHILOSOPHICAL): 0.3,
        (Mood.BARDIC, Mood.AMUSED): 0.2,
    }

    # Weather influences on mood
    WEATHER_MOOD_BIAS = {
        "clear": [Mood.PHILOSOPHICAL, Mood.CONTEMPLATIVE, Mood.AMUSED],
        "rain": [Mood.PHILOSOPHICAL, Mood.DEADPAN, Mood.CONTEMPLATIVE],
        "storm": [Mood.CONCERNED, Mood.BARDIC, Mood.DEADPAN],
        "snow": [Mood.CONTEMPLATIVE, Mood.PHILOSOPHICAL],
        "fog": [Mood.PHILOSOPHICAL, Mood.DEADPAN, Mood.EXISTENTIAL],
    }

    def __init__(self, initial_mood: Mood = Mood.PHILOSOPHICAL):
        self.current_mood = initial_mood
        self.mood_history: List[Mood] = [initial_mood]
        self.time_in_mood = 0

    def update(self, weather_type: str = None, force_transition: bool = False) -> bool:
        """
        Potentially transition to a new mood.

        Returns True if mood changed.
        """
        self.time_in_mood += 1

        # Natural transition probability increases over time
        base_prob = min(0.3, self.time_in_mood * 0.01)

        if force_transition or random.random() < base_prob:
            return self._transition(weather_type)

        return False

    def _transition(self, weather_type: str = None) -> bool:
        """Execute mood transition."""
        candidates = []

        # Weather-biased moods
        if weather_type and weather_type in self.WEATHER_MOOD_BIAS:
            candidates.extend(self.WEATHER_MOOD_BIAS[weather_type])

        # Transition-based candidates
        for (from_mood, to_mood), prob in self.TRANSITIONS.items():
            if from_mood == self.current_mood and random.random() < prob:
                candidates.append(to_mood)

        # Random fallback
        if not candidates:
            candidates = list(Mood)

        new_mood = random.choice(candidates)

        if new_mood != self.current_mood:
            self.mood_history.append(new_mood)
            self.current_mood = new_mood
            self.time_in_mood = 0
            return True

        return False


class Memory:
    """
    Memory system for personality continuity.

    Allows callbacks to previous events, creating the illusion
    of continuous awareness.
    """

    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.entries: List[MemoryEntry] = []

    def store(self, content: str, importance: float = 0.5, category: str = "general"):
        """Store a new memory."""
        entry = MemoryEntry(
            content=content,
            timestamp=time.time(),
            importance=importance,
            category=category
        )

        self.entries.append(entry)

        # Prune if over capacity (remove oldest, least important)
        if len(self.entries) > self.capacity:
            self.entries.sort(key=lambda e: e.recall_probability())
            self.entries = self.entries[-self.capacity:]

    def recall(self, category: str = None) -> Optional[str]:
        """
        Attempt to recall a memory.

        Returns None if recall fails.
        """
        candidates = self.entries

        if category:
            candidates = [e for e in candidates if e.category == category]

        if not candidates:
            return None

        # Weighted random selection by recall probability
        weights = [e.recall_probability() for e in candidates]
        total = sum(weights)

        if total <= 0:
            return None

        r = random.uniform(0, total)
        cumulative = 0

        for entry, weight in zip(candidates, weights):
            cumulative += weight
            if r <= cumulative:
                return entry.content

        return candidates[-1].content


class PersonalityEngine:
    """
    Main personality engine combining mood, memory, and dialogue.

    Now uses the full unified dialogue pool — all 200+ weather comments,
    45+ quips, greetings, and temperature commentary are live.

    Usage:
        engine = PersonalityEngine()
        comment = engine.get_weather_comment("rain")
        quip = engine.get_quip()
        greeting = engine.get_greeting()
        temp_comment = engine.get_temp_comment(72.0)
        engine.update("storm")
    """

    def __init__(self, config: PersonalityConfig = None):
        self.config = config or PersonalityConfig()
        self.mood_machine = MoodStateMachine()
        self.memory = Memory(self.config.memory_capacity)
        self.dialogue = DialogueBank()

        # Track what we've said to avoid repetition
        self._recent_comments: List[str] = []
        self._max_recent = 15

    @property
    def current_mood(self) -> Mood:
        return self.mood_machine.current_mood

    def update(self, weather_type: str = None):
        """Update personality state."""
        self.mood_machine.update(weather_type)

    def get_weather_comment(self, weather_type: str) -> str:
        """Get a weather-appropriate comment from the full dialogue pool."""
        from lib.weather_api import WeatherCondition

        # Normalize string weather types to WeatherCondition for lookup
        weather_map = {
            "clear": WeatherCondition.CLEAR,
            "sunny": WeatherCondition.CLEAR,
            "rain": WeatherCondition.RAIN,
            "drizzle": WeatherCondition.DRIZZLE,
            "heavy_rain": WeatherCondition.HEAVY_RAIN,
            "storm": WeatherCondition.THUNDERSTORM,
            "thunderstorm": WeatherCondition.THUNDERSTORM,
            "snow": WeatherCondition.SNOW,
            "heavy_snow": WeatherCondition.HEAVY_SNOW,
            "fog": WeatherCondition.FOG,
            "mist": WeatherCondition.FOG,
            "haze": WeatherCondition.FOG,
            "cloudy": WeatherCondition.CLOUDY,
            "partly_cloudy": WeatherCondition.PARTLY_CLOUDY,
            "freezing_rain": WeatherCondition.FREEZING_RAIN,
        }

        condition = weather_map.get(weather_type.lower(), WeatherCondition.CLOUDY)
        comments = self.dialogue.WEATHER_COMMENTS.get(
            condition, self.dialogue.WEATHER_COMMENTS.get(WeatherCondition.CLOUDY, [])
        )

        if not comments:
            comments = self.dialogue.PHILOSOPHICAL_QUIPS

        # Select avoiding recent comments
        available = [c for c in comments if c not in self._recent_comments]
        if not available:
            available = comments

        comment = random.choice(available)

        # Track and store
        self._track_comment(comment)
        self.memory.store(f"Said about {weather_type}: {comment[:50]}...",
                         importance=0.3, category="weather_comment")

        return comment

    def get_weather_comment_by_condition(self, condition) -> str:
        """Get a weather comment using a WeatherCondition enum directly."""
        comments = self.dialogue.WEATHER_COMMENTS.get(condition, [])

        if not comments:
            comments = self.dialogue.PHILOSOPHICAL_QUIPS

        available = [c for c in comments if c not in self._recent_comments]
        if not available:
            available = comments

        comment = random.choice(available)
        self._track_comment(comment)
        self.memory.store(f"Said about weather: {comment[:50]}...",
                         importance=0.3, category="weather_comment")
        return comment

    def get_greeting(self) -> str:
        """Get a time-appropriate greeting from the full pool."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 17:
            period = "afternoon"
        elif 17 <= hour < 21:
            period = "evening"
        else:
            period = "night"

        greetings = self.dialogue.GREETINGS.get(period, [])
        if not greetings:
            return "The weather speaks. Listen."

        available = [g for g in greetings if g not in self._recent_comments]
        if not available:
            available = greetings

        greeting = random.choice(available)
        self._track_comment(greeting)
        return greeting

    def get_temp_comment(self, temp_f: float) -> str:
        """Get a temperature-based comment."""
        category = get_temp_category(temp_f)
        comments = self.dialogue.TEMP_COMMENTS.get(category, [])

        if not comments:
            return "The temperature exists. Make of that what you will."

        available = [c for c in comments if c not in self._recent_comments]
        if not available:
            available = comments

        comment = random.choice(available)
        self._track_comment(comment)
        return comment

    def get_quip(self, meta_chance: float = 0.3) -> str:
        """Get a general quip or meta-comment about the simulation."""
        if random.random() < meta_chance:
            pool = self.dialogue.META_QUIPS
        else:
            pool = self.dialogue.QUIPS

        available = [q for q in pool if q not in self._recent_comments]

        if not available:
            available = pool

        quip = random.choice(available)
        self._track_comment(quip)

        return quip

    def get_callback(self) -> Optional[str]:
        """
        Attempt to make a callback to a previous comment/event.

        Returns None if no callback is appropriate.
        """
        if random.random() > self.config.callback_chance:
            return None

        memory = self.memory.recall()

        if memory:
            callbacks = [
                f"I recall mentioning: {memory}",
                f"As I said before... {memory}",
                f"Speaking of which... {memory}",
            ]
            return random.choice(callbacks)

        return None

    def _track_comment(self, comment: str):
        """Track recent comments to avoid repetition."""
        self._recent_comments.append(comment)
        if len(self._recent_comments) > self._max_recent:
            self._recent_comments.pop(0)


# Factory function
def create_personality(name: str = "Stormy", **trait_overrides) -> PersonalityEngine:
    """Create a personality engine with custom traits."""
    config = PersonalityConfig(name=name)

    for trait_name, value in trait_overrides.items():
        try:
            trait = PersonalityTrait[trait_name.upper()]
            config.traits[trait] = value
        except KeyError:
            pass

    return PersonalityEngine(config)
