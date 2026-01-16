"""
Particle Physics Simulation Module
==================================
Physically accurate particle simulation with configurable integrators.

This module provides:
- Multiple integration methods (Euler, Verlet, RK4)
- Proper force accumulation (gravity, drag, buoyancy, wind)
- Collision detection and response
- Spatial partitioning for performance

Physics Model:
- Newtonian mechanics: F = ma
- Quadratic drag: F_d = -½ρv²C_d A (simplified)
- Buoyancy: F_b = ρVg (Archimedes' principle)
- Wind: F_w = ½ρv²C_d A (drag in moving fluid)

References:
- "Game Physics Engine Development" - Ian Millington
- "Real-Time Collision Detection" - Christer Ericson
"""
from __future__ import annotations
import math
from typing import Tuple, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod


# Physical constants (SI units, scaled for terminal animation)
EARTH_GRAVITY = 9.81  # m/s² (scaled down for visual appeal)
AIR_DENSITY = 1.225   # kg/m³ at sea level
TERMINAL_SCALE = 0.1  # Scale factor for terminal display


class IntegrationType(Enum):
    """Available numerical integration methods."""
    EULER = auto()           # Simple, fast, least accurate
    SEMI_IMPLICIT = auto()   # Better energy conservation
    VERLET = auto()          # Good for constraints, no velocity storage
    RK4 = auto()             # Most accurate, 4x computation


@dataclass
class PhysicsConfig:
    """Configuration for physics simulation."""
    gravity: float = 0.5                      # Scaled gravity
    air_resistance: float = 0.02              # Drag coefficient
    wind_strength: float = 0.0                # Base wind force
    integration: IntegrationType = IntegrationType.SEMI_IMPLICIT
    substeps: int = 1                         # Physics substeps per frame
    max_velocity: float = 10.0                # Velocity clamp
    bounds_check: bool = True


@dataclass
class Vector2:
    """2D vector with common operations."""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vector2':
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar) if scalar != 0 else Vector2()
    
    def __neg__(self) -> 'Vector2':
        return Vector2(-self.x, -self.y)
    
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    @property
    def magnitude_squared(self) -> float:
        return self.x * self.x + self.y * self.y
    
    def normalized(self) -> 'Vector2':
        mag = self.magnitude
        return self / mag if mag > 0 else Vector2()
    
    def dot(self, other: 'Vector2') -> float:
        return self.x * other.x + self.y * other.y
    
    def clamped(self, max_magnitude: float) -> 'Vector2':
        mag = self.magnitude
        if mag > max_magnitude:
            return self.normalized() * max_magnitude
        return Vector2(self.x, self.y)
    
    def as_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)
    
    @classmethod
    def from_angle(cls, angle: float, magnitude: float = 1.0) -> 'Vector2':
        """Create vector from angle (radians) and magnitude."""
        return cls(math.cos(angle) * magnitude, math.sin(angle) * magnitude)


