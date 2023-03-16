import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from app.viz import plot_ridership_average, map_bus_routes
from app.viz import plot_recovery_over_this_quarter

from app.load_data import get_rides, get_rides_quarterly, get_route_linestrings
import geopandas as gpd
from streamlit_extras.badges import badge


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


route_linestrings = get_route_linestrings()
# Streamlit app
st.title("MTA Bus Ridership")
st.sidebar.title("TransitScope Baltimore")

rides = get_rides_quarterly()
csv = convert_df(rides)
# Get the top 5 routes from 2022, group by route number and sum the ridership
top_5_routes = (
    rides[rides["date"] >= datetime(2022, 1, 1)]
    .groupby("route")["ridership"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()["route"]
    .tolist()
)
print(type(top_5_routes))
route_numbers = st.sidebar.multiselect(
    "Select routes",
    list(rides["route"].unique()),
    default=top_5_routes,
)

highlight_routes = st.sidebar.checkbox(
    "Show unselected bus routes on map", value=False
)

if route_numbers:
    # Add a toggle to set y-axis to start at 0
    fig = plot_recovery_over_this_quarter(
        rides,
        # Do the top 5 routes from 2022
        route_numbers=route_numbers,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.download_button(
        "Download data",
        csv,
        file_name="mta_bus_ridership.csv",
        mime="text/csv",
    )

else:
    st.write("Select routes to compare")
    st.plotly_chart(
        map_bus_routes(route_linestrings, highlight_routes=highlight_routes),
        use_container_width=True,
    )
