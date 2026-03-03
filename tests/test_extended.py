"""
Extended Tests for Weather Dashboard
====================================
Tests for new modules: extended API, config, effects, achievements.

Run with: pytest tests/test_extended.py -v
"""
import sys
import os
import json
import math
import time
import tempfile
from datetime import datetime, date, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.weather_api import WeatherCondition, WeatherData
from lib.weather_extended import (
    HourlyForecast, DailyForecast, ForecastData,
    WeatherAlert, AlertSeverity, AlertUrgency,
    AstronomicalData, MoonPhase,
    EnvironmentalData, UVLevel, AQILevel,
    WeatherDatabase, HistoricalComparison,
    _calculate_moon_phase, _map_wmo_to_condition,
    output_single_line, output_json,
)
from lib.achievements import (
    Achievement, AchievementTier, AchievementCategory,
    AchievementProgress, AchievementManager, ACHIEVEMENTS,
)
# config_manager was removed — tests that depended on it are gone


# ═══════════════════════════════════════════════════════════════════════════════
# WEATHER EXTENDED TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHourlyForecast:
    """Test HourlyForecast dataclass."""
    
    def test_hour_str_formatting(self):
        """Test hour string formatting."""
        forecast = HourlyForecast(
            time=datetime(2026, 1, 16, 14, 0),
            temperature_f=72.0,
            temperature_c=22.2,
            condition=WeatherCondition.CLEAR,
            description="Clear",
            precipitation_prob=10,
            humidity=45,
            wind_speed_mph=5.0,
            wind_direction=180,
            clouds_percent=10,
            feels_like_f=72.0,
        )
        assert forecast.hour_str == "2pm"
    
    def test_morning_hour_str(self):
        """Test morning hour formatting."""
        forecast = HourlyForecast(
            time=datetime(2026, 1, 16, 9, 0),
            temperature_f=55.0,
            temperature_c=12.8,
            condition=WeatherCondition.CLOUDY,
            description="Cloudy",
            precipitation_prob=20,
            humidity=60,
            wind_speed_mph=8.0,
            wind_direction=270,
            clouds_percent=75,
            feels_like_f=53.0,
        )
        assert forecast.hour_str == "9am"


class TestDailyForecast:
    """Test DailyForecast dataclass."""
    
    def test_day_name_today(self):
        """Test today detection."""
        forecast = DailyForecast(
            date=date.today(),
            temp_high_f=75.0,
            temp_low_f=55.0,
            temp_high_c=23.9,
            temp_low_c=12.8,
            condition=WeatherCondition.CLEAR,
            description="Clear",
            precipitation_prob=0,
            precipitation_amount=0,
            humidity=40,
            wind_speed_mph=5.0,
            sunrise=datetime.now(),
            sunset=datetime.now(),
        )
        assert forecast.day_name == "Today"
    
    def test_day_name_tomorrow(self):
        """Test tomorrow detection."""
        forecast = DailyForecast(
            date=date.today() + timedelta(days=1),
            temp_high_f=75.0,
            temp_low_f=55.0,
            temp_high_c=23.9,
            temp_low_c=12.8,
            condition=WeatherCondition.RAIN,
            description="Rain",
            precipitation_prob=80,
            precipitation_amount=5.0,
            humidity=70,
            wind_speed_mph=10.0,
            sunrise=datetime.now(),
            sunset=datetime.now(),
        )
        assert forecast.day_name == "Tomorrow"
    
    def test_temp_range_str(self):
        """Test temperature range formatting."""
        forecast = DailyForecast(
            date=date.today(),
            temp_high_f=78.0,
            temp_low_f=52.0,
            temp_high_c=25.6,
            temp_low_c=11.1,
            condition=WeatherCondition.PARTLY_CLOUDY,
            description="Partly Cloudy",
            precipitation_prob=20,
            precipitation_amount=0,
            humidity=50,
            wind_speed_mph=8.0,
            sunrise=datetime.now(),
            sunset=datetime.now(),
        )
        assert forecast.temp_range_str == "78°/52°"
    
    def test_trend_vs_warmer(self):
        """Test trend comparison - warmer."""
        today = DailyForecast(
            date=date.today(),
            temp_high_f=80.0, temp_low_f=55.0,
            temp_high_c=26.7, temp_low_c=12.8,
            condition=WeatherCondition.CLEAR, description="Clear",
            precipitation_prob=0, precipitation_amount=0,
            humidity=40, wind_speed_mph=5.0,
            sunrise=datetime.now(), sunset=datetime.now(),
        )
        yesterday = DailyForecast(
            date=date.today() - timedelta(days=1),
            temp_high_f=70.0, temp_low_f=50.0,
            temp_high_c=21.1, temp_low_c=10.0,
            condition=WeatherCondition.CLOUDY, description="Cloudy",
            precipitation_prob=30, precipitation_amount=0,
            humidity=55, wind_speed_mph=8.0,
            sunrise=datetime.now(), sunset=datetime.now(),
        )
        assert today.trend_vs(yesterday) == "↑"


