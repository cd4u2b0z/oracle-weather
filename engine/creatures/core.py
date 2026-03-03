"""
Creatures Module - Easter Egg Creature System
==============================================
Manages rare, weather-dependent creature appearances in the dashboard.

Creatures appear based on:
- Weather condition (fog, rain, snow, storm, clear, cloudy)
- Time of day (day vs night)
- Random chance (rarity factor)

Each creature has:
- Multi-frame ASCII art animation
- Movement speed
- Color theme
- Spawn rarity

Design: Factory pattern for creature spawning, state machine for animation
"""
from __future__ import annotations
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto


class CreatureCategory(Enum):
    """Weather/time categories for creature spawning."""
    FOG_NIGHT = "fog_night"
    FOG_DAY = "fog_day"
    STORM_NIGHT = "storm_night"
    STORM_DAY = "storm_day"
    RAIN_NIGHT = "rain_night"
    RAIN_DAY = "rain_day"
    SNOW_NIGHT = "snow_night"
    SNOW_DAY = "snow_day"
    CLEAR_NIGHT = "clear_night"
    CLEAR_DAY = "clear_day"
    CLOUDY_ANY = "cloudy_any"


@dataclass
class Creature:
    """A single creature definition."""
    name: str
    frames: List[List[str]]
    colour: str
    speed: float
    rarity: float
    
    def get_frame(self, frame_index: int) -> List[str]:
        """Get animation frame by index (wraps around)."""
        return self.frames[frame_index % len(self.frames)]
    
    @property
    def frame_count(self) -> int:
        return len(self.frames)
    
    @property
    def height(self) -> int:
        return len(self.frames[0]) if self.frames else 0
    
    @property
    def width(self) -> int:
        return max(len(line) for line in self.frames[0]) if self.frames else 0


# ═══════════════════════════════════════════════════════════════════════════════
# CREATURE DEFINITIONS - Organized by weather condition and time
# ═══════════════════════════════════════════════════════════════════════════════

