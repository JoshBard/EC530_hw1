import pandas as pd
import math
import os
import re

# Haversine function to calculate the distance between two points helped by ChatGPT
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth."""
    R = 6371.0
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
    if not isinstance(value, str):
        return None

    value = re.sub(r"[^\d.\-NSEW°']", "", value).strip()
    multiplier = -1 if "S" in value or "W" in value else 1
    value = re.sub(r"[^\d.]", "", value)

    try:
        return float(value) * multiplier
    except ValueError:
        return None

import pandas as pd
import re

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
    df = pd.read_csv(input_file, dtype=str)

    # Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]

    # Identify latitude and longitude columns
    lat_cols = ["latitude", "lat", "geo_lat", "latitud"]
    lon_cols = ["longitude", "long", "lng", "geo_lon", "lon"]

    lat_col = next((col for col in df.columns if col in lat_cols), None)
    lon_col = next((col for col in df.columns if col in lon_cols), None)

    if not lat_col or not lon_col:
        print("ERROR: Missing necessary latitude/longitude columns.")
        return None

    # Rename latitude and longitude columns for consistency but keep all columns
    df = df.rename(columns={lat_col: "latitude", lon_col: "longitude"})

    # Convert and clean latitude/longitude while keeping all other columns
    df["latitude"] = df["latitude"].apply(clean_coordinate)
    df["longitude"] = df["longitude"].apply(clean_coordinate)

    # Drop rows with invalid lat/lon values but keep all columns
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]

    # Save the cleaned CSV, keeping all original columns
    df.to_csv(input_file, index=False)
    print(f"Cleaned CSV saved (replacing original): {input_file}")
    return input_file


def process_and_save_matches(your_points_file, option_points_file, output_file):
    """ Read CSVs, find closest matches, and save results. """

    clean_csv(your_points_file)
    clean_csv(option_points_file)

    your_points = pd.read_csv(your_points_file)
    option_points = pd.read_csv(option_points_file)

    required_cols = ["latitude", "longitude"]
    if not all(col in your_points.columns for col in required_cols) or not all(col in option_points.columns for col in required_cols):
        raise ValueError("Missing required columns (latitude, longitude) in one or both files.")

    your_points["latitude"] = pd.to_numeric(your_points["latitude"], errors="coerce")
    your_points["longitude"] = pd.to_numeric(your_points["longitude"], errors="coerce")
    option_points["latitude"] = pd.to_numeric(option_points["latitude"], errors="coerce")
    option_points["longitude"] = pd.to_numeric(option_points["longitude"], errors="coerce")

    your_points = your_points.dropna(subset=["latitude", "longitude"])
    option_points = option_points.dropna(subset=["latitude", "longitude"])

    matched_pairs = []

    for _, your_point in your_points.iterrows():
        closest_option = find_closest_point(your_point, option_points.to_dict(orient="records"))

        # Combine all columns from both dataframes
        matched_entry = {
            f"your_{col}": your_point[col] for col in your_points.columns
        }
        matched_entry.update({
            f"matched_{col}": closest_option[col] for col in option_points.columns
        })

        matched_pairs.append(matched_entry)

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
