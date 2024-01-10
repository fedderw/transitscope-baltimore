import requests
import geopandas as gpd
from datetime import datetime
from janitor import clean_names

def download_mta_bus_stops(ridership_period, file_destination):
    # Endpoint for the metadata
    metadata_url = "https://geodata.md.gov/imap/rest/services/Transportation/MD_Transit/FeatureServer/9?f=pjson"

    # Making a request to the metadata endpoint
    metadata_response = requests.get(metadata_url)
    
    # Check if the request was successful
    if metadata_response.status_code == 200:
        # Extracting description from the metadata
        description = metadata_response.json().get("description", "No description available")
        print("Description from Metadata:", description)
    else:
        print("Failed to retrieve metadata")

    # Downloading the data
    stops = gpd.read_file("https://geodata.md.gov/imap/rest/services/Transportation/MD_Transit/FeatureServer/9/query?where=1%3D1&outFields=*&outSR=4326&f=geojson")

    # Cleaning column names
    stops = stops.clean_names()

    # Extracting latitude and longitude
    stops['latitude'] = stops['geometry'].y
    stops['longitude'] = stops['geometry'].x

    # Adding ridership period and download date
    stops['ridership_period'] = ridership_period
    stops['download_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Displaying the first few rows of the dataframe
    print(stops.head())

    # Saving the data to a parquet file
    stops.to_parquet(file_destination, index=False)

    print(f"Data saved to {file_destination}")

if __name__ == "__main__":
    # Example usage of the function
    download_mta_bus_stops("Summer 2023", "data/mta_bus_stops.parquet")
