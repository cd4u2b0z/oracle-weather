# Changelog

All notable changes to Oracle Weather will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-03-03

### Added
- **Modular Data Layer** — `data/dialogue.py` (151 weather comments, 50 quips, 26 greetings, temp comments, achievements) and `data/art.py` (BIG_DIGITS, WEATHER_MASCOT, WEATHER_SCENES) extracted from the monolith
- **Standalone Screen Modules** — `screens/achievements.py`, `screens/search.py`, `screens/bestiary.py` extracted from weather_dashboard.py
- **Creature Bestiary** — Persistent sighting log in `~/.stormy_data.json`, dedicated bestiary screen (`B` key), 25 ASCII creatures across 11 weather categories
- **Sparkline History** — SQLite-backed 24h temperature, humidity, and wind trends rendered as block-character sparklines in the sidebar (`lib/sparkline.py`)
- **Smooth Weather Transitions** — Smoothstep crossfade on refresh and auto-refresh (60-frame ramp, ~2s at 30fps)
- **pyproject.toml** — Package config with `stormy` CLI entry point, proper setuptools packaging
- **Forecast toggle** — `F` key to show/hide 7-day forecast panel
- **Unit toggle** — `U` key to swap metric/imperial
- **`get_trend_data()`** — New method on `WeatherDatabase` for sparkline data extraction

### Changed
- **Unified Personality System** — All 151 weather comments now live (previously dead code behind `_use_engine=True` flag). `PersonalityEngine` uses the full dialogue pool from `data/dialogue.py`
- **StormyPersonality gutted** — From ~600 lines to ~100 line thin wrapper; delegates all dialogue to engine
- **DialogueBank expanded** — Now includes `get_greeting()`, `get_temp_comment()`, `get_weather_comment_by_condition()`, references full 151-comment pool
- **Creature spawn rates 4x** — 0.0004 → 0.0015, 0.0005 → 0.0018, 0.0006 → 0.002
- **Dashboard reduced** — `weather_dashboard.py` from 2509 → 1830 lines (-27%)
- **Repetition avoidance** — `_max_recent` bumped from 10 to 15
- **Python version** — Now requires Python 3.10+

### Removed
- `main.py`, `weather_live_pro.py`, `config_manager.py`, `config.example.yaml` — Dead files from pre-2.0 era
- `sys.path.insert` hack in `lib/weather_api.py`
- Dead `config_manager` imports and test classes from `tests/test_extended.py`
- Inline ASCII art data (~170 lines) and inline screen functions (~150 lines) from dashboard

### Fixed
- `?` help overlay double-toggle bug — `handle_input()` and `dashboard_main()` both toggled `show_help`, canceling each other out
- Stale venv shebang after project path change

## [2.3.0] - 2026-01-16

### Added
- **󰈈 Demo Mode** - Try oracle-weather without an API key!
  - `--demo` flag runs with mock weather data
  - `--scenario` flag to choose weather type (thunderstorm, snow, rain, etc.)
  - 8 demo scenarios: clear, rain, thunderstorm, snow, fog, cloudy, heavy snow, drizzle
- **󱛘 GitHub Topics** - Added discoverability tags (weather, terminal, ascii-art, python, cli, tui, asciimatics)

### Changed
- Quick Start section now prominently features demo mode
- First-time users can experience Stormy instantly

## [2.2.1] - 2026-01-16

### Added
- **󰕹 Demo GIF** - Animated demo in README showing dashboard, help overlay, and Stormy quips
- **󰙨 GitHub Actions CI** - Automated testing on Python 3.10, 3.11, 3.12
- **󰗀 py.typed markers** - Full type hint support for IDEs and type checkers

### Changed
- README now shows Tests badge
- Windows note updated to "Linux/macOS recommended"

## [2.2.0] - 2026-01-16