CREATURES: Dict[str, List[Dict[str, Any]]] = {
    # ─────────────────────────────────────────────────────────────────────────
    # FOG - Eldritch horrors lurking in the mist
    # ─────────────────────────────────────────────────────────────────────────
    "fog_night": [
        {
            "name": "Cthulhu Tentacle",
            "frames": [
                ["  _/¯", " / _/", "| /  ", "|/   "],
                [" _/¯ ", "/ _/ ", "| /  ", "|/   "],
                ["_/¯  ", " _/  ", "| /  ", " /   "],
            ],
            "colour": "MAGIC",
            "speed": 0.15,
            "rarity": 0.0015,
        },
        {
            "name": "Eldritch Eye",
            "frames": [
                ["  ◉  ", " (◉) ", "  ◉  "],
                [" ◉   ", "(◉)  ", " ◉   "],
                ["◉    ", "(◉)  ", "◉    "],
            ],
            "colour": "DANGER",
            "speed": 0.08,
            "rarity": 0.0015,
        },
    ],
    "fog_day": [
        {
            "name": "Ghost",
            "frames": [
                ["   .-.   ", "  ( o o) ", "  | O |  ", "  |   |  ", " /|   |\\ ", "  '~~~'  "],
                ["   .-.   ", "  (o o ) ", "  | O |  ", "  |   |  ", " /|   |\\ ", " '~~~'   "],
                ["   .-.   ", "  ( o o) ", "  | o |  ", "  |   |  ", " /|   |\\ ", "  '~~~'  "],
            ],
            "colour": "SNOW",
            "speed": 0.08,
            "rarity": 0.0015,
        },
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # THUNDERSTORM - Dragons and storm spirits
    # ─────────────────────────────────────────────────────────────────────────
    "storm_night": [
        {
            "name": "Dragon",
            "frames": [
                ["    __===~~    ", "  <(o )___/    ", "   ( ._> /     ", "    `---'      "],
                ["    __===~`    ", "  <(o )___/    ", "   ( ._> /  ~  ", "    `---'      "],
            ],
            "colour": "DANGER",
            "speed": 0.25,
            "rarity": 0.0015,
        },
        {
            "name": "Storm Wraith",
            "frames": [
                ["  ╱╲  ", " ╱◈◈╲ ", "╱~~~~╲", " ╲~~/╱", "  ╲╱  "],
                [" ╱╲   ", "╱◈◈╲  ", "~~~~╲ ", "╲~~/╱ ", " ╲╱   "],
            ],
            "colour": "FROST",
            "speed": 0.18,
            "rarity": 0.0015,
        },
    ],
    "storm_day": [
        {
            "name": "Thunder Bird",
            "frames": [
                ["  /\\_//\\  ", " /  ◉◉  \\ ", "/   <>   \\", "\\  /\\  / ", " \\_/\\_/  "],
                [" /\\_//\\   ", "/  ◉◉  \\  ", "   <>   \\ ", "\\  /\\  /  ", " \\_/\\_/   "],
            ],
            "colour": "SUN",
            "speed": 0.3,
            "rarity": 0.0015,
        },
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # RAIN - Water spirits and mystical beings
    # ─────────────────────────────────────────────────────────────────────────
    "rain_night": [
        {
            "name": "Sea Serpent",
            "frames": [
                ["  ~~~°)    ", " (°~~~     ", "  ~~~°)    "],
                [" ~~~°)     ", "(°~~~      ", " ~~~°)     "],
            ],
            "colour": "FROST",
            "speed": 0.2,
            "rarity": 0.0015,
        },
        {
            "name": "Will-o-Wisp",
            "frames": [
                ["  *  ", " ◦●◦ ", "  *  "],
                [" *   ", "◦●◦  ", " *   "],
            ],
            "colour": "MAGIC",
            "speed": 0.1,
            "rarity": 0.0015,
        },
    ],
    "rain_day": [
        {
            "name": "Rain Spirit",
            "frames": [
                [" ╭◡╮ ", " │~│ ", " ╰┬╯ ", "  │  "],
                ["╭◡╮  ", "│~│  ", "╰┬╯  ", " │   "],
            ],
            "colour": "FROST",
            "speed": 0.15,
            "rarity": 0.0015,
        },
        {
            "name": "Frog Prince",
            "frames": [
                ["  @..@  ", " (----) ", "(  >  <)", " ^^ ^^  "],
                [" @..@   ", "(----)  ", "(>  <)  ", "^^ ^^   "],
            ],
            "colour": "NATURE",
            "speed": 0.12,
            "rarity": 0.0015,
        },
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # SNOW - Winter spirits and ice creatures
    # ─────────────────────────────────────────────────────────────────────────
    "snow_night": [
        {
            "name": "Ice Wraith",
            "frames": [
                ["  ❄  ", " ╱◇╲ ", "╱ ╳ ╲", "╲   ╱", " ╲ ╱ "],
                [" ❄   ", "╱◇╲  ", " ╳ ╲ ", "\\   ╱", " \\ ╱ "],
            ],
            "colour": "FROST",
            "speed": 0.12,
            "rarity": 0.0015,
        },
        {
            "name": "Wendigo",
            "frames": [
                ["  ╱╲  ", " ╱◉◉╲ ", " │▼▼│ ", "╱│  │╲", "  ││  "],
                [" ╱╲   ", "╱◉◉╲  ", "│▼▼│  ", "│  │╲ ", " ││   "],
            ],
            "colour": "SNOW",
            "speed": 0.1,
            "rarity": 0.0015,
        },
    ],
    "snow_day": [
        {
            "name": "Yeti",
            "frames": [
                [" ╭───╮ ", " │◕ ◕│ ", " │ ▽ │ ", " ╰┬─┬╯ ", "  │ │  "],
                ["╭───╮  ", "│◕ ◕│  ", "│ ▽ │  ", "╰┬─┬╯  ", " │ │   "],
            ],
            "colour": "SNOW",
            "speed": 0.08,
            "rarity": 0.0015,
        },
        {
            "name": "Snowman",
            "frames": [
                ["  .--.  ", " (o  o) ", " /    \\ ", "(  __  )", " \\    / ", "  '--'  "],
                [" .--.   ", "(o  o)  ", "/    \\  ", "(  __  )", "\\    /  ", " '--'   "],
            ],
            "colour": "SNOW",
            "speed": 0.05,
            "rarity": 0.0015,
        },
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # CLEAR NIGHT - Celestial beings and nocturnal creatures
    # ─────────────────────────────────────────────────────────────────────────
    "clear_night": [
        {
            "name": "UFO",
            "frames": [
                ["    __    ", " __/  \\__ ", "(___◦◦___)", "   \\__/   "],
                ["   __     ", "__/  \\__  ", "(___◦◦___) ", "  \\__/    "],
            ],
            "colour": "NATURE",
            "speed": 0.2,
            "rarity": 0.0015,
        },
        {
            "name": "Shooting Star",
            "frames": [
                ["        ★", "      ·  ", "    ·    ", "  ·      "],
                ["       ★ ", "     ·   ", "   ·     ", " ·       "],
            ],
            "colour": "SUN",
            "speed": 0.5,
            "rarity": 0.0015,
        },
        {
            "name": "Bat",
            "frames": [
                [" /\\  /\\ ", "   \\/   "],
                ["/\\  /\\  ", "  \\/    "],
            ],
            "colour": "MUTED",
            "speed": 0.25,
            "rarity": 0.0015,
        },
        {
            "name": "Owl",
            "frames": [
                [" ,_, ", "(O,O)", "(   )", " \" \" "],
                [",_,  ", "(O,O) ", "(   ) ", " \" \"  "],
            ],
            "colour": "MUTED",
            "speed": 0.1,
            "rarity": 0.0015,
        },
        {
            "name": "Firefly",
            "frames": [
                ["  ·* ", " *·  ", "  *· "],
                [" ·*  ", "*·   ", " *·  "],
            ],
            "colour": "SUN",
            "speed": 0.08,
            "rarity": 0.002,
        },
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # CLEAR DAY - Mythical beasts and nature spirits
    # ─────────────────────────────────────────────────────────────────────────
    "clear_day": [
        {
            "name": "Phoenix",
            "frames": [
                ["  ,~~,  ", " {*◉*}  ", " /)~~(\\ ", "  \\||/  "],
                [" ,~~,   ", "{*◉*}   ", "/)~~(\\  ", " \\||/   "],
            ],
            "colour": "DANGER",
            "speed": 0.22,
            "rarity": 0.0015,
        },
        {
            "name": "Butterfly",
            "frames": [
                [" ╱◠╲ ", "◠─◠─◠", " ╲◠╱ "],
                ["╱◠╲  ", "◠─◠─◠", "╲◠╱  "],
            ],
            "colour": "MAGIC",
            "speed": 0.15,
            "rarity": 0.0015,
        },
        {
            "name": "Hummingbird",
            "frames": [
                ["  <\\_ ", " (o>) ", "  /__>"],
                [" <\\_  ", "(o>)  ", " /__> "],
            ],
            "colour": "NATURE",
            "speed": 0.3,
            "rarity": 0.0015,
        },
        {
            "name": "Bee",
            "frames": [
                [" \\_/ ", " -●- ", " / \\ "],
                ["\\_/  ", "-●-  ", "/ \\  "],
            ],
            "colour": "SUN",
            "speed": 0.18,
            "rarity": 0.0018,
        },
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # CLOUDY - Sky creatures
    # ─────────────────────────────────────────────────────────────────────────
    "cloudy_any": [
        {
            "name": "Cloud Whale",
            "frames": [
                ["    .------.    ", "  /   ◉    \\   ", " /          \\  ", "(    ~~~~    ) ", " \\          /  ", "  `--------´   "],
                ["   .------.     ", " /   ◉    \\    ", "/          \\   ", "(    ~~~~    )  ", "\\          /   ", " `--------´    "],
            ],
            "colour": "SNOW",
            "speed": 0.06,
            "rarity": 0.0015,
        },
        {
            "name": "Paper Airplane",
            "frames": [
                ["   /\\ ", "  /  \\", " /____\\"],
                ["  /\\  ", " /  \\ ", "/____\\"],
            ],
            "colour": "SNOW",
            "speed": 0.25,
            "rarity": 0.0018,
        },
    ],
}


class CreatureManager:
    """
    Manages creature spawning, animation, and rendering.
    
    Usage:
        manager = CreatureManager(x=10, width=80, height=40)
        manager.try_spawn(condition="clear", hour=22)
        manager.update()
        manager.draw(screen, colour_map={'MAGIC': 5, 'SNOW': 7, ...})
    """
    
    def __init__(self, animation_x: int, animation_width: int, height: int):
        """
        Initialize the creature manager.
        
        Args:
            animation_x: Left edge of animation area
            animation_width: Width of animation area
            height: Height of animation area
        """
        self.ax = animation_x
        self.aw = animation_width
        self.height = height
        self.active_creature: Optional[Dict] = None
        self.creature_x: float = 0
        self.creature_y: int = 0
        self.creature_frame: int = 0
        self.frame_timer: int = 0
        self._y_set: bool = False
    
    def get_creature_key(self, condition: str, hour: int) -> Optional[str]:
        """
        Get the creature category key for given condition and time.
        
        Args:
            condition: Weather condition string (e.g., 'FOG', 'CLEAR', 'RAIN')
            hour: Current hour (0-23)
            
        Returns:
            Category key string or None
        """
        is_night = hour < 6 or hour >= 20
        time_suffix = "night" if is_night else "day"
        
        condition_upper = condition.upper() if isinstance(condition, str) else str(condition).upper()
        
        # Map conditions to creature categories
        if "FOG" in condition_upper:
            return f"fog_{time_suffix}"
        elif "THUNDER" in condition_upper or "STORM" in condition_upper:
            return f"storm_{time_suffix}"
        elif "RAIN" in condition_upper or "DRIZZLE" in condition_upper:
            return f"rain_{time_suffix}"
        elif "SNOW" in condition_upper:
            return f"snow_{time_suffix}"
        elif "CLEAR" in condition_upper:
            return f"clear_{time_suffix}"
        elif "CLOUD" in condition_upper:
            return "cloudy_any"
        return None
    
    def try_spawn(self, condition: str, hour: int) -> bool:
        """
        Attempt to spawn a creature based on weather and time.
        
        Args:
            condition: Weather condition
            hour: Current hour
            
        Returns:
            True if a creature was spawned
        """
        if self.active_creature:
            return False  # Already have one
        
        key = self.get_creature_key(condition, hour)
        if not key or key not in CREATURES:
            return False
        
        creatures = CREATURES[key]
        for creature in creatures:
            if random.random() < creature["rarity"]:
                self.active_creature = creature
                self.creature_x = self.ax + 2
                self.creature_frame = 0
                self.frame_timer = 0
                self._y_set = False
                return True
        return False
    
    def update(self) -> None:
        """Update creature position and animation."""
        if not self.active_creature:
            return
        
        # Move creature
        self.creature_x += self.active_creature["speed"]
        
        # Animate frames
        self.frame_timer += 1
        if self.frame_timer > 8:
            self.frame_timer = 0
            self.creature_frame = (self.creature_frame + 1) % len(self.active_creature["frames"])
        
        # Remove if off screen
        if self.creature_x > self.ax + self.aw - 5:
            self.active_creature = None
            self._y_set = False
    
    def draw(self, screen, colour_map: Dict[str, int], lightning_active: bool = False) -> None:
        """
        Draw the creature if active.
        
        Args:
            screen: asciimatics Screen object
            colour_map: Dict mapping colour names to colour values
            lightning_active: If True, use lightning colour override
        """
        if not self.active_creature:
            return
        
        frames = self.active_creature["frames"]
        frame = frames[self.creature_frame % len(frames)]
        
        # Get colour
        colour_name = self.active_creature["colour"]
        colour = colour_map.get(colour_name, colour_map.get("SNOW", 7))
        if lightning_active:
            colour = colour_map.get("SUN", 3)
        
        # Set Y position once (random within bounds)
        x = int(self.creature_x)
        if not self._y_set:
            max_y = self.height - len(frame) - 4
            min_y = 6
            if max_y > min_y:
                self.creature_y = random.randint(min_y, max_y)
            else:
                self.creature_y = min_y
            self._y_set = True
        
        # Draw creature
        for i, line in enumerate(frame):
            try:
                px = x
                py = self.creature_y + i
                if self.ax + 1 <= px < self.ax + self.aw - len(line) and 3 <= py < self.height - 3:
                    screen.print_at(line, px, py, colour=colour)
            except Exception:
                pass
    
    @property
    def is_active(self) -> bool:
        """Check if a creature is currently active."""
        return self.active_creature is not None
    
    @property
    def current_creature_name(self) -> Optional[str]:
        """Get the name of the currently active creature."""
        return self.active_creature["name"] if self.active_creature else None


# Backwards compatibility alias
EasterEggManager = CreatureManager
EASTER_EGG_CREATURES = CREATURES
