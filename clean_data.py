import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path

import janitor
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import (
    List,
    Set,
    Dict,
    Tuple,
    Optional,
    Callable,
    Iterator,
    Union,
    Optional,
    Any,
    cast,
)
from typing import Mapping, MutableMapping, Sequence, Iterable
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

# import folium
# import leafmap
# Import a library so to work with dates
import datetime as dt
import calendar


def clean_ridership_data():
    filepath = Path("../data/raw/mta-bus-ridership.csv")
    rides = pd.read_csv(filepath)

    rides = rides.clean_names()

    def convert_date(date):
        # Get the month and year
        month, year = date.split("/")
        # Create a datetime object
        date = dt.datetime(int(year), int(month), 1)
        return date

    # Apply the function to the Date column
    rides["date"] = rides["date"].apply(convert_date)

    # Group the data by route and date
    rides = rides.groupby(["route", "date"]).sum().reset_index()

    # Drop route months where  ridership is 0
    rides = rides[rides["ridership"] > 0]
    rides["quarter"] = rides["date"].dt.quarter

    def get_business_days(row):
        # Get the first day of the month
        first_day = dt.datetime(row["date"].year, row["date"].month, 1)
        # Get the last day of the month
        last_day = dt.datetime(
            row["date"].year,
            row["date"].month,
            calendar.monthrange(row["date"].year, row["date"].month)[1],
        )
        # Get the number of business days in the month
        business_days = pd.bdate_range(first_day, last_day).shape[0]
        return business_days

    # Apply the function to the dataframe
    rides["business_days"] = rides.apply(get_business_days, axis=1)
    # Normalize the ridership by the number of business days in the month
    rides["ridership_weekday"] = rides["ridership"] / rides["business_days"]
    # Create a column for the change over one year ago, two years ago, and three years ago
    for i in range(1, 4):
        rides[f"change_vs_{i}_years_ago"] = (
            rides["ridership_weekday"]
            / rides.groupby("route")["ridership_weekday"].shift(i * 12)
            - 1
        )

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

    rides_grouped = rides.groupby(["route_group", "date"]).sum().reset_index()
    rides_grouped["ridership_weekday"] = (
        rides_grouped["ridership"] / rides_grouped["business_days"]
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
        rides_quarterly["ridership"] / rides_quarterly["total_days"]
    )
    rides_quarterly["ridership_weekday"] = (
        rides_quarterly["ridership"] / rides_quarterly["business_days"]
    )
    # Create a column for the change over one year ago, two years ago, and three years ago
    for i in range(1, 4):
        rides_quarterly[f"change_vs_{i}_years_ago"] = (
            rides_quarterly["ridership_weekday"]
            / rides_quarterly.groupby("route")["ridership_weekday"].shift(
                i * 4
            )
            - 1
        )


import re


def capitalize_citylink(match):
    return "CityLink " + match.group(1).title()


def process_routes(served_routes):

    routes_list = served_routes.split(",")
    modified_routes = [
        re.sub("CityLink ([A-Z]+)", capitalize_citylink, route.strip())
        for route in routes_list
    ]
    return ", ".join(modified_routes)


if __name__ == "__main__":
    pass
