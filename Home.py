# import os,sys
# sys.path.append(os.getcwd())
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from app.viz import plot_ridership_average, map_bus_routes, plot_recovery_over_this_quarter
from app.load_data import get_rides,get_rides_quarterly, get_route_linestrings
import geopandas as gpd
from streamlit_extras.badges import badge
from streamlit_extras.dataframe_explorer import dataframe_explorer
st.experimental_rerun()
st.set_page_config(
layout="wide", 
page_icon="🚌",
page_title="Compare MTA Bus Routes by Ridership",
)



@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')




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
top_5_routes = rides[rides["date"] >= datetime(2022, 1, 1)].groupby("route")["ridership"].sum().sort_values(ascending=False).head(5).reset_index()["route"].tolist()
print(type(top_5_routes))
route_numbers = st.sidebar.multiselect(
    "Select routes", list(rides["route"].unique()), default=top_5_routes,
)
freq=st.sidebar.selectbox("Choose frequency", ["Quarterly", "Monthly"])
if freq == "Quarterly":
    rides = get_rides_quarterly()
    csv = convert_df(rides)
else:
    rides = get_rides()
    csv = convert_df(rides)
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
    # Add a toggle to set y-axis to start at 0
    fig2 = plot_recovery_over_this_quarter(rides, 
                                # Do the top 5 routes from 2022
                                route_numbers=route_numbers, )
    col1, col2 = st.columns([3,2])
    with col1:
        st.plotly_chart(
            fig, 
            use_container_width=True,
            # Increase height of chart
            height=900,
            )
        st.plotly_chart(fig2, use_container_width=True)
        y_axis_zero = st.sidebar.checkbox("Y-axis starts at 0", value=True)

    with col2:
        # Add 3 blank lines 
        st.markdown("### ")
        st.markdown("### ")
        st.markdown("### ")
        map_bus_routes(route_linestrings, route_numbers,highlight_routes=highlight_routes)
    
    with st.expander("See explanation"):
        st.write("NOTE: This is quarterly data. The quarterly data is calculated by taking the sum of the total ridership in each quarter, and dividing it by the number of weekdays in that quarter.")
        st.write("The routes displayed on the map do not include the supplemental services that provide service to Baltimore City Schools. These riders **are** included in the ridership data.")
        st.markdown(":red[Maps may not reflect service changes. These should be considered as a guide to the general service area only.]")
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
    
st.markdown("### Ridership Data")
dataframe = (rides)
filtered_dataframe = dataframe_explorer(dataframe)
st.dataframe(filtered_dataframe, use_container_width=True)

badge(type="twitter", name="willfedder")
badge(type="github", name="fedderw/transitscope-baltimore")
st.sidebar.write("App created by [Will Fedder](https://linkedin.com/in/fedderw).")
st.sidebar.write("Data provided by [MDOT MTA](https://www.arcgis.com/apps/dashboards/1bbc19f2abfe4fde94e4c563f5e8371c). To view a geographic system map in PDF format, visit the [MTA's website](https://s3.amazonaws.com/mta-website-staging/mta-website-staging/files/System%20Maps/Geographic_System_Map_08_2022.pdf).") 
st.sidebar.write("Data extracted using this [script](https://github.com/jamespizzurro/mta-bus-ridership-scraper) authored by James Pizzurro.")


