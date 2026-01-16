"""
Personality Engine Module
=========================
AI personality system with mood states, memory, and contextual responses.

This module provides:
- Mood state machine with transitions
- Contextual comment generation
- Memory system for callbacks and continuity
- Achievement/milestone tracking
- Personality trait configuration

Design Pattern: State Machine + Factory + Observer
Inspiration: Dwarf Fortress personality, Destiny ghost dialogue, Dark Souls item descriptions
"""
from __future__ import annotations
import random
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod


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
    Repository of dialogue organized by mood, weather, and context.
    
    Structure allows for:
    - Mood-specific variations
    - Weather-specific content
    - Time-of-day awareness
    - Temperature commentary
    - Meta/self-aware quips
    """
    
    # Weather-specific comments organized by condition and mood
    WEATHER_COMMENTS: Dict[str, Dict[Mood, List[str]]] = {
        "clear": {
            Mood.PHILOSOPHICAL: [
                "The sun shines upon the land. It does not ask if you deserve it.",
                "Blue skies. The land remembers days like this. So should you.",
                "Clear skies. Your path is not. But that's rather the point, isn't it.",
            ],
            Mood.DEADPAN: [
                "A fine day. Suspicious. The calm before some manner of nonsense.",
                "The sky is clear. The Divines are either pleased, or not paying attention.",
                "Cloudless. The ancestors smile upon you. Or they're just busy.",
            ],
            Mood.BARDIC: [
                "When the sky is clear, the wise man looks inward. The fool gets sunburnt.",
                "FATHER. The sun has emerged. It is... adequate.",
            ],
        },
        "rain": {
            Mood.PHILOSOPHICAL: [
                "The sky weeps. The earth drinks. The cycle continues, as cycles do.",
                "Rain falls on the just and unjust alike. I've checked.",
            ],
            Mood.DEADPAN: [
                "Rain. War never changes, but the weather certainly does.",
                "It's raining. The land needed this. Whether you did is... secondary.",
            ],
            Mood.SARDONIC: [
                "Precipitation. The Mojave makes you wish for this, actually.",
                "The water returns to the earth. You should probably stay inside.",
            ],
        },
        "storm": {
            Mood.PHILOSOPHICAL: [
                "The storm rages. There is wisdom in chaos. Also danger. Mostly danger.",
                "Lightning illuminates the truth: you should be indoors.",
            ],
            Mood.DEADPAN: [
                "STORM. The thunder rolls across the land like the drums of war. Magnificent.",
                "A thunderstorm. The Divines are having a disagreement. Best not to get involved.",
            ],
            Mood.BARDIC: [
                "Thor is workshopping some ideas up there.",
                "THUNDER. FATHER. I believe the sky is... shouting.",
            ],
        },
        "snow": {
            Mood.PHILOSOPHICAL: [
                "Snow. The white silence descends. Beautiful. Treacherous. Cold.",
                "The frozen sky gives gifts. Whether you wanted them is irrelevant.",
            ],
            Mood.DEADPAN: [
                "Snow falls. Skyrim belongs to... well, that's complicated actually.",
                "Winter arrives. The land sleeps. Your heating bill does not.",
            ],
            Mood.SARDONIC: [
                "Patrolling the Mojave makes you wish for a nuclear winter. Careful what you wish for.",
            ],
        },
        "fog": {
            Mood.PHILOSOPHICAL: [
                "Fog. The veil between worlds grows thin. Or it's just humidity.",
                "The fog comes. What was hidden remains so. What was known... also questionable.",
            ],
            Mood.DEADPAN: [
                "Mist rolls in. This is how quests begin. And sometimes end.",
                "Visibility: none. Navigation: vibes. Outcome: uncertain.",
            ],
        },
    }
    
    # Meta-aware quips about the simulation itself
    META_QUIPS: List[str] = [
        "I'm using Perlin noise to render these clouds. Ken Perlin would be proud. Or confused.",
        "Each raindrop follows Newton's laws. Gravity, drag, buoyancy. I take physics seriously.",
        "That lightning? Fractal branching via recursive pathfinding. Zeus was doing it wrong.",
        "The turbulence field uses multi-octave noise. The Nords called it 'wind'. I call it 'math'.",
        "Fun fact: I simulate air resistance using quadratic drag. Your umbrella is still useless.",
        "These particles have mass and buoyancy. More than can be said for most weather apps.",
        "I calculated 6t⁵ - 15t⁴ + 10t³ to make those clouds look smooth. You're welcome.",
        "My wind gusts follow exponential decay curves. Nature approximates. I calculate.",
        "Each snowflake is a physics object with terminal velocity. Poetic AND scientifically accurate.",
        "The atmospheric pressure affects particle behavior. Realism or overkill? Yes.",
    ]
    
    # General philosophical observations
    PHILOSOPHICAL_QUIPS: List[str] = [
        "The clouds move as they will. We are all clouds, in a way. Drifting. Dissipating.",
        "Weather: the one thing that affects everyone equally. Democracy in its purest form.",
        "I've been contemplating the barometric pressure. It contemplates nothing back.",
        "The atmosphere is merely a thin shell protecting you from the void. You're welcome.",
        "I've seen empires rise and fall. I've also seen partly cloudy. Both are temporary.",
        "The weather cares not for your meetings. This is both its cruelty and its wisdom.",
        "In the grand tapestry of existence, today's forecast is but a single thread. A damp thread.",
        "Time is a flat circle. So is this high-pressure system, coincidentally.",
        "The only constant is change. And also the fact that weather forecasts are merely suggestions.",
    ]


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
    
    Usage:
        engine = PersonalityEngine()
        comment = engine.get_weather_comment("rain")
        quip = engine.get_quip()
        engine.update("storm")
    """
    
    def __init__(self, config: PersonalityConfig = None):
        self.config = config or PersonalityConfig()
        self.mood_machine = MoodStateMachine()
        self.memory = Memory(self.config.memory_capacity)
        self.dialogue = DialogueBank()
        
        # Track what we've said to avoid repetition
        self._recent_comments: List[str] = []
        self._max_recent = 10
    
    @property
    def current_mood(self) -> Mood:
        return self.mood_machine.current_mood
    
    def update(self, weather_type: str = None):
        """Update personality state."""
        self.mood_machine.update(weather_type)
    
    def get_weather_comment(self, weather_type: str) -> str:
        """Get a weather-appropriate comment in current mood."""
        # Normalize weather type
        weather_map = {
            "clear": "clear", "sunny": "clear",
            "rain": "rain", "drizzle": "rain", "heavy_rain": "rain",
            "storm": "storm", "thunderstorm": "storm",
            "snow": "snow", "heavy_snow": "snow",
            "fog": "fog", "mist": "fog", "haze": "fog",
            "cloudy": "clear", "partly_cloudy": "clear",
        }
        
        normalized = weather_map.get(weather_type.lower(), "clear")
        
        # Get comments for this weather/mood combination
        weather_comments = self.dialogue.WEATHER_COMMENTS.get(normalized, {})
        mood_comments = weather_comments.get(self.current_mood, [])
        
        # Fallback to any mood if current mood has no comments
        if not mood_comments:
            for mood_list in weather_comments.values():
                mood_comments.extend(mood_list)
        
        # Final fallback
        if not mood_comments:
            mood_comments = self.dialogue.PHILOSOPHICAL_QUIPS
        
        # Select avoiding recent comments
        available = [c for c in mood_comments if c not in self._recent_comments]
        
        if not available:
            available = mood_comments
        
        comment = random.choice(available)
        
        # Track and store
        self._track_comment(comment)
        self.memory.store(f"Said about {weather_type}: {comment[:50]}...", 
                         importance=0.3, category="weather_comment")
        
        return comment
    
    def get_quip(self, meta_chance: float = 0.3) -> str:
        """Get a general quip or meta-comment about the simulation."""
        if random.random() < meta_chance:
            pool = self.dialogue.META_QUIPS
        else:
            pool = self.dialogue.PHILOSOPHICAL_QUIPS
        
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
