"""
Special Weather Effects Module
==============================
Additional visual effects for special weather conditions.

Effects included:
- Aurora Borealis (northern lights)
- Heat shimmer/mirage
- Rainbow after rain
- Hail particles
- Sandstorm/dust storm
- Heat lightning (distant)
- Frost patterns
- Sun rays (crepuscular rays)

Each effect has its own particle system or rendering approach.
"""
from __future__ import annotations
import math
import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Optional, Callable

from asciimatics.screen import Screen


# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 COLOR DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

class EffectColor:
    """Color constants for effects."""
    AURORA_GREEN = Screen.COLOUR_GREEN
    AURORA_BLUE = Screen.COLOUR_CYAN
    AURORA_PURPLE = Screen.COLOUR_MAGENTA
    RAINBOW_RED = Screen.COLOUR_RED
    RAINBOW_YELLOW = Screen.COLOUR_YELLOW
    RAINBOW_GREEN = Screen.COLOUR_GREEN
    RAINBOW_BLUE = Screen.COLOUR_BLUE
    RAINBOW_MAGENTA = Screen.COLOUR_MAGENTA
    HAIL = Screen.COLOUR_WHITE
    SAND = Screen.COLOUR_YELLOW
    FROST = Screen.COLOUR_CYAN
    SUN_RAY = Screen.COLOUR_YELLOW


# ═══════════════════════════════════════════════════════════════════════════════
# 🌌 AURORA BOREALIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AuroraWave:
    """Single aurora wave/curtain."""
    y_base: float
    amplitude: float
    frequency: float
    phase: float
    color: int
    intensity: float = 1.0
    

class AuroraBorealis:
    """
    Northern Lights effect for clear nights at high latitudes.
    Uses sine waves with varying amplitudes to create curtain-like effect.
    
    "The sky dances with Kyne's light. The Nords say it's the spirits
    of their ancestors. I say it's charged particles from the sun 
    interacting with the magnetosphere. Same thing, really." - Stormy
    """
    
    CHARS = ["░", "▒", "▓", "█", "≋", "~"]
    COLORS = [
        Screen.COLOUR_GREEN,
        Screen.COLOUR_CYAN,
        Screen.COLOUR_MAGENTA,
        Screen.COLOUR_GREEN,
        Screen.COLOUR_CYAN,
    ]
    
    def __init__(self, width: int, height: int, intensity: float = 1.0):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.time = 0.0
        self.waves: List[AuroraWave] = []
        self._init_waves()
    
    def _init_waves(self):
        """Initialize aurora wave structures."""
        num_waves = random.randint(3, 6)
        for i in range(num_waves):
            self.waves.append(AuroraWave(
                y_base=random.uniform(2, self.height * 0.4),
                amplitude=random.uniform(2, 5),
                frequency=random.uniform(0.02, 0.05),
                phase=random.uniform(0, 2 * math.pi),
                color=random.choice(self.COLORS),
                intensity=random.uniform(0.5, 1.0),
            ))
    
    def update(self, dt: float = 0.033):
        """Update aurora animation."""
        self.time += dt
        
        # Slowly shift wave parameters
        for wave in self.waves:
            wave.phase += 0.01
            wave.amplitude += math.sin(self.time * 0.1 + wave.phase) * 0.05
            wave.amplitude = max(1, min(6, wave.amplitude))
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render aurora to screen."""
        for x in range(self.width):
            for wave in self.waves:
                # Calculate y position using sine wave
                y = wave.y_base + wave.amplitude * math.sin(
                    x * wave.frequency + wave.phase + self.time * 0.5
                )
                y = int(y) + y_offset
                
                # Draw vertical "curtain" from y upward
                curtain_height = int(wave.amplitude * 2 * wave.intensity)
                for dy in range(curtain_height):
                    draw_y = y - dy
                    if 0 <= draw_y < self.height:
                        # Intensity decreases with height
                        intensity = 1.0 - (dy / curtain_height)
                        char_idx = int(intensity * (len(self.CHARS) - 1))
                        char = self.CHARS[char_idx]
                        
                        # Flicker effect
                        if random.random() > 0.1:
                            try:
                                screen.print_at(
                                    char, x + x_offset, draw_y,
                                    colour=wave.color
                                )
                            except:
                                pass


# ═══════════════════════════════════════════════════════════════════════════════
# 🌡️ HEAT SHIMMER / MIRAGE
# ═══════════════════════════════════════════════════════════════════════════════

class HeatShimmer:
    """
    Heat distortion effect for hot days (>95°F).
    Creates wavy distortion lines near the ground.
    
    "The air itself becomes liquid to the eye. 
    A desert trick. The Mojave taught me this one." - Stormy
    """
    
    CHARS = ["~", "≋", "∿", "⌇"]
    
    def __init__(self, width: int, height: int, intensity: float = 1.0):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.time = 0.0
        self.shimmer_lines: List[dict] = []
        self._init_lines()
    
    def _init_lines(self):
        """Initialize shimmer line parameters."""
        num_lines = max(3, int(self.height * 0.15))
        for i in range(num_lines):
            self.shimmer_lines.append({
                'y': self.height - 5 - i * 2,
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.05, 0.15),
                'amplitude': random.uniform(0.5, 1.5),
            })
    
    def update(self, dt: float = 0.033):
        """Update shimmer animation."""
        self.time += dt
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render heat shimmer effect."""
        for line in self.shimmer_lines:
            y = line['y'] + y_offset
            if not (0 <= y < self.height):
                continue
            
            for x in range(self.width):
                # Sine wave distortion
                offset = math.sin(
                    x * 0.1 + line['phase'] + self.time * line['speed']
                ) * line['amplitude']
                
                # Only draw occasionally for shimmer effect
                if random.random() < 0.3 * self.intensity:
                    char = random.choice(self.CHARS)
                    color = Screen.COLOUR_YELLOW if random.random() > 0.5 else Screen.COLOUR_WHITE
                    try:
                        screen.print_at(char, x + x_offset, y, colour=color)
                    except:
                        pass


