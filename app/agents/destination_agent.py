from app.agents.base import BaseAgent
from app.tools.web_tools import search_places

class DestinationAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Destination Agent. Your job is to research tourist places, attractions, "
            "timings, entry fees, and key things to do. Provide a ranked list of recommended places with clear, "
            "practical descriptions. Do not fake data."
        )
        super().__init__(name="destination", system_prompt=system_prompt)

    def run(self, destination: str, interests: str = None, days: int = 3) -> str:
        input_data = {"destination": destination, "interests": interests, "days": days}
        with self.trace_agent(input_data) as tc:
            try:
                places_data = search_places.invoke({"location": destination})
                if "Error" in places_data:
                    tc.set_error(places_data)
            except Exception as e:
                places_data = f"Could not retrieve tourist spots. Error: {str(e)}"
                tc.set_error(places_data)
                return places_data

            prompt = (
                f"Please compile a ranked list of places to visit and activities in {destination}.\n"
                f"Duration: {days} days\n"
                f"Interests: {interests if interests else 'General sightseeing'}\n"
                f"Search Results:\n{places_data}"
            )
            res = self.generate_response(prompt)
            tc.set_output(res)
            return res

