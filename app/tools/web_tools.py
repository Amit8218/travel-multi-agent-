import requests
from typing import Optional
from langchain.tools import tool
from app.config import TAVILY_API_KEY

import time
import logging
from app.tracing import create_span, end_span

logger = logging.getLogger("AI-Travel-Guide-Tools")

def perform_tavily_search(query: str, max_results: int = 5) -> str:
    """
    Helper function to query Tavily API and return formatted results.
    """
    if not TAVILY_API_KEY:
        return "Error: TAVILY_API_KEY is not configured. Please set it in your environment/.env file."
    
    logger.info(f"Tool called: Tavily search for query: '{query}'")
    start_time = time.time()
    
    span = create_span(
        name="tavily_web_search",
        input={"query": query, "max_results": max_results}
    )
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        exec_time = time.time() - start_time
        
        if response.status_code == 401:
            err_msg = "Error: Invalid Tavily API Key."
            logger.warning(f"Tool failed: {err_msg}")
            if span:
                span[1].update(
                    level="ERROR",
                    status_message=err_msg,
                    metadata={"error": err_msg, "execution_time_seconds": exec_time}
                )
                end_span(span, output=err_msg)
            return err_msg
        
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        num_results = len(results)
        
        if not results:
            output = f"No results found for query: '{query}'."
            if span:
                span[1].update(
                    metadata={
                        "query": query,
                        "number_of_results": 0,
                        "execution_time_seconds": exec_time
                    }
                )
                end_span(span, output=output)
            return output
            
        formatted_results = []
        for idx, result in enumerate(results, 1):
            title = result.get("title", "No Title")
            link = result.get("url", "#")
            content = result.get("content", "")
            formatted_results.append(f"[{idx}] {title}\nURL: {link}\nContent: {content}\n")
            
        res_summary = "\n".join(formatted_results)
        summary_snippet = res_summary[:500] + ("..." if len(res_summary) > 500 else "")
        
        if span:
            span[1].update(
                metadata={
                    "query": query,
                    "number_of_results": num_results,
                    "execution_time_seconds": exec_time
                }
            )
            end_span(span, output=summary_snippet)
            
        return res_summary
        
    except requests.exceptions.Timeout:
        exec_time = time.time() - start_time
        err_msg = "Error: Tavily API search timed out. Please try again later."
        logger.warning(f"Tool failed: {err_msg}")
        if span:
            span[1].update(
                level="ERROR",
                status_message=err_msg,
                metadata={"error": "timeout", "execution_time_seconds": exec_time}
            )
            end_span(span, output=err_msg)
        return err_msg
    except requests.exceptions.RequestException as e:
        exec_time = time.time() - start_time
        err_msg = f"Error: Failed to connect to Tavily Search API. Details: {str(e)}"
        logger.warning(f"Tool failed: {err_msg}")
        if span:
            span[1].update(
                level="ERROR",
                status_message=err_msg,
                metadata={"error": str(e), "execution_time_seconds": exec_time}
            )
            end_span(span, output=err_msg)
        return err_msg
    except Exception as e:
        exec_time = time.time() - start_time
        err_msg = f"Error: An unexpected error occurred while searching. Details: {str(e)}"
        logger.warning(f"Tool failed: {err_msg}")
        if span:
            span[1].update(
                level="ERROR",
                status_message=err_msg,
                metadata={"error": str(e), "execution_time_seconds": exec_time}
            )
            end_span(span, output=err_msg)
        return err_msg

@tool
def web_search(query: str) -> str:
    """Use this to perform general web searches for current, live, or time-sensitive information."""
    return perform_tavily_search(query)

@tool
def search_places(location: str) -> str:
    """Find tourist places, attractions, opening hours, entry fees, famous spots, nearby places, and things to do in a location."""
    query = f"Best tourist places in {location} with timings entry fees and things to do"
    return perform_tavily_search(query)

@tool
def search_transport(source: str, destination: str) -> str:
    """Find transport options (train, bus, flight, cab, and local transport) between source and destination."""
    query = f"How to reach {destination} from {source} by train, bus, flight, cab, and local transport options"
    return perform_tavily_search(query)

@tool
def search_hotels(city: str, budget: Optional[str] = None, preference: Optional[str] = None) -> str:
    """Find good hotels and stay areas in a city based on budget and preferences. Note that exact prices and availability must be verified on booking platforms."""
    query = f"Best hotels and stay areas in {city}"
    if budget:
        query += f" with budget around {budget}"
    if preference:
        query += f" and preference for {preference}"
    
    search_results = perform_tavily_search(query)
    disclaimer = "\nNote: Hotel availability and prices change frequently. Please verify details, booking rules, and live rates on booking platforms."
    return f"{search_results}\n{disclaimer}"

@tool
def search_food_places(location: str) -> str:
    """Find famous local food, dishes, cafes, restaurants, street food, and food markets in a location."""
    query = f"Famous local food, dishes, restaurants, cafes, street food and food markets in {location}"
    return perform_tavily_search(query)

@tool
def search_safety_updates(location: str) -> str:
    """Find safety advisories, travel warnings, current weather alerts, or restrictions for a location."""
    query = f"Current travel safety advisories travel warnings restrictions weather alerts for {location}"
    return perform_tavily_search(query)
