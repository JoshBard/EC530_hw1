import pandas as pd
import re

def clean_coordinate(value):
    """
    Cleans a latitude or longitude value by:
    - Removing degree symbols and extra text (e.g., 'N', 'S', 'E', 'W', 'degrees').
    - Converting directional coordinates (e.g., '40.7128 N' -> 40.7128, '74.006 W' -> -74.006).

    Args:
        value (str): The raw latitude or longitude value.

    Returns:
        float or None: The cleaned coordinate as a float, or None if invalid.
    """

    if not isinstance(value, str):
        return None

    # Remove non-numeric characters except '.' and '-'
    value = re.sub(r"[^\d.\-NSEW°']", "", value).strip()

    # Convert coordinates with directional indicators
    if "S" in value or "W" in value:
        multiplier = -1
    else:
        multiplier = 1

    # Remove remaining non-numeric characters (e.g., degree symbols, extra spaces)
    value = re.sub(r"[^\d.]", "", value)

    try:
        return float(value) * multiplier
    except ValueError:
        return None

def clean_csv(input_file):
    """
    Cleans a CSV file by:
    - Detecting 'code', 'latitude', and 'longitude' columns dynamically.
    - Defaulting to the first column as 'code' if a proper identifier is missing.
    - Removing rows with missing 'code', 'latitude', or 'longitude' values.
    - Cleaning messy latitude/longitude formats.
    - Ensuring latitude is between -90 and 90, and longitude is between -180 and 180.
    - Overwriting the original file with cleaned data.

    Args:
        input_file (str): Path to the input CSV file.
    """

    # Read CSV while treating all columns as strings initially
    df = pd.read_csv(input_file, dtype=str)

    # Standardize column names by stripping spaces and converting to lowercase
    df.columns = [col.strip().lower() for col in df.columns]

    # Identify possible column names for 'code', 'latitude', and 'longitude'
    code_cols = ["code", "name", "identifier", "id"]
    lat_cols = ["latitude", "lat", "geo_lat", "latitud"]
    lon_cols = ["longitude", "long", "lng", "geo_lon", "lon"]

    # Find actual column names present in the CSV
    code_col = next((col for col in df.columns if col in code_cols), None)
    lat_col = next((col for col in df.columns if col in lat_cols), None)
    lon_col = next((col for col in df.columns if col in lon_cols), None)

    # If no code column is found, use the first column unless it's lat/lon
    if not code_col:
        first_col = df.columns[0]
        if first_col not in lat_cols + lon_cols:
            code_col = first_col
        else:
            print("ERROR: No valid identifier column found.")
            return None

    # Ensure latitude and longitude columns exist
    if not lat_col or not lon_col:
        print("ERROR: Missing necessary latitude/longitude columns.")
        return None

    # Keep only the necessary columns and rename them for consistency
    df = df[[code_col, lat_col, lon_col]].rename(columns={code_col: "code", lat_col: "latitude", lon_col: "longitude"})

    # Remove rows with empty 'code', 'latitude', or 'longitude'
    df = df.dropna(subset=["code", "latitude", "longitude"])

    # Clean latitude and longitude values
    df["latitude"] = df["latitude"].apply(clean_coordinate)
    df["longitude"] = df["longitude"].apply(clean_coordinate)

    # Drop rows with invalid lat/lon values
    df = df.dropna(subset=["latitude", "longitude"])

    # Remove nonsensical latitude/longitude values
    df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]

    # Overwrite the original file with cleaned data
    df.to_csv(input_file, index=False)
    
    print(f"Cleaned CSV saved (replacing original): {input_file}")
    return input_file

# Example usage
if __name__ == "__main__":
    input_file_path = "example_input.csv"  # Replace with actual file path
    clean_csv(input_file_path)
