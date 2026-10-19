from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from app.config import OPENROUTER_MODEL, validate_config, SHOW_AGENT_PROGRESS
from app.workflow.graph import run_workflow, supervisor_agent
from app.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    PlanTripRequest,
    PlanTripResponse,
    AgentTestRequest,
    AgentTestResponse,
    ReadyToGoRequest,
    ReadyToGoResponse
)


app = FastAPI(
    title="Multi-Agent AI Travel Guide API",
    description="FastAPI backend exposing a multi-agent travel guide planner using OpenRouter LLM, Tavily, and OpenWeather.",
    version="1.0.0"
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Returns the status of the API, the LLM provider, and system details.
    """
    return HealthResponse(
        status="ok",
        llm_provider="OpenRouter",
        model=OPENROUTER_MODEL,
        system="multi_agent_travel_guide",
        show_agent_progress=SHOW_AGENT_PROGRESS
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Accepts a conversational query and runs the Supervisor-guided LangGraph workflow.
    """
    user_message = request.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    # Warn if configuration is missing
    missing = validate_config()
    if "OPENROUTER_API_KEY" in missing:
        raise HTTPException(
            status_code=500, 
            detail="OPENROUTER_API_KEY is not set. Please configure it in your .env file."
        )

    try:
        # Run workflow via LangGraph, specifying endpoint context for tracing
        result = run_workflow({"user_message": user_message, "endpoint": "/chat"})
        answer = result.get("final_answer", "I'm sorry, I could not generate a plan.")
        agents_used = result.get("agents_used", ["supervisor"])
        trace_id = result.get("trace_id")
        return ChatResponse(answer=answer, agents_used=agents_used, trace_id=trace_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.post("/plan-trip", response_model=PlanTripResponse)
async def plan_trip_endpoint(request: PlanTripRequest):
    """
    Generates a structured, comprehensive multi-agent travel plan using pre-extracted parameters.
    """
    missing = validate_config()
    if "OPENROUTER_API_KEY" in missing:
        raise HTTPException(
            status_code=500, 
            detail="OPENROUTER_API_KEY is not set. Please configure it in your .env file."
        )

    try:
        # Construct the workflow state inputs from the structured request
        state_inputs = {
            "source": request.source.strip(),
            "destination": request.destination.strip(),
            "days": request.days,
            "people": request.people,
            "budget": request.budget.strip(),
            "interests": request.interests.strip() if request.interests else "general sightseeing",
            "travel_style": request.travel_style.strip() if request.travel_style else "medium",
            "food_preference": request.food_preference.strip() if request.food_preference else None,
            "endpoint": "/plan-trip"
        }
        
        result = run_workflow(state_inputs)
        plan = result.get("final_answer", "I'm sorry, I could not generate a plan.")
        agents_used = result.get("agents_used", [])
        trace_id = result.get("trace_id")
        
        return PlanTripResponse(trip_plan=plan, agents_used=agents_used, trace_id=trace_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while planning your trip: {str(e)}"
        )

@app.post("/agent-test", response_model=AgentTestResponse)
async def agent_test_endpoint(request: AgentTestRequest):
    """
    Endpoint for testing individual specialized agents independently.
    """
    agent_name = request.agent.lower().strip()
    query = request.query.strip()
    
    missing = validate_config()
    if "OPENROUTER_API_KEY" in missing:
        raise HTTPException(
            status_code=500, 
            detail="OPENROUTER_API_KEY is not set. Please configure it in your .env file."
        )

    # Setup direct tracing for standalone agent tests
    from app.tracing import create_trace, flush_traces
    trace = create_trace(
        name="travel_plan_request",
        input={"agent_test": agent_name, "query": query},
        metadata={"endpoint_used": "/agent-test", "workflow": "agent_test", "model": OPENROUTER_MODEL}
    )

    try:
        if agent_name == "weather":
            from app.agents.weather_agent import WeatherAgent
            res = WeatherAgent().run(query)
        elif agent_name == "destination":
            from app.agents.destination_agent import DestinationAgent
            res = DestinationAgent().run(query)
        elif agent_name == "transport":
            from app.agents.transport_agent import TransportAgent
            parts = query.split(" to ")
            if len(parts) == 2:
                res = TransportAgent().run(parts[0].strip(), parts[1].strip())
            else:
                res = TransportAgent().run("Delhi", query)
        elif agent_name == "hotel":
            from app.agents.hotel_agent import HotelAgent
            res = HotelAgent().run(query)
        elif agent_name == "food":
            from app.agents.food_agent import FoodAgent
            res = FoodAgent().run(query)
        elif agent_name == "budget":
            from app.agents.budget_agent import BudgetAgent
            res = BudgetAgent().run("Delhi", query, 3, 2, "medium")
        elif agent_name == "itinerary":
            from app.agents.itinerary_agent import ItineraryAgent
            res = ItineraryAgent().run(query, 3)
        elif agent_name == "safety":
            from app.agents.safety_agent import SafetyAgent
            res = SafetyAgent().run(query)
        elif agent_name == "booking_link" or agent_name == "booking":
            from app.agents.booking_link_agent import BookingLinkAgent
            res = BookingLinkAgent().run(source="Delhi", destination=query, date="2026-07-10", people=2, budget="15000", travel_style="budget")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent}")
            
        trace_id = trace.id if trace else None
        if trace:
            trace.update(output=res)
            
        return AgentTestResponse(agent=agent_name, result=res, trace_id=trace_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while testing agent {agent_name}: {str(e)}"
        )
    finally:
        flush_traces()

@app.post("/ready-to-go-plan", response_model=ReadyToGoResponse)
async def ready_to_go_plan_endpoint(request: ReadyToGoRequest):
    """
    Generates a Ready-to-Go plan with direct booking links and safety checklists.
    """
    missing = validate_config()
    if "OPENROUTER_API_KEY" in missing:
        raise HTTPException(
            status_code=500, 
            detail="OPENROUTER_API_KEY is not set. Please configure it in your .env file."
        )

    try:
        state_inputs = {
            "source": request.source.strip(),
            "destination": request.destination.strip(),
            "days": request.days,
            "people": request.people,
            "budget": request.budget.strip(),
            "interests": request.interests.strip() if request.interests else "general sightseeing",
            "travel_style": request.travel_style.strip() if request.travel_style else "medium",
            "food_preference": request.food_preference.strip() if request.food_preference else None,
            "travel_date": request.travel_date.strip() if request.travel_date else "2026-07-10",
            "endpoint": "/ready-to-go-plan"
        }
        
        result = run_workflow(state_inputs)
        plan = result.get("final_answer", "I'm sorry, I could not generate a plan.")
        agents_used = result.get("agents_used", [])
        trace_id = result.get("trace_id")
        
        return ReadyToGoResponse(ready_to_go_plan=plan, agents_used=agents_used, trace_id=trace_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating ready-to-go plan: {str(e)}"
        )

@app.get("/debug/langfuse")
async def debug_langfuse():
    """
    Returns the configuration status of Langfuse tracing.
    """
    from app.config import LANGFUSE_ENABLED, LANGFUSE_HOST, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY
    return {
        "langfuse_enabled": bool(LANGFUSE_ENABLED),
        "host": LANGFUSE_HOST,
        "public_key_configured": bool(LANGFUSE_PUBLIC_KEY),
        "secret_key_configured": bool(LANGFUSE_SECRET_KEY)
    }

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Accepts a conversational query and returns a streaming response.
    """
    user_message = request.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    missing = validate_config()
    if "OPENROUTER_API_KEY" in missing:
        raise HTTPException(
            status_code=500, 
            detail="OPENROUTER_API_KEY is not set. Please configure it in your .env file."
        )

    return StreamingResponse(
        supervisor_agent.run_stream(
            params={"user_message": user_message},
            endpoint="/chat/stream"
        ),
        media_type="text/event-stream"
    )

@app.post("/plan-trip/stream")
async def plan_trip_stream_endpoint(request: PlanTripRequest):
    """
    Generates a streaming travel plan using pre-extracted parameters.
    """
    missing = validate_config()
    if "OPENROUTER_API_KEY" in missing:
        raise HTTPException(
            status_code=500, 
            detail="OPENROUTER_API_KEY is not set. Please configure it in your .env file."
        )

    state_inputs = {
        "source": request.source.strip(),
        "destination": request.destination.strip(),
        "days": request.days,
        "people": request.people,
        "budget": request.budget.strip(),
        "interests": request.interests.strip() if request.interests else "general sightseeing",
        "travel_style": request.travel_style.strip() if request.travel_style else "medium",
        "food_preference": request.food_preference.strip() if request.food_preference else None,
        "travel_date": "2026-07-10"  # default
    }

    return StreamingResponse(
        supervisor_agent.run_stream(
            params=state_inputs,
            endpoint="/plan-trip/stream"
        ),
        media_type="text/event-stream"
    )

@app.post("/ready-to-go-plan/stream")
async def ready_to_go_plan_stream_endpoint(request: ReadyToGoRequest):
    """
    Generates a streaming Ready-to-Go plan with direct booking links and safety checklists.
    """
    missing = validate_config()
    if "OPENROUTER_API_KEY" in missing:
        raise HTTPException(
            status_code=500, 
            detail="OPENROUTER_API_KEY is not set. Please configure it in your .env file."
        )

    state_inputs = {
        "source": request.source.strip(),
        "destination": request.destination.strip(),
        "days": request.days,
        "people": request.people,
        "budget": request.budget.strip(),
        "interests": request.interests.strip() if request.interests else "general sightseeing",
        "travel_style": request.travel_style.strip() if request.travel_style else "medium",
        "food_preference": request.food_preference.strip() if request.food_preference else None,
        "travel_date": request.travel_date.strip() if request.travel_date else "2026-07-10"
    }

    return StreamingResponse(
        supervisor_agent.run_stream(
            params=state_inputs,
            endpoint="/ready-to-go-plan/stream"
        ),
        media_type="text/event-stream"
    )