class TestWeatherAlert:
    """Test WeatherAlert dataclass."""
    
    def test_is_severe(self):
        """Test severe alert detection."""
        alert = WeatherAlert(
            event="Tornado Warning",
            severity=AlertSeverity.EXTREME,
            urgency=AlertUrgency.IMMEDIATE,
            headline="Tornado Warning for County",
            description="A tornado has been spotted...",
            instruction="Take shelter immediately",
            start=datetime.now() - timedelta(hours=1),
            end=datetime.now() + timedelta(hours=2),
            areas=["County A", "County B"],
        )
        assert alert.is_severe
        assert alert.is_active
        assert alert.short_name == "🌪️ TORNADO"
    
    def test_not_severe(self):
        """Test non-severe alert."""
        alert = WeatherAlert(
            event="Wind Advisory",
            severity=AlertSeverity.MINOR,
            urgency=AlertUrgency.EXPECTED,
            headline="Wind Advisory",
            description="Winds up to 40 mph expected",
            instruction="Secure loose objects",
            start=datetime.now() - timedelta(hours=1),
            end=datetime.now() + timedelta(hours=6),
            areas=["Region A"],
        )
        assert not alert.is_severe
        assert "Wind Adv" in alert.short_name


class TestMoonPhase:
    """Test moon phase calculations."""
    
    def test_moon_phase_calculation(self):
        """Test that moon phase calculation returns valid values."""
        phase, illumination, age = _calculate_moon_phase()
        
        assert isinstance(phase, MoonPhase)
        assert 0 <= illumination <= 100
        assert 0 <= age <= 29.53  # Synodic month
    
    def test_astronomical_data_emoji(self):
        """Test moon emoji mapping."""
        data = AstronomicalData(
            sunrise=datetime.now(),
            sunset=datetime.now() + timedelta(hours=12),
            solar_noon=datetime.now() + timedelta(hours=6),
            day_length_hours=12.0,
            moon_phase=MoonPhase.FULL_MOON,
            moon_illumination=100.0,
            moon_age_days=14.77,
        )
        assert data.moon_emoji == "🌕"


class TestEnvironmentalData:
    """Test EnvironmentalData dataclass."""
    
    def test_uv_level_low(self):
        """Test low UV level."""
        data = EnvironmentalData(
            uv_index=2.0,
            uv_level=UVLevel.LOW,
            aqi=35,
            aqi_level=AQILevel.GOOD,
            dominant_pollutant="PM2.5",
            pm25=8.0,
            pm10=12.0,
            ozone=25.0,
        )
        assert data.uv_color == "GREEN"
        assert data.aqi_color == "GREEN"
        assert "gentle" in data.uv_advice.lower()
    
    def test_uv_level_extreme(self):
        """Test extreme UV level."""
        data = EnvironmentalData(
            uv_index=12.0,
            uv_level=UVLevel.EXTREME,
            aqi=180,
            aqi_level=AQILevel.UNHEALTHY,
            dominant_pollutant="O3",
            pm25=45.0,
            pm10=60.0,
            ozone=90.0,
        )
        assert data.uv_color == "MAGENTA"
        assert data.aqi_color == "RED"
        assert "danger" in data.uv_advice.lower()


class TestWMOMapping:
    """Test WMO code mapping."""
    
    def test_clear(self):
        assert _map_wmo_to_condition(0) == WeatherCondition.CLEAR
    
    def test_partly_cloudy(self):
        assert _map_wmo_to_condition(2) == WeatherCondition.PARTLY_CLOUDY
    
    def test_rain(self):
        assert _map_wmo_to_condition(63) == WeatherCondition.RAIN
    
    def test_heavy_rain(self):
        assert _map_wmo_to_condition(65) == WeatherCondition.HEAVY_RAIN
    
    def test_snow(self):
        assert _map_wmo_to_condition(73) == WeatherCondition.SNOW
    
    def test_thunderstorm(self):
        assert _map_wmo_to_condition(95) == WeatherCondition.THUNDERSTORM


