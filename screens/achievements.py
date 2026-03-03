"""Achievements screen — Hall of Fame display."""
import time
from asciimatics.screen import Screen


def draw_achievements_screen(screen: Screen, stormy, Theme):
    """Draw the achievements screen."""
    screen.clear()

    w, h = screen.width, screen.height

    # Title
    title = "STORMY'S HALL OF FAME"
    screen.print_at(title, (w - len(title)) // 2, 1, colour=Theme.SUN)

    subtitle = f"You've unlocked {len(stormy.data['achievements'])} of {len(stormy.ACHIEVEMENTS)} achievements!"
    screen.print_at(subtitle, (w - len(subtitle)) // 2, 3, colour=Theme.FROST)

    y = 5
    col_width = w // 2 - 2
    col = 0

    for key, (icon, name) in stormy.ACHIEVEMENTS.items():
        unlocked = key in stormy.data["achievements"]

        if unlocked:
            text = f"  {icon} {name}"
            colour = Theme.SUN
        else:
            text = f"  [?] ???"
            colour = Theme.MUTED

        x = 2 + col * col_width
        screen.print_at(text[:col_width-2], x, y, colour=colour)

        col += 1
        if col >= 2:
            col = 0
            y += 2

        if y >= h - 4:
            break

    # Stats
    stats = f"Total checks: {stormy.data['check_count']} | Current streak: {stormy.data['streak']} days"
    screen.print_at(stats, (w - len(stats)) // 2, h - 3, colour=Theme.SNOW)

    footer = "Press any key to return..."
    screen.print_at(footer, (w - len(footer)) // 2, h - 1, colour=Theme.FROST)

    screen.refresh()
    screen.wait_for_input(60)
