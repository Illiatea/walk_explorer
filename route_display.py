import folium


def display_route(route):
    # Create a new map centered on the starting point
    start_latitude, start_longitude = route[0]
    map_center = [start_latitude, start_longitude]
    route_map = folium.Map(location=map_center, zoom_start=14)
    
    # Add markers for the starting and ending points
    folium.Marker(location=route[0], popup="Start", icon=folium.Icon(color='green')).add_to(route_map)
    folium.Marker(location=route[-1], popup="End", icon=folium.Icon(color='red')).add_to(route_map)
    
    # Add a polyline to represent the route
    folium.PolyLine(locations=route, color='blue', weight=5, opacity=0.7).add_to(route_map)
    
    # Display the map
    route_map.save("route_map.html")
    print("Route map generated and saved as 'route_map.html'.")
