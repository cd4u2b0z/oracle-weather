"""
Weather Dashboard Engine
========================
Professional-grade modular architecture for terminal-based weather visualization.

Modules:
--------
- physics: Procedural noise, particle physics, atmospheric simulation
- rendering: Performance-aware frame rendering with layer management
- personality: AI personality system with mood states and memory
- weather: Weather data fetching and processing
- creatures: Easter egg creature system

Usage:
------
    from engine import PhysicsEngine, RenderEngine, PersonalityEngine
    from engine.physics import PerlinNoise, ParticleSystem
    from engine.rendering import FrameBudget, RenderStats
"""

__version__ = '2.0.0'
__author__ = 'Weather Dashboard Team'

# High-level imports
from engine.physics.noise import PerlinNoise, SimplexNoise, FractalNoise, DomainWarp
from engine.physics.particles import (
    Vector2, Particle, ParticleSystem, PhysicsConfig,
    GravityForce, DragForce, WindForce, IntegrationType
)
from engine.physics.atmosphere import (
    AtmosphericModel, AtmosphericState, StabilityClass,
    WindModel, calculate_wind_chill, calculate_heat_index
)
from engine.personality.core import (
    PersonalityEngine, MoodStateMachine, Memory, Mood, PersonalityConfig
)
from engine.rendering.core import (
    RenderEngine, RenderStats, FrameBudget, RenderQueue, RenderCommand, RenderLayer
)

__all__ = [
    # Physics - Noise
    'PerlinNoise',
    'SimplexNoise', 
    'FractalNoise',
    'DomainWarp',
    
    # Physics - Particles
    'Vector2',
    'Particle',
    'ParticleSystem',
    'PhysicsConfig',
    'GravityForce',
    'DragForce',
    'WindForce',
    'IntegrationType',
    
    # Physics - Atmosphere
    'AtmosphericModel',
    'AtmosphericState',
    'StabilityClass',
    'WindModel',
    'calculate_wind_chill',
    'calculate_heat_index',
    
    # Personality
    'PersonalityEngine',
    'MoodStateMachine',
    'Memory',
    'Mood',
    'PersonalityConfig',
    
    # Rendering
    'RenderEngine',
    'RenderStats',
    'FrameBudget',
    'RenderQueue',
    'RenderCommand',
    'RenderLayer',
]
