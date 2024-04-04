import requests
import math
import random


def generate_route(start_latitude, start_longitude, duration, area_bounds):
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
        
        # Calculate the maximum distance that can be traveled in the interval duration
        max_distance = interval_duration * 1.4  # Assuming an average walking speed of 1.4 m/s
        
        # Generate random bearing (direction) in degrees
        bearing = math.radians(random.randint(0, 360))
        
        # Calculate the new coordinates based on the current location, bearing, and maximum distance
        new_latitude = math.asin(math.sin(math.radians(current_latitude)) * math.cos(max_distance / 6371000) +
                                 math.cos(math.radians(current_latitude)) * math.sin(max_distance / 6371000) * math.cos(bearing))
        new_longitude = math.radians(current_longitude) + math.atan2(math.sin(bearing) * math.sin(max_distance / 6371000) * math.cos(math.radians(current_latitude)),
                                                                     math.cos(max_distance / 6371000) - math.sin(math.radians(current_latitude)) * math.sin(new_latitude))
        
        new_latitude = math.degrees(new_latitude)
        new_longitude = math.degrees(new_longitude)
        
        # Check if the new coordinates are within the area boundaries
        if not is_within_bounds(new_latitude, new_longitude, area_bounds):
            continue
        
        # Construct the OSRM API request URL
        request_url = url + f"{current_longitude},{current_latitude};{new_longitude},{new_latitude}?steps=true"
        
        try:
            # Send a GET request to the OSRM API
            response = requests.get(request_url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            
            # Parse the JSON response
            data = response.json()
            
            if data["code"] == "Ok":
                # Extract the route geometry from the response
                geometry = data["routes"][0]["geometry"]
                
                # Decode the polyline geometry
                coordinates = decode_polyline(geometry)
                
                # Add the new coordinates to the route list
                route.extend(coordinates)
            else:
                print("An error occurred while generating the route.")
                return None
        
        except requests.exceptions.RequestException as e:
            print("An error occurred while generating the route:")
            print(e)
            return None
    
    # Truncate the route to the specified duration
    truncated_route = truncate_route(route, duration_seconds)
    
    return truncated_route


def is_within_bounds(latitude, longitude, area_bounds):
    min_lat, min_lon, max_lat, max_lon = area_bounds
    return min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon


def truncate_route(route, duration_seconds):
    truncated_route = [route[0]]
    total_distance = 0
    
    for i in range(1, len(route)):
        prev_coord = route[i - 1]
        curr_coord = route[i]
        
        # Calculate the distance between the previous and current coordinates
        distance = haversine_distance(prev_coord, curr_coord)
        total_distance += distance
        
        # Check if the total distance exceeds the specified duration
        if total_distance > duration_seconds * 1.4:  # Assuming an average walking speed of 1.4 m/s
            break
        
        truncated_route.append(curr_coord)
    
    return truncated_route


def haversine_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Convert coordinates from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in meters
    radius = 6371000
    
    distance = radius * c
    return distance


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

        coordinates.append((lat / 1e5, lng / 1e5))

    return coordinates
