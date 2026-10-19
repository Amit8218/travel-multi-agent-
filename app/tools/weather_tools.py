import requests
from langchain.tools import tool
from app.config import OPENWEATHER_API_KEY

@tool
def get_current_weather(city: str) -> str:
    """Get the current weather for a city or location name. Use this tool when the user asks about weather, temperature, rain, humidity, wind, climate right now, or current weather conditions."""
    import time
    import logging
    from app.tracing import create_span, end_span
    
    logger = logging.getLogger("AI-Travel-Guide-Tools")
    
    if not OPENWEATHER_API_KEY:
        return "Error: OPENWEATHER_API_KEY is not configured. Please set it in your environment/.env file."
    
    if not city or not isinstance(city, str):
        return "Error: City name must be a valid string."
        
    city_clean = city.strip("\"'[]{} ")
    logger.info(f"Tool called: OpenWeather search for city: '{city_clean}'")
    start_time = time.time()
    
    span = create_span(
        name="openweather_api_call",
        input={"city": city_clean}
    )
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_clean,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        exec_time = time.time() - start_time
        
        if response.status_code == 401:
            err_msg = "Error: Invalid OpenWeather API Key."
            logger.warning(f"Tool failed: {err_msg}")
            if span:
                span[1].update(
                    level="ERROR",
                    status_message=err_msg,
                    metadata={"error": "unauthorized", "execution_time_seconds": exec_time}
                )
                end_span(span, output=err_msg)
            return err_msg
        elif response.status_code == 404:
            err_msg = f"Error: City '{city_clean}' not found. Please verify the city name."
            logger.warning(f"Tool failed: {err_msg}")
            if span:
                span[1].update(
                    level="ERROR",
                    status_message=err_msg,
                    metadata={"error": "not_found", "execution_time_seconds": exec_time}
                )
                end_span(span, output=err_msg)
            return err_msg
            
        response.raise_for_status()
        data = response.json()
        
        city_name = data.get("name", city_clean)
        country = data.get("sys", {}).get("country", "Unknown")
        main_data = data.get("main", {})
        temp = main_data.get("temp")
        feels_like = main_data.get("feels_like")
        humidity = main_data.get("humidity")
        wind_speed = data.get("wind", {}).get("speed")
        
        weather_list = data.get("weather", [])
        condition = "Unknown"
        summary = "No description available"
        if weather_list:
            condition = weather_list[0].get("main", "Unknown")
            summary = weather_list[0].get("description", "No description")
            
        output = (
            f"Weather details for {city_name}, {country}:\n"
            f"- Temperature: {temp}°C\n"
            f"- Feels Like: {feels_like}°C\n"
            f"- Humidity: {humidity}%\n"
            f"- Wind Speed: {wind_speed} m/s\n"
            f"- Condition: {condition}\n"
            f"- Short Summary: {summary.capitalize()}"
        )
        
        if span:
            span[1].update(
                metadata={
                    "city": city_clean,
                    "temperature": temp,
                    "condition": condition,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "execution_time_seconds": exec_time
                }
            )
            end_span(span, output=output)
            
        return output
        
    except requests.exceptions.Timeout:
        exec_time = time.time() - start_time
        err_msg = "Error: Weather API request timed out. Please try again later."
        logger.warning(f"Tool failed: {err_msg}")
        if span:
            span[1].update(
                level="ERROR",
                status_message=err_msg,
                metadata={"error": "timeout", "execution_time_seconds": exec_time}
            )
            end_span(span, output=err_msg)
        return err_msg
    except requests.exceptions.RequestException as e:
        exec_time = time.time() - start_time
        err_msg = f"Error: Failed to fetch weather data. Details: {str(e)}"
        logger.warning(f"Tool failed: {err_msg}")
        if span:
            span[1].update(
                level="ERROR",
                status_message=err_msg,
                metadata={"error": str(e), "execution_time_seconds": exec_time}
            )
            end_span(span, output=err_msg)
        return err_msg
    except Exception as e:
        exec_time = time.time() - start_time
        err_msg = f"Error: An unexpected error occurred while retrieving weather. Details: {str(e)}"
        logger.warning(f"Tool failed: {err_msg}")
        if span:
            span[1].update(
                level="ERROR",
                status_message=err_msg,
                metadata={"error": str(e), "execution_time_seconds": exec_time}
            )
            end_span(span, output=err_msg)
        return err_msg
