import webbrowser
import requests
from typing import Dict

class MapsOperations:
    """
    Handles all Google Maps-related operations like directions, opening maps in browser, etc.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_directions_url = "https://maps.googleapis.com/maps/api/directions/json"

    def get_directions(self, origin: str, destination: str, mode: str = "driving") -> Dict:
        """
        Get directions between two locations using Google Maps Directions API

        Args:
            origin (str): Starting location
            destination (str): Destination location
            mode (str): Travel mode (driving, walking, bicycling, transit)

        Returns:
            Dict: Success status and data or error message
        """
        try:
            params = {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "key": self.api_key
            }

            response = requests.get(self.base_directions_url, params=params)
            data = response.json()

            if data["status"] != "OK":
                return {
                    "success": False,
                    "error": data.get("error_message", "No directions found.")
                }

            # Extract relevant information
            route = data["routes"][0]["legs"][0]
            return {
                "success": True,
                "origin": route["start_address"],
                "destination": route["end_address"],
                "duration": route["duration"]["text"],
                "distance": route["distance"]["text"],
                "steps": [step["html_instructions"] for step in route["steps"]],
                "map_link": f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode={mode}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def open_map(self, origin: str, destination: str, mode: str = "driving") -> Dict:
        """
        Open Google Maps with route between origin and destination in browser

        Args:
            origin (str): Starting location
            destination (str): Destination location
            mode (str): Travel mode

        Returns:
            Dict: Success status
        """
        try:
            map_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode={mode}"
            webbrowser.open(map_url)
            return {
                "success": True,
                "message": "Opened Google Maps in browser.",
                "map_link": map_url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    API_KEY = "GOOGLE_MAPS_API_KEY"
    maps = MapsOperations(api_key=API_KEY)

    # Get directions
    result = maps.get_directions("Lahore", "Islamabad")
    if result["success"]:
        print("Origin:", result["origin"])
        print("Destination:", result["destination"])
        print("Distance:", result["distance"])
        print("Duration:", result["duration"])
        print("Map:", result["map_link"])
    else:
        print("Error:", result["error"])

    # Open map in browser
    maps.open_map("Lahore", "Islamabad")

