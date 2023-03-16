import pandas as pd
import streamlit as st
from app.load_data import get_rides,get_rides_quarterly, get_route_linestrings
from streamlit_extras.dataframe_explorer import dataframe_explorer
st.set_page_config(
layout="wide", 
page_icon="⬇️",
page_title="Download MTA Bus Ridership Data",
)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

rides = get_rides()

st.markdown("## Ridership data by route")
dataframe = (rides)
filtered_dataframe = dataframe_explorer(dataframe)
st.dataframe(filtered_dataframe, use_container_width=True)
csv = convert_df(filtered_dataframe)
st.download_button(
    label="Download full dataset as CSV",
    data=csv,
    file_name='mta_bus_ridership.csv',
    mime='text/csv',
)
