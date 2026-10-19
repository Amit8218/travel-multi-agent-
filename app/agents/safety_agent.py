from app.agents.base import BaseAgent
from app.tools.web_tools import search_safety_updates

class SafetyAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Safety Agent. Your role is to research current travel advisories, safety "
            "notices, weather warnings, and local rules/laws for the destination. Compile clear safety tips "
            "and create a detailed, destination-appropriate packing checklist for the travelers."
        )
        super().__init__(name="safety", system_prompt=system_prompt)

    def run(self, destination: str) -> str:
        input_data = {"destination": destination}
        with self.trace_agent(input_data) as tc:
            try:
                safety_data = search_safety_updates.invoke({"location": destination})
                if "Error" in safety_data:
                    tc.set_error(safety_data)
            except Exception as e:
                safety_data = f"Could not retrieve live safety details. Error: {str(e)}"
                tc.set_error(safety_data)
                return safety_data

            prompt = (
                f"Provide safety notes, travel restrictions, general safety tips, and a packing checklist for {destination}.\n"
                f"Search Results:\n{safety_data}"
            )
            res = self.generate_response(prompt)
            tc.set_output(res)
            return res

