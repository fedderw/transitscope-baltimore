# import os,sys
# sys.path.append(os.getcwd())
from datetime import datetime

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_extras.badges import badge
from streamlit_extras.dataframe_explorer import dataframe_explorer

from app.constants import CITYLINK_COLORS
from app.load_data import get_rides, get_rides_quarterly, get_route_linestrings
from app.viz import (map_bus_routes, plot_bar_top_n_for_daterange,
                     plot_ridership_average)

st.set_page_config(
    layout="wide",
    page_icon="🚌",
    page_title="Compare MTA Bus Routes by Ridership",
)


def plot_recovery_over_this_quarter(df, route_numbers):
    df = df[(df.route.isin(route_numbers)) & (df.date >= "2020-01-01")]

    fig = px.line(df, x="date", y="recovery_over_2019", color="route")
    fig.update_xaxes(showspikes=True)
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Ridership as a % of 2019 benchmark")
    fig.update_xaxes(tickangle=45)
    fig.update_layout(plot_bgcolor="#F5F5F5")  # Set light background color

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    for trace in fig.data:
        if trace.name in CITYLINK_COLORS:
            trace.marker.color = CITYLINK_COLORS[trace.name]
            trace.line.color = CITYLINK_COLORS[trace.name]

    fig.update_yaxes(showgrid=False)
    fig.update_layout(height=600)

    fig.update_layout(
        title="Ridership as a percentage of ridership for the same period in 2019",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.97,
            xanchor="right",
            x=1,
            title_text="",
        ),
        margin=dict(l=50, r=50, t=100, b=50),
    )

    fig.update_xaxes(tickformat="%b %Y")
    fig.update_yaxes(tickformat=",.0%")
    fig.update_layout(hovermode="x unified")

    return fig


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


route_linestrings = get_route_linestrings()

# Streamlit app
st.title("MTA Bus Ridership")
st.sidebar.title("TransitScope Baltimore")
# Define the mapping
title_mapping = {
    "Monthly": "Ridership per month",
    "Quarterly": "Ridership per quarter",
}
freq = "Monthly"
freq = st.sidebar.selectbox("Choose frequency", ["Monthly", "Quarterly"])
if freq == "Quarterly":
    rides = get_rides_quarterly()
    csv = convert_df(rides)
else:
    rides = get_rides()
    csv = convert_df(rides)


# Get the title from the mapping
title = title_mapping.get(
    freq, "Ridership per month"
)  # Default to 'Ridership per month'
# Get the top 5 routes from 2023, group by route number and sum the ridership
top_5_routes = (
    rides[rides["date"] >= datetime(2023, 1, 1)]
    .groupby("route")["ridership"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()["route"]
    .tolist()
)
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

    # Plot the average ridership for the selected routes
    fig = plot_ridership_average(
        rides,
        # Do the top 5 routes from 2022
        route_numbers=route_numbers,
        start_date=datetime(2018, 1, 1),
        end_date=datetime(2023, 12, 31),
        y_axis_zero=True,
    )
    # Use the title in the plot
    fig.update_layout(
        title=title,
        yaxis_title=title,
    )
    # Add a toggle to set y-axis to start at 0
    fig2 = plot_recovery_over_this_quarter(
        rides,
        # Do the top 5 routes from 2022
        route_numbers=route_numbers,
    )
    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(
            fig,
            use_container_width=True,
            # Increase height of chart
            height=900,
        )
        y_axis_zero = st.sidebar.checkbox("Y-axis starts at 0", value=True)

    with col2:
        # Add 3 blank lines
        st.markdown("### ")
        st.markdown("### ")
        st.markdown("### ")
        map_bus_routes(
            route_linestrings, route_numbers, highlight_routes=highlight_routes
        )

    # Add a date selector, NOT another markdown header
    st.plotly_chart(
        fig2,
        use_container_width=True,
    )
    # NOTE: This is bad practice to just comment this out
    # st.markdown("### Explore the top routes over a date range")
    # start_date = st.date_input("Start date", datetime(2022, 1, 1))
    # end_date = st.date_input("End date", datetime(2022, 12, 31))

    # fig3 = plot_bar_top_n_for_daterange(
    #     rides, top_n=5, col="ridership", daterange=(start_date, end_date)
    # )
    # st.plotly_chart(
    #     fig3,
    #     use_container_width=True,
    # )
    # # Show the ridership recovery chart

    with st.expander("Data details"):
        st.write(
            "The ridership recovery metric uses average daily ridership for the selected period, and compares it to the average daily ridership for the same period in 2019."
        )
        st.write(
            "NOTE: If quarterly data is selected, The quarterly data is calculated by taking the sum of the total ridership in each quarter, and dividing it by the number of days in that quarter."
        )
        st.write(
            "The routes displayed on the map do not include the supplemental services that provide service to Baltimore City Schools. These riders **are** included in the ridership data."
        )
        st.markdown(
            ":red[Maps may not reflect service changes. These should be considered as a guide to the general service area only.]"
        )
        # Add a download link for the data


else:
    # Show a message if no routes are selected
    st.warning("Please select at least one route.")


badge(type="twitter", name="willfedder")
badge(type="github", name="fedderw/transitscope-baltimore")
st.sidebar.write(
    "App created by [Will Fedder](https://linkedin.com/in/fedderw)."
)
st.sidebar.write(
    "Data provided by [MDOT MTA](https://www.arcgis.com/apps/dashboards/1bbc19f2abfe4fde94e4c563f5e8371c). To view a geographic system map in PDF format, visit the [MTA's website](https://s3.amazonaws.com/mta-website-staging/mta-website-staging/files/System%20Maps/Geographic_System_Map_08_2022.pdf)."
)
st.sidebar.write(
    "Data extracted using this [script](https://github.com/jamespizzurro/mta-bus-ridership-scraper) authored by James Pizzurro."
)
st.markdown("#")
