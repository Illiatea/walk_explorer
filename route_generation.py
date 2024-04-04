import requests
import random
import math


def generate_random_route(start_latitude, start_longitude, duration):
    # OpenStreetMap OSRM API endpoint
    url = "http://router.project-osrm.org/route/v1/walking/"
    
    # Convert duration from minutes to seconds
    duration_seconds = duration * 60
    
    # Define the number of intervals and interval duration
    num_intervals = 10
    interval_duration = duration_seconds // num_intervals
    
    # Initialize the route list with the starting coordinates
    route = [(start_latitude, start_longitude)]
    
    # Generate the route points
    for _ in range(num_intervals):
        # Get the current latitude and longitude
        current_latitude, current_longitude = route[-1]
        
        # Generate a random direction (north, south, east, west)
        direction = random.choice(["north", "south", "east", "west"])
        
        # Generate a random distance (in meters) to travel in the selected direction
        distance = random.randint(100, 500)  # Adjust the range as needed
        
        # Calculate the new coordinates based on the direction and distance
        if direction == "north":
            new_latitude = current_latitude + (distance / 111111)
            new_longitude = current_longitude
        elif direction == "south":
            new_latitude = current_latitude - (distance / 111111)
            new_longitude = current_longitude
        elif direction == "east":
            new_latitude = current_latitude
            new_longitude = current_longitude + (distance / (111111 * math.cos(math.radians(current_latitude))))
        else:  # direction == "west"
            new_latitude = current_latitude
            new_longitude = current_longitude - (distance / (111111 * math.cos(math.radians(current_latitude))))
        
        # Construct the OSRM API request URL
        request_url = url + f"{current_longitude},{current_latitude};{new_longitude},{new_latitude}?steps=true"
        
        try:
            # Send a GET request to the OSRM API
            response = requests.get(request_url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            
            # Parse the JSON response
            data = response.json()
            
            if data["code"] == "Ok":
                # Extract the coordinates from the response
                coordinates = decode_polyline(data["routes"][0]["geometry"])
                
                # Add the new coordinates to the route list
                route.extend([(coord[1], coord[0]) for coord in coordinates])
            else:
                print("An error occurred while generating the route.")
                return None
        
        except requests.exceptions.RequestException as e:
            print("An error occurred while generating the route:")
            print(e)
            return None
    
    return route


def decode_polyline(polyline_str):
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    while index < len(polyline_str):
        for unit in ['latitude', 'longitude']:
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if result & 1:
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates
