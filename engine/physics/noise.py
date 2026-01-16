"""
Procedural Noise Generation Module
==================================
Professional-grade noise implementations for natural pattern generation.

This module provides:
- Perlin Noise (gradient noise with smooth interpolation)
- Simplex Noise (faster, fewer directional artifacts)
- Fractal Brownian Motion (fBm) for multi-scale detail
- Domain Warping for organic distortion effects

Mathematical Foundation:
- Perlin: Ken Perlin (1983), improved in 2002
- Simplex: Ken Perlin (2001), O(n²) instead of O(2^n)
- fBm: Mandelbrot (1968), self-similar fractal summation

References:
- "Improving Noise" - Ken Perlin, SIGGRAPH 2002
- "Simplex Noise Demystified" - Stefan Gustavson, 2005
"""
from __future__ import annotations
import math
import random
from typing import Tuple, List, Optional
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class NoiseConfig:
    """Configuration for noise generation."""
    seed: int = 42
    octaves: int = 4
    persistence: float = 0.5  # Amplitude decay per octave
    lacunarity: float = 2.0   # Frequency increase per octave
    scale: float = 1.0


class PerlinNoise:
    """
    2D Perlin Noise Generator
    
    Uses improved Perlin noise algorithm (2002) with:
    - Quintic interpolation (6t⁵ - 15t⁴ + 10t³) for C² continuity
    - Gradient vectors from permutation table
    - Periodic boundary conditions
    
    Time Complexity: O(1) per sample
    Space Complexity: O(512) for permutation table
    """
    
    # Gradient vectors for 2D noise (8 directions)
    _GRADIENTS_2D: List[Tuple[float, float]] = [
        (1, 1), (-1, 1), (1, -1), (-1, -1),
        (1, 0), (-1, 0), (0, 1), (0, -1)
    ]
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional seed for reproducibility."""
        self.seed = seed if seed is not None else int(random.random() * 2**31)
        self._perm = self._generate_permutation_table()
    
    def _generate_permutation_table(self) -> List[int]:
        """Generate shuffled permutation table (0-255, doubled for overflow)."""
        rng = random.Random(self.seed)
        perm = list(range(256))
        rng.shuffle(perm)
        return perm + perm  # Double for easy wrapping
    
    @staticmethod
    def _fade(t: float) -> float:
        """
        Quintic interpolation curve: 6t⁵ - 15t⁴ + 10t³
        
        Properties:
        - f(0) = 0, f(1) = 1
        - f'(0) = f'(1) = 0 (smooth at boundaries)
        - f''(0) = f''(1) = 0 (C² continuous)
        """
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)
    
    @staticmethod
    def _lerp(t: float, a: float, b: float) -> float:
        """Linear interpolation: a + t(b - a)"""
        return a + t * (b - a)
    
    def _gradient(self, hash_val: int, x: float, y: float) -> float:
        """Compute dot product with gradient vector."""
        g = self._GRADIENTS_2D[hash_val & 7]
        return g[0] * x + g[1] * y
    
    def sample(self, x: float, y: float) -> float:
        """
        Sample 2D Perlin noise at coordinates (x, y).
        
        Returns value in range [-1, 1] (approximately, can slightly exceed).
        
        Algorithm:
        1. Find unit grid cell containing point
        2. Get gradient vectors at 4 corners
        3. Compute dot products with offset vectors
        4. Interpolate using quintic fade curve
        """
        # Grid cell coordinates
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        
        # Relative position within cell [0, 1)
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        
        # Fade curves for interpolation
        u = self._fade(xf)
        v = self._fade(yf)
        
        # Hash corner coordinates
        aa = self._perm[self._perm[xi] + yi]
        ab = self._perm[self._perm[xi] + yi + 1]
        ba = self._perm[self._perm[xi + 1] + yi]
        bb = self._perm[self._perm[xi + 1] + yi + 1]
        
        # Compute gradients and interpolate
        x1 = self._lerp(u,
            self._gradient(aa, xf, yf),
            self._gradient(ba, xf - 1, yf)
        )
        x2 = self._lerp(u,
            self._gradient(ab, xf, yf - 1),
            self._gradient(bb, xf - 1, yf - 1)
        )
        
        return self._lerp(v, x1, x2)
    
    def __call__(self, x: float, y: float) -> float:
        """Convenience method: noise(x, y)"""
        return self.sample(x, y)


class SimplexNoise:
    """
    2D Simplex Noise Generator
    
    Advantages over Perlin:
    - Lower computational complexity: O(n²) vs O(2^n)
    - Fewer directional artifacts
    - Better scaling to higher dimensions
    
    Uses simplex (triangle) grid instead of hypercube grid.
    """
    
    # Skewing factors for 2D
    _F2 = 0.5 * (math.sqrt(3.0) - 1.0)  # Skew to simplex
    _G2 = (3.0 - math.sqrt(3.0)) / 6.0   # Unskew from simplex
    
    # Gradient vectors
    _GRAD3: List[Tuple[float, float]] = [
        (1, 1), (-1, 1), (1, -1), (-1, -1),
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (-1, 1), (1, -1), (-1, -1)
    ]
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else int(random.random() * 2**31)
        rng = random.Random(self.seed)
        self._perm = list(range(256))
        rng.shuffle(self._perm)
        self._perm = self._perm + self._perm
        self._perm_mod12 = [x % 12 for x in self._perm]
    
    def sample(self, x: float, y: float) -> float:
        """Sample 2D simplex noise. Returns value in [-1, 1]."""
        # Skew input to simplex cell
        s = (x + y) * self._F2
        i = math.floor(x + s)
        j = math.floor(y + s)
        
        # Unskew back
        t = (i + j) * self._G2
        X0 = i - t
        Y0 = j - t
        x0 = x - X0
        y0 = y - Y0
        
        # Determine which simplex we're in
        if x0 > y0:
            i1, j1 = 1, 0  # Lower triangle
        else:
            i1, j1 = 0, 1  # Upper triangle
        
        x1 = x0 - i1 + self._G2
        y1 = y0 - j1 + self._G2
        x2 = x0 - 1.0 + 2.0 * self._G2
        y2 = y0 - 1.0 + 2.0 * self._G2
        
        # Hash coordinates
        ii = int(i) & 255
        jj = int(j) & 255
        gi0 = self._perm_mod12[ii + self._perm[jj]]
        gi1 = self._perm_mod12[ii + i1 + self._perm[jj + j1]]
        gi2 = self._perm_mod12[ii + 1 + self._perm[jj + 1]]
        
        # Calculate contributions from three corners
        n0 = n1 = n2 = 0.0
        
        t0 = 0.5 - x0*x0 - y0*y0
        if t0 >= 0:
            t0 *= t0
            g = self._GRAD3[gi0]
            n0 = t0 * t0 * (g[0]*x0 + g[1]*y0)
        
        t1 = 0.5 - x1*x1 - y1*y1
        if t1 >= 0:
            t1 *= t1
            g = self._GRAD3[gi1]
            n1 = t1 * t1 * (g[0]*x1 + g[1]*y1)
        
        t2 = 0.5 - x2*x2 - y2*y2
        if t2 >= 0:
            t2 *= t2
            g = self._GRAD3[gi2]
            n2 = t2 * t2 * (g[0]*x2 + g[1]*y2)
        
        # Scale to [-1, 1]
        return 70.0 * (n0 + n1 + n2)
    
    def __call__(self, x: float, y: float) -> float:
        return self.sample(x, y)


class FractalNoise:
    """
    Fractal Brownian Motion (fBm) Noise
    
    Combines multiple octaves of noise at different frequencies
    to create natural-looking, self-similar patterns.
    
    Mathematical formulation:
        fBm(x) = Σ (persistence^i * noise(x * lacunarity^i))
    
    Parameters:
    - octaves: Number of noise layers (detail levels)
    - persistence: Amplitude multiplier per octave (typically 0.5)
    - lacunarity: Frequency multiplier per octave (typically 2.0)
    """
    
    def __init__(self, base_noise: Optional[PerlinNoise] = None, 
                 config: Optional[NoiseConfig] = None):
        self.config = config or NoiseConfig()
        self.base_noise = base_noise or PerlinNoise(self.config.seed)
    
    def sample(self, x: float, y: float, 
               octaves: Optional[int] = None,
               persistence: Optional[float] = None,
               lacunarity: Optional[float] = None) -> float:
        """
        Sample fractal noise at (x, y).
        
        Returns normalized value in approximately [-1, 1].
        """
        octaves = octaves or self.config.octaves
        persistence = persistence or self.config.persistence
        lacunarity = lacunarity or self.config.lacunarity
        
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_amplitude = 0.0
        
        for _ in range(octaves):
            total += self.base_noise.sample(
                x * frequency * self.config.scale,
                y * frequency * self.config.scale
            ) * amplitude
            
            max_amplitude += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        # Normalize to [-1, 1]
        return total / max_amplitude
    
    def __call__(self, x: float, y: float) -> float:
        return self.sample(x, y)


class DomainWarp:
    """
    Domain Warping for organic distortion effects.
    
    Warps the input coordinates using noise before sampling,
    creating flowing, organic patterns.
    
    warp(x, y) = noise(x + noise(x, y), y + noise(x + 5.2, y + 1.3))
    """
    
    def __init__(self, noise: Optional[FractalNoise] = None,
                 warp_strength: float = 4.0):
        self.noise = noise or FractalNoise()
        self.warp_strength = warp_strength
    
    def sample(self, x: float, y: float) -> float:
        """Sample domain-warped noise."""
        # First warp pass
        wx = self.noise.sample(x, y) * self.warp_strength
        wy = self.noise.sample(x + 5.2, y + 1.3) * self.warp_strength
        
        # Second warp pass for more organic feel
        wx2 = self.noise.sample(x + wx, y + wy) * self.warp_strength * 0.5
        wy2 = self.noise.sample(x + wx + 1.7, y + wy + 9.2) * self.warp_strength * 0.5
        
        return self.noise.sample(x + wx + wx2, y + wy + wy2)
    
    def __call__(self, x: float, y: float) -> float:
        return self.sample(x, y)


# Convenience factory functions
def create_perlin(seed: int = None) -> PerlinNoise:
    """Create a Perlin noise generator."""
    return PerlinNoise(seed)

def create_simplex(seed: int = None) -> SimplexNoise:
    """Create a Simplex noise generator."""
    return SimplexNoise(seed)

def create_fractal(seed: int = None, octaves: int = 4) -> FractalNoise:
    """Create a fractal noise generator."""
    config = NoiseConfig(seed=seed or 42, octaves=octaves)
    return FractalNoise(config=config)
