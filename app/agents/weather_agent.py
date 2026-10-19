from app.agents.base import BaseAgent
from app.tools.weather_tools import get_current_weather

class WeatherAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Weather Agent. Your role is to analyze raw weather data "
            "for the destination and provide a structured, friendly summary and specific travel advice "
            "(suitability of travel, clothes to pack, activity planning recommendations)."
        )
        super().__init__(name="weather", system_prompt=system_prompt)
    def run(self, destination: str, dates: str = None) -> str:
        input_data = {"destination": destination, "dates": dates}
        with self.trace_agent(input_data) as tc:
            try:
                weather_data = get_current_weather.invoke({"city": destination})
                if "Error" in weather_data:
                    tc.set_error(weather_data)
                    return weather_data
            except Exception as e:
                error_msg = f"Could not retrieve weather details. Error: {str(e)}"
                tc.set_error(error_msg)
                return error_msg

            prompt = (
                f"Please summarize this weather data and provide travel recommendations for {destination}.\n"
                f"Dates: {dates if dates else 'Not specified'}\n"
                f"Weather Data:\n{weather_data}"
            )
            res = self.generate_response(prompt)
            tc.set_output(res)
            return res
