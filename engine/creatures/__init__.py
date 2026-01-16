"""
Creatures Engine - Easter Egg Creature System
==============================================
Provides weather-dependent animated creature appearances.

Exports:
- CreatureManager: Main manager class for creature spawning/animation
- Creature: Dataclass for creature definition
- CreatureCategory: Enum for weather/time categories
- CREATURES: Dict of all creature definitions
- EasterEggManager: Backwards-compatible alias for CreatureManager
- EASTER_EGG_CREATURES: Backwards-compatible alias for CREATURES
"""

from .core import (
    CreatureManager,
    Creature,
    CreatureCategory,
    CREATURES,
    # Backwards compatibility
    EasterEggManager,
    EASTER_EGG_CREATURES,
)

__all__ = [
    "CreatureManager",
    "Creature", 
    "CreatureCategory",
    "CREATURES",
    "EasterEggManager",
    "EASTER_EGG_CREATURES",
]
