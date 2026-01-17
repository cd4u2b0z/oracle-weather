"""
Mock weather data for --demo mode.
Allows running oracle-weather without an API key.
"""
import random
import time
from .weather_api import WeatherData, WeatherCondition

# Demo weather scenarios
DEMO_SCENARIOS = [
    {
        "name": "Sunny Day",
        "condition": WeatherCondition.CLEAR,
        "temp_f": 72,
        "humidity": 45,
        "wind_mph": 8,
        "description": "Clear sky",
        "clouds": 5,
    },
    {
        "name": "Rainy Afternoon",
        "condition": WeatherCondition.RAIN,
        "temp_f": 58,
        "humidity": 85,
        "wind_mph": 12,
        "description": "Moderate rain",
        "clouds": 90,
        "rain": 2.5,
    },
    {
        "name": "Thunderstorm",
        "condition": WeatherCondition.THUNDERSTORM,
        "temp_f": 68,
        "humidity": 92,
        "wind_mph": 25,
        "description": "Thunderstorm with heavy rain",
        "clouds": 100,
        "rain": 8.0,
    },
    {
        "name": "Snowy Evening",
        "condition": WeatherCondition.SNOW,
        "temp_f": 28,
        "humidity": 78,
        "wind_mph": 10,
        "description": "Light snow",
        "clouds": 95,
        "snow": 1.5,
    },
    {
        "name": "Foggy Morning",
        "condition": WeatherCondition.FOG,
        "temp_f": 52,
        "humidity": 98,
        "wind_mph": 3,
        "description": "Dense fog",
        "clouds": 100,
        "visibility": 200,
    },
    {
        "name": "Partly Cloudy",
        "condition": WeatherCondition.PARTLY_CLOUDY,
        "temp_f": 65,
        "humidity": 55,
        "wind_mph": 15,
        "description": "Scattered clouds",
        "clouds": 40,
    },
    {
        "name": "Heavy Snow",
        "condition": WeatherCondition.HEAVY_SNOW,
        "temp_f": 22,
        "humidity": 88,
        "wind_mph": 18,
        "description": "Heavy snowfall",
        "clouds": 100,
        "snow": 5.0,
    },
    {
        "name": "Drizzle",
        "condition": WeatherCondition.DRIZZLE,
        "temp_f": 55,
        "humidity": 80,
        "wind_mph": 6,
        "description": "Light drizzle",
        "clouds": 85,
        "rain": 0.5,
    },
]


def get_demo_weather(scenario: str = None) -> WeatherData:
    """
    Get mock weather data for demo mode.
    
    Args:
        scenario: Optional scenario name (e.g., "thunderstorm", "snow").
                  If None, picks a random scenario.
    
    Returns:
        WeatherData with mock values.
    """
    if scenario:
        # Find matching scenario (case-insensitive partial match)
        scenario_lower = scenario.lower()
        for s in DEMO_SCENARIOS:
            if scenario_lower in s["name"].lower() or scenario_lower in s["condition"].value:
                selected = s
                break
        else:
            selected = random.choice(DEMO_SCENARIOS)
    else:
        selected = random.choice(DEMO_SCENARIOS)
    
    temp_f = selected["temp_f"] + random.uniform(-3, 3)
    temp_c = (temp_f - 32) * 5 / 9
    
    return WeatherData(
        condition=selected["condition"],
        temperature_f=round(temp_f, 1),
        temperature_c=round(temp_c, 1),
        humidity=selected["humidity"] + random.randint(-5, 5),
        wind_speed_mph=selected["wind_mph"] + random.uniform(-2, 2),
        wind_direction=random.randint(0, 359),
        description=selected["description"],
        location="Demo City, Weatherland",
        timestamp=time.time(),
        clouds_percent=selected.get("clouds", 0),
        rain_intensity=selected.get("rain", 0.0),
        snow_intensity=selected.get("snow", 0.0),
        visibility=selected.get("visibility", 10000),
        pressure=random.randint(1005, 1025),
    )


def cycle_demo_weather() -> WeatherData:
    """
    Cycle through demo scenarios in order.
    Useful for showcasing all weather types.
    """
    if not hasattr(cycle_demo_weather, '_index'):
        cycle_demo_weather._index = 0
    
    selected = DEMO_SCENARIOS[cycle_demo_weather._index]
    cycle_demo_weather._index = (cycle_demo_weather._index + 1) % len(DEMO_SCENARIOS)
    
    temp_f = selected["temp_f"]
    temp_c = (temp_f - 32) * 5 / 9
    
    return WeatherData(
        condition=selected["condition"],
        temperature_f=temp_f,
        temperature_c=round(temp_c, 1),
        humidity=selected["humidity"],
        wind_speed_mph=selected["wind_mph"],
        wind_direction=random.randint(0, 359),
        description=selected["description"],
        location="Demo City, Weatherland",
        timestamp=time.time(),
        clouds_percent=selected.get("clouds", 0),
        rain_intensity=selected.get("rain", 0.0),
        snow_intensity=selected.get("snow", 0.0),
        visibility=selected.get("visibility", 10000),
        pressure=1013,
    )