class TestOutputFormats:
    """Test widget output formats."""
    
    def test_single_line_output(self):
        """Test single-line output format."""
        weather = WeatherData(
            condition=WeatherCondition.CLEAR,
            temperature_f=72.0,
            temperature_c=22.2,
            humidity=45,
            wind_speed_mph=5.0,
            wind_direction=180,
            description="Clear",
            location="Test City",
            timestamp=time.time(),
        )
        output = output_single_line(weather)
        assert "72°F" in output
        assert "☀️" in output
        assert "5mph" in output
        assert "45%" in output
    
    def test_json_output(self):
        """Test JSON output format."""
        weather = WeatherData(
            condition=WeatherCondition.RAIN,
            temperature_f=55.0,
            temperature_c=12.8,
            humidity=85,
            wind_speed_mph=12.0,
            wind_direction=270,
            description="Rain",
            location="Test City",
            timestamp=time.time(),
        )
        output = output_json(weather)
        data = json.loads(output)
        
        assert 'current' in data
        assert data['current']['temperature_f'] == 55.0
        assert data['current']['condition'] == 'rain'


class TestWeatherDatabase:
    """Test weather database operations."""
    
    def test_database_init(self):
        """Test database initialization."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = WeatherDatabase(db_path)
            assert Path(db_path).exists()
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_log_and_retrieve(self):
        """Test logging and retrieving weather data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = WeatherDatabase(db_path)
            
            weather = WeatherData(
                condition=WeatherCondition.CLEAR,
                temperature_f=72.0,
                temperature_c=22.2,
                humidity=45,
                wind_speed_mph=5.0,
                wind_direction=180,
                description="Clear",
                location="Test City",
                timestamp=time.time(),
            )
            
            db.log_weather(weather)
            
            # Query should work without errors
            yesterday = db.get_yesterday("Test City")
            # May or may not have data depending on timestamp
            
        finally:
            Path(db_path).unlink(missing_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG MANAGER TESTS
# ═══════════════════════════════════════════════════════════════════════════════


# TestLocation, TestColorTheme, TestUnitConversion, TestConfig removed
# — they depended on config_manager.py which was nuked as dead code


# ═══════════════════════════════════════════════════════════════════════════════
# ACHIEVEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAchievementDefinitions:
    """Test achievement definitions."""
    
    def test_achievements_exist(self):
        """Test that achievements are defined."""
        assert len(ACHIEVEMENTS) > 0
        assert 'first_check' in ACHIEVEMENTS
        assert 'rain_lover' in ACHIEVEMENTS
    
    def test_achievement_structure(self):
        """Test achievement structure."""
        ach = ACHIEVEMENTS['first_check']
        assert ach.id == 'first_check'
        assert ach.name
        assert ach.description
        assert ach.emoji
        assert isinstance(ach.category, AchievementCategory)
        assert isinstance(ach.tier, AchievementTier)


class TestAchievementProgress:
    """Test achievement progress tracking."""
    
    def test_progress_increment(self):
        """Test incrementing progress."""
        prog = AchievementProgress(achievement_id='rain_lover')
        
        # Shouldn't unlock immediately
        assert not prog.increment(1)
        assert prog.current == 1
        assert not prog.unlocked
        
        # Increment to threshold (10)
        for _ in range(9):
            prog.increment(1)
        
        assert prog.unlocked
    
    def test_progress_serialization(self):
        """Test progress serialization."""
        prog = AchievementProgress(
            achievement_id='test',
            current=5,
            unlocked=True,
            unlock_time=time.time(),
        )
        
        d = prog.to_dict()
        prog2 = AchievementProgress.from_dict(d)
        
        assert prog2.achievement_id == 'test'
        assert prog2.current == 5
        assert prog2.unlocked


class TestAchievementManager:
    """Test achievement manager."""
    
    def test_manager_init(self):
        """Test manager initialization."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            manager = AchievementManager(path)
            assert len(manager.progress) > 0
        finally:
            Path(path).unlink(missing_ok=True)
    
    def test_first_check_unlock(self):
        """Test first check achievement."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            manager = AchievementManager(path)
            
            unlocked = manager.check_weather(
                temperature_f=72.0,
                condition="Clear",
                humidity=45,
                pressure=1015,
                location="Test City",
            )
            
            # Should unlock first_check
            assert any(a.id == 'first_check' for a in unlocked)
        finally:
            Path(path).unlink(missing_ok=True)
    
    def test_rain_achievement(self):
        """Test rain achievements."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            manager = AchievementManager(path)
            
            unlocked = manager.check_weather(
                temperature_f=55.0,
                condition="Rain",
                humidity=85,
                pressure=1005,
                location="Test City",
            )
            
            # Should unlock rain_witness
            assert any(a.id == 'rain_witness' for a in unlocked)
        finally:
            Path(path).unlink(missing_ok=True)
    
    def test_extreme_temp_achievement(self):
        """Test extreme temperature achievements."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            manager = AchievementManager(path)
            
            # Hot
            unlocked = manager.check_weather(
                temperature_f=105.0,
                condition="Clear",
                humidity=30,
                pressure=1010,
                location="Desert City",
            )
            assert any(a.id == 'temp_extreme_hot' for a in unlocked)
            
            # Cold
            unlocked = manager.check_weather(
                temperature_f=-5.0,
                condition="Snow",
                humidity=40,
                pressure=1025,
                location="Arctic City",
            )
            assert any(a.id == 'temp_extreme_cold' for a in unlocked)
        finally:
            Path(path).unlink(missing_ok=True)
    
    def test_action_recording(self):
        """Test recording user actions."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            manager = AchievementManager(path)
            
            # Help
            ach = manager.record_action('help')
            assert ach is not None
            assert ach.id == 'help_reader'
            
            # Theme change
            ach = manager.record_action('theme_change')
            assert ach is not None
            assert ach.id == 'theme_explorer'
        finally:
            Path(path).unlink(missing_ok=True)
    
    def test_stats_summary(self):
        """Test stats summary."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            manager = AchievementManager(path)
            
            # Do some checks
            manager.check_weather(
                temperature_f=72.0,
                condition="Clear",
                humidity=45,
                pressure=1015,
                location="Test City",
            )
            
            stats = manager.get_stats_summary()
            assert 'total' in stats
            assert 'unlocked' in stats
            assert 'percent' in stats
            assert stats['total_checks'] >= 1
        finally:
            Path(path).unlink(missing_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIAL EFFECTS TESTS  
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpecialEffects:
    """Test special effects module."""
    
    def test_aurora_creation(self):
        """Test aurora effect creation."""
        from engine.effects.special_effects import AuroraBorealis
        
        aurora = AuroraBorealis(80, 24, intensity=0.8)
        assert aurora.width == 80
        assert aurora.height == 24
        assert len(aurora.waves) > 0
    
    def test_aurora_update(self):
        """Test aurora animation update."""
        from engine.effects.special_effects import AuroraBorealis
        
        aurora = AuroraBorealis(80, 24)
        initial_time = aurora.time
        aurora.update(0.033)
        assert aurora.time > initial_time
    
    def test_heat_shimmer(self):
        """Test heat shimmer effect."""
        from engine.effects.special_effects import HeatShimmer
        
        shimmer = HeatShimmer(80, 24, intensity=1.0)
        assert len(shimmer.shimmer_lines) > 0
        
        shimmer.update(0.033)
        assert shimmer.time > 0
    
    def test_rainbow(self):
        """Test rainbow effect."""
        from engine.effects.special_effects import Rainbow
        
        rainbow = Rainbow(80, 24)
        assert rainbow.visible
        
        # Fade over time
        for _ in range(200):
            rainbow.update(0.1)
        
        assert rainbow.fade < 1.0
    
    def test_hail(self):
        """Test hail effect."""
        from engine.effects.special_effects import HailEffect
        
        hail = HailEffect(80, 24, intensity=1.0)
        hail.update(0.033)
        
        # Should spawn some hailstones
        assert len(hail.hailstones) > 0
    
    def test_effects_manager(self):
        """Test effects manager."""
        from engine.effects.special_effects import SpecialEffectsManager
        
        manager = SpecialEffectsManager(80, 24)
        
        # Hot day should trigger heat shimmer
        manager.update_for_conditions(
            temperature_f=100.0,
            condition='clear',
            is_night=False,
            latitude=32.0,
            humidity=30,
        )
        
        # Should have at least one effect (heat shimmer)
        heat_effects = [e for e in manager.active_effects 
                       if e.__class__.__name__ == 'HeatShimmer']
        assert len(heat_effects) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
