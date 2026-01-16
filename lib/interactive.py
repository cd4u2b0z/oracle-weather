"""
Interactive Controls Module
===========================
Keyboard handling and interactive features for the weather dashboard.

Features:
- Keyboard shortcuts for all actions
- Location search dialog
- Help screen
- Screenshot capture
- Mode toggles
- Real-time unit switching

"The ancient oracles used entrails to divine the future.
You use keyboard shortcuts. Progress." - Stormy
"""
from __future__ import annotations
import os
import sys
import time
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Callable, Dict, List, Tuple, Any
from pathlib import Path

from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent


# ═══════════════════════════════════════════════════════════════════════════════
# 🎮 INPUT ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class Action(Enum):
    """All possible user actions."""
    NONE = auto()
    QUIT = auto()
    REFRESH = auto()
    TOGGLE_UNITS = auto()
    SWITCH_LOCATION = auto()
    NEXT_LOCATION = auto()
    PREV_LOCATION = auto()
    TOGGLE_FORECAST = auto()
    TOGGLE_COMPACT = auto()
    SCREENSHOT = auto()
    HELP = auto()
    TOGGLE_PARTICLES = auto()
    CYCLE_THEME = auto()
    EXPORT_DATA = auto()
    TOGGLE_ALERTS = auto()
    TOGGLE_MOON = auto()
    SEARCH_LOCATION = auto()


@dataclass
class KeyBinding:
    """Single key binding definition."""
    key: str
    action: Action
    description: str
    category: str = "General"


