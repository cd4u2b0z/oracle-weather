"""Creature Bestiary — collection screen showing all creatures and sighting counts."""
from asciimatics.screen import Screen

# All possible creatures (name -> condition category they appear in)
ALL_CREATURES = {
    "Cthulhu Tentacle": "fog (night)",
    "Eldritch Eye": "fog (night)",
    "Ghost": "fog (day)",
    "Dragon": "storm (night)",
    "Storm Wraith": "storm (night)",
    "Thunder Bird": "storm (day)",
    "Sea Serpent": "rain (night)",
    "Will-o-Wisp": "rain (night)",
    "Rain Spirit": "rain (day)",
    "Frog Prince": "rain (day)",
    "Ice Wraith": "snow (night)",
    "Wendigo": "snow (night)",
    "Yeti": "snow (day)",
    "Snowman": "snow (day)",
    "UFO": "clear (night)",
    "Shooting Star": "clear (night)",
    "Bat": "clear (night)",
    "Owl": "clear (night)",
    "Firefly": "clear (night)",
    "Phoenix": "clear (day)",
    "Butterfly": "clear (day)",
    "Hummingbird": "clear (day)",
    "Bee": "clear (day)",
    "Cloud Whale": "cloudy",
    "Paper Airplane": "cloudy",
}


def draw_bestiary_screen(screen: Screen, stormy, Theme):
    """Draw the creature bestiary / collection screen."""
    screen.clear()
    w, h = screen.width, screen.height
    sightings = stormy.get_creature_sightings()

    # Title
    title = "CREATURE BESTIARY"
    screen.print_at(title, (w - len(title)) // 2, 1, colour=Theme.SUN)

    spotted = sum(1 for name in ALL_CREATURES if name in sightings)
    subtitle = f"Spotted {spotted} of {len(ALL_CREATURES)} creatures"
    screen.print_at(subtitle, (w - len(subtitle)) // 2, 3, colour=Theme.FROST)

    y = 5
    col_width = w // 2 - 2

    for col_start in range(0, len(ALL_CREATURES), 2):
        names = list(ALL_CREATURES.keys())
        for col in range(2):
            idx = col_start + col
            if idx >= len(names):
                break
            name = names[idx]
            condition = ALL_CREATURES[name]
            count = sightings.get(name, 0)

            x = 2 + col * col_width

            if count > 0:
                text = f"  {name} x{count}"
                detail = f"    ({condition})"
                screen.print_at(text[:col_width-2], x, y, colour=Theme.SUN)
                if y + 1 < h - 4:
                    screen.print_at(detail[:col_width-2], x, y + 1, colour=Theme.MUTED)
            else:
                text = f"  ??? ({condition})"
                screen.print_at(text[:col_width-2], x, y, colour=Theme.MUTED)

        y += 3
        if y >= h - 4:
            break

    # Footer
    footer = "Press any key to return..."
    screen.print_at(footer, (w - len(footer)) // 2, h - 1, colour=Theme.FROST)

    screen.refresh()
    screen.wait_for_input(60)
