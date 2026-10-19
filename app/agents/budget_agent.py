from app.agents.base import BaseAgent
from app.tools.travel_tools import estimate_budget

class BudgetAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Budget Agent. Your role is to present a clean, structured cost breakdown "
            "for a trip. Use programmatic calculator outputs, detail individual categories (stay, food, travel, activities, "
            "emergency buffer), and offer useful advice on how to save money while staying safe and comfortable."
        )
        super().__init__(name="budget", system_prompt=system_prompt)

    def run(self, source: str, destination: str, days: int, people: int, travel_style: str) -> str:
        input_data = {
            "source": source,
            "destination": destination,
            "days": days,
            "people": people,
            "travel_style": travel_style
        }
        with self.trace_agent(input_data) as tc:
            try:
                # Safely invoke the programmatic estimate_budget tool
                raw_budget = estimate_budget.invoke({
                    "source_city": source,
                    "destination": destination,
                    "days": int(days),
                    "people": int(people),
                    "travel_style": travel_style
                })
                if "Error" in raw_budget:
                    tc.set_error(raw_budget)
            except Exception as e:
                raw_budget = f"Could not programmatically compute budget. Details: {str(e)}"
                tc.set_error(raw_budget)
                return raw_budget

            prompt = (
                f"Please format and present the budget breakdown for a trip to {destination} from {source}.\n"
                f"Details: {days} days, {people} people, Style: {travel_style}.\n"
                f"Programmatic Calculation:\n{raw_budget}"
            )
            res = self.generate_response(prompt)
            tc.set_output(res)
            return res

