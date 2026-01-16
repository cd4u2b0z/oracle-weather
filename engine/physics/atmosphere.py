"""
Atmospheric Physics Module
==========================
Realistic atmospheric calculations for weather simulation.

This module provides:
- Barometric pressure calculations (altitude, temperature effects)
- Atmospheric stability indices (CAPE-like approximations)
- Visibility calculations (Mie scattering, humidity)
- Wind shear and turbulence models
- Thermal updraft simulation

Physical Models:
- Barometric Formula: P(h) = P₀ × exp(-Mgh/RT)
- Adiabatic Lapse Rate: Γ = -dT/dz ≈ 9.8°C/km (dry)
- Richardson Number: Ri = (g/θ)(∂θ/∂z) / (∂u/∂z)²

References:
- "Atmospheric Science" - Wallace & Hobbs
- "An Introduction to Dynamic Meteorology" - Holton
- NOAA Technical Memorandums
"""
from __future__ import annotations
import math
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto


# Physical constants
R_GAS = 8.314462  # Universal gas constant (J/(mol·K))
M_AIR = 0.0289644  # Molar mass of dry air (kg/mol)
G_EARTH = 9.80665  # Standard gravity (m/s²)
T_KELVIN_OFFSET = 273.15  # Celsius to Kelvin
P_SEA_LEVEL = 101325  # Standard sea level pressure (Pa)
LAPSE_RATE_DRY = 0.0098  # Dry adiabatic lapse rate (K/m)
LAPSE_RATE_MOIST = 0.006  # Approximate moist lapse rate (K/m)


class StabilityClass(Enum):
    """Atmospheric stability classification (Pasquill-Gifford)."""
    VERY_UNSTABLE = auto()    # A - Strong daytime convection
    UNSTABLE = auto()          # B - Moderate convection
    SLIGHTLY_UNSTABLE = auto() # C - Weak convection
    NEUTRAL = auto()           # D - Overcast/windy
    SLIGHTLY_STABLE = auto()   # E - Light wind, clear night
    STABLE = auto()            # F - Very stable, calm night


@dataclass
class AtmosphericState:
    """Current atmospheric conditions."""
    temperature_c: float = 20.0       # Surface temperature (°C)
    pressure_hpa: float = 1013.25     # Surface pressure (hPa)
    humidity_percent: float = 50.0    # Relative humidity (%)
    wind_speed_ms: float = 5.0        # Wind speed (m/s)
    wind_direction_deg: float = 0.0   # Wind direction (degrees)
    cloud_cover_percent: float = 0.0  # Cloud coverage (%)
    dew_point_c: float = 10.0         # Dew point (°C)
    
    @property
    def temperature_k(self) -> float:
        """Temperature in Kelvin."""
        return self.temperature_c + T_KELVIN_OFFSET
    
    @property
    def pressure_pa(self) -> float:
        """Pressure in Pascals."""
        return self.pressure_hpa * 100
    
    @property
    def wind_vector(self) -> Tuple[float, float]:
        """Wind as (u, v) vector in m/s."""
        rad = math.radians(self.wind_direction_deg)
        u = -self.wind_speed_ms * math.sin(rad)  # East component
        v = -self.wind_speed_ms * math.cos(rad)  # North component
        return (u, v)


