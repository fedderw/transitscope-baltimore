from datetime import datetime
from pprint import pprint as print
from typing import Dict, List, Optional, Tuple, Union

import folium
import geopandas as gpd
import leafmap.foliumap as leafmap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import shapely.geometry
import streamlit as st
from annotated_text import annotated_text
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from streamlit_plotly_mapbox_events import plotly_mapbox_events

from app.constants import CITYLINK_COLORS
from app.load_data import (get_bus_stops, get_rides, get_rides_quarterly,
                           get_route_linestrings)
from app.viz import (plot_bar_top_n_for_daterange,
                     plot_recovery_over_this_quarter, plot_ridership_average)

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
        **kwargs,
    )
    # fig.update_traces(marker=dict(color='#FF5F1F'))
    # Change mapbox style
    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


tab1, tab2, tab3 = st.tabs(["Bus Stops", "Shelters", "Ridership Heatmap"])

stops = get_bus_stops()
print(f"number of stops: {len(stops)}")
# stops=stops.dropna().reset_index(drop=True)
# Map "yes" and "no" to True and False for the shelter column
stops["shelter"] = (
    stops["shelter"].map({"Yes": True, "No": False}).astype(bool)
)
# Fill in missing values for the shelter column
stops["shelter"] = stops["shelter"].fillna(False)
print(f"number of stops after dropping na: {len(stops)}")
# Set the index to the stop_id
stops["df_index"] = stops.index
stops = stops.set_index("stop_id")
stops["stop_id"] = stops.index
# So

with tab1:
    st.header("Explore Bus Stops")

    st.write(
        "Click on a stop to see the routes served by that stop.  Ridership data is from Summer 2023. The routes may not be concurrent with service changes. Fixing those is on the to-do list."
    )

    fig = plot_scatter_mapbox(
        gdf=stops,
        height=600,
        # size_max=30,
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
        # size="rider_total",
        zoom=10,
        opacity=0.5,
        # For some reason, using color only returns an array of length 527 in the customdata, so we can't use it to select routes
        # color="shelter",
        # color_discrete_map={True: "green", False: "orange"},
    )
    fig.update_traces(marker=dict(color="blue"))

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

        # print(f"len(fig.data[0].customdata): {len(fig.data[0].customdata)}")
        # print(f"routes_served: {fig.data[0].customdata[index_selection][6]}")
        # Show a badge with each route served

        # print(f"Type of fig.data[0].customdata[index_selection]: {type(fig.data[0].customdata[index_selection])}")
        # Get the latitude and longitude of the stop
        lat, lon = (
            fig.data[0].customdata[index_selection][9],
            fig.data[0].customdata[index_selection][10],
        )
        # Get the routes served by the stop
        routes_served = fig.data[0].customdata[index_selection][6]
        routes_served = routes_served.split(",")
        routes_served = [x.strip() for x in routes_served]
        # There are some strings that are separated by semi-colons instead of commas
        routes_served = [x.split(";") for x in routes_served]
        routes_served = [item for sublist in routes_served for item in sublist]
        routes_served = [x.strip() for x in routes_served]

        # st.subheader("Routes Served")
        annotated_text(
            "Routes Served: ",
            [
                (
                    route,
                    "",
                    CITYLINK_COLORS[route]
                    if route in CITYLINK_COLORS
                    else None,
                )
                for route in routes_served
            ],
        )

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

