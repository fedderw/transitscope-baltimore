import pandas as pd
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer

from app.load_data import get_rides, get_rides_quarterly, get_route_linestrings

st.set_page_config(
    layout="wide", page_icon="⬇️", page_title="Download MTA Bus Ridership Data"
)


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


rides = get_rides()[
    [
        "route",
        "date",
        "ridership",
        "ridership_per_day",
        # "ridership_weekday",
        # "ridership_weekday_2019",
    ]
].rename(
    columns={
        # "ridership_weekday_2019": "ridership_weekday_2019_baseline",
        "business_days": "n_weekdays",
        # "ridership": "ridership_monthly",
    }
)

st.markdown("## Ridership data by route")

with st.expander("Notes"):
    st.write("The 'date' column refers to the first day of the month.")
dataframe = rides
filtered_dataframe = dataframe_explorer(dataframe)
st.dataframe(filtered_dataframe, use_container_width=True, hide_index=True)
csv = convert_df(filtered_dataframe)
st.download_button(
    label="Download filtered dataset as CSV",
    data=csv,
    file_name="mta_bus_ridership_by_route.csv",
    mime="text/csv",
)