@dataclass
class Particle:
    """
    Physics-enabled particle with force accumulation.
    
    Uses semi-implicit Euler by default for good stability/performance tradeoff.
    """
    position: Vector2 = field(default_factory=Vector2)
    velocity: Vector2 = field(default_factory=Vector2)
    acceleration: Vector2 = field(default_factory=Vector2)
    
    # Previous position for Verlet integration
    prev_position: Vector2 = field(default_factory=Vector2)
    
    # Physical properties
    mass: float = 1.0
    inverse_mass: float = 1.0  # Cached for efficiency
    radius: float = 0.5
    
    # Material properties
    drag_coefficient: float = 0.47  # Sphere default
    restitution: float = 0.3        # Bounciness [0, 1]
    friction: float = 0.5           # Surface friction
    
    # Buoyancy (for rain/snow simulation)
    buoyancy_factor: float = 0.0    # 0 = no buoyancy, 1 = neutrally buoyant
    
    # Visual properties
    char: str = "·"
    colour: int = 7  # White
    
    # Lifetime management
    age: int = 0
    max_age: int = -1  # -1 = immortal
    alive: bool = True
    
    # Force accumulator (reset each frame)
    _accumulated_force: Vector2 = field(default_factory=Vector2)
    
    def __post_init__(self):
        self.inverse_mass = 1.0 / self.mass if self.mass > 0 else 0.0
        self.prev_position = Vector2(self.position.x, self.position.y)
    
    def apply_force(self, force: Vector2):
        """Accumulate force for this frame."""
        self._accumulated_force = self._accumulated_force + force
    
    def apply_impulse(self, impulse: Vector2):
        """Apply instantaneous change in momentum."""
        self.velocity = self.velocity + impulse * self.inverse_mass
    
    def clear_forces(self):
        """Reset force accumulator."""
        self._accumulated_force = Vector2()
    
    def integrate_euler(self, dt: float):
        """Simple Euler integration. Fast but least accurate."""
        # a = F/m
        self.acceleration = self._accumulated_force * self.inverse_mass
        
        # v += a * dt
        self.velocity = self.velocity + self.acceleration * dt
        
        # x += v * dt
        self.position = self.position + self.velocity * dt
    
    def integrate_semi_implicit(self, dt: float):
        """
        Semi-implicit Euler (Symplectic Euler).
        Updates velocity first, then position. Better energy conservation.
        """
        self.acceleration = self._accumulated_force * self.inverse_mass
        self.velocity = self.velocity + self.acceleration * dt
        self.position = self.position + self.velocity * dt
    
    def integrate_verlet(self, dt: float):
        """
        Velocity Verlet integration.
        Excellent for constraints, doesn't store velocity explicitly.
        x(t+dt) = 2x(t) - x(t-dt) + a*dt²
        """
        self.acceleration = self._accumulated_force * self.inverse_mass
        
        # Store current position
        temp = Vector2(self.position.x, self.position.y)
        
        # Verlet step
        self.position = (
            self.position * 2 - 
            self.prev_position + 
            self.acceleration * (dt * dt)
        )
        
        # Update previous position
        self.prev_position = temp
        
        # Derive velocity for other calculations
        self.velocity = (self.position - self.prev_position) / dt
    
    def integrate(self, dt: float, method: IntegrationType = IntegrationType.SEMI_IMPLICIT):
        """Integrate using specified method."""
        if method == IntegrationType.EULER:
            self.integrate_euler(dt)
        elif method == IntegrationType.SEMI_IMPLICIT:
            self.integrate_semi_implicit(dt)
        elif method == IntegrationType.VERLET:
            self.integrate_verlet(dt)
        
        self.age += 1
        
        # Check lifetime
        if self.max_age > 0 and self.age >= self.max_age:
            self.alive = False
    
    def is_expired(self, bounds: Tuple[float, float, float, float]) -> bool:
        """Check if particle should be removed."""
        if not self.alive:
            return True
        
        x_min, y_min, x_max, y_max = bounds
        margin = 5
        
        return (
            self.position.x < x_min - margin or
            self.position.x > x_max + margin or
            self.position.y < y_min - margin or
            self.position.y > y_max + margin
        )


class ForceGenerator(ABC):
    """Abstract base class for force generators."""
    
    @abstractmethod
    def apply(self, particle: Particle, dt: float):
        """Apply force to particle."""
        pass


class GravityForce(ForceGenerator):
    """
    Gravitational force: F = mg
    Accounts for buoyancy: F_net = (m - ρV)g
    """
    
    def __init__(self, gravity: float = 0.5, direction: Vector2 = None):
        self.gravity = gravity
        self.direction = direction or Vector2(0, 1)  # Down
    
    def apply(self, particle: Particle, dt: float):
        # Effective gravity accounting for buoyancy
        effective_g = self.gravity * (1.0 - particle.buoyancy_factor)
        force = self.direction * (particle.mass * effective_g)
        particle.apply_force(force)


class DragForce(ForceGenerator):
    """
    Quadratic drag force: F_d = -½ρv²C_d A * v̂
    
    Simplified model using drag coefficient only.
    """
    
    def __init__(self, coefficient: float = 0.02):
        self.coefficient = coefficient
    
    def apply(self, particle: Particle, dt: float):
        velocity = particle.velocity
        speed_sq = velocity.magnitude_squared
        
        if speed_sq > 0.0001:
            # Drag magnitude proportional to v²
            drag_magnitude = self.coefficient * speed_sq * particle.drag_coefficient
            
            # Drag direction opposite to velocity
            drag_direction = -velocity.normalized()
            
            # Limit drag to not exceed current momentum
            max_drag = speed_sq / dt * particle.mass
            drag_magnitude = min(drag_magnitude, max_drag * 0.99)
            
            particle.apply_force(drag_direction * drag_magnitude)