### Added
- **󰎈 Noir Weather Oracle** - Complete personality system overhaul
  - 6 mood modes: noir, wasteland, prophet, crooner, absurdist, philosophical
  - Noir Detective style: Hard-boiled weather narration
  - Fallout/Wasteland: Vault-Tec approved observations
  - Elder Scrolls/Prophet: Mystical weather prophecies
  - Crooner: Jazz era musical references (Sinatra, Ink Spots, Mills Brothers)
  - Absurdist: Monty Python inspired weather commentary
- **󰔏 Temperature comments** - Unique observations for freezing, cold, cool, mild, warm, and hot
- **󰥔 Time-based greetings** - Period-appropriate greetings throughout the day
- **󰆥 15 new achievements** - Century club, noir night, vault dweller, and more
- **󰔊 40+ quips** - Philosophical observations across all personality styles

### Changed
- StormyPersonality class completely rewritten (~700 lines)
- Weather comments now vary by mood and include cultural references
- Achievement system expanded from 10 to 25 achievements

### Inspired By
- Carrot Weather (iOS) - Dark humor approach
- Fallout - Atomic age optimism meets doom
- Elder Scrolls/Morrowind - Mystical prophecy style
- Monty Python - British absurdism
- Jazz era (Sinatra, Ink Spots, Mills Brothers, Bing Crosby) - Musical references

## [2.1.1] - 2026-01-16

### Fixed
- **󱀝 Startup Performance** - Extended data now fetched in background thread
- **󰔟 Loading Animation** - Reduced delay from 1.2s to 0.4s
- **󰏗 Broken venv** - Recreated virtual environment after project rename

### Changed
- Extended weather data loads lazily after first frame renders
- Dashboard now usable immediately while forecast data loads in background

## [2.1.0] - 2026-01-16

### Added
- **󱗆 Creatures Module** - Extracted easter egg creature system to `engine/creatures/`
  - 11 weather categories with unique animated creatures
  - `CreatureManager` class with backwards-compatible `EasterEggManager` alias
  - Proper module structure with type hints and documentation
- **󰏗 Improved lib package** - Proper `__all__` exports and lazy loading
- **󰂓 ParticleSystem enhancements** - Added `clear()` and `__len__()` methods

### Changed
- Renamed project from `asciimatics-weather-toys` to `oracle-weather`
- Updated all package references and cache paths
- Replaced bare `except:` with `except Exception:` across all files
- Added comprehensive type hints to `lib/particles.py`
- Updated engine docstrings for accurate module listing

### Removed
- Empty `engine/weather/` module (was unused placeholder)

### Fixed
- Duplicate creature code in `weather_dashboard.py` (~658 lines removed)
- Dashboard reduced from 2870 to 2212 lines (-23%)

## [2.0.0] - 2026-01-16

### Added
- **󰒓 Professional Engine Architecture**
  - `engine/physics/` - Perlin noise, particle physics, atmospheric simulation
  - `engine/rendering/` - Performance-aware frame rendering with layer management
  - `engine/personality/` - AI personality system with mood states
  - `engine/effects/` - Special weather effects (aurora, rainbows, fog, heat shimmer)
  - `engine/creatures/` - Easter egg animated creatures for each weather type

- **󰐗 New Features**
  - 7-day forecast panel with condition icons
  - Weather alerts and warnings display
  - Location search with 'S' key
  - Sunrise/sunset display
  - Moon phase indicator
  - Dynamic theme adaptation (warm/cool based on temperature)
  - ASCII art weather icons

### Changed
- Complete architecture refactor from single file to modular engine
- Improved particle physics with realistic mass and buoyancy
- Enhanced performance monitoring with frame time tracking

## [1.0.0] - 2026-01-15

### Added
- Initial release
- Real-time weather display with asciimatics rendering
- Weather conditions: clear, cloudy, rain, snow, thunderstorm, fog
- Animated particle systems for precipitation
- Temperature display in F/C
- Wind speed and direction
- Humidity display
- Basic personality system with weather comments
- Keyboard controls (Q to quit, R to refresh)
