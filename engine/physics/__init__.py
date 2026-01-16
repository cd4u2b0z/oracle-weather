"""Physics Engine Module - Procedural noise, particles, and atmospheric simulation."""

from engine.physics.noise import PerlinNoise, SimplexNoise, FractalNoise, DomainWarp, NoiseConfig
from engine.physics.particles import (
    Vector2, Particle, ParticleSystem, PhysicsConfig,
    GravityForce, DragForce, WindForce, TurbulenceForce,
    ForceGenerator, IntegrationType
)
from engine.physics.atmosphere import (
    AtmosphericModel, AtmosphericState, StabilityClass,
    WindModel, calculate_wind_chill, calculate_heat_index
)

__all__ = [
    'PerlinNoise', 'SimplexNoise', 'FractalNoise', 'DomainWarp', 'NoiseConfig',
    'Vector2', 'Particle', 'ParticleSystem', 'PhysicsConfig',
    'GravityForce', 'DragForce', 'WindForce', 'TurbulenceForce',
    'ForceGenerator', 'IntegrationType',
    'AtmosphericModel', 'AtmosphericState', 'StabilityClass',
    'WindModel', 'calculate_wind_chill', 'calculate_heat_index',
]