class AtmosphericModel:
    """
    Physical atmospheric model for weather simulation.
    
    Provides calculations for:
    - Pressure at altitude
    - Air density
    - Stability classification
    - Thermal effects
    """
    
    def __init__(self, state: AtmosphericState = None):
        self.state = state or AtmosphericState()
    
    def pressure_at_altitude(self, altitude_m: float) -> float:
        """
        Calculate pressure at altitude using barometric formula.
        
        P(h) = P₀ × exp(-Mgh/RT)
        
        Args:
            altitude_m: Altitude in meters
            
        Returns:
            Pressure in hPa
        """
        exponent = -(M_AIR * G_EARTH * altitude_m) / (R_GAS * self.state.temperature_k)
        pressure_pa = self.state.pressure_pa * math.exp(exponent)
        return pressure_pa / 100  # Convert to hPa
    
    def temperature_at_altitude(self, altitude_m: float, moist: bool = False) -> float:
        """
        Calculate temperature at altitude using lapse rate.
        
        T(h) = T₀ - Γh
        
        Args:
            altitude_m: Altitude in meters
            moist: Use moist adiabatic lapse rate
            
        Returns:
            Temperature in °C
        """
        lapse = LAPSE_RATE_MOIST if moist else LAPSE_RATE_DRY
        return self.state.temperature_c - lapse * altitude_m
    
    def air_density(self, altitude_m: float = 0) -> float:
        """
        Calculate air density using ideal gas law.
        
        ρ = PM / RT
        
        Returns:
            Density in kg/m³
        """
        p = self.pressure_at_altitude(altitude_m) * 100  # Pa
        t = self.temperature_at_altitude(altitude_m) + T_KELVIN_OFFSET
        return (p * M_AIR) / (R_GAS * t)
    
    def virtual_temperature(self) -> float:
        """
        Calculate virtual temperature (accounts for moisture).
        
        T_v = T × (1 + 0.61q)
        
        where q is specific humidity.
        """
        # Approximate specific humidity from RH and T
        e_sat = self.saturation_vapor_pressure(self.state.temperature_c)
        e = e_sat * self.state.humidity_percent / 100
        q = 0.622 * e / (self.state.pressure_pa - 0.378 * e)
        
        return self.state.temperature_k * (1 + 0.61 * q)
    
    @staticmethod
    def saturation_vapor_pressure(temp_c: float) -> float:
        """
        Calculate saturation vapor pressure using Magnus formula.
        
        e_s = 611.2 × exp(17.67T / (T + 243.5))
        
        Returns:
            Saturation vapor pressure in Pa
        """
        return 611.2 * math.exp((17.67 * temp_c) / (temp_c + 243.5))
    
    def classify_stability(self) -> StabilityClass:
        """
        Classify atmospheric stability (Pasquill-Gifford method).
        
        Based on:
        - Wind speed
        - Solar radiation (approximated by cloud cover + time)
        - Surface conditions
        """
        wind = self.state.wind_speed_ms
        clouds = self.state.cloud_cover_percent
        
        # Simplified stability based on wind and clouds
        if wind < 2:
            if clouds < 30:
                return StabilityClass.VERY_UNSTABLE
            elif clouds < 70:
                return StabilityClass.UNSTABLE
            else:
                return StabilityClass.NEUTRAL
        elif wind < 5:
            if clouds < 30:
                return StabilityClass.UNSTABLE
            elif clouds < 70:
                return StabilityClass.SLIGHTLY_UNSTABLE
            else:
                return StabilityClass.NEUTRAL
        elif wind < 8:
            return StabilityClass.NEUTRAL
        else:
            if clouds > 70:
                return StabilityClass.NEUTRAL
            else:
                return StabilityClass.SLIGHTLY_STABLE
    
    def turbulence_intensity(self) -> float:
        """
        Calculate turbulence intensity factor [0, 1].
        
        Based on stability class and wind speed.
        """
        stability = self.classify_stability()
        
        # Base turbulence from stability
        stability_factor = {
            StabilityClass.VERY_UNSTABLE: 0.9,
            StabilityClass.UNSTABLE: 0.7,
            StabilityClass.SLIGHTLY_UNSTABLE: 0.5,
            StabilityClass.NEUTRAL: 0.3,
            StabilityClass.SLIGHTLY_STABLE: 0.15,
            StabilityClass.STABLE: 0.05
        }[stability]
        
        # Wind contribution
        wind_factor = min(1.0, self.state.wind_speed_ms / 15)
        
        return min(1.0, stability_factor + wind_factor * 0.3)
    
    def thermal_updraft_strength(self, solar_intensity: float = 0.5) -> float:
        """
        Calculate thermal updraft strength.
        
        Based on:
        - Surface temperature vs air temperature
        - Solar intensity
        - Stability
        
        Args:
            solar_intensity: Relative solar intensity [0, 1]
            
        Returns:
            Updraft velocity in m/s (terminal units)
        """
        stability = self.classify_stability()
        
        if stability in (StabilityClass.STABLE, StabilityClass.SLIGHTLY_STABLE):
            return 0.0
        
        # Temperature difference creates convection
        base_strength = 0.5 * solar_intensity
        
        # Instability multiplier
        multiplier = {
            StabilityClass.VERY_UNSTABLE: 2.0,
            StabilityClass.UNSTABLE: 1.5,
            StabilityClass.SLIGHTLY_UNSTABLE: 1.0,
            StabilityClass.NEUTRAL: 0.3
        }.get(stability, 0)
        
        return base_strength * multiplier
    
    def visibility_estimate(self) -> float:
        """
        Estimate visibility in meters.
        
        Based on:
        - Humidity (fog/mist)
        - Precipitation
        - Aerosols (simplified)
        """
        # Humidity-based visibility reduction
        rh = self.state.humidity_percent
        
        if rh >= 100:
            # Fog
            return 100
        elif rh >= 95:
            # Dense mist
            return 500
        elif rh >= 90:
            # Mist
            return 2000
        elif rh >= 80:
            # Haze
            return 5000
        else:
            # Clear
            return 10000 + (100 - rh) * 100


