import math
from typing import Optional
from langchain.tools import tool

@tool
def estimate_budget(
    destination: str, 
    days: int, 
    people: int, 
    travel_style: str, 
    source_city: Optional[str] = None
) -> str:
    """
    Estimate a rough trip budget including stay, food, local transport, activities, inter-city travel, and emergency buffer.
    All inputs should be converted to correct types (days: int, people: int, travel_style: str).
    """
    try:
        days_val = int(days)
    except:
        days_val = 3
        
    try:
        people_val = int(people)
    except:
        people_val = 2
        
    style = travel_style.lower() if travel_style else "medium"
    rooms = math.ceil(people_val / 2)
    
    if style == "budget":
        stay_per_room_day = 1000
        food_per_person_day = 400
        local_transport_per_person_day = 200
        activities_per_person_day = 300
        travel_cost_per_person = 1200 if source_city else 1000
        emergency_buffer = 1000
    elif style == "luxury":
        stay_per_room_day = 7000
        food_per_person_day = 2000
        local_transport_per_person_day = 1500
        activities_per_person_day = 2000
        travel_cost_per_person = 8500 if source_city else 8000
        emergency_buffer = 6000
    else:  # medium
        style = "medium"
        stay_per_room_day = 2500
        food_per_person_day = 900
        local_transport_per_person_day = 500
        activities_per_person_day = 800
        travel_cost_per_person = 3500 if source_city else 3000
        emergency_buffer = 3000
        
    stay_cost = days_val * rooms * stay_per_room_day
    food_cost = days_val * people_val * food_per_person_day
    local_transport_cost = days_val * people_val * local_transport_per_person_day
    activities_cost = days_val * people_val * activities_per_person_day
    travel_cost = people_val * travel_cost_per_person
    
    total = stay_cost + food_cost + local_transport_cost + activities_cost + travel_cost + emergency_buffer
    
    source_str = f" from {source_city}" if source_city else ""
    
    output = (
        f"Rough Estimated Budget for a {days_val}-day trip to {destination}{source_str} ({people_val} people, Style: {style.capitalize()}):\n"
        f"- Stay (Rooms: {rooms}, Rate: ~{stay_per_room_day}/night): INR {stay_cost}\n"
        f"- Food (~{food_per_person_day}/day/person): INR {food_cost}\n"
        f"- Local Transport (~{local_transport_per_person_day}/day/person): INR {local_transport_cost}\n"
        f"- Activities & Sightseeing (~{activities_per_person_day}/day/person): INR {activities_cost}\n"
        f"- Travel/Inter-city transport (~{travel_cost_per_person}/person): INR {travel_cost}\n"
        f"- Emergency Buffer: INR {emergency_buffer}\n"
        f"--------------------------------------------------\n"
        f"Total Estimated Cost: INR {total}\n\n"
        f"Disclaimer: This is a rough approximate estimate. Actual rates may vary based on travel season, advanced booking, and specific choices. Please verify all details before making bookings."
    )
    return output
