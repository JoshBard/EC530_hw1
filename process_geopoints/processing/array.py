import math

#help from ChatGPT on this function
def haversine(lat1, lon1, lat2, lon2):
    # Earth radius in kilometers
    R = 6371.0
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_point(start_point, options):
    # Tried to optimize a bit by using sort, rather than an explicit for loop
    closest_point = sorted(options, key=lambda option: haversine(start_point[0], start_point[1], option[0], option[1]))
    return closest_point[0]

def sort_points(points_one, points_two): 
    sorted = []
    if((points_one == None) or (points_two == None)):
        return []
    for i in range(len(points_one)):
        sorted.append([points_one[i], find_point(points_one[i], points_two)])
    print(sorted)

# Test cases written by ChatGPT
def main():
    """
    # Test Case 1: One point in each array
    points_one = [(37.7749, -122.4194)]  # San Francisco
    points_two = [(34.0522, -118.2437)]  # Los Angeles
    print("Test Case 1: One point in each array")
    sort_points(points_one, points_two)

    # Test Case 2: Multiple points in each array
    points_one = [(37.7749, -122.4194), (40.7128, -74.0060)]  # SF, NYC
    points_two = [(34.0522, -118.2437), (36.7783, -119.4179), (25.7617, -80.1918)]  # LA, Fresno, Miami
    print("\nTest Case 2: Multiple points in each array")
    sort_points(points_one, points_two)

    # Test Case 3: Empty arrays
    points_one = []
    points_two = []
    print("\nTest Case 3: Empty arrays")
    sort_points(points_one, points_two)

    # Test Case 4: Null arrays (None)
    points_one = None
    points_two = None
    print("\nTest Case 4: Null arrays")
    sort_points(points_one, points_two)

    # Test Case 5: Unequal sizes
    points_one = [(37.7749, -122.4194)]  # SF
    points_two = [(34.0522, -118.2437), (36.7783, -119.4179)]  # LA, Fresno
    print("\nTest Case 5: Unequal sizes")
    sort_points(points_one, points_two)

    # Test Case 6: Large arrays
    points_one = [(37.7749, -122.4194), (40.7128, -74.0060), (25.7617, -80.1918)]  # SF, NYC, Miami
    points_two = [(34.0522, -118.2437), (36.7783, -119.4179), (47.6062, -122.3321), (25.7617, -80.1918)]  # LA, Fresno, Seattle, Miami
    print("\nTest Case 6: Large arrays")
    sort_points(points_one, points_two)
    """
    print("Enter the first array: ")
    points_one_input = input()
    points_one = eval(points_one_input)

    print("Enter the second array: ")
    points_two_input = input()
    points_two = eval(points_two_input)
    
    sort_points(points_one, points_two)

if __name__ == "__main__":
    main()