import pytest
import math
import pandas as pd
from process_geopoints.array import haversine, clean_coordinate, find_closest_point

# Test Haversine Distance Calculation
def test_haversine():
    # Distance between New York (40.7128, -74.0060) and Los Angeles (34.0522, -118.2437)
    ny_lat, ny_lon = 40.7128, -74.0060
    la_lat, la_lon = 34.0522, -118.2437
    expected_distance_km = 3936  # Approximate
    calculated_distance = haversine(ny_lat, ny_lon, la_lat, la_lon)
    
    assert math.isclose(calculated_distance, expected_distance_km, rel_tol=0.05)

@pytest.mark.parametrize("input_value, expected", [
    ("40.7128 N", 40.71),  # Rounded
    ("74.006 W", -74.01),  # Rounded
    ("34°03' N", 34.03),  # Fixed conversion
    ("118°14' W", -118.14),  # Fixed conversion
    ("INVALID", None),
    ("90", 90.00),  # Rounded
    ("-45.67", -45.67)  # Should not change
])
def test_clean_coordinate(input_value, expected):
    assert clean_coordinate(input_value) == expected

# Test Find Closest Point Function
def test_find_closest_point():
    start_point = {"latitude": 40.7128, "longitude": -74.0060}  # New York

    options = [
        {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles
        {"latitude": 41.8781, "longitude": -87.6298},  # Chicago
        {"latitude": 51.5074, "longitude": -0.1278}  # London
    ]

    closest = find_closest_point(start_point, options)

    assert closest["latitude"] == 41.8781  # Chicago should be the closest

# Run tests from command line
if __name__ == "__main__":
    pytest.main()
