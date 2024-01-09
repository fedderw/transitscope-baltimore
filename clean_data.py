import calendar
import datetime as dt
import json
import os
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests


def clean_ridership_data(url_or_path='https://github.com/fedderw/mta-bus-ridership-scraper/blob/a46aaf701bee079e46ad3c715432bfc9be48be14/data/processed/mta_bus_ridership.csv?raw=true'):
    
    # Load the data
    rides = pd.read_csv(url_or_path, parse_dates=["date"])

    # Drop route months where  ridership is 0
    rides = rides[rides["ridership"] > 0]
    rides["quarter"] = rides["date"].dt.quarter

    

    # Organize the bus data by type
    rides["route_group"] = rides["route"].apply(
        lambda x: "Commuter"
        if x.isnumeric() and int(x) >= 100
        else "LocalLink"
        if x.isnumeric() and int(x) < 100
        else "CityLink"
        if "CityLink" in x
        else x
    )

    rides_quarterly = (
        rides.groupby(["route", pd.Grouper(key="date", freq="Q")])
        .sum()
        .reset_index()
    )
    rides_quarterly["quarter"] = rides_quarterly["date"].dt.quarter
    rides_quarterly["year"] = rides_quarterly["date"].dt.year
    rides_quarterly["quarter_year"] = (
        rides_quarterly["year"].astype(str)
        + "Q"
        + rides_quarterly["quarter"].astype(str)
    )
    rides_quarterly["ridership_per_day"] = (
        rides_quarterly["ridership"] / rides_quarterly["num_days_in_month"]
    )
    # Create a column for the change over one year ago, two years ago, and three years ago
    for i in range(1, 4):
        rides_quarterly[f"change_vs_{i}_years_ago"] = (
            rides_quarterly["ridership_per_day"]
            / rides_quarterly.groupby("route")["ridership_per_day"].shift(
                i * 4
            )
            - 1
        )

    return rides, rides_quarterly

def write_ridership_data_to_parquet(rides, rides_quarterly, data_dir=Path("data")):
    # Write the data to parquet
    rides.to_parquet(data_dir / "mta_bus_ridership.parquet")
    rides_quarterly.to_parquet(data_dir / "mta_bus_ridership_quarterly.parquet")


if __name__ == "__main__":
    rides, rides_quarterly = clean_ridership_data()
    write_ridership_data_to_parquet(rides, rides_quarterly)
