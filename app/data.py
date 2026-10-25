"""Loading the cleaned data and applying the sidebar filters."""
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

HOST_ORDER = ["Single", "Small (2-10)", "Professional (11+)"]
PRICE_ORDER = ["Budget (<€100)", "Mid-range (€100-199)", "Premium (€200+)"]
ROOM_ORDER = ["Entire home/apt", "Private room", "Shared room", "Hotel room"]
STAY_ORDER = ["Short-term", "Long-term (30+ nights)"]
ALL = "All neighbourhoods"
CENTRE = (44.49381, 11.34265)  # Piazza Maggiore, the main square of Bologna
SOURCE_URL = "https://insideairbnb.com/get-the-data/"


def km_to_centre(lat, lon):
    """Distance in km to Piazza Maggiore (good enough for a city this size)."""
    return 111.32 * np.hypot(lat - CENTRE[0], (lon - CENTRE[1]) * np.cos(np.radians(CENTRE[0])))


@st.cache_data
def load_data():
    """Load the cleaned data made by the notebook and restore the category order."""
    df = pd.read_csv(Path(__file__).parent / "clean_listings.csv", parse_dates=["last_review"])
    df["host_type"] = pd.Categorical(df["host_type"], HOST_ORDER, ordered=True)
    df["price_category"] = pd.Categorical(df["price_category"], PRICE_ORDER, ordered=True)
    df["km_to_centre"] = km_to_centre(df["latitude"], df["longitude"]).round(2)
    df["link"] = "https://www.airbnb.com/rooms/" + df["id"].astype(str)
    return df


def apply_filters(df, neighbourhood, rooms, max_price, stays):
    """Return (all areas, chosen area). The first keeps every neighbourhood so areas can be compared."""
    all_areas = df[df["room_type"].isin(rooms) & df["stay_type"].isin(stays or []) & (df["price"] <= max_price)]
    chosen = all_areas if neighbourhood == ALL else all_areas[all_areas["neighbourhood"] == neighbourhood]
    return all_areas, chosen
