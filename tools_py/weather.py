import requests
from typing import Dict, Any, Annotated


# ========================
# Core API helpers
# ========================

def _get_coordinates(city: str) -> Dict[str, Any]:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}

    res = requests.get(url, params=params)
    data = res.json()

    if "results" not in data:
        return {}

    r = data["results"][0]
    return {
        "name": r["name"],
        "lat": r["latitude"],
        "lon": r["longitude"],
        "country": r.get("country", "")
    }


def _get_weather_raw(lat: float, lon: float, days: int = 7) -> Dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "sunrise",
            "sunset",
            "windspeed_10m_max"
        ],
        "hourly": [
            "precipitation",
            "windspeed_10m"
        ],
        "forecast_days": days,
        "timezone": "auto"
    }

    return requests.get(url, params=params).json()


# ========================
# Formatting helpers
# ========================

def _format_current(data: Dict[str, Any]) -> str:
    cw = data.get("current_weather", {})

    return (
        f"Current temperature: {cw.get('temperature')}°C\n"
        f"Wind speed: {cw.get('windspeed')} km/h\n"
        f"Wind direction: {cw.get('winddirection')}°"
    )


def _format_today(data: Dict[str, Any]) -> str:
    daily = data.get("daily", {})

    return (
        f"Today:\n"
        f"Max temp: {daily['temperature_2m_max'][0]}°C\n"
        f"Min temp: {daily['temperature_2m_min'][0]}°C\n"
        f"Rain: {daily['precipitation_sum'][0]} mm\n"
        f"Wind max: {daily['windspeed_10m_max'][0]} km/h\n"
        f"Sunrise: {daily['sunrise'][0]}\n"
        f"Sunset: {daily['sunset'][0]}"
    )


def _format_forecast(data: Dict[str, Any], days: int) -> str:
    daily = data.get("daily", {})

    out = "Forecast:\n"
    for i in range(days):
        out += (
            f"Day {i+1}: "
            f"{daily['temperature_2m_min'][i]}–{daily['temperature_2m_max'][i]}°C, "
            f"Rain: {daily['precipitation_sum'][i]} mm\n"
        )

    return out.strip()


# ========================
# LLM Tools
# ========================

def get_weather_now(city: Annotated[str,"The city you want the data for"]) -> str:
    """Get current weather (temperature, wind) for a city."""
    loc = _get_coordinates(city)
    if not loc:
        return "Location not found."

    data = _get_weather_raw(loc["lat"], loc["lon"], 1)

    return f"{loc['name']} ({loc['country']}):\n" + _format_current(data)


def get_weather_today(city: Annotated[str,"The city you want the data for"]) -> str:
    """Get today's weather including temperature, rain, sunrise, sunset."""
    loc = _get_coordinates(city)
    if not loc:
        return "Location not found."

    data = _get_weather_raw(loc["lat"], loc["lon"], 1)

    return f"{loc['name']}:\n" + _format_today(data)


def get_weather_forecast(city: Annotated[str,"The city you want the data for"], days: Annotated[int,"The number of days to return a forecast for"] = 7) -> str:
    """Get multi-day forecast (temperature, rain)."""
    days = max(1, min(days, 14))

    loc = _get_coordinates(city)
    if not loc:
        return "Location not found."

    data = _get_weather_raw(loc["lat"], loc["lon"], days)

    return f"{loc['name']}:\n" + _format_forecast(data, days)


def get_weather_full_report(city: Annotated[str,"The city you want the data for"], days: Annotated[int,"The number of days to return a forecast for"] = 7) -> str:
    """
    Full weather report combining:
    - current weather
    - today details (sunrise/sunset, rain, wind)
    - multi-day forecast
    """
    days = max(1, min(days, 14))

    loc = _get_coordinates(city)
    if not loc:
        return "Location not found."

    data = _get_weather_raw(loc["lat"], loc["lon"], days)

    return (
        f"Weather report for {loc['name']} ({loc['country']}):\n\n"
        + _format_current(data) + "\n\n"
        + _format_today(data) + "\n\n"
        + _format_forecast(data, days)
    )