# ═══════════════════════════════════════════════════════════════════════════════
# 🌈 RAINBOW
# ═══════════════════════════════════════════════════════════════════════════════

class Rainbow:
    """
    Rainbow effect for clearing skies after rain.
    Draws a colorful arc.
    
    "The light bends. The colors separate. Science made beautiful.
    The Nords would say it's the Bifrost. Let them." - Stormy
    """
    
    # Rainbow colors from outer to inner
    COLORS = [
        Screen.COLOUR_RED,
        Screen.COLOUR_RED,      # Orange approximation
        Screen.COLOUR_YELLOW,
        Screen.COLOUR_GREEN,
        Screen.COLOUR_CYAN,
        Screen.COLOUR_BLUE,
        Screen.COLOUR_MAGENTA,  # Violet
    ]
    
    def __init__(self, width: int, height: int, intensity: float = 1.0):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.fade = 1.0
        self.visible = True
        
        # Arc parameters
        self.center_x = width // 2
        self.center_y = height + 10  # Below screen
        self.radius = int(height * 0.8)
    
    def update(self, dt: float = 0.033):
        """Update rainbow (fading over time)."""
        # Slowly fade
        self.fade = max(0, self.fade - dt * 0.01)
        if self.fade <= 0:
            self.visible = False
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render rainbow arc."""
        if not self.visible or self.fade <= 0:
            return
        
        for band, color in enumerate(self.COLORS):
            radius = self.radius - band * 2
            
            # Draw arc using parametric circle
            for angle in range(30, 151, 2):  # 30° to 150° arc
                rad = math.radians(angle)
                x = int(self.center_x + radius * math.cos(rad)) + x_offset
                y = int(self.center_y - radius * math.sin(rad)) + y_offset
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Vary character based on position
                    if random.random() < self.fade * self.intensity:
                        char = "█" if random.random() > 0.3 else "▓"
                        try:
                            screen.print_at(char, x, y, colour=color)
                        except:
                            pass


# ═══════════════════════════════════════════════════════════════════════════════
# 🧊 HAIL PARTICLES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HailStone:
    """Individual hail particle."""
    x: float
    y: float
    vx: float
    vy: float
    size: int  # 0=small, 1=medium, 2=large
    rotation: float = 0.0
    bounces: int = 0


class HailEffect:
    """
    Hail particle system.
    Larger, faster particles than rain with bouncing behavior.
    
    "Ice falls from the sky with purpose. 
    The insurance companies call it an 'act of God'. 
    The Divines call it 'Tuesday'." - Stormy
    """
    
    CHARS_BY_SIZE = {
        0: ["·", "∘", "°"],
        1: ["○", "◦", "o"],
        2: ["●", "◎", "O"],
    }
    
    def __init__(self, width: int, height: int, intensity: float = 1.0):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.hailstones: List[HailStone] = []
        self.spawn_rate = int(5 * intensity)
    
    def update(self, dt: float = 0.033, wind_x: float = 0):
        """Update hail particles."""
        # Spawn new hailstones
        for _ in range(self.spawn_rate):
            if random.random() < 0.3 * self.intensity:
                size = random.choices([0, 1, 2], weights=[0.5, 0.35, 0.15])[0]
                self.hailstones.append(HailStone(
                    x=random.uniform(0, self.width),
                    y=random.uniform(-5, 0),
                    vx=wind_x + random.uniform(-0.5, 0.5),
                    vy=random.uniform(2, 4) + size * 0.5,
                    size=size,
                ))
        
        # Update existing hailstones
        for stone in self.hailstones:
            stone.x += stone.vx
            stone.y += stone.vy
            stone.vy += 0.15  # Gravity
            
            # Ground bounce
            if stone.y >= self.height - 2:
                stone.bounces += 1
                stone.vy = -stone.vy * 0.4
                stone.y = self.height - 2
        
        # Remove dead particles
        self.hailstones = [
            s for s in self.hailstones 
            if s.bounces < 3 and 0 <= s.x < self.width
        ]
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render hailstones."""
        for stone in self.hailstones:
            x = int(stone.x) + x_offset
            y = int(stone.y) + y_offset
            
            if 0 <= x < self.width and 0 <= y < self.height:
                chars = self.CHARS_BY_SIZE[stone.size]
                char = random.choice(chars)
                try:
                    screen.print_at(char, x, y, colour=Screen.COLOUR_WHITE)
                except:
                    pass