# Default key bindings
DEFAULT_BINDINGS: List[KeyBinding] = [
    KeyBinding('q', Action.QUIT, "Quit the dashboard", "General"),
    KeyBinding('r', Action.REFRESH, "Refresh weather data", "General"),
    KeyBinding('?', Action.HELP, "Show this help screen", "General"),
    
    KeyBinding('u', Action.TOGGLE_UNITS, "Toggle °F/°C units", "Display"),
    KeyBinding('f', Action.TOGGLE_FORECAST, "Toggle forecast panel", "Display"),
    KeyBinding('c', Action.TOGGLE_COMPACT, "Toggle compact mode", "Display"),
    KeyBinding('a', Action.TOGGLE_PARTICLES, "Toggle animations", "Display"),
    KeyBinding('t', Action.CYCLE_THEME, "Cycle color theme", "Display"),
    KeyBinding('m', Action.TOGGLE_MOON, "Toggle moon/sun display", "Display"),
    KeyBinding('w', Action.TOGGLE_ALERTS, "Toggle weather alerts", "Display"),
    
    KeyBinding('l', Action.SEARCH_LOCATION, "Search for location", "Location"),
    KeyBinding('n', Action.NEXT_LOCATION, "Next saved location", "Location"),
    KeyBinding('p', Action.PREV_LOCATION, "Previous saved location", "Location"),
    
    KeyBinding('s', Action.SCREENSHOT, "Save screenshot", "Export"),
    KeyBinding('e', Action.EXPORT_DATA, "Export weather data", "Export"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# ⌨️ INPUT HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class InputHandler:
    """
    Handles keyboard input and maps to actions.
    """
    
    def __init__(self, bindings: List[KeyBinding] = None):
        self.bindings = bindings or DEFAULT_BINDINGS
        self._key_map: Dict[str, Action] = {}
        self._build_key_map()
    
    def _build_key_map(self):
        """Build key to action mapping."""
        self._key_map.clear()
        for binding in self.bindings:
            self._key_map[binding.key.lower()] = binding.action
    
    def handle_event(self, event) -> Action:
        """
        Handle a keyboard event and return the action.
        """
        if event is None:
            return Action.NONE
        
        if isinstance(event, KeyboardEvent):
            key_code = event.key_code
            
            # Handle special keys
            if key_code == Screen.KEY_ESCAPE or key_code == ord('q'):
                return Action.QUIT
            
            # Convert to character
            if 32 <= key_code < 127:
                char = chr(key_code).lower()
                return self._key_map.get(char, Action.NONE)
            
            # Handle arrow keys for navigation
            if key_code == Screen.KEY_RIGHT:
                return Action.NEXT_LOCATION
            if key_code == Screen.KEY_LEFT:
                return Action.PREV_LOCATION
        
        return Action.NONE
    
    def get_bindings_by_category(self) -> Dict[str, List[KeyBinding]]:
        """Get bindings organized by category."""
        categories: Dict[str, List[KeyBinding]] = {}
        for binding in self.bindings:
            if binding.category not in categories:
                categories[binding.category] = []
            categories[binding.category].append(binding)
        return categories


# ═══════════════════════════════════════════════════════════════════════════════
# 📸 SCREENSHOT CAPTURE
# ═══════════════════════════════════════════════════════════════════════════════

class ScreenshotCapture:
    """
    Captures terminal content as ANSI art or plain text.
    """
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path.home() / "stormy_screenshots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def capture(self, screen: Screen, filename: str = None) -> str:
        """
        Capture current screen content.
        Returns the path to the saved file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stormy_{timestamp}.txt"
        
        filepath = self.output_dir / filename
        
        # Capture screen content
        lines = []
        for y in range(screen.height):
            line_chars = []
            for x in range(screen.width):
                char, fg, attr, bg = screen.get_from(x, y)
                if char:
                    line_chars.append(chr(char) if isinstance(char, int) else char)
                else:
                    line_chars.append(' ')
            lines.append(''.join(line_chars).rstrip())
        
        # Write to file
        content = '\n'.join(lines)
        filepath.write_text(content)
        
        return str(filepath)
    
    def capture_with_ansi(self, screen: Screen, filename: str = None) -> str:
        """
        Capture screen with ANSI color codes preserved.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stormy_{timestamp}_ansi.txt"
        
        filepath = self.output_dir / filename
        
        # ANSI color code mapping
        fg_codes = {
            Screen.COLOUR_BLACK: 30,
            Screen.COLOUR_RED: 31,
            Screen.COLOUR_GREEN: 32,
            Screen.COLOUR_YELLOW: 33,
            Screen.COLOUR_BLUE: 34,
            Screen.COLOUR_MAGENTA: 35,
            Screen.COLOUR_CYAN: 36,
            Screen.COLOUR_WHITE: 37,
        }
        
        lines = []
        for y in range(screen.height):
            line_parts = []
            last_fg = None
            
            for x in range(screen.width):
                char, fg, attr, bg = screen.get_from(x, y)
                
                # Add color code if changed
                if fg != last_fg and fg in fg_codes:
                    line_parts.append(f"\033[{fg_codes[fg]}m")
                    last_fg = fg
                
                if char:
                    line_parts.append(chr(char) if isinstance(char, int) else char)
                else:
                    line_parts.append(' ')
            
            # Reset at end of line
            line_parts.append("\033[0m")
            lines.append(''.join(line_parts).rstrip())
        
        content = '\n'.join(lines)
        filepath.write_text(content)
        
        return str(filepath)


# ═══════════════════════════════════════════════════════════════════════════════
# 🔍 LOCATION SEARCH DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class LocationSearchDialog:
    """
    Interactive location search dialog.
    """
    
    def __init__(self, screen: Screen):
        self.screen = screen
        self.query = ""
        self.results: List[Dict] = []
        self.selected_index = 0
        self.searching = False
        self.error_message = ""
    
    def draw(self):
        """Draw the search dialog."""
        width = min(60, self.screen.width - 4)
        height = min(15, self.screen.height - 4)
        x = (self.screen.width - width) // 2
        y = (self.screen.height - height) // 2
        
        # Draw box
        self._draw_box(x, y, width, height, "🔍 Search Location")
        
        # Draw search input
        input_y = y + 2
        self.screen.print_at("Enter city name:", x + 2, input_y, 
                            colour=Screen.COLOUR_WHITE)
        
        # Input field
        input_field = self.query + "█"
        self.screen.print_at(input_field[:width-4], x + 2, input_y + 1,
                            colour=Screen.COLOUR_CYAN)
        
        # Status
        if self.searching:
            self.screen.print_at("Searching...", x + 2, input_y + 3,
                                colour=Screen.COLOUR_YELLOW)
        elif self.error_message:
            self.screen.print_at(self.error_message[:width-4], x + 2, input_y + 3,
                                colour=Screen.COLOUR_RED)
        
        # Results
        results_y = input_y + 4
        for i, result in enumerate(self.results[:5]):
            prefix = "→ " if i == self.selected_index else "  "
            color = Screen.COLOUR_GREEN if i == self.selected_index else Screen.COLOUR_WHITE
            
            loc_name = result.get('display_name', result.get('name', 'Unknown'))[:width-6]
            self.screen.print_at(f"{prefix}{loc_name}", x + 2, results_y + i,
                                colour=color)
        
        # Instructions
        inst_y = y + height - 2
        self.screen.print_at("Enter: Select | Esc: Cancel | ↑↓: Navigate",
                            x + 2, inst_y, colour=Screen.COLOUR_WHITE)
    
    def _draw_box(self, x: int, y: int, width: int, height: int, title: str):
        """Draw a box with title."""
        # Top border
        self.screen.print_at("╔" + "═" * (width - 2) + "╗", x, y,
                            colour=Screen.COLOUR_CYAN)
        
        # Title
        title_x = x + (width - len(title)) // 2
        self.screen.print_at(title, title_x, y, colour=Screen.COLOUR_CYAN)
        
        # Sides
        for row in range(1, height - 1):
            self.screen.print_at("║" + " " * (width - 2) + "║", x, y + row,
                                colour=Screen.COLOUR_CYAN)
        
        # Bottom border
        self.screen.print_at("╚" + "═" * (width - 2) + "╝", x, y + height - 1,
                            colour=Screen.COLOUR_CYAN)
    
    def handle_input(self, event) -> Optional[Dict]:
        """
        Handle input. Returns selected location dict or None.
        """
        if not isinstance(event, KeyboardEvent):
            return None
        
        key = event.key_code
        
        # Escape - cancel
        if key == Screen.KEY_ESCAPE:
            return {'cancelled': True}
        
        # Enter - select
        if key in (10, 13):  # Enter
            if self.results and 0 <= self.selected_index < len(self.results):
                return self.results[self.selected_index]
            elif self.query:
                self._search()
            return None
        
        # Backspace
        if key in (8, 127, Screen.KEY_BACK):
            self.query = self.query[:-1]
            return None
        
        # Arrow keys
        if key == Screen.KEY_UP:
            self.selected_index = max(0, self.selected_index - 1)
            return None
        if key == Screen.KEY_DOWN:
            self.selected_index = min(len(self.results) - 1, self.selected_index + 1)
            return None
        
        # Printable characters
        if 32 <= key < 127:
            self.query += chr(key)
            return None
        
        return None
    
    def _search(self):
        """Perform location search."""
        self.searching = True
        self.error_message = ""
        self.results = []
        
        try:
            from lib.weather_api import geocode_location
            
            result = geocode_location(self.query)
            if result:
                # Build display name
                if result.get('state'):
                    display = f"{result['name']}, {result['state']}, {result['country']}"
                else:
                    display = f"{result['name']}, {result['country']}"
                
                result['display_name'] = display
                self.results = [result]
                self.selected_index = 0
            else:
                self.error_message = "Location not found"
        except Exception as e:
            self.error_message = f"Search error: {str(e)[:30]}"
        
        self.searching = False


# ═══════════════════════════════════════════════════════════════════════════════
# ❓ HELP SCREEN
# ═══════════════════════════════════════════════════════════════════════════════

class HelpScreen:
    """
    Displays help information and keyboard shortcuts.
    """
    
    def __init__(self, screen: Screen, input_handler: InputHandler):
        self.screen = screen
        self.input_handler = input_handler
        self.scroll_offset = 0
    
    def draw(self):
        """Draw the help screen."""
        width = min(70, self.screen.width - 4)
        height = min(25, self.screen.height - 4)
        x = (self.screen.width - width) // 2
        y = (self.screen.height - height) // 2
        
        # Draw box
        self._draw_box(x, y, width, height, "⚡ STORMY - Weather Dashboard Help")
        
        # Content
        content_y = y + 2
        
        # Header
        self.screen.print_at("\"Knowledge is power. Power is weather forecast.\"",
                            x + 2, content_y, colour=Screen.COLOUR_CYAN)
        self.screen.print_at("                                    - Stormy",
                            x + 2, content_y + 1, colour=Screen.COLOUR_CYAN)
        
        content_y += 3
        
        # Key bindings by category
        categories = self.input_handler.get_bindings_by_category()
        
        for category, bindings in categories.items():
            if content_y >= y + height - 3:
                break
            
            # Category header
            self.screen.print_at(f"═══ {category} ═══", x + 2, content_y,
                                colour=Screen.COLOUR_YELLOW)
            content_y += 1
            
            for binding in bindings:
                if content_y >= y + height - 3:
                    break
                
                key_str = f"[{binding.key.upper()}]"
                self.screen.print_at(key_str, x + 2, content_y,
                                    colour=Screen.COLOUR_GREEN)
                self.screen.print_at(binding.description, x + 8, content_y,
                                    colour=Screen.COLOUR_WHITE)
                content_y += 1
            
            content_y += 1
        
        # Footer
        self.screen.print_at("Press any key to close", x + (width - 22) // 2,
                            y + height - 2, colour=Screen.COLOUR_WHITE)
    
    def _draw_box(self, x: int, y: int, width: int, height: int, title: str):
        """Draw a box with title."""
        # Top border
        self.screen.print_at("╔" + "═" * (width - 2) + "╗", x, y,
                            colour=Screen.COLOUR_MAGENTA)
        
        # Title centered
        title_x = x + (width - len(title)) // 2
        self.screen.print_at(title, title_x, y, colour=Screen.COLOUR_MAGENTA)
        
        # Sides
        for row in range(1, height - 1):
            self.screen.print_at("║" + " " * (width - 2) + "║", x, y + row,
                                colour=Screen.COLOUR_MAGENTA)
        
        # Bottom border
        self.screen.print_at("╚" + "═" * (width - 2) + "╝", x, y + height - 1,
                            colour=Screen.COLOUR_MAGENTA)
    
    def handle_input(self, event) -> bool:
        """Handle input. Returns True if should close."""
        if isinstance(event, KeyboardEvent):
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 NOTIFICATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Notification:
    """A notification message."""
    message: str
    color: int = Screen.COLOUR_WHITE
    duration: float = 3.0  # seconds
    created_at: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
    
    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.duration


class NotificationManager:
    """
    Manages on-screen notifications.
    """
    
    def __init__(self, max_notifications: int = 3):
        self.notifications: List[Notification] = []
        self.max_notifications = max_notifications
    
    def add(self, message: str, color: int = Screen.COLOUR_WHITE, duration: float = 3.0):
        """Add a notification."""
        notif = Notification(message=message, color=color, duration=duration)
        self.notifications.append(notif)
        
        # Limit count
        while len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
    
    def add_success(self, message: str):
        """Add a success notification."""
        self.add(message, Screen.COLOUR_GREEN)
    
    def add_error(self, message: str):
        """Add an error notification."""
        self.add(message, Screen.COLOUR_RED, duration=5.0)
    
    def add_info(self, message: str):
        """Add an info notification."""
        self.add(message, Screen.COLOUR_CYAN)
    
    def add_achievement(self, name: str, emoji: str = "🏆"):
        """Add an achievement notification."""
        self.add(f"{emoji} Achievement Unlocked: {name}", Screen.COLOUR_YELLOW, duration=5.0)
    
    def update(self):
        """Remove expired notifications."""
        self.notifications = [n for n in self.notifications if not n.is_expired]
    
    def draw(self, screen: Screen, x: int, y: int):
        """Draw active notifications."""
        for i, notif in enumerate(self.notifications):
            # Calculate fade
            age = time.time() - notif.created_at
            if age > notif.duration - 0.5:
                # Fade out effect - just reduce characters
                visible_len = int(len(notif.message) * ((notif.duration - age) / 0.5))
                message = notif.message[:visible_len]
            else:
                message = notif.message
            
            screen.print_at(message, x, y + i, colour=notif.color)


# ═══════════════════════════════════════════════════════════════════════════════
# 🎛️ STATE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardState:
    """
    Tracks the current state of the dashboard UI.
    """
    
    def __init__(self):
        # Display modes
        self.show_forecast = True
        self.show_hourly = True
        self.show_alerts = True
        self.show_moon = True
        self.show_particles = True
        self.compact_mode = False
        
        # Dialogs
        self.show_help = False
        self.show_location_search = False
        
        # Data
        self.needs_refresh = True
        self.last_refresh = 0.0
        self.refresh_interval = 300.0  # 5 minutes
        
        # UI
        self.notification_manager = NotificationManager()
    
    def toggle(self, attr: str) -> bool:
        """Toggle a boolean attribute. Returns new value."""
        current = getattr(self, attr, False)
        setattr(self, attr, not current)
        return not current
    
    def should_refresh(self) -> bool:
        """Check if data should be refreshed."""
        if self.needs_refresh:
            return True
        return time.time() - self.last_refresh > self.refresh_interval
    
    def mark_refreshed(self):
        """Mark that data was just refreshed."""
        self.needs_refresh = False
        self.last_refresh = time.time()


# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🎮 Interactive Controls Module")
    print("\nDefault Key Bindings:")
    
    handler = InputHandler()
    categories = handler.get_bindings_by_category()
    
    for category, bindings in categories.items():
        print(f"\n═══ {category} ═══")
        for binding in bindings:
            print(f"  [{binding.key.upper()}] {binding.description}")
