from app.agents.base import BaseAgent
from app.tools.web_tools import search_transport

class TransportAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Transport Agent. Your role is to determine transport routes between "
            "a source city and a destination city. Provide flight, train, bus, cab, and local transit options. "
            "Give approximate travel durations, estimated costs, and a final practical recommendation."
        )
        super().__init__(name="transport", system_prompt=system_prompt)

    def run(self, source: str, destination: str) -> str:
        input_data = {"source": source, "destination": destination}
        with self.trace_agent(input_data) as tc:
            try:
                transport_data = search_transport.invoke({"source": source, "destination": destination})
                if "Error" in transport_data:
                    tc.set_error(transport_data)
            except Exception as e:
                transport_data = f"Could not retrieve transport options. Error: {str(e)}"
                tc.set_error(transport_data)
                return transport_data

            prompt = (
                f"Explain how to travel from {source} to {destination}.\n"
                f"Identify routes, modes, durations, and give a recommendation.\n"
                f"Search Results:\n{transport_data}"
            )
            res = self.generate_response(prompt)
            tc.set_output(res)
            return res

