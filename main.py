"""
Minimal asciimatics demo - animated ASCII text.
Run: python main.py
"""
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Print
from asciimatics.renderers import FigletText


def demo(screen):
    effects = [
        Print(
            screen,
            FigletText("WEATHER TOYS", font="banner3"),
            x=(screen.width - 80) // 2,
            y=screen.height // 2 - 4,
            colour=Screen.COLOUR_CYAN,
            speed=1
        ),
        Print(
            screen,
            FigletText("asciimatics", font="small"),
            x=(screen.width - 50) // 2,
            y=screen.height // 2 + 4,
            colour=Screen.COLOUR_WHITE,
            speed=1
        )
    ]
    screen.play([Scene(effects, duration=200)], stop_on_resize=True)


if __name__ == "__main__":
    Screen.wrapper(demo)
