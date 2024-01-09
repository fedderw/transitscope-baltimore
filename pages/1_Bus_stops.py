from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import geopandas as gpd
import leafmap.foliumap as leafmap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import shapely.geometry
import streamlit as st
from streamlit_plotly_mapbox_events import plotly_mapbox_events
from ppprint import ppprint 
from pprint import pprint as print

from app.constants import CITYLINK_COLORS
from app.load_data import (
    get_bus_stops,
    get_rides,
    get_rides_quarterly,
    get_route_linestrings,
)
from app.viz import (
    plot_bar_top_n_for_daterange,
    plot_recovery_over_this_quarter,
    plot_ridership_average,
)

st.set_page_config(
    layout="wide",
    page_icon="🚌",
    page_title="Explore MTA Bus Stops",
)

# Get the linestrings of the routes served
routes_linestrings = get_route_linestrings()

# M


def map_bus_routes(
    gdf: gpd.GeoDataFrame,
    route_numbers: List[str],
    highlight_routes: bool = False,
    width: int = 400,
    height: int = 400,
    bus_stop_x: float = None,
    bus_stop_y: float = None,
):
    """
    > This function takes a GeoDataFrame of bus routes, a list of route numbers, and a boolean
    indicating whether to highlight the selected routes, and returns a map of the bus routes.

    :param gdf: The GeoDataFrame containing the bus routes
    :type gdf: gpd.GeoDataFrame
    :param route_numbers: A list of route numbers to highlight
    :type route_numbers: List[str]
    :param highlight_routes: If True, the selected routes will be highlighted in red, and all other
    routes will be gray, defaults to False
    :type highlight_routes: bool (optional)
    :param width: int=400, height: int=400, defaults to 400
    :type width: int (optional)
    :param height: int=400, width: int=400, defaults to 400
    :type height: int (optional)
    """

    # Get the data for the route
    route = gdf[gdf["route"].isin(route_numbers)]

    # Create a map
    m = leafmap.Map(draw_control=False)
    # Use a light basemap
    m.add_basemap("CartoDB.Positron")  # Change basemap to "CartoDB.Positron"
    # Turn off the toolbar
    m.toolbar = False
    # Show the route highlighted in red, then plot all the other routes in gray
    if highlight_routes:
        non_highlighted_routes = gdf[~gdf["route"].isin(route_numbers)]
        # Add the bus routes to the map
        m.add_gdf(
            non_highlighted_routes,
            layer_name="Other Bus Routes",
            style={"color": "black", "weight": 1, "opacity": 1},
        )
        m.add_gdf(
            route,
            layer_name="Selected Bus Routes",
            style={"color": "red", "weight": 3, "opacity": 1},
        )
    else:
        # Add the bus routes to the map
        m.add_gdf(
            route,
            layer_name="Bus Routes",
            # Color the routes by route number
            style_function=lambda x: {
                "color": CITYLINK_COLORS[x["properties"]["route"]]
                if x["properties"]["route"] in CITYLINK_COLORS
                else "black",
                "weight": 3
                if x["properties"]["route"] in CITYLINK_COLORS
                else 1,
                "opacity": 0.8,
            },
        )
    # Add a marker for the bus stop
    if bus_stop_x and bus_stop_y:
        m.add_marker(
            [bus_stop_y, bus_stop_x],
            layer_name="Bus Stop",
            popup="Bus Stop",
        )
    # Zoom to the bus routes
    m.zoom_to_gdf(route)
    # Display the map
    return m.to_streamlit(height=height, width=width)


def plot_scatter_mapbox(gdf: gpd.GeoDataFrame, **kwargs):
    fig = px.scatter_mapbox(
        gdf,
        lat=gdf.geometry.y,
        lon=gdf.geometry.x,
        opacity=0.6,
        **kwargs,
    )
    # fig.update_traces(marker=dict(color='#FF5F1F'))
    # Change mapbox style
    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


