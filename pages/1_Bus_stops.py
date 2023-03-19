import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from app.viz import (
    plot_ridership_average,
    map_bus_routes,
    plot_recovery_over_this_quarter,
    plot_bar_top_n_for_daterange,
    plot_scatter_mapbox,
)
from app.load_data import (
    get_rides,
    get_rides_quarterly,
    get_route_linestrings,
    get_bus_stops,
)
import geopandas as gpd

# from streamlit_plotly_events import plotly_events
from streamlit_plotly_mapbox_events import plotly_mapbox_events


st.set_page_config(
    layout="wide",
    page_icon="🚌",
    page_title="Explore MTA Bus Stops",
)

stops = get_bus_stops()
stops.index = stops["stop_id"]
st.header("Explore Bus Stops")
st.write("Click on a stop to see the routes served by that stop.")
fig = plot_scatter_mapbox(stops, color="rider_on", zoom=10, height=500)
# Update color scale


# Get mapbox events (clicks) from the user
mapbox_events = plotly_mapbox_events(
    fig,
    click_event=True,
)
# If the user clicks, get the index of the stop
if mapbox_events[0]:
    index_selection = mapbox_events[0][0]["pointIndex"]
    # Use the index to get the stop data from the stops GeoDataFrame
    series = stops.iloc[index_selection]
    # Get the latitude and longitude of the stop
    lat, lon = series["latitude"], series["longitude"]
    # Get the routes served by the stop
    routes_served = series["routes_served"]
    routes_served = routes_served.split(",")
    routes_served = [x.strip() for x in routes_served]
    # Print the routes served to the Streamlit app
    # Get the linestrings of the routes served
    routes_linestrings = get_route_linestrings()
    # routes_linestrings = routes_linestrings[routes_linestrings["route"].isin(routes_served)]
    st.subheader("Routes Served")

    col1, col2 = st.columns([2, 1])
    # Plot the map of the routes served
    with col1:
        map = map_bus_routes(
            routes_linestrings,
            route_numbers=routes_served,
            highlight_routes=True,
            height=500,
            width=800,
        )
    with col2:
        st.dataframe(series, use_container_width=True)
