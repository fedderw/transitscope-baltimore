import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from viz import plot_ridership_average, map_bus_routes
import geopandas as gpd
from streamlit_extras.badges import badge


st.set_page_config(
layout="wide", 
page_title="MTA Bus Ridership"
)

@st.cache_data
def get_rides(file_path="data/mta_bus_ridership.parquet"):
    """Get the MTA bus ridership data"""
    rides = pd.read_parquet(file_path)
    return rides[[ "route","date", "ridership_weekday",'ridership']]

@st.cache_data
def get_rides_quarterly(file_path="data/mta_bus_ridership_quarterly.parquet"):
    """Get the MTA bus ridership data"""
    rides = pd.read_parquet(file_path)
    return rides[[ "route","date", "ridership_weekday",'quarter_year','ridership']]

@st.cache_data
def get_route_linestrings(file_path="data/mta_bus_route_linestring.geojson"):
    """Get the MTA bus ridership data"""
    gdf = gpd.read_file(file_path)
    # The geometry column contains many multiline strings	, so we need to convert them to single linestrings
    
    return gdf
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')




rides = get_rides_quarterly()
route_linestrings = get_route_linestrings()
csv = convert_df(rides)
# Streamlit app
st.title("MTA Bus Ridership")
st.sidebar.title("TransitScope Baltimore")
# Get the top 5 routes from 2022, group by route number and sum the ridership
top_5_routes = rides[rides["date"] >= datetime(2022, 1, 1)].groupby("route")["ridership"].sum().sort_values(ascending=False).head(5).reset_index()["route"].tolist()
print(type(top_5_routes))
route_numbers = st.sidebar.multiselect(
    "Select routes", list(rides["route"].unique()), default=top_5_routes,
)

highlight_routes=st.sidebar.checkbox("Show unselected bus routes on map", value=False)

if route_numbers:
    # Add a toggle to set y-axis to start at 0
    
    # Plot the average ridership for the selected routes
    fig = plot_ridership_average(rides, 
                                # Do the top 5 routes from 2022
                                route_numbers=route_numbers, 
                                start_date= datetime(2018, 1, 1), 
                                end_date=datetime(2022, 12, 31), 
                                y_axis_zero = True
                                )
    col1, col2 = st.columns([3,2])
    with col1:
        st.plotly_chart(
            fig, 
            use_container_width=True,
            # Increase height of chart
            height=900,
            )
        y_axis_zero = st.sidebar.checkbox("Y-axis starts at 0", value=True)

    with col2:
        
        map_bus_routes(route_linestrings, route_numbers,highlight_routes=highlight_routes)
    # st.markdown("### Ridership Data")
    # dataframe = (rides[rides["route"].isin(route_numbers)])
    # filtered_dataframe = dataframe_explorer(dataframe)
    # st.dataframe(filtered_dataframe, use_container_width=True)
    # Add a download link for the data
    st.download_button(
        label="Download full dataset as CSV",
        data=csv,
        file_name='mta_bus_ridership_quarterly.csv',
        mime='text/csv',
    )
   

else:
    # Show a message if no routes are selected
    st.warning("Please select at least one route.")
badge(type="twitter", name="willfedder")
badge(type="github", name="fedderw/transitscope-baltimore")
st.sidebar.write("App created by [Will Fedder](https://linkedin.com/in/fedderw).")
st.sidebar.write("Data provided by [MDOT MTA](https://www.arcgis.com/apps/dashboards/1bbc19f2abfe4fde94e4c563f5e8371c). To view a geographic system map in PDF format, visit the [MTA's website](https://s3.amazonaws.com/mta-website-staging/mta-website-staging/files/System%20Maps/Geographic_System_Map_08_2022.pdf).") 
st.sidebar.write("Data extracted using this [script](https://github.com/jamespizzurro/mta-bus-ridership-scraper) authored by James Pizzurro.")