stops = get_bus_stops()
print(f"number of stops: {len(stops)}")
stops=stops.dropna().reset_index(drop=True)
print(f"number of stops after dropping na: {len(stops)}")
# Set the index to the stop_id
stops['df_index'] = stops.index
stops = stops.set_index("stop_id")
stops["stop_id"] = stops.index
# So
st.header("Explore Bus Stops")
st.write(
    "Click on a stop to see the routes served by that stop. The size of the marker is proportional to the number of boardings at the stop. Ridership data is from September 2022-Early February 2023. The routes may not be concurrent with service changes. Fixing those is on the to-do list."
)

fig = plot_scatter_mapbox(
    gdf=stops,
    height=600,
    size_max=30,
    hover_data=[
        # "index",
        "objectid",
        "stop_id",
        "stop_name",
        "rider_on",
        "rider_off",
        "rider_total",
        "routes_served",
        "shelter",
        "df_index",
        "latitude",
        "longitude",
    ],
    # custom_data=[
    #     # "index",
    #     "objectid",
    #     "stop_id",
    #     "stop_name",
    #     "rider_on",
    #     "routes_served",
    #     "shelter",
    #     "df_index"
    # ],
    size="rider_total",
    zoom=10,
    # color="shelter",
    # color_discrete_map={"Yes": "purple", "No": "orange"},
)


# Get mapbox events (clicks) from the user
mapbox_events = plotly_mapbox_events(
    fig,
    click_event=True,
    key="mapbox_events",
)
# If the user clicks, get the index of the stop
# print(st.session_state.keys())
plot_name_holder_clicked = st.empty()
# plot_name_holder_clicked.write(f"Clicked Point: {mapbox_events[0]}")
if mapbox_events[0]:
    index_selection = mapbox_events[0][0]["pointIndex"]
    # ppprint(f"mapbox_events[0][0]: {mapbox_events[0][0]}")
    # print(f"point index: {index_selection}")
    # Use the index to get the stop data from the stops GeoDataFrame
    # series = stops.iloc[index_selection]
    # series.name = stops.iloc[index_selection]["stop_id"]
    # print(f"series: {series}")
    # print(f"index selection: {index_selection}")
    # print(f"index selection type: {type(index_selection)}")
    # print(f"index_selection + 1: {index_selection + 1}")
    # print(f"series.index: {series.index}")
    # print(f"series.stop_id: {series.stop_id}")
    # print(f"series.name: {series.name}")
    # print(f"series.stop_name: {series['stop_name']}")

    # print(
    #     f"series.routes_served: {series['routes_served']}",
    # )
    
    # Try selection the data from the fig object
    # print(f"{fig.data[0]}")
    # We can use the index to get the data from the fig object
    # st.write(fig.data[0].customdata[index_selection])
    print(f"len(fig.data[0].customdata): {len(fig.data[0].customdata)}")
    # st.write(fig.data[0])
    print(f"routes_served: {fig.data[0].customdata[index_selection][4]}")
    print(f"Type of fig.data[0].customdata[index_selection]: {type(fig.data[0].customdata[index_selection])}")
    # Get the latitude and longitude of the stop
    lat, lon = fig.data[0].customdata[index_selection][9], fig.data[0].customdata[index_selection][10]
    # Get the routes served by the stop
    routes_served = fig.data[0].customdata[index_selection][6]
    routes_served = routes_served.split(",")
    routes_served = [x.strip() for x in routes_served]
    # There are some strings that are separated by semi-colons instead of commas
    routes_served = [x.split(";") for x in routes_served]
    routes_served = [item for sublist in routes_served for item in sublist]
    routes_served = [x.strip() for x in routes_served]
    # Print the routes served to the Streamlit app

    # routes_linestrings = routes_linestrings[routes_linestrings["route"].isin(routes_served)]
    st.subheader("Routes Served")

    # Plot the map of the routes served
    map = map_bus_routes(
        routes_linestrings,
        route_numbers=routes_served,
        highlight_routes=False,
        height=500,
        width=800,
        bus_stop_x=lon,
        bus_stop_y=lat,
    )


# for key in st.session_state.keys():
# st.write(key)
