import concurrent.futures
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END

from app.agents.supervisor_agent import SupervisorAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.destination_agent import DestinationAgent
from app.agents.transport_agent import TransportAgent
from app.agents.hotel_agent import HotelAgent
from app.agents.food_agent import FoodAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.itinerary_agent import ItineraryAgent
from app.agents.safety_agent import SafetyAgent
from app.agents.booking_link_agent import BookingLinkAgent

# Initialize agents
supervisor_agent = SupervisorAgent()
weather_agent = WeatherAgent()
destination_agent = DestinationAgent()
transport_agent = TransportAgent()
hotel_agent = HotelAgent()
food_agent = FoodAgent()
budget_agent = BudgetAgent()
itinerary_agent = ItineraryAgent()
safety_agent = SafetyAgent()
booking_link_agent = BookingLinkAgent()

class AgentState(TypedDict):
    user_message: Optional[str]
    source: Optional[str]
    destination: Optional[str]
    days: Optional[int]
    people: Optional[int]
    budget: Optional[str]
    interests: Optional[str]
    travel_style: Optional[str]
    food_preference: Optional[str]
    travel_date: Optional[str]
    
    # Routing control
    agents_to_run: List[str]
    agents_used: List[str]
    follow_up_question: Optional[str]
    
    # Results
    weather_result: Optional[str]
    destination_result: Optional[str]
    transport_result: Optional[str]
    hotel_result: Optional[str]
    food_result: Optional[str]
    budget_result: Optional[str]
    itinerary_result: Optional[str]
    safety_result: Optional[str]
    booking_result: Optional[str]
    final_answer: Optional[str]

