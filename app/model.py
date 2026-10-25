"""The Random Forest price model and the helpers that use it."""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from data import ROOM_ORDER, load_data

MODEL_CAT = ["neighbourhood", "room_type"]
MODEL_NUM = ["km_to_centre", "minimum_nights", "number_of_reviews", "reviews_last_12m",
             "availability_365", "host_listings_count"]
FEATURE_NAMES = {"neighbourhood": "Neighbourhood", "room_type": "Room type", "km_to_centre": "Distance to centre",
                 "minimum_nights": "Minimum nights", "number_of_reviews": "Total reviews",
                 "reviews_last_12m": "Reviews (12 months)", "availability_365": "Available days",
                 "host_listings_count": "Host's listings"}

# Inside Airbnb's occupancy model: about half of guests leave a review, a stay lasts at least 3 nights
# (or the minimum stay if longer), and occupancy is capped at 70% of the year.
REVIEW_RATE = 0.5
MIN_STAY = 3
MAX_OCCUPANCY = 0.7


@st.cache_resource(show_spinner="Training the price model…")
def train_model():
    """Random Forest on log(price). Returns the model, its test scores and data for the charts."""
    data = load_data()
    X, y = data[MODEL_CAT + MODEL_NUM], data["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline([
        ("prep", ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), MODEL_CAT)],
                                   remainder="passthrough")),
        ("forest", RandomForestRegressor(n_estimators=300, min_samples_leaf=5, random_state=42, n_jobs=-1)),
    ])
    model.fit(X_train, np.log(y_train))
    predicted = np.exp(model.predict(X_test))

    scores = {
        "mae": mean_absolute_error(y_test, predicted),
        "baseline_mae": mean_absolute_error(y_test, np.full(len(y_test), y_train.median())),
        "r2": r2_score(y_test, predicted),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    test = pd.DataFrame({"Actual price": y_test.values, "Predicted price": predicted,
                         "Room type": X_test["room_type"].values})

    # Add up the importance of the one-hot columns so each original feature gets one number
    names = model.named_steps["prep"].get_feature_names_out()
    raw = pd.Series(model.named_steps["forest"].feature_importances_, index=names)
    grouped = raw.groupby(lambda n: next(f for f in MODEL_CAT + MODEL_NUM if f in n)).sum()
    importance = (grouped.rename(index=FEATURE_NAMES).sort_values().reset_index()
                  .set_axis(["feature", "importance"], axis=1))
    return model, scores, test, importance


def predict(model, listings):
    """Estimated price per night (€) for each row of `listings`."""
    return np.exp(model.predict(listings[MODEL_CAT + MODEL_NUM]))


def price_curve(model, listing, distances):
    """Estimated price of one listing if it were at each of the given distances from the centre."""
    rows = pd.concat([listing] * len(distances), ignore_index=True)
    rows["km_to_centre"] = distances
    return predict(model, rows)


def room_prices(model, listing):
    """Estimated price of one listing for every room type."""
    rows = pd.concat([listing] * len(ROOM_ORDER), ignore_index=True)
    rows["room_type"] = ROOM_ORDER
    return pd.Series(predict(model, rows), index=ROOM_ORDER)


def income_estimate(price, reviews_12m, minimum_nights):
    """Rough yearly bookings and income, using Inside Airbnb's occupancy model."""
    nights = min(reviews_12m / REVIEW_RATE * max(MIN_STAY, minimum_nights), MAX_OCCUPANCY * 365)
    return nights, nights / 365, nights * price