class WindModel:
    """
    Wind dynamics model including shear and gusts.
    """
    
    def __init__(self, base_speed: float = 5.0, base_direction: float = 0.0):
        self.base_speed = base_speed
        self.base_direction = base_direction
        self.gust_state = 0.0
        self.gust_timer = 0.0
    
    def wind_at_height(self, height_m: float, surface_speed: float = None) -> float:
        """
        Calculate wind speed at height using power law profile.
        
        u(z) = u_ref × (z / z_ref)^α
        
        where α ≈ 0.14 for neutral stability over open terrain.
        """
        surface_speed = surface_speed or self.base_speed
        alpha = 0.14  # Power law exponent
        z_ref = 10.0  # Reference height (standard anemometer)
        
        if height_m <= 0:
            return 0
        
        return surface_speed * (height_m / z_ref) ** alpha
    
    def update_gusts(self, dt: float, turbulence: float = 0.3):
        """
        Update gust simulation using stochastic model.
        
        Gusts are modeled as exponentially decaying impulses.
        """
        # Decay current gust
        self.gust_state *= math.exp(-2 * dt)
        
        # Random new gust generation
        self.gust_timer -= dt
        if self.gust_timer <= 0:
            # Generate new gust
            import random
            if random.random() < turbulence * 0.1:
                self.gust_state = random.uniform(0.5, 2.0) * self.base_speed
            self.gust_timer = random.uniform(0.5, 3.0)
    
    def get_wind(self) -> Tuple[float, float]:
        """Get current wind vector including gusts."""
        speed = self.base_speed + self.gust_state
        rad = math.radians(self.base_direction)
        return (speed * math.sin(rad), speed * math.cos(rad))


# Convenience functions
def calculate_wind_chill(temp_c: float, wind_speed_ms: float) -> float:
    """
    Calculate wind chill temperature (Environment Canada formula).
    
    Valid for T < 10°C and wind > 4.8 km/h
    """
    wind_kmh = wind_speed_ms * 3.6
    
    if temp_c >= 10 or wind_kmh < 4.8:
        return temp_c
    
    return (
        13.12 + 
        0.6215 * temp_c - 
        11.37 * (wind_kmh ** 0.16) + 
        0.3965 * temp_c * (wind_kmh ** 0.16)
    )


def calculate_heat_index(temp_c: float, humidity: float) -> float:
    """
    Calculate heat index (NOAA formula).
    
    Valid for T > 27°C and RH > 40%
    """
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    rh = humidity
    
    hi_f = (
        -42.379 +
        2.04901523 * temp_f +
        10.14333127 * rh -
        0.22475541 * temp_f * rh -
        6.83783e-3 * temp_f**2 -
        5.481717e-2 * rh**2 +
        1.22874e-3 * temp_f**2 * rh +
        8.5282e-4 * temp_f * rh**2 -
        1.99e-6 * temp_f**2 * rh**2
    )
    
    return (hi_f - 32) * 5/9
