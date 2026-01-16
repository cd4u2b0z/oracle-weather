"""
Shared particle system utilities for weather toys.
"""
import random
from dataclasses import dataclass, field


@dataclass
class Particle:
    """A single particle with position, velocity, and appearance."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 1.0
    char: str = "."
    colour: int = 7  # White
    age: int = 0
    max_age: int = -1  # -1 = infinite

    def update(self, gravity: float = 0.0, wind: float = 0.0, drag: float = 0.0):
        """Update particle position based on physics."""
        # Apply forces
        self.vy += gravity
        self.vx += wind
        
        # Apply drag
        self.vx *= (1.0 - drag)
        self.vy *= (1.0 - drag)
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        self.age += 1

    def is_alive(self, screen_width: int, screen_height: int) -> bool:
        """Check if particle is still active."""
        if self.max_age > 0 and self.age >= self.max_age:
            return False
        if self.y > screen_height or self.y < 0:
            return False
        if self.x < 0 or self.x > screen_width:
            return False
        return True


@dataclass
class ParticleSystem:
    """Manages a collection of particles."""
    particles: list = field(default_factory=list)
    gravity: float = 0.0
    wind: float = 0.0
    drag: float = 0.0

    def spawn(self, particle: Particle):
        """Add a new particle to the system."""
        self.particles.append(particle)

    def update(self, screen_width: int, screen_height: int):
        """Update all particles and remove dead ones."""
        for p in self.particles:
            p.update(self.gravity, self.wind, self.drag)
        
        self.particles = [
            p for p in self.particles 
            if p.is_alive(screen_width, screen_height)
        ]

    def draw(self, screen):
        """Render all particles to the screen."""
        for p in self.particles:
            try:
                screen.print_at(p.char, int(p.x), int(p.y), colour=p.colour)
            except Exception:
                pass  # Ignore out-of-bounds


def random_spawn_top(screen_width: int, char: str = ".", colour: int = 7,
                     vy_range: tuple = (0.5, 1.5), vx_range: tuple = (-0.1, 0.1)) -> Particle:
    """Spawn a particle at a random position along the top of the screen."""
    return Particle(
        x=random.uniform(0, screen_width),
        y=0,
        vx=random.uniform(*vx_range),
        vy=random.uniform(*vy_range),
        char=char,
        colour=colour
    )
