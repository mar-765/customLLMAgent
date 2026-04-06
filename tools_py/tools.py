from .weather import get_weather_forecast,get_weather_full_report,get_weather_now


from datetime import datetime

def get_current_datetime() -> str:
    """Get current local date and time."""
    
    now = datetime.now()

    return now.strftime(
        "Current date: %A, %d %B %Y\nCurrent time: %H:%M"
    )


tools = [get_weather_now,get_weather_forecast,get_weather_full_report,get_current_datetime]