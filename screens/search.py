"""Location search screen — interactive city search with live results."""
import time
from typing import Optional

from asciimatics.screen import Screen

from lib.weather_api import WeatherData, search_and_fetch_weather


def location_search_screen(screen: Screen, Theme) -> Optional[WeatherData]:
    """
    Interactive location search screen.
    Type a city name and press Enter to search.
    """
    screen.clear()
    w, h = screen.width, screen.height

    # Title
    title = "LOCATION SEARCH"
    screen.print_at(title, (w - len(title)) // 2, 2, colour=Theme.SUN)

    subtitle = "Type a city name and press Enter"
    screen.print_at(subtitle, (w - len(subtitle)) // 2, 4, colour=Theme.FROST)

    # Examples
    examples = [
        "Examples:  Summerville, SC  |  New York, NY  |  Moscow, Russia",
        "           Tokyo, Japan  |  London, UK  |  Paris, France"
    ]
    for i, ex in enumerate(examples):
        screen.print_at(ex, (w - len(ex)) // 2, 6 + i, colour=Theme.MUTED)

    # Input box
    box_y = 10
    box_width = min(60, w - 4)
    box_x = (w - box_width) // 2

    # Draw box
    screen.print_at("┌" + "─" * (box_width - 2) + "┐", box_x, box_y, colour=Theme.FROST)
    screen.print_at("│" + " " * (box_width - 2) + "│", box_x, box_y + 1, colour=Theme.FROST)
    screen.print_at("└" + "─" * (box_width - 2) + "┘", box_x, box_y + 2, colour=Theme.FROST)

    # Instructions
    instructions = "Enter = Search  |  Esc = Cancel  |  Backspace = Delete"
    screen.print_at(instructions, (w - len(instructions)) // 2, box_y + 4, colour=Theme.MUTED)

    screen.refresh()

    # Input loop
    query = ""

    while True:
        # Clear input area and redraw
        screen.print_at(" " * (box_width - 4), box_x + 2, box_y + 1)
        screen.print_at(query[-box_width+6:], box_x + 2, box_y + 1, colour=Theme.SUN)

        # Cursor
        cursor_pos = box_x + 2 + min(len(query), box_width - 6)
        screen.print_at("▌", cursor_pos, box_y + 1, colour=Theme.FROST)

        # Clear status line
        screen.print_at(" " * (w - 4), 2, box_y + 6)
        screen.refresh()

        ev = screen.get_key()

        if ev == Screen.KEY_ESCAPE or ev == ord('q'):
            return None

        if ev in (10, 13):  # Enter key
            if query.strip():
                # Show searching message
                msg = f"Searching for '{query}'..."
                screen.print_at(" " * (w - 4), 2, box_y + 6)
                screen.print_at(msg, (w - len(msg)) // 2, box_y + 6, colour=Theme.FROST)
                screen.refresh()

                # Search!
                weather = search_and_fetch_weather(query.strip())

                if weather:
                    success = f"Found: {weather.location} - {weather.temperature_f:.0f}°F, {weather.description}"
                    screen.print_at(" " * (w - 4), 2, box_y + 6)
                    screen.print_at(success[:w-4], (w - min(len(success), w-4)) // 2, box_y + 6, colour=Theme.SUN)
                    screen.refresh()
                    time.sleep(1.5)
                    return weather
                else:
                    error = f"Location not found: '{query}'"
                    screen.print_at(" " * (w - 4), 2, box_y + 6)
                    screen.print_at(error, (w - len(error)) // 2, box_y + 6, colour=Screen.COLOUR_RED)
                    screen.refresh()
                    time.sleep(1.5)
                    query = ""

        elif ev == Screen.KEY_BACK or ev == 127 or ev == 8:  # Backspace
            query = query[:-1]

        elif ev is not None and 32 <= ev < 127:  # Printable characters
            query += chr(ev)

        time.sleep(0.033)
