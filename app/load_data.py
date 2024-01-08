from datetime import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
import streamlit as st


def add_ridership_weekday_2019(
    df: pd.DataFrame, freq: str = "quarter"
) -> pd.DataFrame:
    """Calculate the ridership recovery over 2019 for a given frequency

    Args:
        df (pd.DataFrame): DataFrame with ridership and date columns
        freq (str, optional): Frequency to group by. Can be 'quarter' or 'month'. Defaults to 'quarter'.

    Returns:
        pd.DataFrame: DataFrame with additional columns for the ridership recovery over 2019
    """
    # Extract quarter and year information from date column

    # freq can be 'quarter' or 'month'

    df[freq] = (
        df["date"].dt.quarter if freq == "quarter" else df["date"].dt.month
    )
    df["year"] = df["date"].dt.year

    # Filter to same quarter in 2019
    filter_df = (
        df[(df["year"] == 2019) & (df[freq] == df[freq])]
        .groupby(["route", freq])[["ridership_weekday"]]
        .sum()
        .reset_index()
    )

    # Merge filtered DataFrame with original DataFrame
    merged_df = df.merge(
        filter_df, on=["route", freq], how="left", suffixes=("", "_2019")
    )
    merged_df.date = pd.to_datetime(merged_df.date)
    merged_df["recovery_over_2019"] = np.where(
        merged_df.date.dt.year < 2020,
        np.nan,
        merged_df["ridership_weekday"] / merged_df["ridership_weekday_2019"],
    )

    return merged_df


cols = [
    "route",
    "date",
    "ridership_weekday",
    "ridership",
]


@st.cache_data
def get_rides(file_path="data/mta_bus_ridership.parquet"):
    """Get the MTA bus ridership data"""
    rides = pd.read_parquet(file_path)
    rides = add_ridership_weekday_2019(rides, freq="month")
    return rides


@st.cache_data
def get_rides_quarterly(file_path="data/mta_bus_ridership_quarterly.parquet"):
    """Get the MTA bus ridership data"""
    rides = pd.read_parquet(file_path)
    rides = add_ridership_weekday_2019(rides, freq="quarter")
    return rides


@st.cache_data
def get_route_linestrings(file_path="data/mta_bus_route_linestring.geojson"):
    """Get the MTA bus ridership data"""
    gdf = gpd.read_file(file_path)
    # The geometry column contains many multiline strings	, so we need to convert them to single linestrings

    return gdf


@st.cache_data
def get_bus_stops(file_path="data/mta_bus_stops.parquet"):
    return gpd.read_parquet(file_path)
