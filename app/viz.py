import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import geopandas as gpd
import leafmap.foliumap as leafmap
from app.constants import CITYLINK_COLORS
import numpy as np
from typing import List, Optional, Tuple, Union, Dict


def plot_ridership_average(
    rides, route_numbers, start_date, end_date, y_axis_zero=True
):
    """
    Plot the average ridership for the selected routes over time

    Parameters
    ----------
    rides : pd.DataFrame
        The MTA bus ridership data
    route_numbers : list
        The route numbers to plot
    start_date : datetime
        The start date to plot
    end_date : datetime
        The end date to plot

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The plotly figure
    """
    date_col = "date"
    title = f"Ridership by Route over Time"

    # Convert start_date and end_date to datetime64[ns]
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Get the data for the route
    route = rides[rides["route"].isin(route_numbers)]

    # Filter the data by the start and end dates
    route = route[
        (route[date_col] >= start_date) & (route[date_col] <= end_date)
    ]

    # Plot the ridership over time
    fig = px.line(route, x=date_col, y="ridership", color="route")

    fig.update_layout(title=title)

    # Add spikelines to the x and y axes
    fig.update_xaxes(showspikes=True)
    # fig.update_yaxes(showspikes=True)

    # Show the y-value for all traces when hovering over the chart
    fig.update_traces(hoverinfo="all")

    # Add labels to the x and y axes
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text=f"Ridership")

    # Angle the x-axis labels
    fig.update_xaxes(tickangle=45)

    # Set background color to white
    fig.update_layout(plot_bgcolor="white")
    # # try another color
    # fig.update_layout(plot_bgcolor="#BDB9B3")
    fig.update_layout(plot_bgcolor="#363B3D")
    fig.update_layout(plot_bgcolor="black")

    if y_axis_zero:
        # Start the y-axis at 0
        y_max = route["ridership"].max()
        # Let's add 10% to the max y-value
        y_max = y_max + y_max * 0.1
        fig.update_yaxes(range=[0, y_max])
    # Add an option to only show a certain date range
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))
    # iterate through the traces and apply the CITYLINK_COLORS to the plot
    for i, trace in enumerate(fig.data):
        if trace.name in CITYLINK_COLORS:
            trace.marker.color = CITYLINK_COLORS[trace.name]
            trace.line.color = CITYLINK_COLORS[trace.name]
    # Remove major gridlines
    fig.update_yaxes(showgrid=False)
    # Increase the height of the plot to accommodate the legend
    fig.update_layout(height=600)
    fig.update_layout(
        title=title,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.97,
            xanchor="right",
            x=1,
            # Don't show the legend title
            title_text="",
        ),
        margin=dict(l=50, r=50, t=100, b=50),
    )
    fig.update_layout(hovermode="x unified")

    return fig


def map_bus_routes(
    gdf: gpd.GeoDataFrame,
    route_numbers: List[str],
    highlight_routes: bool = False,
    width: int = 400,
    height: int = 400,
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
    m = leafmap.Map()
    # Use a minimal basemap
    m.add_basemap("CartoDB.Positron")
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

        # Zoom to the bus routes
        m.zoom_to_gdf(route)
        # Display the map
        return m.to_streamlit()
    else:
        # Q: Whare do I find the list of basemaps?
        # A:
        # Add the bus routes to the map
        m.add_gdf(
            route,
            layer_name="Bus Routes",
            # Color the routes by route number
            style_function=lambda x: {
                "color": CITYLINK_COLORS[x["properties"]["route"]]
                if x["properties"]["route"] in CITYLINK_COLORS
                else "gray",
                "weight": 3,
                "opacity": 1,
            },
        )
        # Zoom to the bus routes
        m.zoom_to_gdf(route)
        # Display the map
        return m.to_streamlit(height=height, width=width)


def plot_recovery_over_this_quarter(df, route_numbers):
    df = df[df.route.isin(route_numbers)]
    # Drop dates before January 2021
    df = df[df.date >= "2021-01-01"]

    fig = px.line(df, x="date", y="recovery_over_2019", color="route")

    # Hover: show the 'recovery_over_2019' value, 'ridership_weekday', and 'ridership_weekday_2019'
    fig.update_traces(
        hovertemplate="<b>Route: %{customdata[0]}</b><br>Recovery over 2019: %{y:.2f}<br>Ridership (weekday): %{customdata[1]:.0f}<br>Ridership (weekday 2019): %{customdata[2]:.0f}<extra></extra>",
        customdata=df[
            ["route", "ridership_weekday", "ridership_weekday_2019"]
        ],
    )
    return None


def plot_bar_top_n_for_daterange(
    df, top_n=5, col="ridership", daterange=("2020-05-01", "2023-01-01")
):
    """Plot a bar chart of the top N routes for a given date range"""
    daterange = pd.date_range(start=daterange[0], end=daterange[1])
    df = df[df.date.isin(daterange)]
    df = (
        df.groupby(["route"])
        .sum()
        .reset_index()
        .sort_values(by=col, ascending=False)
    )
    df = df.head(top_n)
    fig = px.bar(
        df.sort_values(by=col, ascending=False),
        x=col,
        y="route",
        orientation="h",
    )
    fig.update_layout(title="Top routes for the selected date range")
    fig.update_layout(plot_bgcolor="white")
    fig.update_layout(
        title="Top routes for the selected date range",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.97,
            xanchor="right",
            x=1,
            # Don't show the legend title
            title_text="",
        ),
        margin=dict(l=50, r=50, t=100, b=50),
    )
    return fig
