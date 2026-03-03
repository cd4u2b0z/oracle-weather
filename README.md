<!-- Original work by Dr. Baklava • github.com/cd4u2b0z • 2026 -->
<!-- 4472 426b 6c76 -->

# 󰖐 Oracle Weather

**Stormy - Weather Oracle of the Terminal**

A terminal weather dashboard with physics-simulated particles, atmospheric modeling, 25 collectible ASCII creatures, a noir/wasteland/prophet AI personality engine, and 151 lines of hand-written dialogue. Built with Python and asciimatics.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Version](https://img.shields.io/badge/Version-3.0.0-blue?style=flat)
![Tests](https://github.com/cd4u2b0z/oracle-weather/actions/workflows/test.yml/badge.svg)

---

![Demo](assets/demo.gif)

## 󰓎 Features

### Core
| Feature | Description |
|---------|-------------|
| **Live Weather** | Dual API: OpenWeatherMap (primary) + OpenMeteo (fallback) |
| **Physics Particles** | Newtonian rain, snow, fog with drag, buoyancy, and wind forces |
| **Personality Engine** | "Stormy" — mood state machine with 151 weather comments across 6 voices |
| **Creature Bestiary** | 25 ASCII creatures spawn by weather + time, persistent sighting log |
| **Sparkline History** | SQLite-backed 24h temperature, humidity, and wind trends in sidebar |
| **Smooth Transitions** | Smoothstep crossfade when weather changes on refresh |
| **20 Achievements** | Persistent progress tracking with Nerd Font glyphs |
| **Location Search** | Search any city worldwide, instant weather swap |
| **7-Day Forecast** | Hourly breakdown with condition icons |
| **Special Effects** | Aurora, rainbow, heat shimmer, frost crystals |

### Weather Types
- 󰖗 Rain (drizzle, moderate, heavy, freezing)
- 󰖘 Snow (light, heavy, blizzard)
- 󰖓 Thunderstorms (fractal branching lightning)
- 󰖑 Fog and mist (Perlin noise layers)
- 󰖐 Clouds (partly cloudy, overcast)
- 󰖙 Clear sky (day sparkles, night stars)

### Stormy's Voices
Noir detective, Fallout wasteland survivor, Elder Scrolls prophet, jazz crooner, Monty Python absurdist, and physics meta-commentary. 151 weather-specific lines, 50 random quips, 26 time-of-day greetings, temperature commentary.

### Engine Modules
| Module | Description |
|--------|-------------|
| 󰂓 **Physics** | Gravity, drag, wind, buoyancy. Euler/Verlet/RK4 integration |
| 󱗆 **Atmosphere** | Barometric formula, Pasquill-Gifford stability, wind chill, heat index |
| 󰘨 **Noise** | Perlin, Simplex, Fractal noise + Domain Warping for organic clouds |
| 󰔊 **Personality** | 8-mood state machine, memory with decay, repetition avoidance |
| 󱕍 **Rendering** | Frame budget, adaptive quality, layer-ordered render queue |

---

## 󰑣 Quick Start

### Demo Mode (No API Key)
```bash
git clone https://github.com/cd4u2b0z/oracle-weather.git
cd oracle-weather && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python weather_dashboard.py --demo
```

Try specific scenarios:
```bash
python weather_dashboard.py --demo --scenario thunderstorm
python weather_dashboard.py --demo --scenario snow
python weather_dashboard.py --demo --scenario fog
```

### Full Install
```bash
git clone https://github.com/cd4u2b0z/oracle-weather.git
cd oracle-weather && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create `config.py`:
```python
OPENWEATHERMAP_API_KEY = "your_key_here"      # free at openweathermap.org/api
OPENWEATHERMAP_CITY_ID = "4597040"
LATITUDE = 32.4840
LONGITUDE = -80.1756
TIMEZONE = "America/New_York"
LOCATION_NAME = "Summerville, SC"
CACHE_FILE = "/tmp/oracle_weather_cache.json"
CACHE_MAX_AGE = 300
```

Run:
```bash
python weather_dashboard.py
```

---

## 󰌌 Keyboard Controls

| Key | Action |
|-----|--------|
| `Q` | Quit |
| `R` | Refresh weather (smooth crossfade) |
| `S` / `L` | Search location worldwide |
| `A` | Achievements hall of fame |
| `B` | Creature bestiary |
| `F` | Toggle forecast panel |
| `U` | Toggle metric / imperial |
| `?` | Help overlay |
| `Space` | Toggle Stormy's quips |

---

## 󰆥 Achievements

20 achievements tracked persistently in `~/.stormy_data.json`. Unlocked automatically based on weather conditions, time, temperature, streaks, and dedication.

| Achievement | Trigger |
|-------------|---------|
| 󰈙 **The Journey Begins** | First weather check |
| 󰖗 **Walks in Rain** | 10 rainy days |
| 󰖘 **Winter's Herald** | Check during snow |
| 󰖓 **Voice of Thunder** | Check during thunderstorm |
| 󰖔 **Walker of Night** | Check between midnight-5 AM |
| 󰖙 **Dawn Watcher** | Check between 5-6 AM |
| 󰈸 **Forged in Fire** | 100°F+ |
| 󰖎 **Heart of Winter** | Below 0°F |
| 󰖑 **Mist Walker** | Check during fog |
| 󰃭 **The Dedicated** | 7-day streak |
| 󰆥 **Century Club** | 100 total checks |
| 󰖌 **Humidity Hero** | Humidity > 90% |
| 󰖝 **Wind Warrior** | 30+ mph winds |
| 󰖙 **Goldilocks** | 72°F, clear, low humidity |
| 󰽥 **Midnight Oracle** | Check at stroke of midnight |
| 󰥔 **Marathon Watcher** | 10 checks in one day |
| 󰗇 **Lucky Seven** | Exactly 77°F |
| 󰎈 **Noir Night** | Rainy night |
| 󱂵 **Vault Dweller** | Severe weather, safely inside |
| 󰧗 **Weekend Warrior** | Every weekend for a month |

---

## 󰙅 Project Structure

```
oracle-weather/
├── weather_dashboard.py    # Main app (1830 lines)
├── config.py               # API key + location (gitignored)
├── pyproject.toml           # Package config, `stormy` CLI entry point
├── requirements.txt         # Python dependencies
├── pytest.ini               # Test configuration
│
├── data/                    # Dialogue + art data (extracted from monolith)
│   ├── dialogue.py          # 151 weather comments, 50 quips, greetings, achievements
│   └── art.py               # BIG_DIGITS, WEATHER_MASCOT, WEATHER_SCENES
│
├── screens/                 # Standalone UI screens
│   ├── achievements.py      # Hall of Fame
│   ├── search.py            # Location search
│   └── bestiary.py          # Creature collection
│
├── engine/                  # Modular engine
│   ├── physics/
│   │   ├── noise.py         # Perlin, Simplex, Fractal, DomainWarp
│   │   ├── particles.py     # Vector2, ParticleSystem, Forces
│   │   └── atmosphere.py    # AtmosphericModel, stability, wind chill
│   ├── rendering/
│   │   └── core.py          # RenderStats, FrameBudget, RenderQueue
│   ├── personality/
│   │   └── core.py          # PersonalityEngine, MoodStateMachine, Memory
│   ├── effects/
│   │   └── special_effects.py  # Aurora, rainbow, shimmer, frost
│   └── creatures/
│       └── core.py          # CreatureManager, 25 creatures
│
├── lib/                     # Shared utilities
│   ├── weather_api.py       # OWM + OpenMeteo client, WeatherCondition enum
│   ├── weather_extended.py  # Forecasts, alerts, WeatherDatabase (SQLite)
│   ├── sparkline.py         # Block-character sparkline renderer
│   ├── achievements.py      # Achievement system with tiers
│   ├── interactive.py       # Input handling, notifications
│   ├── dashboard_panels.py  # ForecastPanel, AlertBanner, etc.
│   ├── particles.py         # Legacy particle system (still used)
│   └── mock_weather.py      # Demo mode data
│
├── tests/
│   ├── test_engine.py       # Engine unit tests (37 tests)
│   └── test_extended.py     # Extended features tests (38 tests)
│
└── assets/
    └── demo.gif             # Terminal recording
```

---

## 󰈈 Engine Architecture

### Physics (`engine/physics/`)
```python
from engine.physics.noise import PerlinNoise, FractalNoise, DomainWarp

noise = PerlinNoise(seed=42)
value = noise.sample(x, y)  # Quintic interpolation

# Domain warping for swirling clouds
warp = DomainWarp(FractalNoise(), warp_strength=4.0)
organic = warp.sample(x, y)
```

```python
from engine.physics.particles import ParticleSystem, GravityForce, DragForce, WindForce

system = ParticleSystem(max_particles=1000)
system.add_force_generator(GravityForce(9.81))
system.add_force_generator(DragForce(0.47))
system.add_force_generator(WindForce(wind_x=2.0))
system.update(dt=0.016)
```

### Personality (`engine/personality/`)
```python
from engine.personality.core import PersonalityEngine

engine = PersonalityEngine()
engine.update(weather_type="storm")

# 151 weather comments across all conditions, no dead code
comment = engine.get_weather_comment("thunderstorm")
# "Thunder rolled like a landlord demanding rent. Lightning cracked the sky's alibi."

greeting = engine.get_greeting()
# "Night owl, are we? The moon sees you. It judges nothing. I judge slightly."

quip = engine.get_quip()
# "That lightning? Fractal branching via recursive pathfinding. Zeus was doing it wrong."
```

### Sparklines (`lib/sparkline.py`)
```python
from lib.sparkline import sparkline, sparkline_with_range

print(sparkline([55, 58, 62, 71, 78, 82, 79, 72, 65]))
# ▁▁▂▅▆█▇▅▃

print(sparkline_with_range([55, 82, 79, 65], "Temp", width=10))
# Temp ▁█▇▃ 55-82
```

---

## 󰙨 Testing

```bash
# Run all 75 tests
.venv/bin/python -m pytest tests/ -v

# Engine tests only
.venv/bin/python -m pytest tests/test_engine.py -v

# With coverage
.venv/bin/python -m pytest tests/ --cov=engine --cov-report=term-missing
```

---

## 󰋗 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| API key error | Create `config.py` with your key (see Quick Start) |
| Terminal too small | Resize to 120x40+ (80x24 minimum) |
| Colors missing | Use Kitty, Alacritty, or iTerm2 |
| Stale venv | `rm -rf .venv && python3 -m venv .venv && pip install -r requirements.txt` |

---

## 󱘖 Integration

### Quickshell / Waybar (Hyprland)
```qml
// Right-click weather widget to launch
Process {
    command: ["kitty", "-e", "bash", "-c",
        "cd ~/projects/oracle-weather && source .venv/bin/activate && python weather_dashboard.py"]
}
```

### Shell Alias
```bash
alias weather='cd ~/projects/oracle-weather && source .venv/bin/activate && python weather_dashboard.py'
```

---

## 󰋚 Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

**Latest: v3.0.0** - Unified personality, modular architecture, sparklines, bestiary, smooth transitions

---

## 󰈙 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 󱗗 Credits

- **asciimatics** - Terminal animation framework
- **OpenWeatherMap** - Primary weather API
- **OpenMeteo** - Fallback weather API

---

<div align="center">

**"The sky has wisdom to share..."** - Stormy

</div>

---

<sub>Original work by **Dr. Baklava** • [github.com/cd4u2b0z](https://github.com/cd4u2b0z) • 2026</sub>

<!-- ZHIuYmFrbGF2YQ== -->
