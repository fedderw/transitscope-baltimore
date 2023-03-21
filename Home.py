# import os,sys
# sys.path.append(os.getcwd())
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from app.viz import (
    plot_ridership_average,
    map_bus_routes,
    # plot_recovery_over_this_quarter,
    plot_bar_top_n_for_daterange,
)
from app.load_data import get_rides, get_rides_quarterly, get_route_linestrings
from app.constants import CITYLINK_COLORS
import geopandas as gpd
from streamlit_extras.badges import badge
from streamlit_extras.dataframe_explorer import dataframe_explorer

st.set_page_config(
    layout="wide",
    page_icon="🚌",
    page_title="Compare MTA Bus Routes by Ridership",
)


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

def plot_recovery_over_this_quarter(df, route_numbers):
    # Filter DataFrame to specified route numbers and dates on or after January 1, 2021
    df = df[df.route.isin(route_numbers)]
    df = df[df.date >= "2021-01-01"]

    # Create line chart
    fig = px.line(df, x="date", y="recovery_over_2019", color="route")

    # TODO: I can't get the hovertemplate to work with the customdata. Not sure why. I'm sure it's something simple.
    
    # Set customdata for each trace
    # Hover: show the 'recovery_over_2019' value, 'ridership_weekday', and 'ridership_weekday_2019'
    # fig.update_traces(
    #     hovertemplate="<b>Route: %{customdata[0]}</b><br>Recovery over 2019: %{y:.2f}<br>Ridership (weekday): %{customdata[1]:.0f}<br>Ridership (weekday 2019): %{customdata[2]:.0f}<extra></extra>",
    #     customdata=df[
    #         ["route", "ridership_weekday", "ridership_weekday_2019"]
    #     ].values,
    # )

    # st.write(#df is your dataframe
    # df.shape)
    # st.write("""#df is your dataframe
    # df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ]""")
    # st.write(#df is your dataframe
    # df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ])
    # st.write("""#df is your dataframe
    # df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ].iloc[0]""")
    # st.write(df[["route", "ridership_weekday", "ridership_weekday_2019"]].iloc[0])
    # st.write(df[["route", "ridership_weekday", "ridership_weekday_2019"]].iloc[1])
        
    # st.write("""df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ].values[0]""")
    # st.write(df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ].values[0])
    # st.write(df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ].values[1])
    # st.write("""df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ].values[0][0]""")
    # st.write(df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ].values[0][0])
    # st.write(df[
    #     ["route", "ridership_weekday", "ridership_weekday_2019"]
    # ].values[0][1])
  

    # Add spikelines to the x and y axes
    fig.update_xaxes(showspikes=True)

    # Add labels to the x and y axes
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text=f"Ridership as a % of 2019 benchmark")

    # Angle the x-axis labels
    fig.update_xaxes(tickangle=45)

    # Set background color to white
    fig.update_layout(plot_bgcolor="white")
    fig.update_layout(plot_bgcolor="#363B3D")
    fig.update_layout(plot_bgcolor="black")

    # Add an option to only show a certain date range
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    # Iterate through the traces and apply the CITYLINK_COLORS to the plot
    for i, trace in enumerate(fig.data):
        if trace.name in CITYLINK_COLORS:
            trace.marker.color = CITYLINK_COLORS[trace.name]
            trace.line.color = CITYLINK_COLORS[trace.name]
    # Remove major gridlines
    fig.update_yaxes(showgrid=False)

    # Increase the height of the plot to accommodate the legend
    fig.update_layout(height=600)
    fig.update_layout(
        title="Ridership as a percentage of ridership for the same quarter in 2019",
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

    # Represent the x-axis as a quarter of the year
    fig.update_xaxes(tickformat="%b %Y")
    # Format y as %
    fig.update_yaxes(tickformat=",.0%")
    # Hover mode should be to highlight all traces
    fig.update_layout(hovermode="x unified")
    return fig


route_linestrings = get_route_linestrings()
# Streamlit app
st.title("MTA Bus Ridership")
st.sidebar.title("TransitScope Baltimore")
freq = "Quarterly"
if freq == "Quarterly":
    rides = get_rides_quarterly()
    csv = convert_df(rides)
else:
    rides = get_rides()
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
freq = st.sidebar.selectbox("Choose frequency", ["Quarterly", "Monthly"])
if freq == "Quarterly":
    rides = get_rides_quarterly()
    csv = convert_df(rides)
else:
    rides = get_rides()
    csv = convert_df(rides)
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
        end_date=datetime(2022, 12, 31),
        y_axis_zero=True,
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
    st.markdown("### Explore the top routes over a date range")
    start_date = st.date_input("Start date", datetime(2022, 1, 1))
    end_date = st.date_input("End date", datetime(2022, 12, 31))

    fig3 = plot_bar_top_n_for_daterange(
        rides, top_n=5, col="ridership", daterange=(start_date, end_date)
    )
    st.plotly_chart(
        fig3,
        use_container_width=True,
    )
    # Show the ridership recovery chart

    with st.expander("Data details"):
        st.write(
            "NOTE: This is quarterly data. The quarterly data is calculated by taking the sum of the total ridership in each quarter, and dividing it by the number of weekdays in that quarter."
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

# Rerun on input
input("Press Enter to continue...")
st.experimental_rerun()
