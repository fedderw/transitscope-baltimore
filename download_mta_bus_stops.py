import argparse
import requests
import geopandas as gpd
from datetime import datetime
from janitor import clean_names

# Function to download MTA bus stops data
def download_mta_bus_stops(ridership_period, file_destination):
    metadata_url = "https://geodata.md.gov/imap/rest/services/Transportation/MD_Transit/FeatureServer/9?f=pjson"
    metadata_response = requests.get(metadata_url)
    if metadata_response.status_code == 200:
        description = metadata_response.json().get("description", "No description available")
        print("Description from Metadata:", description)
    else:
        print("Failed to retrieve metadata")

    stops = gpd.read_file("https://geodata.md.gov/imap/rest/services/Transportation/MD_Transit/FeatureServer/9/query?where=1%3D1&outFields=*&outSR=4326&f=geojson")
    stops = stops.clean_names()
    stops['latitude'] = stops['geometry'].y
    stops['longitude'] = stops['geometry'].x
    stops['ridership_period'] = ridership_period
    stops['download_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(stops.head())
    stops.to_parquet(file_destination)
    print(f"Data saved to {file_destination}")

# Main function to parse arguments and call download function
def main():
    parser = argparse.ArgumentParser(description='Download MTA Bus Stops Data')
    parser.add_argument('ridership_period', type=str, help='Ridership period for the data')
    parser.add_argument('file_destination', type=str, help='Destination file path to save the data')
    args = parser.parse_args()
    download_mta_bus_stops(args.ridership_period, args.file_destination)

if __name__ == "__main__":
    main()
