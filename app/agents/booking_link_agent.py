from app.agents.base import BaseAgent
from app.tools.booking_tools import search_stay_recommendations, search_transport_recommendations

class BookingLinkAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the specialized Booking Link Agent. Your role is to provide direct, useful booking recommendation links "
            "for hotel/stay search, trains, buses, flights, and maps/routes.\n"
            "Rules:\n"
            "- Never state that bookings are confirmed.\n"
            "- Never generate fake ticket IDs, PNR numbers, hotel confirmation IDs, or payment confirmations.\n"
            "- Present recommendations and search links clearly so the user can manually verify and book.\n"
            "- If a link cannot be found, provide a safe search link instead."
        )
        super().__init__(name="booking_link", system_prompt=system_prompt)

    def run(self, source: str, destination: str, date: str = None, people: int = 1, budget: str = None, travel_style: str = "medium") -> str:
        input_data = {
            "source": source,
            "destination": destination,
            "date": date,
            "people": people,
            "budget": budget,
            "travel_style": travel_style
        }
        with self.trace_agent(input_data) as tc:
            try:
                # Call stay recommendations tool
                try:
                    stay_info = search_stay_recommendations.invoke({
                        "destination": destination,
                        "budget": budget if budget else "medium",
                        "travel_style": travel_style,
                        "people": int(people)
                    })
                    if "Error" in stay_info:
                        tc.set_error(stay_info)
                except Exception as e:
                    stay_info = f"Failed to retrieve stay recommendations. Error: {str(e)}"
                    tc.set_error(stay_info)
                    
                # Call transport recommendations tool
                try:
                    transport_info = search_transport_recommendations.invoke({
                        "source": source,
                        "destination": destination,
                        "date": date if date else "today",
                        "people": int(people),
                        "budget": budget if budget else "medium"
                    })
                    if "Error" in transport_info:
                        tc.set_error(transport_info)
                except Exception as e:
                    transport_info = f"Failed to retrieve transport recommendations. Error: {str(e)}"
                    tc.set_error(transport_info)

                # Trace booking link generation span
                from app.tracing import create_span, end_span
                travel_date_val = date if date else "today"
                bl_span = create_span(
                    name="booking_link_generation",
                    input={"source": source, "destination": destination, "date": travel_date_val},
                    metadata={
                        "source": source,
                        "destination": destination,
                        "travel_date": travel_date_val,
                        "hotel_links": [
                            f"https://www.booking.com/searchresults.html?ss={destination}",
                            f"https://www.makemytrip.com/hotels/hotel-listing/?city={destination}",
                            f"https://www.agoda.com/search?city={destination}",
                            f"https://www.google.com/travel/hotels?q=hotels+in+{destination}"
                        ],
                        "transport_links": [
                            "https://www.irctc.co.in/nget/train-search",
                            f"https://www.redbus.in/search?fromCityName={source}&toCityName={destination}",
                            f"https://www.makemytrip.com/flight/search?tripType=O&itinerary={source}-{destination}-{travel_date_val}"
                        ],
                        "maps_links": [
                            f"https://www.google.com/maps/dir/{source}/{destination}"
                        ]
                    }
                )
                if bl_span:
                    end_span(bl_span, output="Booking links generated successfully.")
                    
                prompt = (
                    f"Generate stay and transport booking recommendations with direct search/booking links for a trip "
                    f"from {source} to {destination} on {date if date else 'unspecified date'}.\n"
                    f"Travelers: {people}, Budget: {budget}, Style: {travel_style}.\n\n"
                    f"Here are the stay recommendations retrieved:\n{stay_info}\n\n"
                    f"Here are the transport recommendations retrieved:\n{transport_info}\n\n"
                    f"Organize this response cleanly with Markdown links. Warn the user to verify pricing, timing, reviews, and policies."
                )
                res = self.generate_response(prompt)
                tc.set_output(res)
                return res
            except Exception as e:
                error_msg = f"Failed to generate booking links. Error: {str(e)}"
                tc.set_error(error_msg)
                return error_msg

