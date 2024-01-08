import geopandas as gpd
import janitor

# Define the URL of the ArcGIS polygon layer in GeoJSON format
url = "https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/services/Existing_Walkshed_Areas/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"

# Read the GeoJSON data into a GeoDataFrame
gdf = gpd.read_file(url).clean_names()
gdf.to_file("../data/mta_rail_walksheds.geojson", driver="GeoJSON")
