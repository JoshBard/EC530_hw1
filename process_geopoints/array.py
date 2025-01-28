import pandas as pd
import math
import os
import re

# Haversine function to calculate the distance between two points helped by ChatGPT
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_closest_point(start, options):
    return min(options, key=lambda option: haversine(start["latitude"], start["longitude"], option["latitude"], option["longitude"]))

def clean_coordinate(value):
    """
    Cleans and converts a coordinate (latitude or longitude) from various formats:
    - Decimal Degrees (DD): "40.7128 N" → 40.7128
    - Degrees and Minutes (DM): "34°03' N" → 34.05
    - Degrees, Minutes, and Seconds (DMS): "34°03'30\" N" → 34.0583
    """
    if not isinstance(value, str):
        return None

    value = value.strip().upper()

    # Ensure the format is correct
    if not re.match(r"^\d+°?\d*'?(\d*\"?)?\s?[NSEW]?$", value):
        return None  # Reject invalid formats like "N 40.7128"

    # Determine multiplier for direction (N/E = positive, S/W = negative)
    multiplier = -1 if 'S' in value or 'W' in value else 1

    # Remove non-numeric characters except '.', '-', '°', "'", and '"'
    cleaned_value = re.sub(r"[^0-9.\-°'\"]", " ", value).strip()

    # Check for Degrees, Minutes, and Seconds (DMS) format: "34°03'30" N"
    match = re.match(r"^(\d+)°(\d+)'(\d+(?:\.\d*)?)\"", cleaned_value)
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))

        # Validate ranges
        if not (0 <= minutes < 60 and 0 <= seconds < 60) or degrees > 180:
            return None  # Reject invalid values

        decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
        decimal_degrees *= multiplier

        # Ensure valid latitude and longitude ranges
        if abs(decimal_degrees) > 180 or (abs(decimal_degrees) > 90 and 'N' in value or 'S' in value):
            return None

        return round(decimal_degrees, 6)

    # Check for Degrees and Minutes (DM) format: "34°03' N"
    match = re.match(r"^(\d+)°(\d+(?:\.\d*)?)'", cleaned_value)
    if match:
        degrees = int(match.group(1))
        minutes = float(match.group(2))

        # Validate ranges
        if not (0 <= minutes < 60) or degrees > 180:
            return None

        decimal_degrees = degrees + (minutes / 60)
        decimal_degrees *= multiplier

        # Ensure valid latitude and longitude ranges
        if abs(decimal_degrees) > 180 or (abs(decimal_degrees) > 90 and 'N' in value or 'S' in value):
            return None

        return round(decimal_degrees, 6)

    # Handle plain decimal degrees (DD)
    try:
        numeric_value = float(re.sub(r"[^\d.\-]", "", cleaned_value))
        
        # Ensure valid latitude and longitude ranges
        if abs(numeric_value) > 180 or (abs(numeric_value) > 90 and 'N' in value or 'S' in value):
            return None

        return round(numeric_value * multiplier, 6)
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
