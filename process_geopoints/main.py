import pandas as pd
import math
import os
import re
import logging
import cProfile
import pstats

logging.basicConfig(
    filename='app.log', 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
    logging.info("Finding the closest point for: ", start, ".")
    return min(options, key=lambda option: haversine(start["latitude"], start["longitude"], option["latitude"], option["longitude"]))

# Parsing functions, got some help from ChatGPT on these as well
def clean_coordinate(value):
    if not isinstance(value, str):
        logging.warning("No value found in clean coordinates.")
        return None

    value = value.strip().upper()

    # Determine multiplier for direction (N/E = positive, S/W = negative)
    multiplier = -1 if 'S' in value or 'W' in value else 1

    # Ensure only valid characters are present
    cleaned_value = re.sub(r"[^0-9.\-°'\"]", " ", value).strip()

    # Check for Degrees, Minutes, and Seconds (DMS) format: "34°03'30" N"
    match = re.match(r"^(\d+)°(\d+)'(\d+(?:\.\d*)?)\"", cleaned_value)
    if match:
        logging.warning("DMS format found in clean coordinates.")
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))

        # Validate ranges
        if not (0 <= minutes < 60 and 0 <= seconds < 60):
            return None

        decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
        return round(decimal_degrees * multiplier, 6)

    # Check for Degrees and Minutes (DM) format
    match = re.match(r"^(\d+)°(\d+(?:\.\d*)?)'", cleaned_value)
    if match:
        logging.warning("DM format found in clean coordinates.")
        degrees = int(match.group(1))
        minutes = float(match.group(2))

        # Validate ranges
        if not (0 <= minutes < 60):
            return None

        decimal_degrees = degrees + (minutes / 60)
        return round(decimal_degrees * multiplier, 6)

    # Handle plain decimal degrees (DD)
    try:
        logging.info("DD format found in clean coordinates.")
        numeric_value = float(re.sub(r"[^\d.\-]", "", cleaned_value))
        
        # Validate latitude and longitude ranges
        if abs(numeric_value) > 180:
            return None

        return round(numeric_value * multiplier, 6)
    except ValueError:
        return None
    
def clean_csv(input_file):
    logging.info("Cleaning csv: ", input_file, ".")
    df = pd.read_csv(input_file, dtype=str)

    # Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]

    # Identify latitude and longitude columns
    lat_cols = ["latitude", "lat", "geo_lat", "latitud"]
    lon_cols = ["longitude", "long", "lng", "geo_lon", "lon"]

    lat_col = next((col for col in df.columns if col in lat_cols), None)
    lon_col = next((col for col in df.columns if col in lon_cols), None)

    if not lat_col or not lon_col:
        logging.error("No latitude or longitude column found.")
        return None

    # Rename latitude and longitude columns for consistency
    df = df.rename(columns={lat_col: "latitude", lon_col: "longitude"})

    # Convert and clean latitude/longitude while keeping all other columns
    df["latitude"] = df["latitude"].apply(clean_coordinate)
    df["longitude"] = df["longitude"].apply(clean_coordinate)

    # Drop rows with invalid lat/lon values
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]

    # Save the cleaned CSV, keeping all original columns
    df.to_csv(input_file, index=False)
    print(f"Cleaned CSV saved (replacing original): {input_file}")
    return input_file


def process_and_save_matches(your_points_file, option_points_file, output_file):
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

    logging.info("Dropping NaN values from csvs.")
    your_points = your_points.dropna(subset=["latitude", "longitude"])
    option_points = option_points.dropna(subset=["latitude", "longitude"])

    matched_pairs = []

    for _, your_point in your_points.iterrows():
        closest_option = find_closest_point(your_point, option_points.to_dict(orient="records"))

        matched_entry = {
            f"your_{col}": your_point[col] for col in your_points.columns
        }
        matched_entry.update({
            f"matched_{col}": closest_option[col] for col in option_points.columns
        })

        matched_pairs.append(matched_entry)

    output_df = pd.DataFrame(matched_pairs)
    output_df.to_csv(output_file, index=False)

    logging.info("Matched pairs saved to ", output_file, ".")
    return output_file

# Prompts the user to create or upload a .csv
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
            print("Profiling execution...")

            with cProfile.Profile() as pr:
                process_and_save_matches(your_points_file, option_points_file, output_file)

            # Save profiling results
            pr.dump_stats("profile_results.prof")

            # Display top 10 slowest functions
            stats = pstats.Stats(pr)
            stats.strip_dirs().sort_stats("cumulative").print_stats(10)

            print(f"Processing complete. Results saved in {output_file}. Profiling saved to profile_results.prof")
        else:
            print("Processing canceled.")

    else:
        print("Required files are missing. Please ensure they are in the correct directories and try again.")