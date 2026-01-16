# Changelog

All notable changes to Oracle Weather will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-01-16

### Added
- **Creatures Module** - Extracted easter egg creature system to `engine/creatures/`
  - 11 weather categories with unique animated creatures
  - `CreatureManager` class with backwards-compatible `EasterEggManager` alias
  - Proper module structure with type hints and documentation
- **Improved lib package** - Proper `__all__` exports and lazy loading
- **ParticleSystem enhancements** - Added `clear()` and `__len__()` methods

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
- **Professional Engine Architecture**
  - `engine/physics/` - Perlin noise, particle physics, atmospheric simulation
  - `engine/rendering/` - Performance-aware frame rendering with layer management
  - `engine/personality/` - AI personality system with mood states
  - `engine/effects/` - Special weather effects (aurora, rainbows, fog, heat shimmer)
  - `engine/creatures/` - Easter egg creature appearances

- **New Feature Modules**
  - Achievement system with gamification
  - Interactive keyboard controls
  - Extended weather forecasts
  - Dashboard panel system
  - Special effects manager

- **Weather Effects**
  - Branching lightning with fractal paths
  - Realistic rain with splash effects
  - Layered snowfall with accumulation
  - Dynamic fog with density gradients
  - Aurora borealis for clear nights
  - Rainbow effects after rain

### Changed
- Complete rewrite of weather visualization engine
- Modular architecture for better maintainability
- Improved particle physics simulation
- Enhanced ASCII art weather scenes

## [1.0.0] - 2026-01-03

### Added
- Initial release
- Basic weather dashboard with ASCII animations
- OpenWeatherMap API integration
- OpenMeteo fallback API
- Waybar integration for click-to-launch
- Rain, snow, fog, and clear weather effects
- Day/night cycle visualization
