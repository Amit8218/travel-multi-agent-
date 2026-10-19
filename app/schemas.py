from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., description="Message/prompt for the travel planner")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Response answer compiled from the agents")
    agents_used: List[str] = Field(..., description="Specialized agents utilized during execution")
    trace_id: Optional[str] = Field(None, description="Langfuse trace identifier for tracing execution flow")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Status of the API")
    llm_provider: str = Field(..., description="The LLM integration provider")
    model: str = Field(..., description="OpenRouter model configured")
    system: str = Field(..., description="Name of the system")
    show_agent_progress: Optional[bool] = Field(False, description="Whether to show agent progress details")


class PlanTripRequest(BaseModel):
    source: str = Field(..., description="Source city of the trip")
    destination: str = Field(..., description="Destination of the trip")
    days: int = Field(..., description="Number of days for the trip")
    people: int = Field(..., description="Number of people traveling")
    budget: str = Field(..., description="Approximate budget/budget limit for the trip")
    interests: Optional[str] = Field(None, description="Interests, e.g. history, food, photography")
    travel_style: Optional[str] = Field("budget", description="Travel style, e.g. budget, medium, luxury")
    food_preference: Optional[str] = Field(None, description="Food preferences, e.g. vegetarian, vegan")

class PlanTripResponse(BaseModel):
    trip_plan: str = Field(..., description="Generated comprehensive travel plan")
    agents_used: List[str] = Field(..., description="Specialized agents utilized during execution")
    trace_id: Optional[str] = Field(None, description="Langfuse trace identifier for tracing execution flow")

class AgentTestRequest(BaseModel):
    agent: str = Field(..., description="Name of the agent to test")
    query: str = Field(..., description="Query or prompt for the agent")

class AgentTestResponse(BaseModel):
    agent: str = Field(..., description="Name of the agent tested")
    result: str = Field(..., description="Result produced by the agent")
    trace_id: Optional[str] = Field(None, description="Langfuse trace identifier for tracing execution flow")

class ReadyToGoRequest(BaseModel):
    source: str = Field(..., description="Source city of the trip")
    destination: str = Field(..., description="Destination of the trip")
    days: int = Field(..., description="Number of days for the trip")
    people: int = Field(..., description="Number of people traveling")
    budget: str = Field(..., description="Approximate budget/budget limit for the trip")
    interests: Optional[str] = Field(None, description="Interests, e.g. history, food, photography")
    travel_style: Optional[str] = Field("budget", description="Travel style, e.g. budget, medium, luxury")
    food_preference: Optional[str] = Field(None, description="Food preferences, e.g. vegetarian, vegan")
    travel_date: Optional[str] = Field("2026-07-10", description="Date of travel, e.g. YYYY-MM-DD")

class ReadyToGoResponse(BaseModel):
    ready_to_go_plan: str = Field(..., description="Generated comprehensive ready-to-go plan with booking links")
    agents_used: List[str] = Field(..., description="Specialized agents utilized during execution")
    trace_id: Optional[str] = Field(None, description="Langfuse trace identifier for tracing execution flow")

