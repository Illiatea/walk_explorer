import requests


def geocode_address(address):
    # OpenStreetMap Nominatim API endpoint
    url = "https://nominatim.openstreetmap.org/search"
    
    # Parameters for the API request
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    
    try:
        # Send a GET request to the Nominatim API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        
        # Parse the JSON response
        data = response.json()
        
        if data:
            # Extract the latitude and longitude from the response
            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])
            return latitude, longitude
        else:
            print("No results found for the provided address.")
            return None, None
    
    except requests.exceptions.RequestException as e:
        print("An error occurred while geocoding the address:")
        print(e)
        return None, None
