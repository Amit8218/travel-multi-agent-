import urllib.parse
from typing import Optional
from langchain.tools import tool
from app.tools.web_tools import perform_tavily_search

@tool
def generate_hotel_booking_links(
    destination: str,
    checkin_date: Optional[str] = None,
    checkout_date: Optional[str] = None,
    people: Optional[int] = None,
    budget: Optional[str] = None
) -> str:
    """
    Generate direct search/booking URL templates for hotels at the destination.
    Inputs checkin_date, checkout_date, people, budget are optional.
    """
    q_dest = urllib.parse.quote(destination.strip())
    
    booking_url = f"https://www.booking.com/searchresults.html?ss={q_dest}"
    mmt_url = f"https://www.makemytrip.com/hotels/hotel-listing/?city={q_dest}"
    agoda_url = f"https://www.agoda.com/search?city={q_dest}"
    google_url = f"https://www.google.com/travel/hotels?q=hotels+in+{q_dest}"
    
    output = (
        f"🏨 **Hotel Search & Booking Links for {destination}:**\n"
        f"- [Search on Booking.com]({booking_url})\n"
        f"- [Search on MakeMyTrip Hotels]({mmt_url})\n"
        f"- [Search on Agoda]({agoda_url})\n"
        f"- [Search on Google Hotels]({google_url})\n\n"
        f"⚠️ *Note: Prices and availability change frequently. Do not claim availability or exact price unless verified from active search results. Please verify the final price, reviews, and cancellation policies before booking.*"
    )
    return output

@tool
def generate_transport_booking_links(
    source: str,
    destination: str,
    date: Optional[str] = None,
    transport_type: Optional[str] = None
) -> str:
    """
    Generate direct search/booking URL templates for transport between source and destination.
    Input date and transport_type are optional.
    """
    q_src = urllib.parse.quote(source.strip())
    q_dest = urllib.parse.quote(destination.strip())
    q_date = urllib.parse.quote(date.strip()) if date else "today"
    
    irctc_url = f"https://www.irctc.co.in/nget/train-search"
    redbus_url = f"https://www.redbus.in/search?fromCityName={q_src}&toCityName={q_dest}"
    mmt_flights_url = f"https://www.makemytrip.com/flight/search?tripType=O&itinerary={q_src}-{q_dest}-{q_date}"
    google_maps_url = f"https://www.google.com/maps/dir/{q_src}/{q_dest}"
    
    output = (
        f"✈️🚍🚆 **Transport Search & Booking Links:**\n"
        f"- **Train Booking:** [IRCTC Train Search]({irctc_url}) (Search route: {source} to {destination})\n"
        f"- **Bus Booking:** [RedBus Search]({redbus_url})\n"
        f"- **Flight Booking:** [MakeMyTrip Flights]({mmt_flights_url})\n"
        f"- **Route Navigation:** [Google Maps Route Link]({google_maps_url})\n\n"
        f"⚠️ *Note: Verify timings, prices, and schedules directly on the booking platforms before completing any reservations.*"
    )
    return output

@tool
def search_stay_recommendations(
    destination: str,
    budget: str,
    travel_style: str,
    people: int
) -> str:
    """
    Find stay recommendations (best stay areas, budget hotels, hostels, family hotels, and safe areas)
    using Tavily search, and provide direct search links.
    """
    query = f"Best stay areas safe neighborhoods budget hotels hostels family hotels in {destination} style {travel_style}"
    search_data = perform_tavily_search(query, max_results=4)
    
    # Generate booking links to append
    booking_links = generate_hotel_booking_links.invoke({
        "destination": destination,
        "people": people,
        "budget": budget
    })
    
    output = (
        f"🔍 **Stay Area Research & Recommendations for {destination}:**\n\n"
        f"{search_data}\n\n"
        f"{booking_links}"
    )
    return output

@tool
def search_transport_recommendations(
    source: str,
    destination: str,
    date: str,
    people: int,
    budget: str
) -> str:
    """
    Find transport options (train, bus, flight, cab route possibilities) between source and destination
    using Tavily, and generate a markdown comparison table with booking links.
    """
    query = f"travel options train bus flight cab route from {source} to {destination} price time"
    search_data = perform_tavily_search(query, max_results=4)
    
    # Programmatic comparison templates
    table = (
        f"| Transport Mode | Approx Time | Approx Cost | Best For | Booking / Search Link |\n"
        f"| :--- | :--- | :--- | :--- | :--- |\n"
        f"| **Train** | Varies (e.g. 4-6h) | INR 300 - 1200 | Budget & Comfort | [IRCTC Train Search](https://www.irctc.co.in/nget/train-search) |\n"
        f"| **Bus** | Varies (e.g. 5-7h) | INR 400 - 1000 | Budget & Flexible timing | [RedBus Search](https://www.redbus.in/search?fromCityName={urllib.parse.quote(source)}&toCityName={urllib.parse.quote(destination)}) |\n"
        f"| **Flight** | Varies (e.g. 1h) | INR 2500 - 6000 | Speed & Comfort | [MakeMyTrip Flights](https://www.makemytrip.com/flight/search?tripType=O&itinerary={urllib.parse.quote(source)}-{urllib.parse.quote(destination)}-{urllib.parse.quote(date)}) |\n"
        f"| **Cab/Self-Drive** | Varies (e.g. 5h) | INR 3000 - 8000 | Groups & Doorstep travel | [Google Maps Navigation](https://www.google.com/maps/dir/{urllib.parse.quote(source)}/{urllib.parse.quote(destination)}) |\n"
    )
    
    output = (
        f"📊 **Transit Options & Comparison from {source} to {destination}:**\n\n"
        f"{table}\n\n"
        f"🔍 **Search details retrieved:**\n"
        f"{search_data}\n"
    )
    return output

@tool
def create_ready_to_go_package(
    source: str,
    destination: str,
    days: int,
    people: int,
    budget: str,
    interests: str,
    travel_style: str,
    food_preference: Optional[str] = None
) -> str:
    """
    Format a standardized baseline for the ready-to-go package structure.
    Used by the merging pipeline to combine reports.
    """
    return (
        f"Consolidated ready-to-go travel package for {destination} from {source}.\n"
        f"Duration: {days} days | Travelers: {people} | Budget: {budget} | Style: {travel_style}\n"
    )
