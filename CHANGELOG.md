# Changelog

All notable changes to Oracle Weather will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
