from user_input import get_user_input
from geocoding import geocode_address
from route_generation import generate_random_route
from route_display import display_route


def main():
    # Get user input
    start_location, duration = get_user_input()
    
    if start_location and duration:
        # Geocode the starting location
        start_latitude, start_longitude = geocode_address(start_location)
        
        if start_latitude and start_longitude:
            # Generate a random route
            route = generate_random_route(start_latitude, start_longitude, duration)
            
            if route:
                # Display the generated route
                display_route(route)
            else:
                print("Failed to generate a route.")
        else:
            print("Failed to geocode the starting location.")
    else:
        print("Invalid user input.")


if __name__ == "__main__":
    main()