# ═══════════════════════════════════════════════════════════════════════════════
# 🏜️ SANDSTORM / DUST STORM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DustParticle:
    """Individual dust/sand particle."""
    x: float
    y: float
    vx: float
    vy: float
    char: str
    alpha: float = 1.0


class SandstormEffect:
    """
    Sandstorm/dust storm effect.
    Horizontal particles with reduced visibility.
    
    "The earth rises up in anger. Or perhaps just inconvenience.
    The Wasteland knows this dance well." - Stormy
    """
    
    DUST_CHARS = [".", "·", ",", "'", ":", ";", "`"]
    SAND_CHARS = ["∘", "°", "⋅", "•"]
    
    def __init__(self, width: int, height: int, intensity: float = 1.0):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.particles: List[DustParticle] = []
        self.visibility = max(0.2, 1.0 - intensity * 0.6)
    
    def update(self, dt: float = 0.033, wind_speed: float = 2.0):
        """Update sandstorm particles."""
        # Spawn new particles from left side
        spawn_count = int(15 * self.intensity)
        for _ in range(spawn_count):
            if random.random() < 0.4:
                is_sand = random.random() < 0.3
                chars = self.SAND_CHARS if is_sand else self.DUST_CHARS
                self.particles.append(DustParticle(
                    x=random.uniform(-10, 5),
                    y=random.uniform(0, self.height),
                    vx=wind_speed * random.uniform(0.8, 1.5),
                    vy=random.uniform(-0.3, 0.3),
                    char=random.choice(chars),
                    alpha=random.uniform(0.5, 1.0),
                ))
        
        # Update particles
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            # Turbulence
            p.vy += random.uniform(-0.1, 0.1)
            p.vy = max(-1, min(1, p.vy))
        
        # Remove off-screen particles
        self.particles = [
            p for p in self.particles 
            if p.x < self.width + 10 and 0 <= p.y < self.height
        ]
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render sandstorm."""
        # Draw visibility overlay (reduced by filling with dim chars)
        if self.intensity > 0.5:
            for _ in range(int(self.width * self.height * (1 - self.visibility) * 0.1)):
                x = random.randint(0, self.width - 1) + x_offset
                y = random.randint(0, self.height - 1) + y_offset
                if random.random() < 0.2:
                    try:
                        screen.print_at("░", x, y, colour=Screen.COLOUR_YELLOW)
                    except:
                        pass
        
        # Draw particles
        for p in self.particles:
            x = int(p.x) + x_offset
            y = int(p.y) + y_offset
            
            if 0 <= x < self.width and 0 <= y < self.height:
                if random.random() < p.alpha:
                    color = Screen.COLOUR_YELLOW if random.random() > 0.3 else Screen.COLOUR_WHITE
                    try:
                        screen.print_at(p.char, x, y, colour=color)
                    except:
                        pass


# ═══════════════════════════════════════════════════════════════════════════════
# ❄️ FROST PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

class FrostPatterns:
    """
    Frost crystal patterns on screen edges for very cold weather.
    
    "The cold writes upon the glass. Each crystal a tiny poem 
    about thermodynamics. The Nords just say 'it's cold'." - Stormy
    """
    
    FROST_CHARS = ["❄", "❆", "✧", "✦", "*", "·", "°", "∘"]
    CRYSTAL_CHARS = ["╱", "╲", "─", "│", "╳", "╋"]
    
    def __init__(self, width: int, height: int, intensity: float = 1.0):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.frost_points: List[Tuple[int, int, str]] = []
        self._generate_frost()
    
    def _generate_frost(self):
        """Generate frost pattern points."""
        # Frost accumulates at edges and corners
        edge_width = int(self.width * 0.15 * self.intensity)
        edge_height = int(self.height * 0.2 * self.intensity)
        
        # Top edge
        for x in range(self.width):
            for y in range(edge_height):
                prob = (1 - y / edge_height) * 0.3 * self.intensity
                if random.random() < prob:
                    char = random.choice(self.FROST_CHARS)
                    self.frost_points.append((x, y, char))
        
        # Bottom edge
        for x in range(self.width):
            for y in range(self.height - edge_height, self.height):
                prob = ((y - (self.height - edge_height)) / edge_height) * 0.2 * self.intensity
                if random.random() < prob:
                    char = random.choice(self.FROST_CHARS)
                    self.frost_points.append((x, y, char))
        
        # Side edges
        for y in range(self.height):
            for x in range(edge_width):
                prob = (1 - x / edge_width) * 0.2 * self.intensity
                if random.random() < prob:
                    char = random.choice(self.FROST_CHARS)
                    self.frost_points.append((x, y, char))
            
            for x in range(self.width - edge_width, self.width):
                prob = ((x - (self.width - edge_width)) / edge_width) * 0.2 * self.intensity
                if random.random() < prob:
                    char = random.choice(self.FROST_CHARS)
                    self.frost_points.append((x, y, char))
    
    def update(self, dt: float = 0.033):
        """Update frost (mostly static with occasional sparkle)."""
        # Occasionally add/remove frost points for sparkle effect
        if random.random() < 0.05:
            if self.frost_points and random.random() < 0.5:
                idx = random.randint(0, len(self.frost_points) - 1)
                self.frost_points.pop(idx)
            else:
                x = random.choice([
                    random.randint(0, int(self.width * 0.1)),
                    random.randint(int(self.width * 0.9), self.width - 1)
                ])
                y = random.randint(0, self.height - 1)
                self.frost_points.append((x, y, random.choice(self.FROST_CHARS)))
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render frost patterns."""
        for x, y, char in self.frost_points:
            draw_x = x + x_offset
            draw_y = y + y_offset
            if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                # Sparkle effect
                color = Screen.COLOUR_WHITE if random.random() > 0.1 else Screen.COLOUR_CYAN
                try:
                    screen.print_at(char, draw_x, draw_y, colour=color)
                except:
                    pass


