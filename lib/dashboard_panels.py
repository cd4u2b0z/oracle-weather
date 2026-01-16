"""
Enhanced Weather Dashboard Integration
======================================
Main integration module that brings together all the new features
into the weather dashboard.

This module provides:
- Enhanced UI panels for new data
- Unified rendering pipeline
- State management integration
- Effect coordination

"I've upgraded from meteorology to theatrical performance art.
The weather is my stage." - Stormy
"""
from __future__ import annotations
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any, TYPE_CHECKING
import math

from asciimatics.screen import Screen


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 FORECAST PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class ForecastPanel:
    """
    Renders forecast information with ASCII art.
    """
    
    # Weather condition icons (2x3 mini art)
    WEATHER_ICONS = {
        'clear': [
            r"  \|/  ",
            r" .-'-. ",
            r"  / \  ",
        ],
        'clouds': [
            r"  .--.  ",
            r" (    ) ",
            r" '--'   ",
        ],
        'rain': [
            r"  .--.  ",
            r" (    ) ",
            r" ' ' '  ",
        ],
        'storm': [
            r"  .--.  ",
            r" (    ) ",
            r" */\*   ",
        ],
        'snow': [
            r"  .--.  ",
            r" (    ) ",
            r" * * *  ",
        ],
        'mist': [
            r" ≈≈≈≈≈  ",
            r" ≈≈≈≈≈  ",
            r" ≈≈≈≈≈  ",
        ],
    }
    
    def __init__(self, screen: Screen, use_metric: bool = False):
        self.screen = screen
        self.use_metric = use_metric
    
    def draw_hourly(self, hourly_data: List, x: int, y: int, width: int = 60):
        """Draw hourly forecast strip."""
        if not hourly_data:
            return
        
        # Title
        self.screen.print_at("📅 HOURLY FORECAST", x, y, 
                            colour=Screen.COLOUR_CYAN,
                            attr=Screen.A_BOLD)
        y += 1
        
        # Draw separator
        self.screen.print_at("─" * width, x, y, colour=Screen.COLOUR_CYAN)
        y += 1
        
        # Calculate how many hours to show
        hours_to_show = min(8, len(hourly_data), (width - 2) // 7)
        
        # Time row
        time_str = ""
        for i in range(hours_to_show):
            hour = hourly_data[i]
            time_str += f" {hour.time.strftime('%H:%M'):^5}"
        self.screen.print_at(time_str[:width], x, y, colour=Screen.COLOUR_WHITE)
        y += 1
        
        # Temperature row
        temp_str = ""
        for i in range(hours_to_show):
            hour = hourly_data[i]
            temp = hour.temperature
            if not self.use_metric:
                temp = temp * 9/5 + 32
            temp_str += f" {temp:>4.0f}° "
        self.screen.print_at(temp_str[:width], x, y, colour=Screen.COLOUR_YELLOW)
        y += 1
        
        # Precipitation row
        precip_str = ""
        for i in range(hours_to_show):
            hour = hourly_data[i]
            pct = int(hour.precipitation_probability)
            if pct > 0:
                precip_str += f" {pct:>3}%💧 "
            else:
                precip_str += "   --  "
        self.screen.print_at(precip_str[:width], x, y, colour=Screen.COLOUR_CYAN)
        y += 1
        
        return y
    
    def draw_daily(self, daily_data: List, x: int, y: int, width: int = 60):
        """Draw daily forecast with mini icons."""
        if not daily_data:
            return
        
        # Title
        self.screen.print_at("📆 7-DAY FORECAST", x, y,
                            colour=Screen.COLOUR_CYAN,
                            attr=Screen.A_BOLD)
        y += 1
        
        self.screen.print_at("─" * width, x, y, colour=Screen.COLOUR_CYAN)
        y += 1
        
        days_to_show = min(7, len(daily_data))
        
        for i in range(days_to_show):
            day = daily_data[i]
            
            # Day name
            day_name = day.date.strftime("%a")
            if i == 0:
                day_name = "Today"
            
            # Temperature range
            temp_min = day.temperature_min
            temp_max = day.temperature_max
            if not self.use_metric:
                temp_min = temp_min * 9/5 + 32
                temp_max = temp_max * 9/5 + 32
            
            # Get icon for condition
            icon_char = self._get_condition_icon(day.description)
            
            # Precipitation
            precip = f"{day.precipitation_probability}%" if day.precipitation_probability else "  "
            
            line = f" {day_name:<6} {icon_char} {temp_max:>3.0f}°/{temp_min:>3.0f}° {precip:>3}💧"
            
            # Color based on temperature
            color = self._temp_color(temp_max)
            self.screen.print_at(line[:width], x, y, colour=color)
            y += 1
        
        return y
    
    def _get_condition_icon(self, description: str) -> str:
        """Get a simple icon character for weather condition."""
        desc_lower = description.lower()
        
        if 'storm' in desc_lower or 'thunder' in desc_lower:
            return "⛈️ "
        elif 'rain' in desc_lower or 'drizzle' in desc_lower:
            return "🌧️ "
        elif 'snow' in desc_lower:
            return "❄️ "
        elif 'cloud' in desc_lower:
            return "☁️ "
        elif 'clear' in desc_lower or 'sunny' in desc_lower:
            return "☀️ "
        elif 'mist' in desc_lower or 'fog' in desc_lower:
            return "🌫️ "
        else:
            return "🌤️ "
    
    def _temp_color(self, temp_f: float) -> int:
        """Get color based on temperature."""
        if temp_f >= 90:
            return Screen.COLOUR_RED
        elif temp_f >= 75:
            return Screen.COLOUR_YELLOW
        elif temp_f >= 55:
            return Screen.COLOUR_GREEN
        elif temp_f >= 35:
            return Screen.COLOUR_CYAN
        else:
            return Screen.COLOUR_BLUE


# ═══════════════════════════════════════════════════════════════════════════════
# ⚠️ ALERT BANNER
# ═══════════════════════════════════════════════════════════════════════════════

class AlertBanner:
    """
    Draws weather alert banners with urgency styling.
    """
    
    SEVERITY_COLORS = {
        'extreme': Screen.COLOUR_RED,
        'severe': Screen.COLOUR_RED,
        'moderate': Screen.COLOUR_YELLOW,
        'minor': Screen.COLOUR_CYAN,
        'unknown': Screen.COLOUR_WHITE,
    }
    
    SEVERITY_ICONS = {
        'extreme': "🚨",
        'severe': "⚠️ ",
        'moderate': "⚡",
        'minor': "ℹ️ ",
        'unknown': "📢",
    }
    
    def __init__(self, screen: Screen):
        self.screen = screen
        self.scroll_offset = 0
        self.last_scroll_time = 0
    
    def draw(self, alerts: List, x: int, y: int, width: int):
        """Draw alert banners."""
        if not alerts:
            return y
        
        for alert in alerts[:3]:  # Show max 3 alerts
            severity = getattr(alert, 'severity', 'unknown').lower()
            color = self.SEVERITY_COLORS.get(severity, Screen.COLOUR_WHITE)
            icon = self.SEVERITY_ICONS.get(severity, "📢")
            
            # Draw alert box
            self.screen.print_at("╔" + "═" * (width - 2) + "╗", x, y, colour=color)
            y += 1
            
            # Title line
            event = getattr(alert, 'event', 'Weather Alert')
            title = f"║ {icon} {event[:width-6]:^{width-6}} ║"
            self.screen.print_at(title, x, y, colour=color, attr=Screen.A_BOLD)
            y += 1
            
            # Description (scrolling if too long)
            desc = getattr(alert, 'headline', getattr(alert, 'description', ''))[:200]
            desc_lines = self._wrap_text(desc, width - 4)
            
            for line in desc_lines[:2]:  # Max 2 lines of description
                self.screen.print_at(f"║ {line:<{width-4}} ║", x, y, colour=color)
                y += 1
            
            # Time info
            expires = getattr(alert, 'expires', None)
            if expires:
                if isinstance(expires, str):
                    expires_str = expires[:16]
                else:
                    expires_str = expires.strftime("%Y-%m-%d %H:%M")
                time_line = f"║ Expires: {expires_str:<{width-14}} ║"
                self.screen.print_at(time_line, x, y, colour=color)
                y += 1
            
            # Bottom border
            self.screen.print_at("╚" + "═" * (width - 2) + "╝", x, y, colour=color)
            y += 2
        
        return y
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to fit width."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word[:width]
        
        if current_line:
            lines.append(current_line)
        
        return lines


# ═══════════════════════════════════════════════════════════════════════════════
# 🌙 ASTRONOMICAL PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class AstronomicalPanel:
    """
    Displays sun/moon information with ASCII art.
    """
    
    # Moon phase ASCII art
    MOON_ART = {
        'new': [
            "   🌑   ",
            "  New   ",
            "  Moon  ",
        ],
        'waxing_crescent': [
            "   🌒   ",
            " Waxing ",
            "Crescent",
        ],
        'first_quarter': [
            "   🌓   ",
            " First  ",
            "Quarter ",
        ],
        'waxing_gibbous': [
            "   🌔   ",
            " Waxing ",
            "Gibbous ",
        ],
        'full': [
            "   🌕   ",
            "  Full  ",
            "  Moon  ",
        ],
        'waning_gibbous': [
            "   🌖   ",
            " Waning ",
            "Gibbous ",
        ],
        'last_quarter': [
            "   🌗   ",
            "  Last  ",
            "Quarter ",
        ],
        'waning_crescent': [
            "   🌘   ",
            " Waning ",
            "Crescent",
        ],
    }
    
    def __init__(self, screen: Screen):
        self.screen = screen
    
    def draw(self, astro_data, x: int, y: int, width: int = 30):
        """Draw astronomical information panel."""
        if not astro_data:
            return y
        
        # Title
        self.screen.print_at("🌞 SUN & MOON", x, y,
                            colour=Screen.COLOUR_YELLOW,
                            attr=Screen.A_BOLD)
        y += 1
        
        self.screen.print_at("─" * width, x, y, colour=Screen.COLOUR_YELLOW)
        y += 1
        
        # Sunrise/Sunset
        sunrise = getattr(astro_data, 'sunrise', None)
        sunset = getattr(astro_data, 'sunset', None)
        
        if sunrise:
            sr_str = sunrise.strftime("%H:%M") if hasattr(sunrise, 'strftime') else str(sunrise)
            self.screen.print_at(f"  🌅 Sunrise: {sr_str}", x, y, colour=Screen.COLOUR_YELLOW)
            y += 1
        
        if sunset:
            ss_str = sunset.strftime("%H:%M") if hasattr(sunset, 'strftime') else str(sunset)
            self.screen.print_at(f"  🌇 Sunset:  {ss_str}", x, y, colour=Screen.COLOUR_YELLOW)
            y += 1
        
        # Day length
        if sunrise and sunset:
            try:
                day_length = sunset - sunrise
                hours = day_length.seconds // 3600
                minutes = (day_length.seconds % 3600) // 60
                self.screen.print_at(f"  ⏱️  Day: {hours}h {minutes}m", x, y, 
                                    colour=Screen.COLOUR_WHITE)
                y += 1
            except Exception:
                pass
        
        y += 1
        
        # Moon phase
        moon_phase = getattr(astro_data, 'moon_phase', None)
        if moon_phase:
            phase_name = moon_phase.name.lower() if hasattr(moon_phase, 'name') else str(moon_phase)
            moon_art = self.MOON_ART.get(phase_name, self.MOON_ART['full'])
            
            for line in moon_art:
                self.screen.print_at(line, x + 2, y, colour=Screen.COLOUR_WHITE)
                y += 1
        
        return y


# ═══════════════════════════════════════════════════════════════════════════════
# 🌿 ENVIRONMENTAL PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class EnvironmentalPanel:
    """
    Displays UV Index and Air Quality information.
    """
    
    UV_COLORS = {
        'low': Screen.COLOUR_GREEN,
        'moderate': Screen.COLOUR_YELLOW,
        'high': Screen.COLOUR_RED,
        'very_high': Screen.COLOUR_MAGENTA,
        'extreme': Screen.COLOUR_RED,
    }
    
    AQI_COLORS = {
        'good': Screen.COLOUR_GREEN,
        'moderate': Screen.COLOUR_YELLOW,
        'unhealthy_sensitive': Screen.COLOUR_YELLOW,
        'unhealthy': Screen.COLOUR_RED,
        'very_unhealthy': Screen.COLOUR_MAGENTA,
        'hazardous': Screen.COLOUR_RED,
    }
    
    def __init__(self, screen: Screen):
        self.screen = screen
    
    def draw(self, env_data, x: int, y: int, width: int = 30):
        """Draw environmental data panel."""
        if not env_data:
            return y
        
        # Title
        self.screen.print_at("🌿 ENVIRONMENT", x, y,
                            colour=Screen.COLOUR_GREEN,
                            attr=Screen.A_BOLD)
        y += 1
        
        self.screen.print_at("─" * width, x, y, colour=Screen.COLOUR_GREEN)
        y += 1
        
        # UV Index
        uv_index = getattr(env_data, 'uv_index', None)
        if uv_index is not None:
            uv_level = getattr(env_data, 'uv_level', None)
            level_name = uv_level.value if hasattr(uv_level, 'value') else str(uv_level) if uv_level else 'unknown'
            color = self.UV_COLORS.get(level_name, Screen.COLOUR_WHITE)
            
            # UV bar visualization
            bar_length = min(int(uv_index), 11)
            bar = "█" * bar_length + "░" * (11 - bar_length)
            
            self.screen.print_at(f"  ☀️  UV Index: {uv_index:.1f}", x, y, colour=color)
            y += 1
            self.screen.print_at(f"     [{bar}] {level_name.upper()}", x, y, colour=color)
            y += 2
        
        # Air Quality
        aqi = getattr(env_data, 'aqi', None)
        if aqi is not None:
            aqi_level = getattr(env_data, 'aqi_level', None)
            level_name = aqi_level.value if hasattr(aqi_level, 'value') else str(aqi_level) if aqi_level else 'unknown'
            color = self.AQI_COLORS.get(level_name, Screen.COLOUR_WHITE)
            
            # AQI bar
            bar_length = min(int(aqi / 50), 10)
            bar = "█" * bar_length + "░" * (10 - bar_length)
            
            self.screen.print_at(f"  💨 Air Quality: {aqi}", x, y, colour=color)
            y += 1
            self.screen.print_at(f"     [{bar}] {level_name.replace('_', ' ').upper()}", x, y, colour=color)
            y += 2
        
        # Pollutants
        pm25 = getattr(env_data, 'pm25', None)
        pm10 = getattr(env_data, 'pm10', None)
        
        if pm25 is not None:
            self.screen.print_at(f"     PM2.5: {pm25:.1f} µg/m³", x, y, 
                                colour=Screen.COLOUR_WHITE)
            y += 1
        
        if pm10 is not None:
            self.screen.print_at(f"     PM10:  {pm10:.1f} µg/m³", x, y,
                                colour=Screen.COLOUR_WHITE)
            y += 1
        
        return y


# ═══════════════════════════════════════════════════════════════════════════════
# 🏆 ACHIEVEMENT DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

class AchievementDisplay:
    """
    Shows achievement unlocks and progress.
    """
    
    TIER_COLORS = {
        'BRONZE': Screen.COLOUR_YELLOW,
        'SILVER': Screen.COLOUR_WHITE,
        'GOLD': Screen.COLOUR_YELLOW,
        'PLATINUM': Screen.COLOUR_CYAN,
        'LEGENDARY': Screen.COLOUR_MAGENTA,
    }
    
    def __init__(self, screen: Screen):
        self.screen = screen
        self.pending_achievements: List[Tuple[str, str, str]] = []  # (name, desc, tier)
        self.display_time = 0.0
        self.display_duration = 5.0
    
    def queue_achievement(self, name: str, description: str, tier: str = 'BRONZE'):
        """Queue an achievement for display."""
        self.pending_achievements.append((name, description, tier))
    
    def draw_popup(self, x: int, y: int, width: int = 50):
        """Draw achievement popup if there's a pending one."""
        import time
        
        if not self.pending_achievements:
            return
        
        # Start timer on first display
        if self.display_time == 0:
            self.display_time = time.time()
        
        # Check if display time expired
        if time.time() - self.display_time > self.display_duration:
            self.pending_achievements.pop(0)
            self.display_time = 0
            return
        
        name, description, tier = self.pending_achievements[0]
        color = self.TIER_COLORS.get(tier, Screen.COLOUR_WHITE)
        
        # Draw popup box
        height = 5
        
        # Border
        self.screen.print_at("╔" + "═" * (width - 2) + "╗", x, y, colour=color)
        for i in range(1, height - 1):
            self.screen.print_at("║" + " " * (width - 2) + "║", x, y + i, colour=color)
        self.screen.print_at("╚" + "═" * (width - 2) + "╝", x, y + height - 1, colour=color)
        
        # Content
        title = "🏆 ACHIEVEMENT UNLOCKED! 🏆"
        self.screen.print_at(title, x + (width - len(title)) // 2, y + 1,
                            colour=Screen.COLOUR_YELLOW, attr=Screen.A_BOLD)
        
        self.screen.print_at(name[:width-4], x + 2, y + 2, colour=color)
        self.screen.print_at(description[:width-4], x + 2, y + 3, colour=Screen.COLOUR_WHITE)


# ═══════════════════════════════════════════════════════════════════════════════
# 📜 HISTORICAL COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

class HistoricalComparisonPanel:
    """
    Shows comparison between current weather and historical averages.
    """
    
    def __init__(self, screen: Screen):
        self.screen = screen
    
    def draw(self, comparison_data: Dict, x: int, y: int, width: int = 40):
        """Draw historical comparison."""
        if not comparison_data:
            return y
        
        # Title
        self.screen.print_at("📊 VS HISTORICAL", x, y,
                            colour=Screen.COLOUR_MAGENTA,
                            attr=Screen.A_BOLD)
        y += 1
        
        self.screen.print_at("─" * width, x, y, colour=Screen.COLOUR_MAGENTA)
        y += 1
        
        # Temperature comparison
        temp_diff = comparison_data.get('temperature_diff', 0)
        if temp_diff != 0:
            direction = "↑" if temp_diff > 0 else "↓"
            color = Screen.COLOUR_RED if temp_diff > 0 else Screen.COLOUR_BLUE
            self.screen.print_at(f"  🌡️  Temp: {direction} {abs(temp_diff):.1f}° from avg",
                                x, y, colour=color)
            y += 1
        
        # Records
        record_high = comparison_data.get('record_high')
        record_low = comparison_data.get('record_low')
        
        if record_high:
            self.screen.print_at(f"  🔥 Record High: {record_high:.1f}°", x, y,
                                colour=Screen.COLOUR_RED)
            y += 1
        
        if record_low:
            self.screen.print_at(f"  ❄️  Record Low: {record_low:.1f}°", x, y,
                                colour=Screen.COLOUR_BLUE)
            y += 1
        
        # Average
        avg_temp = comparison_data.get('average_temperature')
        if avg_temp:
            self.screen.print_at(f"  📈 Avg: {avg_temp:.1f}°", x, y,
                                colour=Screen.COLOUR_WHITE)
            y += 1
        
        # Sample count
        sample_count = comparison_data.get('sample_count', 0)
        if sample_count:
            self.screen.print_at(f"  📊 Based on {sample_count} records", x, y,
                                colour=Screen.COLOUR_WHITE)
            y += 1
        
        return y


# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 INTEGRATED RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

class EnhancedDashboardRenderer:
    """
    Coordinates rendering of all enhanced panels.
    """
    
    def __init__(self, screen: Screen):
        self.screen = screen
        self.forecast_panel = ForecastPanel(screen)
        self.alert_banner = AlertBanner(screen)
        self.astro_panel = AstronomicalPanel(screen)
        self.env_panel = EnvironmentalPanel(screen)
        self.achievement_display = AchievementDisplay(screen)
        self.historical_panel = HistoricalComparisonPanel(screen)
    
    def render_sidebar(self, y_start: int, 
                       astro_data=None, 
                       env_data=None, 
                       historical_data=None):
        """Render the right sidebar with additional data."""
        x = self.screen.width - 35
        y = y_start
        width = 32
        
        if astro_data:
            y = self.astro_panel.draw(astro_data, x, y, width)
            y += 1
        
        if env_data:
            y = self.env_panel.draw(env_data, x, y, width)
            y += 1
        
        if historical_data:
            y = self.historical_panel.draw(historical_data, x, y, width)
        
        return y
    
    def render_bottom_panel(self, hourly_data=None, daily_data=None):
        """Render the bottom panel with forecast data."""
        y = self.screen.height - 15
        x = 2
        width = min(80, self.screen.width - 4)
        
        if hourly_data:
            y = self.forecast_panel.draw_hourly(hourly_data, x, y, width)
            y += 1
        
        if daily_data:
            y = self.forecast_panel.draw_daily(daily_data, x, y, width)
        
        return y
    
    def render_alerts(self, alerts, y_start: int = 2):
        """Render alert banners at the top."""
        if not alerts:
            return y_start
        
        x = 2
        width = min(76, self.screen.width - 4)
        return self.alert_banner.draw(alerts, x, y_start, width)
    
    def render_achievement_popup(self):
        """Render achievement unlock popup."""
        x = (self.screen.width - 50) // 2
        y = 5
        self.achievement_display.draw_popup(x, y, 50)


# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🎨 Enhanced Dashboard Integration Module")
    print("This module provides UI panels for:")
    print("  📊 Hourly & Daily Forecast")
    print("  ⚠️  Weather Alerts")
    print("  🌙 Sun & Moon Data")
    print("  🌿 UV & Air Quality")
    print("  🏆 Achievement Popups")
    print("  📜 Historical Comparison")