with tab2:
    st.header("Explore Shelters")
    col1, col2, col3 = st.columns([1, 1, 1])
    col1.metric("Sheltered", stops["shelter"].sum())
    col2.metric("Unsheltered", (~stops["shelter"]).sum())
    col3.metric("Total", len(stops))
    # Create an option to size the points by ridership
    size_by_ridership = st.checkbox("Size points by average daily boardings")
    if size_by_ridership:
        stops_selection = stops[stops["rider_on"] > 0]
    else:
        stops_selection = stops
    fig2 = plot_scatter_mapbox(
        gdf=stops_selection,
        height=600,
        width=800,
        # size_max=40,
        hover_data=[
            "stop_id",
            "stop_name",
            "rider_on",
            "rider_off",
            "rider_total",
            "routes_served",
            "shelter",
        ],
        size=stops_selection["rider_on"].values if size_by_ridership else None,
        zoom=10,
        opacity=0.5,
        # For some reason, using color only returns an array of length 527 in the customdata, so we can't use it to select routes
        color="shelter",
        color_discrete_map={True: "blue", False: "orange"},
    )
    fig2
    # Create a bar graph comparing the number of boardings at sheltered and unsheltered stops
    grouped_by_shelter = (
        stops[["shelter", "rider_on"]].groupby("shelter").sum().reset_index()
    )
    grouped_by_shelter["shelter_text"] = grouped_by_shelter["shelter"].map(
        {True: "Sheltered", False: "Unsheltered"}
    )
    fig3 = px.bar(
        grouped_by_shelter,
        y="shelter_text",
        x="rider_on",
        color="shelter_text",
        color_discrete_map={"Sheltered": "blue", "Unsheltered": "orange"},
    )
    fig3.update_layout(showlegend=False)
    fig3.update_xaxes(title_text="Average Daily Boardings, Summer 2023")
    fig3.update_yaxes(title_text="")
    # Add a title
    fig3.update_layout(
        title_text="Daily Boardings at Sheltered vs. Unsheltered Stops, Summer 2023",
        title_x=0.2,
        title_y=0.95,
    )
    # Label the bars to "Sheltered" and "Unsheltered" instead of "True" and "False"
    fig3.update_traces(
        texttemplate="%{x:.2s}",
        textposition="outside",
    )
    # st.header("Boardings at Sheltered vs. Unsheltered Stops")
    fig3
    # <------------------------>
    # Creat a new dataframe where each row is identified by a route, a stop, and a shelter. Since each stop can have multiple routes, we need to create a new row for each route
    route_stop = stops.copy()
    # Drop geometry column
    route_stop = route_stop.drop(columns=["geometry"])
    # Convert from geodataframe to dataframe

    # We need to split on commas and semicolons
    route_stop["routes_served"] = route_stop["routes_served"].str.split(",")
    # st.dataframe(route_stop)
    route_stop = route_stop.explode("routes_served")
    # Split on semicolons
    route_stop["routes_served"] = route_stop["routes_served"].str.split(";")
    route_stop = route_stop.explode("routes_served")
    # st.dataframe(route_stop)
    route_stop["routes_served"] = route_stop["routes_served"].str.strip()

    # Dictionary mapping short color codes to their corresponding CityLink route names
    color_to_citylink = {
        "BL": "CityLink Blue",
        "BR": "CityLink Brown",
        "CityLink BLUE": "CityLink Blue",
        "CityLink NAVY": "CityLink Navy",
        "CityLink ORANGE": "CityLink Orange",
        "CityLink RED": "CityLink Red",
        "CityLink SILVER": "CityLink Silver",
        "GD": "CityLink Gold",
        "GR": "CityLink Green",
        "LM": "CityLink Lime",
        "NV": "CityLink Navy",
        "OR": "CityLink Orange",
        "PK": "CityLink Pink",
        "PR": "CityLink Purple",
        "RD": "CityLink Red",
        "SV": "CityLink Silver",
        "YW": "CityLink Yellow",
    }

    # Function to map colors to their full names, keeping unmatched values
    def map_color_to_citylink(color):
        return color_to_citylink.get(color, color)

    # Apply the function to the 'routes_served' column
    route_stop["routes_served"] = route_stop["routes_served"].apply(
        map_color_to_citylink
    )
    # st.dataframe(route_stop)

    # Group by route and shelter
    grouped_by_route_shelter = (
        route_stop[
            [
                "routes_served",
                "stop_id",
                "shelter",
            ]
        ]
        .groupby(["routes_served"])
        .sum("shelter")
        .reset_index()
        .sort_values(by="shelter", ascending=False)
    )
    # Rename the columns
    grouped_by_route_shelter = grouped_by_route_shelter.rename(
        columns={
            "routes_served": "route",
            "shelter": "number_of_sheltered_stops",
        }
    )
    # Replace NaN values with 0
    grouped_by_route_shelter = grouped_by_route_shelter.fillna(0)
    # Create a vertical bar chart showing the number of sheltered stops for each route
    fig4 = px.bar(
        grouped_by_route_shelter,
        y="route",
        x="number_of_sheltered_stops",
        color="route",
        color_discrete_map=CITYLINK_COLORS,
        width=800,
        height=2000,
    )
    fig4.update_layout(showlegend=False)
    fig4.update_xaxes(title_text="")
    fig4.update_yaxes(title_text="Number of Sheltered Stops")
    # Add a title
    fig4.update_layout(
        title_text="Number of Sheltered Stops by Route",
        title_x=0.2,
        # title_y=0.95,
    )
    # iterate through the traces and apply the CITYLINK_COLORS to the plot
    for i, trace in enumerate(fig4.data):
        if trace.name in CITYLINK_COLORS:
            trace.marker.color = CITYLINK_COLORS[trace.name]
        else:
            trace.marker.color = "gray"
    fig4.update_traces(
        texttemplate="%{x:.0s}",
        textposition="outside",
    )

    # Counting sheltered and total stops for each route
    total_counts = (
        route_stop[["routes_served", "shelter"]]
        .groupby(["routes_served"])
        .count()
        .reset_index()
        .sort_values(by="shelter", ascending=False)
    )
    total_counts = total_counts.rename(
        columns={"routes_served": "route", "shelter": "total_stops"}
    )
    # Replace NaN values with 0
    total_counts = total_counts.fillna(0)

    # Merging the counts
    merged_data = pd.merge(
        grouped_by_route_shelter, total_counts, on="route"
    ).reset_index(drop=True)

    # Calculating the percentage of sheltered stops
    merged_data["sheltered_percentage"] = (
        merged_data["number_of_sheltered_stops"]
        / merged_data["total_stops"]
        * 100
    )
    merged_data = merged_data.sort_values(
        by="sheltered_percentage", ascending=False
    )
    # Make sure route names are strings
    merged_data["route"] = merged_data["route"].astype(str)
    # Plotting the graph
    fig5 = px.bar(
        merged_data,
        y="route",
        x="sheltered_percentage",
        color="route",
        color_discrete_map=CITYLINK_COLORS,
        width=800,
        height=2000,
    )
    fig5.update_layout(showlegend=False)
    fig5.update_yaxes(title_text="")
    fig5.update_xaxes(title_text="Percentage of Sheltered Stops")
    # Add a title
    fig5.update_layout(
        title_text="Percentage of Sheltered Stops by Route",
        title_x=0.2,
    )
    # iterate through the traces and apply the CITYLINK_COLORS to the plot
    for i, trace in enumerate(fig5.data):
        if trace.name in CITYLINK_COLORS:
            trace.marker.color = CITYLINK_COLORS[trace.name]
        else:
            trace.marker.color = "gray"
    fig5.update_traces(
        # Format the x-axis as a percentage
        texttemplate="%{x:.0f}%",
        textposition="outside",
    )
    fig5.update_yaxes(type="category")

    # Select an option to show the bar graph of sheltered stops by route as a percentage of total stops or as a raw count
    show_as_percentage = st.checkbox("Show as percentage of total stops")
    if show_as_percentage:
        fig5
    else:
        fig4


with tab3:
    st.header("Explore Ridership")
    st.write(
        "This is a heatmap of MTA bus ridership by stop.  The data is from Summer 2023."
    )
    select_column = st.selectbox(
        "Select a column",
        [
            "rider_total",
            "rider_on",
            "rider_off",
        ],
    )
    # if no column is selected, default to "rider_total"
    if not select_column:
        select_column = "rider_total"
    heat_df = stops[["latitude", "longitude", select_column]]
    # Drop NaN values from the data
    heat_df = heat_df.dropna(
        axis=0, subset=["latitude", "longitude", select_column]
    )
    m = folium.Map(
        [stops["latitude"].mean(), stops["longitude"].mean()], zoom_start=10
    )
    heat_data = [
        [row["latitude"], row["longitude"], row[select_column]]
        for index, row in heat_df.iterrows()
    ]
    # Plot it on the map
    HeatMap(
        heat_data,
        radius=25,
        blur=15,
        # gradient={0.2: "blue", 0.4: "lime", 0.6: "yellow", 1: "red"},
        min_opacity=0.3,
    ).add_to(m)

    st_data = st_folium(m, width=900, height=800)