# Nodes
def supervisor_analyze_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes the query, extracts variables, and plans routing.
    """
    from app.tracing import create_span, end_span
    node_span = create_span(name="supervisor_analyze", input=dict(state))
    
    user_msg = state.get("user_message")
    
    # If the request already has structured destination parameters,
    # skip analysis and enable all agents for a full plan.
    if state.get("destination"):
        updates = {
            "agents_to_run": ["destination", "weather", "transport", "hotel", "food", "budget", "itinerary", "booking_link", "safety"],
            "agents_used": [],
            "follow_up_question": ""
        }
        if node_span:
            end_span(node_span, output=updates)
        return updates
        
    if not user_msg:
        updates = {"final_answer": "No message provided."}
        if node_span:
            end_span(node_span, output=updates)
        return updates
        
    # Analyze freeform message using supervisor LLM
    analysis = supervisor_agent.analyze_query(user_msg, endpoint=state.get("endpoint", "/chat"))
    
    # Extract parameters
    params = analysis.get("extracted_params", {})
    updates = {}
    
    for k in ["source", "destination", "days", "people", "budget", "interests", "travel_style", "food_preference"]:
        if params.get(k) is not None:
            updates[k] = params[k]
            
    # Handle follow-up question if critical details are missing
    follow_up = analysis.get("follow_up_question", "")
    if analysis.get("is_planning") and (not params.get("destination") or follow_up):
        if not follow_up:
            follow_up = "Which city would you like to travel to?"
        updates["final_answer"] = follow_up
        updates["agents_to_run"] = []
        updates["agents_used"] = ["supervisor"]
        if node_span:
            end_span(node_span, output=updates)
        return updates
        
    updates["agents_to_run"] = analysis.get("agents_to_run", [])
    updates["agents_used"] = []
    updates["follow_up_question"] = ""
    
    # If not planning and no specific agents matched, default to general chatbot
    if not analysis.get("is_planning") and not updates["agents_to_run"]:
        res = supervisor_agent.generate_response(user_msg)
        updates["final_answer"] = res
        updates["agents_used"] = ["supervisor"]
        
    if node_span:
        end_span(node_span, output=updates)
    return updates

def execute_agents_parallel_node(state: AgentState) -> Dict[str, Any]:
    """
    Runs Destination, Weather, Transport, Hotel, Food, Budget, Booking Link, and Safety agents
    in parallel using ThreadPoolExecutor.
    """
    from app.tracing import create_span, end_span
    node_span = create_span(name="execute_agents_parallel", input=dict(state))
    
    agents_to_run = state.get("agents_to_run", [])
    if not agents_to_run:
        if node_span:
            end_span(node_span, output={})
        return {}
        
    results = {}
    agents_used = list(state.get("agents_used", []))
    
    def run_single_agent(agent_name: str):
        if agent_name == "destination" and state.get("destination"):
            res = destination_agent.run(
                destination=state["destination"],
                interests=state.get("interests"),
                days=state.get("days", 3)
            )
            return "destination_result", "destination", res
            
        elif agent_name == "weather" and state.get("destination"):
            res = weather_agent.run(destination=state["destination"])
            return "weather_result", "weather", res
            
        elif agent_name == "transport" and state.get("destination") and state.get("source"):
            res = transport_agent.run(source=state["source"], destination=state["destination"])
            return "transport_result", "transport", res
            
        elif agent_name == "hotel" and state.get("destination"):
            res = hotel_agent.run(
                destination=state["destination"],
                budget=state.get("budget"),
                travelers=state.get("people", 1),
                travel_style=state.get("travel_style", "medium")
            )
            return "hotel_result", "hotel", res
            
        elif agent_name == "food" and state.get("destination"):
            res = food_agent.run(destination=state["destination"], food_preference=state.get("food_preference"))
            return "food_result", "food", res
            
        elif agent_name == "budget" and state.get("destination"):
            res = budget_agent.run(
                source=state.get("source", "Delhi"),
                destination=state["destination"],
                days=state.get("days", 3),
                people=state.get("people", 2),
                travel_style=state.get("travel_style", "medium")
            )
            return "budget_result", "budget", res
            
        elif agent_name == "booking_link" and state.get("destination"):
            res = booking_link_agent.run(
                source=state.get("source", "Delhi"),
                destination=state["destination"],
                date=state.get("travel_date"),
                people=state.get("people", 2),
                budget=state.get("budget"),
                travel_style=state.get("travel_style", "medium")
            )
            return "booking_result", "booking_link", res
            
        elif agent_name == "safety" and state.get("destination"):
            res = safety_agent.run(destination=state["destination"])
            return "safety_result", "safety", res
            
        return None

    targets = [name for name in agents_to_run if name not in ["supervisor", "itinerary"]]
    if not targets:
        if node_span:
            end_span(node_span, output={})
        return {}

    from app.tracing import copy_context_to_thread
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(copy_context_to_thread, run_single_agent, name): name for name in targets}
        for future in concurrent.futures.as_completed(futures):
            val = future.result()
            if val:
                state_key, agent_name, response_text = val
                results[state_key] = response_text
                agents_used.append(agent_name)

    results["agents_used"] = agents_used
    if node_span:
        end_span(node_span, output=results)
    return results

def itinerary_node(state: AgentState) -> Dict[str, Any]:
    from app.tracing import create_span, end_span
    node_span = create_span(name="itinerary_node", input=dict(state))
    
    if "itinerary" not in state.get("agents_to_run", []) or not state.get("destination"):
        if node_span:
            end_span(node_span, output={})
        return {}
        
    # Build context from previous agents
    context_parts = []
    if state.get("destination_result"):
        context_parts.append(f"Attractions: {state['destination_result']}")
    if state.get("weather_result"):
        context_parts.append(f"Weather: {state['weather_result']}")
    if state.get("hotel_result"):
        context_parts.append(f"Hotel Areas: {state['hotel_result']}")
    if state.get("food_result"):
        context_parts.append(f"Food Areas: {state['food_result']}")
        
    res = itinerary_agent.run(
        destination=state["destination"],
        days=state.get("days", 3),
        interests=state.get("interests"),
        travel_style=state.get("travel_style", "medium"),
        context="\n\n".join(context_parts)
    )
    updates = {
        "itinerary_result": res,
        "agents_used": state.get("agents_used", []) + ["itinerary"]
    }
    if node_span:
        end_span(node_span, output=updates)
    return updates

def supervisor_merge_node(state: AgentState) -> Dict[str, Any]:
    """
    Final node. If multiple agents ran, merge their findings.
    If only a single agent ran, use its output directly.
    """
    from app.tracing import create_span, end_span
    node_span = create_span(name="supervisor_merge", input=dict(state))
    
    if state.get("final_answer"):
        if node_span:
            end_span(node_span, output={})
        return {}
        
    agents_run = state.get("agents_to_run", [])
    if not agents_run:
        updates = {"final_answer": "I'm sorry, I could not process that request."}
        if node_span:
            end_span(node_span, output=updates)
        return updates
        
    # Gather agent outputs
    outputs = {}
    if state.get("destination_result"):
        outputs["destination"] = state["destination_result"]
    if state.get("weather_result"):
        outputs["weather"] = state["weather_result"]
    if state.get("transport_result"):
        outputs["transport"] = state["transport_result"]
    if state.get("hotel_result"):
        outputs["hotel"] = state["hotel_result"]
    if state.get("food_result"):
        outputs["food"] = state["food_result"]
    if state.get("budget_result"):
        outputs["budget"] = state["budget_result"]
    if state.get("itinerary_result"):
        outputs["itinerary"] = state["itinerary_result"]
    if state.get("booking_result"):
        outputs["booking_link"] = state["booking_result"]
    if state.get("safety_result"):
        outputs["safety"] = state["safety_result"]
        
    if len(outputs) == 1:
        single_result = list(outputs.values())[0]
        used = state.get("agents_used", [])
        updates = {
            "final_answer": f"{single_result}\n\n[Agents used: {', '.join(used)}]"
        }
        if node_span:
            end_span(node_span, output=updates)
        return updates
        
    merged = supervisor_agent.merge_responses(
        params={
            "source": state.get("source"),
            "destination": state.get("destination"),
            "days": state.get("days"),
            "people": state.get("people"),
            "budget": state.get("budget"),
            "interests": state.get("interests"),
            "travel_style": state.get("travel_style"),
            "food_preference": state.get("food_preference")
        },
        agent_outputs=outputs,
        agents_used=state.get("agents_used", [])
    )
    updates = {"final_answer": merged}
    if node_span:
        end_span(node_span, output=updates)
    return updates

# Route logic
def route_after_supervisor(state: AgentState) -> str:
    if not state.get("agents_to_run"):
        return "end"
    return "execute"

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("supervisor_analyze", supervisor_analyze_node)
builder.add_node("execute_agents_parallel", execute_agents_parallel_node)
builder.add_node("itinerary", itinerary_node)
builder.add_node("supervisor_merge", supervisor_merge_node)

builder.set_entry_point("supervisor_analyze")

# Conditional edges from supervisor
builder.add_conditional_edges(
    "supervisor_analyze",
    route_after_supervisor,
    {
        "end": END,
        "execute": "execute_agents_parallel"
    }
)

builder.add_edge("execute_agents_parallel", "itinerary")
builder.add_edge("itinerary", "supervisor_merge")
builder.add_edge("supervisor_merge", END)

workflow = builder.compile()

def run_workflow(state_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the workflow graph.
    """
    from app.tracing import create_trace, create_span, end_span, active_trace_var, supervisor_span_var, flush_traces
    from app.config import OPENROUTER_MODEL
    
    # 1. Initialize trace and parent supervisor span
    endpoint_val = state_inputs.get("endpoint", "/chat")
    trace = create_trace(
        name="travel_plan_request",
        input=state_inputs,
        metadata={
            "workflow": "multi_agent_travel_guide",
            "model": OPENROUTER_MODEL,
            "source": state_inputs.get("source"),
            "destination": state_inputs.get("destination"),
            "days": state_inputs.get("days"),
            "people": state_inputs.get("people"),
            "travel_style": state_inputs.get("travel_style"),
            "endpoint_used": endpoint_val
        }
    )
    
    super_span_data = create_span(name="supervisor_agent", input=state_inputs)
    token = None
    if super_span_data:
        token = supervisor_span_var.set(super_span_data)
        
    initial_state = {
        "user_message": state_inputs.get("user_message"),
        "source": state_inputs.get("source"),
        "destination": state_inputs.get("destination"),
        "days": state_inputs.get("days"),
        "people": state_inputs.get("people"),
        "budget": state_inputs.get("budget"),
        "interests": state_inputs.get("interests"),
        "travel_style": state_inputs.get("travel_style"),
        "food_preference": state_inputs.get("food_preference"),
        "travel_date": state_inputs.get("travel_date"),
        "endpoint": endpoint_val,  # Pass endpoint down
        "agents_to_run": [],
        "agents_used": [],
        "follow_up_question": None,
        "weather_result": None,
        "destination_result": None,
        "transport_result": None,
        "hotel_result": None,
        "food_result": None,
        "budget_result": None,
        "itinerary_result": None,
        "booking_result": None,
        "safety_result": None,
        "final_answer": None
    }
    
    try:
        result = workflow.invoke(initial_state)
        
        # Add trace metadata at completion
        if trace:
            trace.update(
                output=result.get("final_answer"),
                metadata={
                    "workflow": "multi_agent_travel_guide",
                    "agents_used": result.get("agents_used", []),
                    "model": OPENROUTER_MODEL,
                    "source": result.get("source"),
                    "destination": result.get("destination"),
                    "days": result.get("days"),
                    "people": result.get("people"),
                    "travel_style": result.get("travel_style"),
                    "endpoint_used": endpoint_val
                }
            )
            # Add trace_id so endpoint can return it
            result["trace_id"] = trace.trace_id
            
        if super_span_data:
            super_span_data[1].update(output=result.get("final_answer"))
            
        return result
    except Exception as e:
        if super_span_data:
            super_span_data[1].update(level="ERROR", status_message=str(e))
        raise e
    finally:
        if super_span_data:
            end_span(super_span_data)
        if token:
            supervisor_span_var.reset(token)
        # End trace/root span
        from app.tracing import active_trace_var
        root_data = active_trace_var.get()
        if root_data:
            end_span(root_data)
        flush_traces()


