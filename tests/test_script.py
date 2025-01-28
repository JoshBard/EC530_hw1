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
    #Decimal Degrees (DD) Format
    ("40.7128 N", 40.7128),
    ("74.006 W", -74.006),
    ("-45.67", -45.67),
    ("90", 90.0),
    ("-90", -90.0),
    ("180", 180.0),
    ("-180", -180.0),
    
    #Degrees and Minutes (DM) Format
    ("34°03' N", 34.05),  # 3' minutes → 3/60 = 0.05
    ("118°14' W", -118.2333),  # 14' minutes → 14/60 = 0.2333
    ("0°30' N", 0.5),  # 30' minutes → 30/60 = 0.5
    ("12°45' S", -12.75),  # 45' minutes → 45/60 = 0.75

    #Degrees, Minutes, and Seconds (DMS) Format
    ("34°03'30\" N", 34.0583),  # 30" seconds → 30/3600 = 0.0083
    ("118°14'45\" W", -118.2458),  # 45" seconds → 45/3600 = 0.0125
    ("0°30'30\" N", 0.5083),  # 30'30" → (30/60) + (30/3600)
    ("89°59'59\" S", -89.9997),  # 59'59" → (59/60) + (59/3600)
    
    #Edge Cases
    ("00°00'00\" N", 0.0),  # Exactly 0 degrees
    ("00°00'01\" S", -0.0003),  # One second south
    ("180°00'00\" E", 180.0),  # Maximum longitude
    ("180°00'00\" W", -180.0),  # Minimum longitude

    #Invalid Inputs (Should return `None`)
    ("INVALID", None),
    ("N 40.7128", None),  # Incorrect format
    ("34°61' N", None),  # Invalid minutes (>60)
    ("118°14'61\" W", None),  # Invalid seconds (>60)
    ("200°00'00\" N", None),  # Invalid degrees (>180)
    ("-91°00'00\" S", None),  # Invalid latitude (<-90)
])
def test_clean_coordinate(input_value, expected):
    assert clean_coordinate(input_value) == expected

# Test Find Closest Point Function
def test_find_closest_point():
    start_point = {"latitude": 40.7128, "longitude": -74.0060}

    options = [
        {"latitude": 34.0522, "longitude": -118.2437},
        {"latitude": 41.8781, "longitude": -87.6298},
        {"latitude": 51.5074, "longitude": -0.1278}
    ]

    closest = find_closest_point(start_point, options)

    assert closest["latitude"] == 41.8781

if __name__ == "__main__":
    pytest.main()
