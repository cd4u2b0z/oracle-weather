"""
Oracle Weather - Library Package
================================
Shared utilities and modules for the weather dashboard.

Modules:
--------
- weather_api: OpenWeatherMap and OpenMeteo API integration
- weather_extended: Extended forecast and astronomical data
- particles: Simple particle system for weather effects
- achievements: Gamification and achievement tracking
- interactive: Keyboard bindings and interactive controls
- dashboard_panels: Modular dashboard panel components
"""

from .weather_api import (
    WeatherCondition,
    WeatherData,
    get_weather,
    search_and_fetch_weather,
)
from .particles import Particle, ParticleSystem, random_spawn_top

__all__ = [
    # weather_api
    "WeatherCondition",
    "WeatherData", 
    "get_weather",
    "search_and_fetch_weather",
    # particles
    "Particle",
    "ParticleSystem",
    "random_spawn_top",
]

# Lazy imports for heavier modules (loaded on demand)
def __getattr__(name):
    """Lazy load heavier modules."""
    if name == "AchievementManager":
        from .achievements import AchievementManager
        return AchievementManager
    elif name == "InteractiveManager":
        from .interactive import InteractiveManager
        return InteractiveManager
    elif name == "DashboardPanels":
        from .dashboard_panels import PanelManager
        return PanelManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
