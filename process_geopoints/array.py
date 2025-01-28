import pandas as pd
import math
import os
import re

# Haversine function to calculate the distance between two points
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth."""
    R = 6371.0  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_closest_point(start, options):
    """Find the closest latitude/longitude match using Haversine distance."""
    return min(options, key=lambda option: haversine(start["latitude"], start["longitude"], option["latitude"], option["longitude"]))

def clean_coordinate(value):
    """
    Cleans a latitude or longitude value by:
    - Removing degree symbols and extra text (e.g., 'N', 'S', 'E', 'W', 'degrees').
    - Converting directional coordinates (e.g., '40.7128 N' -> 40.7128, '74.006 W' -> -74.006).
    """
    if not isinstance(value, str):
        return None

    value = re.sub(r"[^\d.\-NSEW°']", "", value).strip()
    multiplier = -1 if "S" in value or "W" in value else 1
    value = re.sub(r"[^\d.]", "", value)

    try:
        return float(value) * multiplier
    except ValueError:
        return None

def clean_csv(input_file):
    """
    Cleans a CSV file by:
    - Detecting 'code', 'latitude', and 'longitude' columns dynamically.
    - Removing rows with missing 'code', 'latitude', or 'longitude' values.
    - Cleaning messy latitude/longitude formats.
    - Ensuring latitude is between -90 and 90, and longitude is between -180 and 180.
    - Overwriting the original file with cleaned data.
    """
    df = pd.read_csv(input_file, dtype=str)
    df.columns = [col.strip().lower() for col in df.columns]

    code_cols = ["code", "name", "identifier", "id"]
    lat_cols = ["latitude", "lat", "geo_lat", "latitud"]
    lon_cols = ["longitude", "long", "lng", "geo_lon", "lon"]

    code_col = next((col for col in df.columns if col in code_cols), None)
    lat_col = next((col for col in df.columns if col in lat_cols), None)
    lon_col = next((col for col in df.columns if col in lon_cols), None)

    if not code_col:
        first_col = df.columns[0]
        if first_col not in lat_cols + lon_cols:
            code_col = first_col
        else:
            print("ERROR: No valid identifier column found.")
            return None

    if not lat_col or not lon_col:
        print("ERROR: Missing necessary latitude/longitude columns.")
        return None

    df = df[[code_col, lat_col, lon_col]].rename(columns={code_col: "code", lat_col: "latitude", lon_col: "longitude"})

    df = df.dropna(subset=["code", "latitude", "longitude"])

    df["latitude"] = df["latitude"].apply(clean_coordinate)
    df["longitude"] = df["longitude"].apply(clean_coordinate)

    df = df.dropna(subset=["latitude", "longitude"])
    df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]

    df.to_csv(input_file, index=False)
    print(f"Cleaned CSV saved (replacing original): {input_file}")
    return input_file

def process_and_save_matches(your_points_file, option_points_file, output_file):
    """ Read CSVs, find closest matches, and save results. """

    clean_csv(your_points_file)
    clean_csv(option_points_file)

    your_points = pd.read_csv(your_points_file)
    option_points = pd.read_csv(option_points_file)

    required_cols = ["code", "latitude", "longitude"]
    if not all(col in your_points.columns for col in required_cols) or not all(col in option_points.columns for col in required_cols):
        raise ValueError("Missing required columns (code, latitude, longitude) in one or both files.")

    your_points["latitude"] = pd.to_numeric(your_points["latitude"], errors="coerce")
    your_points["longitude"] = pd.to_numeric(your_points["longitude"], errors="coerce")
    option_points["latitude"] = pd.to_numeric(option_points["latitude"], errors="coerce")
    option_points["longitude"] = pd.to_numeric(option_points["longitude"], errors="coerce")

    your_points = your_points.dropna(subset=["latitude", "longitude"])
    option_points = option_points.dropna(subset=["latitude", "longitude"])

    matched_pairs = []
    for _, your_point in your_points.iterrows():
        closest_option = find_closest_point(your_point, option_points.to_dict(orient="records"))
        matched_pairs.append({
            "your_code": your_point["code"],
            "your_latitude": your_point["latitude"],
            "your_longitude": your_point["longitude"],
            "matched_code": closest_option["code"],
            "matched_latitude": closest_option["latitude"],
            "matched_longitude": closest_option["longitude"],
            "distance_km": round(haversine(your_point["latitude"], your_point["longitude"], closest_option["latitude"], closest_option["longitude"]), 2)
        })

    output_df = pd.DataFrame(matched_pairs)
    output_df.to_csv(output_file, index=False)

    print(f"Matched pairs saved to {output_file}")
    return output_file

if __name__ == "__main__":
    print("Please place your CSV files in the following directories:")
    print(" - Your points CSV in: uploads/your_points/")
    print(" - Option points CSV in: uploads/option_points/")

    your_filename = input("Enter the name of your points file (e.g., your_file.csv): ").strip()
    option_filename = input("Enter the name of the option points file (e.g., option_file.csv): ").strip()

    your_points_file = f"uploads/your_points/{your_filename}"
    option_points_file = f"uploads/option_points/{option_filename}"
    output_file = "uploads/matched_pairs.csv"

    if not os.path.exists(your_points_file):
        print(f"File not found: {your_points_file}")
    if not os.path.exists(option_points_file):
        print(f"File not found: {option_points_file}")

    if os.path.exists(your_points_file) and os.path.exists(option_points_file):
        confirm = input(f"Files found:\n  - {your_points_file}\n  - {option_points_file}\nProceed with processing? (y/n): ").strip().lower()
        if confirm == "y":
            process_and_save_matches(your_points_file, option_points_file, output_file)
            print(f"Processing complete. Results saved in {output_file}")
        else:
            print("Processing canceled.")
    else:
        print("Required files are missing. Please ensure they are in the correct directories and try again.")