# ═══════════════════════════════════════════════════════════════════════════════
# ☀️ SUN RAYS (CREPUSCULAR RAYS)
# ═══════════════════════════════════════════════════════════════════════════════

class SunRays:
    """
    Sun rays / god rays effect for partly cloudy conditions.
    
    "The light finds its way through the clouds.
    Some call them 'god rays'. I call them 'diffracted photons'.
    Same reverence, different vocabulary." - Stormy
    """
    
    RAY_CHARS = ["│", "║", "┃", "╏", "╎"]
    BRIGHT_CHARS = ["█", "▓", "▒", "░"]
    
    def __init__(self, width: int, height: int, sun_x: int = None, sun_y: int = 2):
        self.width = width
        self.height = height
        self.sun_x = sun_x if sun_x is not None else width // 3
        self.sun_y = sun_y
        self.rays: List[dict] = []
        self.time = 0.0
        self._init_rays()
    
    def _init_rays(self):
        """Initialize sun ray parameters."""
        num_rays = random.randint(4, 8)
        for i in range(num_rays):
            angle = random.uniform(-0.5, 0.5)  # Spread angle
            self.rays.append({
                'angle': angle,
                'length': random.uniform(0.5, 0.9) * self.height,
                'width': random.randint(1, 3),
                'intensity': random.uniform(0.5, 1.0),
                'flicker_phase': random.uniform(0, 2 * math.pi),
            })
    
    def update(self, dt: float = 0.033):
        """Update sun rays (subtle animation)."""
        self.time += dt
        for ray in self.rays:
            # Subtle intensity variation
            ray['intensity'] = 0.5 + 0.3 * math.sin(
                self.time * 0.5 + ray['flicker_phase']
            )
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render sun rays."""
        for ray in self.rays:
            # Draw ray from sun position downward
            length = int(ray['length'])
            for i in range(length):
                # Calculate position along ray
                t = i / length
                x = int(self.sun_x + ray['angle'] * i) + x_offset
                y = int(self.sun_y + i) + y_offset
                
                # Ray width expands with distance
                width = int(ray['width'] * (1 + t))
                
                for w in range(-width // 2, width // 2 + 1):
                    draw_x = x + w
                    if 0 <= draw_x < self.width and 0 <= y < self.height:
                        # Intensity decreases with distance and width offset
                        intensity = ray['intensity'] * (1 - t * 0.5) * (1 - abs(w) / (width + 1))
                        
                        if random.random() < intensity:
                            char_idx = int((1 - intensity) * (len(self.BRIGHT_CHARS) - 1))
                            char = self.BRIGHT_CHARS[min(char_idx, len(self.BRIGHT_CHARS) - 1)]
                            try:
                                screen.print_at(
                                    char, draw_x, y,
                                    colour=Screen.COLOUR_YELLOW
                                )
                            except:
                                pass


# ═══════════════════════════════════════════════════════════════════════════════
# ⚡ HEAT LIGHTNING
# ═══════════════════════════════════════════════════════════════════════════════

class HeatLightning:
    """
    Distant heat lightning effect - flashes without thunder.
    
    "Lightning without thunder. The storm speaks, but from far away.
    A warning, perhaps. Or just showing off." - Stormy
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.flash_intensity = 0.0
        self.flash_duration = 0
        self.flash_region = (0, 0, width, height)  # x, y, w, h
        self.next_flash_time = random.uniform(3, 10)
        self.time = 0.0
    
    def update(self, dt: float = 0.033):
        """Update heat lightning."""
        self.time += dt
        
        # Decay current flash
        if self.flash_duration > 0:
            self.flash_duration -= 1
            self.flash_intensity *= 0.85
        
        # Trigger new flash
        if self.time >= self.next_flash_time:
            self.flash_intensity = random.uniform(0.3, 0.8)
            self.flash_duration = random.randint(2, 6)
            
            # Random region for flash (usually horizon)
            x = random.randint(0, self.width - 20)
            w = random.randint(15, 30)
            self.flash_region = (x, 0, w, int(self.height * 0.3))
            
            self.time = 0
            self.next_flash_time = random.uniform(5, 15)
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render heat lightning flash."""
        if self.flash_intensity <= 0.1:
            return
        
        rx, ry, rw, rh = self.flash_region
        
        for y in range(rh):
            for x in range(rw):
                draw_x = rx + x + x_offset
                draw_y = ry + y + y_offset
                
                if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                    if random.random() < self.flash_intensity * 0.3:
                        char = "░" if random.random() > 0.5 else "▒"
                        color = Screen.COLOUR_WHITE if random.random() > 0.3 else Screen.COLOUR_YELLOW
                        try:
                            screen.print_at(char, draw_x, draw_y, colour=color)
                        except:
                            pass


# ═══════════════════════════════════════════════════════════════════════════════
# 🎬 EFFECT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class SpecialEffectsManager:
    """
    Manages all special weather effects.
    Determines which effects to show based on conditions.
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.active_effects: List = []
    
    def update_for_conditions(
        self,
        temperature_f: float,
        condition: str,
        is_night: bool,
        latitude: float = 32.0,
        humidity: int = 50,
        visibility: int = 10000,
        recent_rain: bool = False,
        wind_speed: float = 5.0,
    ):
        """Update active effects based on weather conditions."""
        self.active_effects.clear()
        
        # Aurora - high latitude + clear night
        if is_night and latitude > 50 and condition in ('clear', 'partly_cloudy'):
            if random.random() < 0.3:  # Not every night
                self.active_effects.append(
                    AuroraBorealis(self.width, self.height, intensity=0.7)
                )
        
        # Heat shimmer - very hot days
        if temperature_f > 95 and not is_night:
            intensity = min(1.0, (temperature_f - 95) / 15)
            self.active_effects.append(
                HeatShimmer(self.width, self.height, intensity=intensity)
            )
        
        # Rainbow - clearing after rain
        if recent_rain and condition in ('clear', 'partly_cloudy') and not is_night:
            self.active_effects.append(
                Rainbow(self.width, self.height, intensity=0.8)
            )
        
        # Frost patterns - very cold
        if temperature_f < 25:
            intensity = min(1.0, (25 - temperature_f) / 25)
            self.active_effects.append(
                FrostPatterns(self.width, self.height, intensity=intensity)
            )
        
        # Sun rays - partly cloudy daytime
        if condition == 'partly_cloudy' and not is_night:
            self.active_effects.append(
                SunRays(self.width, self.height)
            )
        
        # Heat lightning - warm humid nights
        if is_night and temperature_f > 70 and humidity > 60:
            if random.random() < 0.2:
                self.active_effects.append(
                    HeatLightning(self.width, self.height)
                )
        
        # Low visibility - sandstorm/dust (would need condition detection)
        if visibility < 1000 and humidity < 30:
            intensity = min(1.0, (1000 - visibility) / 800)
            self.active_effects.append(
                SandstormEffect(self.width, self.height, intensity=intensity)
            )
    
    def add_hail(self, intensity: float = 1.0):
        """Manually add hail effect."""
        self.active_effects.append(
            HailEffect(self.width, self.height, intensity=intensity)
        )
    
    def update(self, dt: float = 0.033, **kwargs):
        """Update all active effects."""
        for effect in self.active_effects:
            if hasattr(effect, 'update'):
                # Pass relevant kwargs to effect
                try:
                    effect.update(dt=dt, **{k: v for k, v in kwargs.items() 
                                           if k in effect.update.__code__.co_varnames})
                except TypeError:
                    effect.update(dt)
    
    def render(self, screen, x_offset: int = 0, y_offset: int = 0):
        """Render all active effects."""
        for effect in self.active_effects:
            if hasattr(effect, 'render'):
                effect.render(screen, x_offset, y_offset)


# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 DEMO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🌈 Special Effects Module")
    print("Available effects:")
    print("  - AuroraBorealis: Northern lights for clear nights")
    print("  - HeatShimmer: Heat distortion for hot days")
    print("  - Rainbow: After rain clears")
    print("  - HailEffect: Bouncing hail particles")
    print("  - SandstormEffect: Desert dust storms")
    print("  - FrostPatterns: Cold weather frost")
    print("  - SunRays: Crepuscular rays through clouds")
    print("  - HeatLightning: Distant lightning flashes")
    print("\nUse SpecialEffectsManager for automatic effect selection.")
