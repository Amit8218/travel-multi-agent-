from app.agents.base import BaseAgent

class ItineraryAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Itinerary Agent. Your job is to create a highly structured, "
            "realistic, and engaging day-wise travel schedule. Avoid unrealistic timings. "
            "For each day, present:\n"
            "- Morning: Activity/sightseeing\n"
            "- Afternoon: Sightseeing/meal/rest\n"
            "- Evening: Relaxed walk/activity\n"
            "- Food suggestion: Specific dish or area to eat\n"
            "- Movement tip: How to travel within the city\n"
            "- Estimated cost: A rough estimate for that day's local activities."
        )
        super().__init__(name="itinerary", system_prompt=system_prompt)

    def run(self, destination: str, days: int, interests: str = None, travel_style: str = "medium", context: str = "") -> str:
        input_data = {
            "destination": destination,
            "days": days,
            "interests": interests,
            "travel_style": travel_style,
            "context": context
        }
        with self.trace_agent(input_data) as tc:
            try:
                prompt = (
                    f"Generate a detailed day-wise itinerary for a {days}-day trip to {destination}.\n"
                    f"Travel Style: {travel_style}\n"
                    f"Interests: {interests if interests else 'General sightseeing'}\n"
                    f"Surrounding Context (destination details, hotels, local food, weather):\n{context}\n\n"
                    f"Plan the schedule carefully, making sure it is pleasant and not overly rushed."
                )
                res = self.generate_response(prompt)
                tc.set_output(res)
                return res
            except Exception as e:
                error_msg = f"Failed to generate itinerary. Error: {str(e)}"
                tc.set_error(error_msg)
                return error_msg

