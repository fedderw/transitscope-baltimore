import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import geopandas as gpd
import leafmap.foliumap as leafmap
from constants import CITYLINK_COLORS


def plot_ridership_average(rides, route_numbers, start_date, end_date, y_axis_zero=True ):
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
    title = f"Average Weekday Ridership by Route over Time"

    # Convert start_date and end_date to datetime64[ns]
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Get the data for the route
    route = rides[rides["route"].isin(route_numbers)]

    # Filter the data by the start and end dates
    route = route[(route[date_col] >= start_date) & (route[date_col] <= end_date)]

    

    # Plot the ridership over time
    fig = px.line(
        route, x=date_col, y='ridership_weekday', color="route"
    )

    fig.update_layout(title=title)

    # Add spikelines to the x and y axes
    fig.update_xaxes(showspikes=True)
    # fig.update_yaxes(showspikes=True)

    # Show the y-value for all traces when hovering over the chart
    fig.update_traces(hoverinfo="all")

    # Add labels to the x and y axes
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text=f"Average Weekday ridership")

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
        y_max = route["ridership_weekday"].max()
        # Let's add 10% to the max y-value
        y_max = y_max + y_max * 0.1
        fig.update_yaxes(range=[0, y_max])
    
    # Add an option to only show a certain date range
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            
            type="date"
        )
    )
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
        margin=dict(l=50, r=50, t=100, b=50)
    )

    return fig

def map_bus_routes(gdf, route_numbers, highlight_routes=False, width=400, height=400):
    
    # Get the data for the route
    route = gdf[gdf["route"].isin(route_numbers)]
    
    # Create a map
    m = leafmap.Map(

    )
    # Use a minimal basemap
    m.add_basemap("CartoDB.DarkMatter")
    # Turn off the toolbar
    m.toolbar = False
    # Show the route highlighted in red, then plot all the other routes in gray
    if highlight_routes:
        non_highlighted_routes = gdf[~gdf["route"].isin(route_numbers)]
        # Add the bus routes to the map
        m.add_gdf(non_highlighted_routes,
            layer_name="Other Bus Routes",
            style = {'color': 'white', 'weight': 1, 'opacity': 0.6},
        )
        m.add_gdf(route,
                    layer_name="Selected Bus Routes",
                    style = {'color': 'red', 'weight': 3, 'opacity': 0.9},
                )
        
        # Zoom to the bus routes
        m.zoom_to_gdf(route)
        # Display the map
        return m.to_streamlit()
    else:
        
        # Q: Whare do I find the list of basemaps?
        # A: 
        # Add the bus routes to the map
        m.add_gdf(route,
                    layer_name="Bus Routes",
                # Color the routes by route number
                    style_function=lambda x: {
                        'color': CITYLINK_COLORS[x['properties']['route']] if x['properties']['route'] in CITYLINK_COLORS else 'gray',
                        'weight': 3,
                        'opacity': 0.7,
                    },
                )
        # Zoom to the bus routes
        m.zoom_to_gdf(route)
        # Display the map
        return m.to_streamlit(height=height, width=width)



