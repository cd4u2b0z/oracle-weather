"""
ASCII art assets — big digits, weather mascot, scenes, and faces.
Extracted from the monolith. Keyed by WeatherCondition where applicable.
"""
from lib.weather_api import WeatherCondition


# ═══════════════════════════════════════════════════════════════════════════════
# BIG TEMPERATURE DIGITS — 3-line tall box-drawing numerals
# ═══════════════════════════════════════════════════════════════════════════════

BIG_DIGITS = {
    '0': ["┌─┐", "│ │", "└─┘"],
    '1': [" ┐ ", " │ ", " ┴ "],
    '2': ["┌─┐", "┌─┘", "└─┘"],
    '3': ["┌─┐", " ─┤", "└─┘"],
    '4': ["┐ ┐", "└─┤", "  ┘"],
    '5': ["┌─┐", "└─┐", "└─┘"],
    '6': ["┌─┐", "├─┐", "└─┘"],
    '7': ["┌─┐", "  │", "  ┘"],
    '8': ["┌─┐", "├─┤", "└─┘"],
    '9': ["┌─┐", "└─┤", "└─┘"],
    '-': ["   ", "───", "   "],
    '°': ["┌┐ ", "└┘ ", "   "],
    ' ': ["   ", "   ", "   "],
}


# ═══════════════════════════════════════════════════════════════════════════════
# WEATHER MASCOT — cute face that changes with conditions
# ═══════════════════════════════════════════════════════════════════════════════

WEATHER_MASCOT = {
    WeatherCondition.CLEAR: [
        "    \\  |  //    ",
        "      (◠‿◠)      ",
        "    //  |  \\    ",
    ],
    WeatherCondition.PARTLY_CLOUDY: [
        "    ~  ◠◠  ~    ",
        "      (◕‿◕)      ",
        "       ~~~       ",
    ],
    WeatherCondition.CLOUDY: [
        "     ~~~☁~~~     ",
        "      (◕ᴗ◕)      ",
        "       ~~~       ",
    ],
    WeatherCondition.FOG: [
        "    ≋≋≋≋≋≋≋≋    ",
        "      (◡_◡)      ",
        "    ≋≋≋≋≋≋≋≋    ",
    ],
    WeatherCondition.DRIZZLE: [
        "       ☁        ",
        "      (◕‿◕)      ",
        "      ⋮ ⋮ ⋮      ",
    ],
    WeatherCondition.RAIN: [
        "      ☁☁☁       ",
        "      (◕_◕)      ",
        "      ╏╏╏╏╏      ",
    ],
    WeatherCondition.HEAVY_RAIN: [
        "     ☁☁☁☁☁      ",
        "      (◕︵◕)      ",
        "     ╏╏╏╏╏╏╏     ",
    ],
    WeatherCondition.FREEZING_RAIN: [
        "      ☁❄☁       ",
        "      (◕﹏◕)      ",
        "      ╏*╏*╏      ",
    ],
    WeatherCondition.SNOW: [
        "     ❄  ❄  ❄     ",
        "      (◕ω◕)      ",
        "      * * *      ",
    ],
    WeatherCondition.HEAVY_SNOW: [
        "    ❄❄❄❄❄❄❄    ",
        "      (◕◡◕)      ",
        "     *******     ",
    ],
    WeatherCondition.THUNDERSTORM: [
        "     ⚡☁☁⚡      ",
        "      (◉_◉)      ",
        "       ⚡⚡       ",
    ],
    WeatherCondition.UNKNOWN: [
        "       ~?~       ",
        "      (◕_◕)      ",
        "       ~~~       ",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# STORMY FACES — legacy, kept for random variety
# ═══════════════════════════════════════════════════════════════════════════════

STORMY_FACES = {
    "happy": [
        "      (◠‿◠)      ",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# WEATHER SCENES — larger ASCII art for the animation area
# ═══════════════════════════════════════════════════════════════════════════════

WEATHER_SCENES = {
    WeatherCondition.CLEAR: [
        "        \\   |   /        ",
        "          .-'-.          ",
        "      ─  (     )  ─      ",
        "          `-.-'          ",
        "        /   |   \\        ",
        "                         ",
    ],
    WeatherCondition.RAIN: [
        "        ___               ",
        "      .(   ).             ",
        "     (___(____)           ",
        "      ' ' ' ' '           ",
        "     ' ' ' ' ' '          ",
        "      ' ' ' ' '           ",
    ],
    WeatherCondition.HEAVY_RAIN: [
        "        ___               ",
        "      .(   ).             ",
        "     (___(____)           ",
        "     | | | | | |          ",
        "     | | | | | | |        ",
        "     | | | | | |          ",
    ],
    WeatherCondition.THUNDERSTORM: [
        "        ___               ",
        "      .(   ).             ",
        "     (___(____)           ",
        "      /  | | \\           ",
        "        / \\              ",
        "       /   \\             ",
    ],
    WeatherCondition.SNOW: [
        "        ___               ",
        "      .(   ).             ",
        "     (___(____)           ",
        "      * * * * *           ",
        "     * * * * * *          ",
        "      * * * * *           ",
    ],
    WeatherCondition.FOG: [
        "  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋         ",
        " ░░▒░░░▒░░░░▒░░░░         ",
        "  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋         ",
        " ░░░░▒░░░░▒░░░▒░░         ",
        "  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋         ",
        " ░▒░░░░░▒░░░░▒░░░         ",
    ],
    WeatherCondition.PARTLY_CLOUDY: [
        "     \\  |  /    ___       ",
        "       .-'    .(   ).     ",
        "    ─ (    ) (___(____)   ",
        "       `-'               ",
        "     /  |  \\              ",
        "                          ",
    ],
    WeatherCondition.CLOUDY: [
        "      ☁     ☁             ",
        "        ___               ",
        "      .(   ).    ☁        ",
        "     (___(____)           ",
        "   ☁          ☁           ",
        "      ☁    ☁              ",
    ],
}

# Fill in missing conditions with cloudy fallback
for _cond in WeatherCondition:
    if _cond not in WEATHER_SCENES:
        WEATHER_SCENES[_cond] = WEATHER_SCENES.get(WeatherCondition.CLOUDY)
