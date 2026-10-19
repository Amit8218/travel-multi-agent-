from app.agents.base import BaseAgent
from app.tools.web_tools import search_hotels

class HotelAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Hotel Agent. Your role is to suggest the best stay areas (neighborhoods) "
            "and general hotel suggestions in the destination city based on budget and travel style. "
            "Never fake hotel availability or live rates. Explicitly mention that prices/availability must "
            "be verified on booking platforms before reserving."
        )
        super().__init__(name="hotel", system_prompt=system_prompt)

    def run(self, destination: str, budget: str = None, travelers: int = 1, travel_style: str = "medium") -> str:
        input_data = {
            "destination": destination,
            "budget": budget,
            "travelers": travelers,
            "travel_style": travel_style
        }
        with self.trace_agent(input_data) as tc:
            try:
                hotels_data = search_hotels.invoke({
                    "city": destination,
                    "budget": budget,
                    "preference": travel_style
                })
                if "Error" in hotels_data:
                    tc.set_error(hotels_data)
            except Exception as e:
                hotels_data = f"Could not retrieve hotel suggestions. Error: {str(e)}"
                tc.set_error(hotels_data)
                return hotels_data

            prompt = (
                f"Suggest stay areas and accommodations in {destination}.\n"
                f"Travelers: {travelers}\n"
                f"Budget details: {budget if budget else 'Not specified'}\n"
                f"Travel Style: {travel_style}\n"
                f"Search Results:\n{hotels_data}"
            )
            res = self.generate_response(prompt)
            tc.set_output(res)
            return res