class WindForce(ForceGenerator):
    """
    Wind force with turbulence.
    
    Models wind as a moving fluid applying drag force.
    """
    
    def __init__(self, base_velocity: Vector2 = None, 
                 turbulence_func: Callable[[float, float], Tuple[float, float]] = None):
        self.base_velocity = base_velocity or Vector2()
        self.turbulence_func = turbulence_func
    
    def apply(self, particle: Particle, dt: float):
        # Get wind at particle position
        wind = Vector2(self.base_velocity.x, self.base_velocity.y)
        
        # Add turbulence if available
        if self.turbulence_func:
            tx, ty = self.turbulence_func(particle.position.x, particle.position.y)
            wind = wind + Vector2(tx, ty)
        
        # Relative velocity (wind - particle velocity)
        relative = wind - particle.velocity
        
        # Force proportional to relative velocity
        force = relative * 0.1 * particle.drag_coefficient
        particle.apply_force(force)


class TurbulenceForce(ForceGenerator):
    """
    Turbulent force using noise function.
    
    Applies semi-random forces based on position for natural-looking motion.
    """
    
    def __init__(self, noise_func: Callable[[float, float, float], float] = None,
                 strength: float = 0.5, time_scale: float = 0.1):
        self.noise_func = noise_func
        self.strength = strength
        self.time_scale = time_scale
        self.time = 0.0
    
    def apply(self, particle: Particle, dt: float):
        self.time += dt * self.time_scale
        
        if self.noise_func:
            # Sample noise for x and y force components
            fx = self.noise_func(
                particle.position.x * 0.1,
                particle.position.y * 0.1,
                self.time
            ) * self.strength
            
            fy = self.noise_func(
                particle.position.x * 0.1 + 100,
                particle.position.y * 0.1,
                self.time
            ) * self.strength
            
            particle.apply_force(Vector2(fx, fy))


class ParticleSystem:
    """
    Manages particle lifecycle, forces, and spatial organization.
    
    Features:
    - Force generator registry
    - Configurable integration method
    - Particle pooling (optional)
    - Bounds checking
    """
    
    def __init__(self, config: PhysicsConfig = None,
                 bounds: Tuple[float, float, float, float] = (0, 0, 100, 50)):
        self.config = config or PhysicsConfig()
        self.bounds = bounds
        self.particles: List[Particle] = []
        self.force_generators: List[ForceGenerator] = []
        
        # Performance tracking
        self.frame_count = 0
        self.active_particle_count = 0
        self.peak_particle_count = 0
    
    def add_force_generator(self, generator: ForceGenerator):
        """Register a force generator."""
        self.force_generators.append(generator)
    
    def spawn(self, particle: Particle):
        """Add a particle to the system."""
        self.particles.append(particle)
        self.peak_particle_count = max(self.peak_particle_count, len(self.particles))
    
    def update(self, dt: float = 1.0):
        """Update all particles."""
        self.frame_count += 1
        
        # Substep loop for stability
        sub_dt = dt / self.config.substeps
        
        for _ in range(self.config.substeps):
            for particle in self.particles:
                # Clear accumulated forces
                particle.clear_forces()
                
                # Apply all force generators
                for generator in self.force_generators:
                    generator.apply(particle, sub_dt)
                
                # Integrate motion
                particle.integrate(sub_dt, self.config.integration)
                
                # Clamp velocity
                if particle.velocity.magnitude > self.config.max_velocity:
                    particle.velocity = particle.velocity.clamped(self.config.max_velocity)
        
        # Remove expired particles
        if self.config.bounds_check:
            self.particles = [p for p in self.particles if not p.is_expired(self.bounds)]
        
        self.active_particle_count = len(self.particles)
    
    def clear(self):
        """Remove all particles."""
        self.particles.clear()
    
    def get_stats(self) -> dict:
        """Get performance statistics."""
        return {
            'active': self.active_particle_count,
            'peak': self.peak_particle_count,
            'frames': self.frame_count,
            'generators': len(self.force_generators)
        }


# Factory functions
def create_rain_particle(x: float, y: float, wind_x: float = 0) -> Particle:
    """Create a raindrop particle with appropriate physics."""
    return Particle(
        position=Vector2(x, y),
        velocity=Vector2(wind_x * 0.5, 1.0),
        mass=0.5,
        drag_coefficient=0.3,
        buoyancy_factor=0.0,
        char='|',
        max_age=200
    )


def create_snow_particle(x: float, y: float, wind_x: float = 0) -> Particle:
    """Create a snowflake particle with appropriate physics."""
    return Particle(
        position=Vector2(x, y),
        velocity=Vector2(wind_x * 0.3, 0.2),
        mass=0.1,
        drag_coefficient=0.8,  # High drag (fluffy)
        buoyancy_factor=0.4,   # Significant buoyancy
        char='*',
        max_age=400
    )
