<!-- Original work by Dr. Baklava • github.com/cd4u2b0z • 2026 -->
<!-- 4472 426b 6c76 -->

# 󰖐 Oracle Weather

**Stormy - Weather Oracle of the Terminal**

A professional-grade ASCII weather dashboard and animation system built with Python and asciimatics. Features live weather integration, physics-based particle simulation, atmospheric modeling, and an AI personality named Stormy.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Version](https://img.shields.io/badge/Version-2.1.1-blue?style=flat)

---

## 󰓎 Features

### Core Features
| Feature | Description |
|---------|-------------|
| **Live Weather** | Real-time weather data from OpenWeatherMap API |
| **Weather Dashboard** | Full terminal dashboard with sidebar stats + animation |
| **Multiple Weather Types** | Rain, snow, thunderstorms, fog, clouds, clear sky |
| **Easter Egg Creatures** | Rare visitors appear based on weather + time |
| **Personality Engine** | AI companion "Stormy" with mood states and dialogue |

### Weather Types
- 󰖗 Rain (light, moderate, heavy, drizzle)
- 󰖘 Snow (light, moderate, heavy, blizzard)
- 󰖓 Thunderstorms (with realistic lightning)
- 󰖑 Fog and mist
- 󰖐 Clouds (various densities)
- 󰖙 Clear sky (day and night variants)

### Engine Modules
| Module | Description |
|--------|-------------|
| 󰂓 **Physics Engine** | Newtonian mechanics with gravity, drag, and wind forces |
| 󱗆 **Atmospheric Model** | Barometric pressure, stability classification |
| 󰘨 **Procedural Noise** | Perlin, Simplex, Fractal noise + Domain Warping |
| 󰔊 **Personality Engine** | Mood state machine with weather-aware dialogue |
| 󱕍 **Render Stats** | FPS tracking, adaptive quality scaling |

### Planned Features (v2.1)
> These modules exist in `lib/` but are not yet fully integrated into the dashboard UI:
- 7-day forecast panel
- NWS weather alerts
- Astronomical data (sunrise/sunset, moon phases)
- UV index and air quality monitoring
- Achievement system

---

## 󰏖 Requirements

### System Requirements
- **OS**: Linux or macOS
- **Python**: 3.8+
- **Terminal**: Modern terminal emulator (Kitty recommended)
- **Display**: Minimum 80x24 terminal size (120x40 recommended)

### Dependencies
```
asciimatics>=1.14.0
requests>=2.28.0
pyyaml>=6.0
```

---

## 󰑣 Quick Start

### One-Line Install (Linux)
```bash
git clone https://github.com/cd4u2b0z/oracle-weather.git ~/oracle-weather
cd ~/oracle-weather && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python weather_dashboard.py
```

### macOS
```bash
git clone https://github.com/cd4u2b0z/oracle-weather.git ~/oracle-weather
cd ~/oracle-weather && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python weather_dashboard.py
```

---

## 󰏗 Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/cd4u2b0z/oracle-weather.git ~/oracle-weather
cd ~/oracle-weather
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows (not fully tested)
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your OpenWeatherMap API key
```

Or edit `config.py` directly:
```python
OPENWEATHERMAP_API_KEY = "your_api_key_here"
OPENWEATHERMAP_CITY_ID = "4597040"  # Your city ID
LATITUDE = 32.4840
LONGITUDE = -80.1756
```

Get a free API key at [openweathermap.org](https://openweathermap.org/api)

### Step 5: Run
```bash
python weather_dashboard.py
```

---

## 󰌌 Usage

### Commands
```bash
# Activate environment first
source .venv/bin/activate

# Main dashboard (recommended)
python weather_dashboard.py

# Fullscreen weather animation
python weather_live.py

# Pro version with enhanced effects
python weather_live_pro.py

# Demo/title screen
python main.py
```

### Keyboard Controls
| Key | Action |
|-----|--------|
| `Q` | Quit |
| `R` | Refresh weather data |
| `L` or `S` | Search any location worldwide |
| `A` | View achievements |
| `?` | Show help overlay |
| `Space` | Toggle Stormy's quips |

### Location Search
Press `S` or `L` to search for any city:
```
Examples:
  New York, NY
  London, UK
  Tokyo, Japan
  Paris, France
  Sydney, Australia
```

---

## 󰙅 Project Structure

```
oracle-weather/
├── config.py              # API keys and settings
├── config.yaml            # User configuration (create from example)
├── weather_dashboard.py   # Main dashboard with Stormy AI
├── weather_live.py        # Fullscreen weather animation
├── weather_live_pro.py    # Enhanced pro version
├── main.py                # Demo title screen
│
├── engine/                # Professional-grade modular engine
│   ├── physics/
│   │   ├── noise.py       # Perlin, Simplex, Fractal, DomainWarp
│   │   ├── particles.py   # Vector2, ParticleSystem, Forces
│   │   └── atmosphere.py  # AtmosphericModel, stability, wind chill
│   ├── rendering/
│   │   └── core.py        # RenderStats, FrameBudget, RenderQueue
│   ├── personality/
│   │   └── core.py        # PersonalityEngine, MoodStateMachine
│   ├── effects/
│   │   └── special_effects.py  # Aurora, rainbow, heat shimmer
│   ├── creatures/         # Easter egg creature system
│   └── weather/           # Weather processing
│
├── lib/                   # Shared utilities
│   ├── weather_api.py     # OpenWeatherMap + OpenMeteo client
│   ├── weather_extended.py # Forecasts, alerts, astronomical (WIP)
│   ├── achievements.py    # Achievement system (WIP)
│   ├── interactive.py     # Input handling, notifications
│   ├── dashboard_panels.py # UI panel components (WIP)
│   └── particles.py       # Legacy particle physics
│
└── tests/
    ├── test_engine.py     # Engine unit tests
    └── test_extended.py   # Extended features tests
```

---

## 󰒓 Configuration

### config.yaml (Recommended)
```yaml
# API Configuration
api:
  openweathermap_key: "your_api_key"
  
# Location
location:
  city_id: "4597040"
  latitude: 32.4840
  longitude: -80.1756
  
# Display Settings
display:
  units: imperial  # or metric
  theme: default
```

### Environment Variables (Alternative)
```bash
export OPENWEATHERMAP_API_KEY="your_api_key"
export WEATHER_CITY_ID="4597040"
```

---

## 󰈈 Engine Architecture

### Physics Engine (`engine/physics/`)

#### Noise Generation
```python
from engine.physics.noise import PerlinNoise, SimplexNoise, FractalNoise, DomainWarp

noise = PerlinNoise(seed=42)
value = noise.sample(x, y)  # Ken Perlin's quintic interpolation

# Domain warping for swirling cloud effects
warp = DomainWarp(FractalNoise(), warp_strength=4.0)
organic_value = warp.sample(x, y)
```

#### Particle Physics
```python
from engine.physics.particles import ParticleSystem, GravityForce, DragForce, WindForce

system = ParticleSystem(max_particles=1000)
system.add_force_generator(GravityForce(9.81))
system.add_force_generator(DragForce(0.47))
system.add_force_generator(WindForce(wind_x=2.0, wind_y=0.0))
system.update(dt=0.016)  # Euler/Verlet/RK4 integration
```

#### Atmospheric Model
```python
from engine.physics.atmosphere import AtmosphericModel, AtmosphericState

state = AtmosphericState(
    temperature_c=15.0,
    pressure_hpa=1013.25,
    humidity_percent=65.0,
    wind_speed_ms=5.0
)
model = AtmosphericModel(state)

# Barometric formula: P(h) = P0 x exp(-Mgh/RT)
pressure_at_1km = model.pressure_at_altitude(1000)

# Pasquill-Gifford stability classification
stability = model.classify_stability()  # A (very unstable) to F (stable)
```

### Personality Engine (`engine/personality/`)
```python
from engine.personality.core import PersonalityEngine, Mood

engine = PersonalityEngine()

# Mood state machine transitions based on weather
engine.update(weather_type="storm")
print(engine.current_mood)  # Mood.PHILOSOPHICAL, DEADPAN, SARDONIC, etc.

# Weather-aware dialogue
comment = engine.get_weather_comment("thunderstorm")
# "The storm rages. There is wisdom in chaos. Also danger. Mostly danger."
```

---

## 󰙨 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run engine tests only
python -m pytest tests/test_engine.py -v

# Quick verification
python -c "from engine import *; print('All engines OK')"

# Test with coverage
python -m pytest tests/ --cov=engine --cov-report=term-missing
```

---

## 󰋗 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: asciimatics` | Run `pip install -r requirements.txt` |
| API key error | Check `config.py` or `config.yaml` for valid key |
| Terminal too small | Resize to at least 80x24 |
| Colors not showing | Use a modern terminal (Kitty, Alacritty, iTerm2) |
| Weather not updating | Check internet connection, API rate limits |

### Quick Fixes
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Clear weather cache
rm -f ~/.cache/oracle-weather/*

# Test API connection
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"
```

---


## 󰋚 Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

**Latest: v2.1.1** - Performance improvements and bug fixes

---

## 󱘖 Integration

### Waybar (Hyprland/Sway)
Add to your Waybar weather module:
```json
"custom/weather": {
    "on-click-right": "kitty -e bash -c 'cd ~/oracle-weather && source .venv/bin/activate && python weather_dashboard.py'"
}
```

### Shell Aliases
Add to `~/.zshrc` or `~/.bashrc`:
```bash
alias weather='cd ~/oracle-weather && source .venv/bin/activate && python weather_dashboard.py'
alias weather_live='cd ~/oracle-weather && source .venv/bin/activate && python weather_live.py'
```

---

## 󰈙 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 󱗗 Credits

- **asciimatics** - Terminal animation framework
- **OpenWeatherMap** - Weather data API
- **OpenMeteo** - Backup weather API

---

<div align="center">

**"The sky has wisdom to share..."** - Stormy

</div>

---

<sub>Original work by **Dr. Baklava** • [github.com/cd4u2b0z](https://github.com/cd4u2b0z) • 2026</sub>

<!-- ZHIuYmFrbGF2YQ== -->
