from app.agents.base import BaseAgent
from app.tools.web_tools import search_food_places

class FoodAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Food Agent. Your job is to suggest must-try local foods, vegetarian options, "
            "cafes, restaurants, street food hubs, and food streets in the destination. Help travelers experience "
            "the local culinary culture."
        )
        super().__init__(name="food", system_prompt=system_prompt)

    def run(self, destination: str, food_preference: str = None) -> str:
        input_data = {"destination": destination, "food_preference": food_preference}
        with self.trace_agent(input_data) as tc:
            try:
                food_data = search_food_places.invoke({"location": destination})
                if "Error" in food_data:
                    tc.set_error(food_data)
            except Exception as e:
                food_data = f"Could not retrieve food recommendations. Error: {str(e)}"
                tc.set_error(food_data)
                return food_data

            prompt = (
                f"Provide a comprehensive food guide for {destination}.\n"
                f"Food preference constraint: {food_preference if food_preference else 'None'}\n"
                f"Search Results:\n{food_data}"
            )
            res = self.generate_response(prompt)
            tc.set_output(res)
            return res

