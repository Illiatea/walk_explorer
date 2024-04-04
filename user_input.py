def get_user_input():
    start_location = input("Enter the starting location for your walk (address or coordinates): ")
    duration = input("Enter the desired duration of your walk (in minutes): ")
    
    try:
        duration = int(duration)
        if duration <= 0:
            raise ValueError
    except ValueError:
        print("Invalid duration. Please enter a positive integer value.")
        return None, None
    
    return start_location, duration
