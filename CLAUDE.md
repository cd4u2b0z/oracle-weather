# Oracle Weather — Project Context

## What This Is
Terminal-based weather dashboard with physics-simulated particles, a noir/wasteland/prophet personality engine ("Stormy"), ASCII creature easter eggs, achievements, sparkline history, and real weather data from OpenWeatherMap + OpenMeteo.

**Entry point:** `python weather_dashboard.py` (alias: `weather_dashboard`)
**CLI entry:** `stormy` (via pyproject.toml)
**Venv:** `.venv/` in project root

## v3.0 Refactor — COMPLETE

All 6 tasks done:
1. Unified personality system — 151 weather comments + 50 quips all live (was dead code)
2. Broke the monolith — 2509 -> 1830 lines, extracted to data/ and screens/
3. pyproject.toml with `stormy` entry point, sys.path hack removed
4. Weather history sparklines — SQLite logging + block-char trends in sidebar
5. Smooth weather transitions — crossfade on refresh (smoothstep ramp)
6. Creature bestiary — persistent sighting log, bestiary screen (B key), spawn rates 4x

## Architecture

### Key Files
- `weather_dashboard.py` — Main app (1830 lines)
- `data/dialogue.py` — All 151 weather comments, 50 quips, greetings, temp comments, achievements
- `data/art.py` — BIG_DIGITS, WEATHER_MASCOT, STORMY_FACES, WEATHER_SCENES
- `screens/achievements.py` — Hall of Fame screen
- `screens/search.py` — Location search screen
- `screens/bestiary.py` — Creature collection screen
- `engine/personality/core.py` — PersonalityEngine, MoodStateMachine, DialogueBank, Memory
- `engine/creatures/core.py` — CreatureManager, 25 creatures, spawn rates ~0.0015-0.002
- `engine/physics/noise.py` — PerlinNoise, SimplexNoise, FractalNoise, DomainWarp
- `engine/physics/particles.py` — Vector2, Particle, ParticleSystem, forces
- `engine/physics/atmosphere.py` — AtmosphericModel, wind chill, heat index
- `engine/rendering/core.py` — RenderStats, FrameBudget, RenderQueue
- `engine/effects/special_effects.py` — Aurora, shimmer, rainbow, frost, etc.
- `lib/weather_api.py` — OWM + OpenMeteo client, WeatherCondition enum, WeatherData
- `lib/weather_extended.py` — Forecasts, alerts, astronomical, WeatherDatabase (SQLite)
- `lib/sparkline.py` — Block-character sparkline renderer
- `lib/achievements.py` — 30+ achievements with tiers
- `lib/interactive.py` — InputHandler, keybindings, screenshots
- `lib/dashboard_panels.py` — ForecastPanel, AlertBanner, etc.
- `lib/particles.py` — Legacy simple particles (still used for drifting)
- `lib/mock_weather.py` — Demo mode data

### Dashboard Structure (weather_dashboard.py)
- Local classes: PerlinNoise (wrapper), TurbulenceField, WindGustSystem, LightningBolt, PhysicsParticle, Theme, StormyPersonality (thin wrapper), WeatherDashboard
- StormyPersonality delegates to PersonalityEngine for all dialogue, keeps only persistence/achievements/creature sightings
- `transition_to()` method for smooth weather crossfades on refresh
- Two particle systems: legacy `self.particles` for drifting, `self.physics_particles` for precipitation

### Keyboard Shortcuts
Q=quit, R=refresh, S/L=search, A=achievements, B=bestiary, F=forecast, U=units, ?=help, Space=quips

### Persistence
- `~/.stormy_data.json` — achievements, creature sightings, check_count, streak
- `/tmp/oracle_weather_cache.json` — weather cache (5 min TTL)
- `~/.stormy_weather.db` — SQLite history (sparkline source)

## Config
- `config.py` — GITIGNORED, local only, has API key
- Imports: OPENWEATHERMAP_API_KEY, OPENWEATHERMAP_CITY_ID, LATITUDE, LONGITUDE, TIMEZONE, LOCATION_NAME, CACHE_FILE, CACHE_MAX_AGE

## Tests
- `tests/test_engine.py` — Engine unit tests
- `tests/test_extended.py` — Extended features tests
- Run: `cd ~/projects/oracle-weather && .venv/bin/python -m pytest tests/ -v`
- 75 tests, all passing
