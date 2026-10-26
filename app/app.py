"""
Bologna Airbnb: Host vs Guest dashboard
Unit 3 Final Project - Khalid Alotaibi

Run it from this folder with:
    py -m streamlit run app.py

Files:
    app.py    page layout, filters (top bar and sidebar) and the 8 views (this file)
    ui.py     colours, CSS and drawing helpers (cards, KPI tiles, insights, chart style)
    data.py   loading the cleaned data and applying the filters
    model.py  the Random Forest price model and its helpers
"""
import re
from html import escape

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data import ALL, HOST_ORDER, PRICE_ORDER, ROOM_ORDER, SOURCE_URL, STAY_ORDER, apply_filters, load_data
from model import MAX_OCCUPANCY, MIN_STAY, REVIEW_RATE, income_estimate, predict, price_curve, room_prices, train_model
from ui import (COLUMNS, CORAL, CORAL_LIGHT, GREY, HOST_COLORS, INK, PRICE_COLORS, ROOM_COLORS, SILVER, TEAL,
                bar_room, card, chart, html, insights, kpis, pct, section, setup_page, small_title, style, verdict)

AUTHOR = "Khalid Alotaibi"

st.set_page_config(page_title="Bologna Airbnb · Host vs Guest", page_icon="🏠", layout="wide",
                   initial_sidebar_state="auto")  # open on desktop, collapsed on phones
setup_page()

try:
    df = load_data()
except FileNotFoundError:
    st.error("`clean_listings.csv` was not found. Put the file from the notebook next to `app.py` and reload.")
    st.stop()


# ------------------------------------------------------------------ State and callbacks
DEFAULTS = {"f_nb": ALL, "f_rooms": ROOM_ORDER, "f_max_price": 1000, "f_stay": STAY_ORDER}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def reset_filters():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.toast("All filters cleared", icon=":material/restart_alt:")


def set_filter(key, value, message):
    st.session_state[key] = value
    st.toast(message, icon=":material/filter_alt_off:")


def select_area(chart_key):
    """Clicking a neighbourhood bar focuses the whole dashboard on that neighbourhood."""
    points = st.session_state[chart_key]["selection"]["points"]
    if points:
        st.session_state["f_nb"] = points[0]["y"]
        st.toast(f"Focused on {points[0]['y']}", icon=":material/my_location:")


def go_to(view):
    st.session_state["seg_nav"] = view


# ------------------------------------------------------------------ Filters (on top of the page and in the sidebar)
# The sidebar widgets (keys f_*) own the filter values. The bar on top has its own widgets (keys t_*):
# they are copied from the sidebar before anything is drawn, and write back when you change them.
FILTERS = ["nb", "rooms", "max_price", "stay"]
for name in FILTERS:
    st.session_state[f"t_{name}"] = st.session_state[f"f_{name}"]


def from_top(name):
    st.session_state[f"f_{name}"] = st.session_state[f"t_{name}"]


def filter_widgets(prefix, spots):
    """Draw the 4 filters into `spots`: prefix "f" for the sidebar, "t" for the bar on top."""
    def keys(name):
        if prefix == "f":
            return {"key": f"f_{name}"}
        return {"key": f"t_{name}", "on_change": from_top, "args": (name,)}

    spots[0].selectbox("Neighbourhood", [ALL] + sorted(df["neighbourhood"].unique()), **keys("nb"))
    spots[1].multiselect("Room type", ROOM_ORDER, placeholder="Choose room types", **keys("rooms"))
    spots[2].slider("Max price per night", 50, 1000, step=10, format="€%d", **keys("max_price"))
    spots[3].pills("Stay type", STAY_ORDER, selection_mode="multi", **keys("stay"))


# ------------------------------------------------------------------ Welcome dialog (first visit only)
def mark_welcomed():
    st.session_state["welcomed"] = True


@st.dialog("Welcome 👋", width="medium", on_dismiss=mark_welcomed)
def welcome():
    html("<p style='font-size:1.05rem;color:#3A3A3C'>Explore Bologna's 4,530 Airbnb listings as a "
         "<b>host</b> or as a <b>guest</b>. Three tips to get started:</p>")
    st.markdown(
        "1. 📖 **Start with the Story** for the 5 key findings, one by one.\n"
        "2. 🎛️ **Use the filters** at the top of the page (they are also in the sidebar).\n"
        "3. 👆 **Click things**: neighbourhood bars focus the dashboard, table rows open a listing, "
        "and the 🔮 **Predict** view prices any listing you describe."
    )
    if st.button("Let's explore", type="primary", width="stretch"):
        mark_welcomed()
        st.rerun()


if not st.session_state.get("welcomed"):
    welcome()


# ------------------------------------------------------------------ Sidebar
with st.sidebar:
    html("<div class='brand'><div class='logo'>⌂</div><div><div class='name'>Bologna Airbnb</div>"
         "<div class='sub'>Host vs Guest · Unit 3 Final Project</div></div></div>")
    st.markdown(
        f"Every Airbnb listing in **Bologna, Italy**, collected on **19 September 2026** by "
        f"[Inside Airbnb]({SOURCE_URL}). After cleaning, **{len(df):,} listings** remain."
    )
    with st.expander("What is in the data?"):
        st.markdown(
            "- **price**: price per night in euros\n"
            "- **room_type**: entire home, private room, shared room or hotel room\n"
            "- **neighbourhood**: one of 6 city areas\n"
            "- **reviews_last_12m**: reviews in the last 12 months (used as *demand*)\n"
            "- **host_type**: Single, Small (2-10 listings) or Professional (11+)\n"
            "- **stay_type**: Long-term if the minimum stay is 30+ nights"
        )

    st.sidebar.header("Filters")
    filter_widgets("f", [st] * 4)
    st.button("Reset all filters", key="reset_side", on_click=reset_filters, icon=":material/restart_alt:",
              type="tertiary")

    with st.expander("About this project"):
        st.markdown(
            f"**Built by {AUTHOR}** · Unit 3 Final Project\n\n"
            "- **Data:** Inside Airbnb, Bologna, 19 Sep 2026 (5,094 listings, 4,530 after cleaning)\n"
            "- **Tools:** Python, pandas, Plotly, scikit-learn, Streamlit\n"
            "- **Model:** Random Forest on log(price), 80/20 train/test split\n\n"
            "Independent student project, not affiliated with Airbnb."
        )

selected = st.session_state["f_nb"]
max_price = st.session_state["f_max_price"]
f_all_areas, f = apply_filters(df, selected, st.session_state["f_rooms"], max_price, st.session_state["f_stay"])
is_filtered = len(f) != len(df)


def compare(value, overall, fmt, higher_is_good=None):
    """Note for a KPI tile: how the filtered value compares with the whole city."""
    if not is_filtered or abs(value - overall) < 1e-9:
        return None, "neutral"
    tone = "neutral" if higher_is_good is None else ("up" if (value > overall) == higher_is_good else "down")
    return f"{fmt(value - overall)} vs all Bologna", tone


def area_colors(names, base):
    """Colour every area with `base`, or grey them out and highlight the selected one."""
    if selected == ALL:
        return [base] * len(names)
    return [CORAL if name == selected else SILVER for name in names]


def area_chart(fig, key):
    """A neighbourhood bar chart you can click, plus a button to go back to all areas."""
    chart(fig, key=key, on_select=lambda: select_area(key), selection_mode="points")
    if selected != ALL:
        st.button("Show all areas", key=f"{key}_all", on_click=set_filter, args=("f_nb", ALL, "Showing all areas"),
                  icon=":material/zoom_out_map:", type="tertiary")


AREA_HINT = "Click a bar to focus the whole dashboard on that area" if selected == ALL else \
            f"{selected} highlighted · click another bar to switch"


# ------------------------------------------------------------------ Header, filter bar and navigation
html(
    f"<div class='eyebrow'>Bologna · Inside Airbnb · 19 September 2026 · by {AUTHOR}</div>"
    "<h1 class='headline'>Two sides of Bologna's <span class='grad'>Airbnb market.</span></h1>"
    f"<p class='subhead'>{len(df):,} listings, one city. Explore it as a <b>host</b> or as a <b>guest</b>, "
    "compare neighbourhoods, open any listing, and let a machine-learning model price one for you.</p>"
)

with st.container(key="card_filters"):
    top_row = st.columns([1, 1.6], gap="large")
    bottom_row = st.columns([1, 1.6], gap="large", vertical_alignment="bottom")
    filter_widgets("t", [top_row[0], top_row[1], bottom_row[0], bottom_row[1]])

html(f"<div class='count'>Showing <b>{len(f):,}</b> of {len(df):,} listings</div>")
if is_filtered:
    st.button("Reset all filters", key="reset_top", on_click=reset_filters, icon=":material/restart_alt:",
              type="tertiary")

VIEWS = {"Story": ":material/auto_stories:", "Overview": ":material/space_dashboard:",
         "Host": ":material/home_work:", "Guest": ":material/luggage:", "Compare": ":material/compare_arrows:",
         "Explore": ":material/travel_explore:", "Predict": ":material/auto_awesome:", "Data": ":material/table_rows:"}
st.session_state.setdefault("seg_nav", "Story")
view = st.segmented_control("View", list(VIEWS), format_func=lambda v: f"{VIEWS[v]} {v}",
                            required=True, key="seg_nav", label_visibility="collapsed")

# Story and Predict always use all listings; the other views need at least one listing after filtering
if (view in ("Overview", "Host", "Guest", "Explore", "Data") and f.empty) or (view == "Compare" and f_all_areas.empty):
    st.warning("No listings match these filters. Try a higher price, or add room types or stay types.",
               icon=":material/filter_alt_off:")
    st.stop()


# ------------------------------------------------------------------ 📖 Story
def story_step(delta):
    st.session_state["seg_story"] = min(5, max(1, st.session_state["seg_story"] + delta))


def story():
    section("The story in 5 findings",
            "A guided tour of what the data says, using all 4,530 listings (the filters don't apply here).")
    model, scores, test, _ = train_model()

    nb_counts = df["neighbourhood"].value_counts().sort_values()
    top_two = nb_counts.iloc[-2:]
    is_pro = df["host_type"] == "Professional (11+)"
    demand = df.groupby("price_category", observed=True)["reviews_last_12m"].median()
    room_med = df.groupby("room_type")["price"].median()
    nb_med = df.groupby("neighbourhood")["price"].median().sort_values()
    room_saving = room_med["Entire home/apt"] - room_med["Private room"]
    area_saving = nb_med.iloc[-1] - nb_med.iloc[0]
    improvement = 1 - scores["mae"] / scores["baseline_mae"]

    def chart_centre():
        counts = nb_counts.reset_index()
        fig = px.bar(counts, x="count", y="neighbourhood", orientation="h", text="count",
                     labels={"count": "Listings", "neighbourhood": ""})
        fig.update_traces(textposition="outside", hovertemplate="%{y}: %{x:,} listings<extra></extra>",
                          marker_color=[CORAL if n in top_two.index else SILVER for n in counts["neighbourhood"]])
        chart(bar_room(style(fig, height=360), counts["count"], axis="x"))

    def chart_hosts():
        counts = df.groupby("host_type", observed=False).size().reset_index(name="listings")
        fig = px.pie(counts, values="listings", names="host_type", hole=0.62, color="host_type",
                     color_discrete_map=HOST_COLORS, category_orders={"host_type": HOST_ORDER})
        fig.update_traces(textinfo="percent", textfont_size=14, sort=False,
                          hovertemplate="%{label}: %{value:,} listings<extra></extra>")
        fig.add_annotation(text=f"<b>{pct(is_pro.mean())}</b><br>professional", showarrow=False,
                           font=dict(size=18, color=INK))
        chart(style(fig, height=360, legend=True))

    def chart_demand():
        data = demand.reset_index(name="median_reviews")
        fig = px.bar(data, x="price_category", y="median_reviews", color="price_category", text="median_reviews",
                     color_discrete_map=PRICE_COLORS, labels={"price_category": "", "median_reviews": "Median reviews"})
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside",
                          hovertemplate="%{x}: %{y:.0f} reviews a year<extra></extra>")
        chart(bar_room(style(fig, height=360), data["median_reviews"]))

    def chart_savings():
        data = pd.DataFrame({
            "option": ["Entire home", "Private room", nb_med.index[-1], nb_med.index[0]],
            "price": [room_med["Entire home/apt"], room_med["Private room"], nb_med.iloc[-1], nb_med.iloc[0]],
            "group": ["Room type", "Room type", "Neighbourhood", "Neighbourhood"],
        })
        fig = px.bar(data, x="option", y="price", color="option", text="price",
                     color_discrete_sequence=[CORAL, CORAL_LIGHT, INK, GREY],
                     labels={"option": "", "price": "Median price per night (€)"})
        fig.update_traces(texttemplate="€%{text:.0f}", textposition="outside",
                          hovertemplate="%{x}: €%{y:.0f}<extra></extra>")
        chart(bar_room(style(fig, height=360), data["price"]))

    def chart_model():
        fig = px.scatter(test, x="Actual price", y="Predicted price", color="Room type", opacity=0.5,
                         color_discrete_map=ROOM_COLORS, category_orders={"Room type": ROOM_ORDER})
        fig.update_traces(marker=dict(size=6, line=dict(width=0)))
        fig.add_trace(go.Scatter(x=[0, 1000], y=[0, 1000], mode="lines", name="Perfect prediction",
                                 line=dict(color=INK, dash="dash", width=1.5)))
        chart(style(fig, height=360, legend=True))

    chapters = [
        ("Host", "", pct(top_two.sum() / len(df)), "The historic centre holds most of the market",
         f"<b>{top_two.index[1]}</b> and <b>{top_two.index[0]}</b> hold {pct(top_two.sum() / len(df))} of Bologna's "
         f"{len(df):,} listings, so that is where a new host faces the most competition.", chart_centre, "Host"),
        ("Host", "", pct(is_pro.mean()), f"{df.loc[is_pro, 'host_id'].nunique()} professional hosts run "
         f"{pct(is_pro.mean())} of all listings",
         f"Only {pct(df.loc[is_pro, 'host_id'].nunique() / df['host_id'].nunique())} of the "
         f"{df['host_id'].nunique():,} hosts manage more than 10 listings, yet they control over a quarter of "
         "the market.", chart_hosts, "Host"),
        ("Host", "", f"{demand.iloc[1]:.0f} vs {demand.iloc[0]:.0f}", "The mid-range is the demand sweet spot",
         f"Listings at €100–199 get a median of <b>{demand.iloc[1]:.0f} reviews a year</b>, compared with "
         f"{demand.iloc[0]:.0f} for budget listings. Being cheapest does not mean being busiest.",
         chart_demand, "Host"),
        ("Guest", "guest", f"€{area_saving:.0f}", "Guests can save a lot by choosing well",
         f"A private room saves about <b>€{room_saving:.0f}</b> a night compared with an entire home, and "
         f"{nb_med.index[0]} is <b>€{area_saving:.0f}</b> cheaper than {nb_med.index[-1]}.", chart_savings, "Guest"),
        ("Model", "model", f"€{scores['mae']:.0f}", "Price is hard to predict from this data alone",
         f"Our Random Forest's average error is €{scores['mae']:.0f}, <b>{pct(improvement)} better</b> than guessing "
         f"the median, but it explains only {pct(scores['r2'])} of the price. Size, bedrooms and photos are missing.",
         chart_model, "Predict"),
    ]

    st.session_state.setdefault("seg_story", 1)
    st.segmented_control("Chapter", [1, 2, 3, 4, 5], key="seg_story", required=True, label_visibility="collapsed",
                         format_func=lambda n: f"{n}. {['Centre', 'Hosts', 'Demand', 'Savings', 'Model'][n - 1]}")
    number = st.session_state["seg_story"]
    tag, tag_class, big, title, text, draw, target = chapters[number - 1]

    left, right = st.columns([2, 3], gap="large", vertical_alignment="center")
    with left:
        html(f"<div class='chapter'><span class='tag {tag_class}'>{tag} · finding {number} of 5</span>"
             f"<div class='big grad'>{big}</div><div class='title'>{title}</div><div class='text'>{text}</div></div>")
        st.button(f"See it in the {target} view", on_click=go_to, args=(target,), icon=":material/arrow_outward:")
    with right, card(f"story_{number}", title):
        draw()

    dots = "".join(f"<span class='{'on' if n == number else ''}'></span>" for n in range(1, 6))
    prev_col, dots_col, next_col = st.columns([1, 3, 1], vertical_alignment="center")
    prev_col.button("Previous", on_click=story_step, args=(-1,), icon=":material/arrow_back:",
                    disabled=number == 1, width="stretch")
    with dots_col:
        html(f"<div class='dots' style='justify-content:center'>{dots}</div>")
    next_col.button("Next", on_click=story_step, args=(1,), icon=":material/arrow_forward:", icon_position="right",
                    disabled=number == 5, width="stretch", type="primary")


# ------------------------------------------------------------------ Overview
def overview():
    section("Overview", "The market at a glance, for the listings that match your filters.")
    kpis([
        ("Listings", f"{len(f):,}", f"{pct(len(f) / len(df))} of all listings" if is_filtered else None, "neutral"),
        ("Median price / night", f"€{f['price'].median():.0f}",
         *compare(f["price"].median(), df["price"].median(), lambda d: f"{d:+.0f} €")),
        ("Avg. reviews, last 12 months", f"{f['reviews_last_12m'].mean():.1f}",
         *compare(f["reviews_last_12m"].mean(), df["reviews_last_12m"].mean(), lambda d: f"{d:+.1f}", True)),
        ("Entire homes", pct((f["room_type"] == "Entire home/apt").mean()), None, "neutral"),
    ])

    left, right = st.columns(2, gap="medium")
    with left, card("ov_price", "Price at a glance", f"Median €{f['price'].median():.0f} per night"):
        fig = px.histogram(f, x="price", color_discrete_sequence=[CORAL], labels={"price": "Price per night (€)"})
        fig.update_traces(xbins=dict(start=0, end=1000, size=50), marker_cornerradius=5,
                          hovertemplate="€%{x}: %{y} listings<extra></extra>")
        chart(style(fig, height=250).update_layout(yaxis_title="Listings", bargap=0.08))
    with right, card("ov_areas", "Where the listings are", "Share of listings per neighbourhood"):
        counts = f["neighbourhood"].value_counts().reset_index()
        fig = px.pie(counts, values="count", names="neighbourhood", hole=0.6,
                     color_discrete_sequence=[CORAL, "#FF8A8E", CORAL_LIGHT, INK, GREY, SILVER])
        fig.update_traces(textinfo="percent", hovertemplate="%{label}: %{value:,} listings<extra></extra>")
        chart(style(fig, height=250, legend=True).update_layout(legend=dict(orientation="v", y=0.5, x=1.02)))

    room_med = f.groupby("room_type")["price"].median()
    top = f_all_areas["neighbourhood"].value_counts()
    lines = [f"A typical night costs <b>€{f['price'].median():.0f}</b>; half of the listings cost "
             f"<b>€{f['price'].quantile(.25):.0f}–€{f['price'].quantile(.75):.0f}</b>.",
             f"<b>{top.index[0]}</b> has the most listings ({pct(top.iloc[0] / len(f_all_areas))})."]
    if {"Entire home/apt", "Private room"} <= set(room_med.index):
        lines.append(f"Entire homes cost a median of <b>€{room_med['Entire home/apt']:.0f}</b>, "
                     f"private rooms <b>€{room_med['Private room']:.0f}</b>.")
    insights(lines)

    left, right = st.columns([3, 2], gap="medium")
    with left:
        small_title("Data preview")
        st.dataframe(f.head(10), hide_index=True, column_config=COLUMNS,
                     column_order=["name", "neighbourhood", "room_type", "price", "minimum_nights",
                                   "reviews_last_12m", "host_type"])
        st.caption("First 10 listings that match the filters. The Explore and Data views show all of them.")
    with right:
        small_title("Summary statistics")
        stats = (f[["price", "minimum_nights", "reviews_last_12m", "availability_365", "km_to_centre"]]
                 .describe().T[["mean", "50%", "min", "max"]]
                 .rename(columns={"mean": "Mean", "50%": "Median", "min": "Min", "max": "Max"})
                 .rename(index={"price": "Price (€)", "minimum_nights": "Minimum nights",
                                "reviews_last_12m": "Reviews (12 mo)", "availability_365": "Available days",
                                "km_to_centre": "Km to centre"}))
        st.dataframe(stats.round(1))


# ------------------------------------------------------------------ Host view
def host_view():
    section("If I list a property, what should I do?", "Competition, pricing and demand from a host's point of view.")
    is_pro = f["host_type"] == "Professional (11+)"
    kpis([
        ("Listings", f"{len(f):,}", None, "neutral"),
        ("Run by professional hosts", pct(is_pro.mean()),
         *compare(is_pro.mean(), (df["host_type"] == "Professional (11+)").mean(), lambda d: f"{d * 100:+.0f} pts")),
        ("Avg. reviews, last 12 months", f"{f['reviews_last_12m'].mean():.1f}",
         *compare(f["reviews_last_12m"].mean(), df["reviews_last_12m"].mean(), lambda d: f"{d:+.1f}", True)),
        ("Show a license number", pct(f["has_license"].mean()), None, "neutral"),
    ])

    left, right = st.columns(2, gap="medium")
    with left, card("host_types", "Who controls the market?", "Listings by host type"):
        counts = f.groupby("host_type", observed=False).size().reset_index(name="listings")
        fig = px.bar(counts, x="host_type", y="listings", color="host_type", text="listings",
                     color_discrete_map=HOST_COLORS, labels={"host_type": "", "listings": "Listings"})
        fig.update_traces(textposition="outside", hovertemplate="%{x}: %{y:,} listings<extra></extra>")
        chart(bar_room(style(fig), counts["listings"]))
    with right, card("host_price", "Do professional hosts charge more?", "Price per night by host type"):
        fig = px.box(f, x="host_type", y="price", color="host_type", points="outliers",
                     category_orders={"host_type": HOST_ORDER}, color_discrete_map=HOST_COLORS,
                     labels={"host_type": "", "price": "Price per night (€)"})
        fig.update_traces(marker=dict(size=3, opacity=0.35))
        chart(style(fig))

    left, right = st.columns(2, gap="medium")
    with left, card("host_areas", "Where is the competition?", AREA_HINT):
        nb_counts = f_all_areas["neighbourhood"].value_counts().sort_values().reset_index()
        fig = px.bar(nb_counts, x="count", y="neighbourhood", orientation="h", text="count",
                     labels={"count": "Listings", "neighbourhood": ""})
        fig.update_traces(textposition="outside", marker_color=area_colors(nb_counts["neighbourhood"], CORAL),
                          hovertemplate="%{y}: %{x:,} listings<extra></extra>")
        area_chart(bar_room(style(fig), nb_counts["count"], axis="x"), key="host_area")
    with right, card("host_demand", "Which price range gets the most demand?", "Median reviews in the last 12 months"):
        demand = (f.groupby("price_category", observed=True)["reviews_last_12m"]
                  .median().reset_index(name="median_reviews"))
        fig = px.bar(demand, x="price_category", y="median_reviews", color="price_category", text="median_reviews",
                     color_discrete_map=PRICE_COLORS, category_orders={"price_category": PRICE_ORDER},
                     labels={"price_category": "", "median_reviews": "Median reviews"})
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside",
                          hovertemplate="%{x}: %{y:.0f} reviews<extra></extra>")
        chart(bar_room(style(fig), demand["median_reviews"]))

    with card("host_scatter", "Does a higher price mean less demand?",
              "Drag a box around dots to analyse those listings · double-click to clear · click a legend item to hide it"):
        # Row numbers (not listing ids) identify the dots: Airbnb ids are too long for the browser to keep exact
        points_df = f.reset_index(drop=True).assign(row=lambda d: d.index)
        fig = px.scatter(points_df, x="price", y="reviews_last_12m", color="room_type", opacity=0.55, custom_data=["row"],
                         color_discrete_map=ROOM_COLORS, category_orders={"room_type": ROOM_ORDER},
                         hover_name="name", hover_data={"neighbourhood": True, "price": ":.0f", "room_type": False},
                         labels={"price": "Price per night (€)", "reviews_last_12m": "Reviews (12 months)"})
        fig.update_traces(marker=dict(size=7, line=dict(width=0)))
        event = chart(style(fig, height=400, legend=True).update_layout(dragmode="select"), key="host_select",
                      on_select="rerun", selection_mode=("box", "lasso"))
        rows = sorted({int(point["customdata"][0]) for point in event["selection"]["points"] if point.get("customdata")})
        if rows:
            picked = points_df.iloc[rows]
            kpis([
                ("Selected listings", f"{len(picked):,}", f"{pct(len(picked) / len(f))} of those shown", "coral"),
                ("Median price", f"€{picked['price'].median():.0f}",
                 f"{picked['price'].median() - f['price'].median():+.0f} € vs all shown", "neutral"),
                ("Avg. reviews, 12 months", f"{picked['reviews_last_12m'].mean():.1f}", None, "neutral"),
                ("Professional hosts", pct((picked["host_type"] == "Professional (11+)").mean()), None, "neutral"),
            ])
            st.dataframe(picked.sort_values("reviews_last_12m", ascending=False), hide_index=True, height=240,
                         column_config=COLUMNS,
                         column_order=["name", "neighbourhood", "room_type", "price", "reviews_last_12m", "link"])

    small_title("Host insights")
    lines = [f"<b>{f.loc[is_pro, 'host_id'].nunique()} professional hosts</b> run <b>{pct(is_pro.mean())}</b> "
             f"of the {len(f):,} listings shown."]
    if not demand.empty:
        best = demand.loc[demand["median_reviews"].idxmax()]
        lines.append(f"The <b>{best['price_category']}</b> range gets the most demand: a median of "
                     f"<b>{best['median_reviews']:.0f} reviews</b> a year.")
    by_host = f.groupby("host_type", observed=True).agg(price=("price", "median"), reviews=("reviews_last_12m", "mean"))
    if {"Single", "Professional (11+)"} <= set(by_host.index):
        single, pro = by_host.loc["Single"], by_host.loc["Professional (11+)"]
        lines.append(f"Professionals charge <b>€{pro['price']:.0f}</b> vs <b>€{single['price']:.0f}</b> for single "
                     f"hosts, but get <b>{pro['reviews']:.1f}</b> reviews a year vs <b>{single['reviews']:.1f}</b>.")
    top = f_all_areas["neighbourhood"].value_counts()
    lines.append(f"The most crowded area is <b>{top.index[0]}</b> with <b>{pct(top.iloc[0] / len(f_all_areas))}</b> "
                 f"of the listings.")
    if len(f) > 2:
        corr = f["price"].corr(f["reviews_last_12m"])
        strength = "almost none" if abs(corr) < 0.2 else "weak" if abs(corr) < 0.4 else "clear"
        lines.append(f"Correlation between price and demand: <b>{corr:.2f}</b> ({strength}).")
    insights(lines)


# ------------------------------------------------------------------ Guest view
def guest_view():
    section("If I visit Bologna, where should I stay?", "Prices, areas and the best value, from a guest's point of view.")
    nb_stats = f_all_areas.groupby("neighbourhood")["price"].agg(["median", "size"])
    pool = nb_stats[nb_stats["size"] >= 10] if (nb_stats["size"] >= 10).any() else nb_stats
    cheapest = pool["median"].idxmin()
    median_price = f["price"].median()
    kpis([
        ("Median price / night", f"€{median_price:.0f}",
         *compare(median_price, df["price"].median(), lambda d: f"{d:+.0f} €")),
        ("Cheapest area", cheapest, f"Median €{pool.loc[cheapest, 'median']:.0f}", "neutral"),
        ("Budget listings (< €100)", f"{(f['price'] < 100).sum():,}", None, "neutral"),
        ("Accept short stays", pct((f["stay_type"] == "Short-term").mean()), None, "neutral"),
    ])

    left, right = st.columns(2, gap="medium")
    with left, card("guest_hist", "What does a night cost?", f"Price distribution · median €{median_price:.0f}"):
        fig = px.histogram(f, x="price", color_discrete_sequence=[CORAL], labels={"price": "Price per night (€)"})
        fig.update_traces(xbins=dict(start=0, end=1000, size=50), marker_cornerradius=6,
                          hovertemplate="€%{x}: %{y} listings<extra></extra>")
        fig.add_vline(x=median_price, line_dash="dot", line_color=INK, line_width=2)
        chart(style(fig).update_layout(yaxis_title="Listings", bargap=0.08))
    with right, card("guest_areas", "Which areas are cheapest?", AREA_HINT):
        nb_price = nb_stats["median"].sort_values().reset_index()
        fig = px.bar(nb_price, x="median", y="neighbourhood", orientation="h", text="median",
                     labels={"median": "Median price per night (€)", "neighbourhood": ""})
        fig.update_traces(texttemplate="€%{text:.0f}", textposition="outside",
                          marker_color=area_colors(nb_price["neighbourhood"], INK),
                          hovertemplate="%{y}: €%{x:.0f}<extra></extra>")
        area_chart(bar_room(style(fig), nb_price["median"], axis="x"), key="guest_area")

    left, right = st.columns(2, gap="medium")
    with left, card("guest_rooms", "Entire home or private room?", "Price per night by room type"):
        fig = px.box(f, x="room_type", y="price", color="room_type", points="outliers",
                     category_orders={"room_type": ROOM_ORDER}, color_discrete_map=ROOM_COLORS,
                     labels={"room_type": "", "price": "Price per night (€)"})
        fig.update_traces(marker=dict(size=3, opacity=0.35))
        chart(style(fig, height=430))
    with right, card("guest_map", "Where are the listings?", "Hover a dot for details · scroll to zoom"):
        with st.container(horizontal=True, gap="small"):
            map_type = st.segmented_control("Map type", ["Dots", "Heat"], default="Dots", required=True,
                                            key="seg_maptype", label_visibility="collapsed")
            if map_type == "Dots":
                color_by = st.segmented_control("Colour by", ["Price", "Room type", "Host type"], default="Price",
                                                required=True, key="seg_map", label_visibility="collapsed")
        centre = dict(lat=f["latitude"].median(), lon=f["longitude"].median())
        if map_type == "Heat":
            fig = px.density_map(f, lat="latitude", lon="longitude", radius=9, center=centre, zoom=11.3,
                                 map_style="carto-positron",
                                 color_continuous_scale=[[0, "rgba(255,90,95,0)"], [0.25, CORAL_LIGHT],
                                                         [0.6, CORAL], [1, "#B4235A"]])
            fig.update_coloraxes(showscale=False)
            chart(style(fig, height=380))
        else:
            column, colors, order = {"Price": ("price_category", PRICE_COLORS, PRICE_ORDER),
                                     "Room type": ("room_type", ROOM_COLORS, ROOM_ORDER),
                                     "Host type": ("host_type", HOST_COLORS, HOST_ORDER)}[color_by]
            fig = px.scatter_map(f, lat="latitude", lon="longitude", color=column, color_discrete_map=colors,
                                 category_orders={column: order}, hover_name="name",
                                 hover_data={"price": ":.0f", "room_type": True, "neighbourhood": True,
                                             "latitude": False, "longitude": False, column: False},
                                 center=centre, zoom=11.3, map_style="carto-positron", opacity=0.8)
            fig.update_traces(marker=dict(size=7))
            chart(style(fig, height=380, legend=True).update_layout(legend=dict(y=-0.02)))

    small_title("💎 Best-value picks")
    area_median = f_all_areas.groupby("neighbourhood")["price"].transform("median").reindex(f.index)
    busy = f["reviews_last_12m"] >= f["reviews_last_12m"].quantile(0.75)
    picks = (f[(f["price"] < area_median) & busy & (f["stay_type"] == "Short-term")]
             .sort_values(["reviews_last_12m", "price"], ascending=[False, True]).head(10))
    if picks.empty:
        st.info("No best-value picks with these filters. Try a higher price or more room types.",
                icon=":material/search_off:")
    else:
        st.dataframe(picks, hide_index=True, column_config=COLUMNS,
                     column_order=["name", "neighbourhood", "room_type", "price", "reviews_last_12m", "link"])
        st.caption("Short-stay listings cheaper than their neighbourhood's median price and among the 25% most "
                   "reviewed in the last 12 months.")

    small_title("Guest insights")
    lines = [f"A typical night costs <b>€{median_price:.0f}</b>; half of the listings cost "
             f"<b>€{f['price'].quantile(.25):.0f}–€{f['price'].quantile(.75):.0f}</b>."]
    room_med = f.groupby("room_type")["price"].median()
    if {"Entire home/apt", "Private room"} <= set(room_med.index):
        saving = room_med["Entire home/apt"] - room_med["Private room"]
        lines.append(f"A private room costs <b>€{room_med['Private room']:.0f}</b> vs "
                     f"<b>€{room_med['Entire home/apt']:.0f}</b> for an entire home: <b>€{saving:.0f} less</b> a night.")
    if len(pool) > 1:
        dearest = pool["median"].idxmax()
        lines.append(f"<b>{cheapest}</b> is the cheapest area (€{pool.loc[cheapest, 'median']:.0f}), "
                     f"<b>{dearest}</b> the most expensive (€{pool.loc[dearest, 'median']:.0f}).")
    long_term = (f["stay_type"] != "Short-term").sum()
    if long_term:
        lines.append(f"<b>{long_term:,} listings</b> only accept stays of 30+ nights, so check the minimum stay.")
    insights(lines, "guest")


# ------------------------------------------------------------------ ⚖️ Compare areas
AREAS = sorted(df["neighbourhood"].unique())
st.session_state.setdefault("c_a", "Santo Stefano")
st.session_state.setdefault("c_b", "Savena")


def swap_areas():
    st.session_state["c_a"], st.session_state["c_b"] = st.session_state["c_b"], st.session_state["c_a"]


def compare_view():
    section("Compare two neighbourhoods", "Side by side, with the filters (except neighbourhood) applied.")
    col_a, col_swap, col_b = st.columns([5, 1, 5], vertical_alignment="bottom")
    col_a.selectbox("Area A", AREAS, key="c_a")
    col_swap.button("⇄", on_click=swap_areas, help="Swap the two areas", width="stretch")
    col_b.selectbox("Area B", AREAS, key="c_b")
    a, b = st.session_state["c_a"], st.session_state["c_b"]
    if a == b:
        st.info("Pick two different neighbourhoods to compare.", icon=":material/compare_arrows:")
        return
    fa, fb = f_all_areas[f_all_areas["neighbourhood"] == a], f_all_areas[f_all_areas["neighbourhood"] == b]
    if fa.empty or fb.empty:
        st.warning(f"No listings in {a if fa.empty else b} with these filters.", icon=":material/filter_alt_off:")
        return

    # (label, how to compute it, how to show it, which value wins: "low", "high" or None)
    metrics = [
        ("Listings", lambda d: len(d), lambda v: f"{v:,}", None),
        ("Median price / night", lambda d: d["price"].median(), lambda v: f"€{v:.0f}", "low"),
        ("Avg. reviews, last 12 months", lambda d: d["reviews_last_12m"].mean(), lambda v: f"{v:.1f}", "high"),
        ("Entire homes", lambda d: (d["room_type"] == "Entire home/apt").mean(), pct, None),
        ("Professional hosts", lambda d: (d["host_type"] == "Professional (11+)").mean(), pct, None),
        ("Accept short stays", lambda d: (d["stay_type"] == "Short-term").mean(), pct, "high"),
        ("Median distance to centre", lambda d: d["km_to_centre"].median(), lambda v: f"{v:.1f} km", "low"),
    ]
    rows = [f"<div class='vs-row'><div></div><div class='vs-head a'>{a}</div><div class='vs-head'>{b}</div></div>"]
    for label, calc, show, best in metrics:
        va, vb = calc(fa), calc(fb)
        win_a = best is not None and va != vb and ((va < vb) == (best == "low"))
        win_b = best is not None and va != vb and not win_a
        rows.append(f"<div class='vs-row'><div class='vs-label'>{label}</div>"
                    f"<div class='vs-val{' win' if win_a else ''}'>{show(va)}</div>"
                    f"<div class='vs-val{' win' if win_b else ''}'>{show(vb)}</div></div>")
    html(f"<div class='vs'>{''.join(rows)}</div>")
    st.caption("🏆 marks the better value for a guest: lower price, more reviews, more short stays, closer to the centre.")

    both = pd.concat([fa.assign(Area=a), fb.assign(Area=b)])
    colors = {a: CORAL, b: INK}
    left, right = st.columns(2, gap="medium")
    with left, card("cmp_price", "Price distribution", "Share of each area's listings per €50 price band"):
        fig = px.histogram(both, x="price", color="Area", barmode="overlay", histnorm="percent", opacity=0.6,
                           color_discrete_map=colors, labels={"price": "Price per night (€)"})
        fig.update_traces(xbins=dict(start=0, end=1000, size=50), hovertemplate="€%{x}: %{y:.1f}%<extra></extra>")
        chart(style(fig, height=320, legend=True).update_layout(yaxis_title="% of listings", bargap=0.06))
    with right, card("cmp_rooms", "Room type mix", "Share of listings by room type"):
        mix = (both.groupby("Area")["room_type"].value_counts(normalize=True).rename("share").reset_index())
        fig = px.bar(mix, x="Area", y="share", color="room_type", text="share", color_discrete_map=ROOM_COLORS,
                     category_orders={"room_type": ROOM_ORDER, "Area": [a, b]}, labels={"share": "", "Area": ""})
        fig.update_traces(texttemplate="%{text:.0%}", textposition="inside",
                          hovertemplate="%{x} · %{fullData.name}: %{y:.0%}<extra></extra>")
        chart(style(fig, height=320, legend=True).update_layout(barmode="stack", yaxis_tickformat=".0%"))

    with card("cmp_demand", "Demand by price range", "Median reviews in the last 12 months"):
        demand = (both.groupby(["Area", "price_category"], observed=True)["reviews_last_12m"]
                  .median().rename("median_reviews").reset_index())
        fig = px.bar(demand, x="price_category", y="median_reviews", color="Area", barmode="group", text="median_reviews",
                     color_discrete_map=colors, category_orders={"price_category": PRICE_ORDER, "Area": [a, b]},
                     labels={"price_category": "", "median_reviews": "Median reviews"})
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
        chart(bar_room(style(fig, height=320, legend=True), demand["median_reviews"]))

    pa, pb = fa["price"].median(), fb["price"].median()
    ra, rb = fa["reviews_last_12m"].mean(), fb["reviews_last_12m"].mean()
    cheaper, dearer, gap = (a, b, pb - pa) if pa < pb else (b, a, pa - pb)
    busier, quieter = (a, b) if ra > rb else (b, a)
    lines = [f"<b>{cheaper}</b> is <b>€{gap:.0f} cheaper</b> per night than {dearer} "
             f"({pct(gap / max(pa, pb))} less)." if gap else f"Both areas have the same median price (€{pa:.0f}).",
             f"<b>{busier}</b> sees more demand: <b>{max(ra, rb):.1f}</b> reviews a year per listing vs "
             f"{min(ra, rb):.1f} in {quieter}.",
             f"Professional hosts run {pct((fa['host_type'] == 'Professional (11+)').mean())} of listings in {a} "
             f"and {pct((fb['host_type'] == 'Professional (11+)').mean())} in {b}."]
    insights(lines, "guest")


# ------------------------------------------------------------------ 🔎 Explore listings
SORTS = {"Most reviewed (12 months)": ("reviews_last_12m", False), "Cheapest first": ("price", True),
         "Most expensive first": ("price", False), "Closest to the centre": ("km_to_centre", True)}


def explore_view():
    section("Explore listings", "Search, sort, and click any listing to see its details and whether its price is fair.")
    model, scores, _, _ = train_model()

    search_col, sort_col = st.columns([3, 2])
    search = search_col.text_input("Search by name", placeholder="e.g. terrace, loft, Piazza Maggiore",
                                   key="x_search", icon=":material/search:")
    sort_by = sort_col.selectbox("Sort by", list(SORTS), key="x_sort")
    rows = f[f["name"].str.contains(search, case=False, regex=False, na=False)] if search else f
    column, ascending = SORTS[sort_by]
    rows = rows.sort_values(column, ascending=ascending).reset_index(drop=True)
    if rows.empty:
        st.info(f"No listing names contain “{search}”. Try another word.", icon=":material/search_off:")
        return

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.caption(f"{len(rows):,} listings · click a row to open it")
        event = st.dataframe(rows, key="x_table", on_select="rerun", selection_mode="single-row", hide_index=True,
                             height=560, column_config=COLUMNS,
                             column_order=["name", "neighbourhood", "room_type", "price", "reviews_last_12m",
                                           "km_to_centre"])
        picked = event["selection"]["rows"]
        index = min(picked[0], len(rows) - 1) if picked else 0

    listing = rows.iloc[[index]]
    item = listing.iloc[0]
    estimate = float(predict(model, listing)[0])
    similar = df[(df["neighbourhood"] == item["neighbourhood"]) & (df["room_type"] == item["room_type"])]
    gap = item["price"] - similar["price"].median()
    kind, text = verdict(item["price"], estimate, scores["mae"])
    with right:
        html(
            f"<div class='result'><div class='name'>{escape(str(item['name']))}</div>"
            f"<div class='meta'>{item['neighbourhood']} · {item['room_type']} · {item['host_type']} host</div>"
            f"<div class='price' style='margin-top:.6rem'><span class='grad'>€{item['price']:.0f}</span> "
            f"<span class='per'>/ night</span></div>"
            f"<span class='pill {'up' if gap <= 0 else 'down'}'>€{gap:+.0f} vs similar listings "
            f"(median €{similar['price'].median():.0f})</span>"
            f"<div class='facts'><div>Model estimate<b>€{estimate:.0f}</b></div>"
            f"<div>Reviews (12 mo)<b>{item['reviews_last_12m']}</b></div>"
            f"<div>Total reviews<b>{item['number_of_reviews']}</b></div>"
            f"<div>Min. nights<b>{item['minimum_nights']}</b></div>"
            f"<div>Available days<b>{item['availability_365']}</b></div>"
            f"<div>Km to centre<b>{item['km_to_centre']:.1f}</b></div></div>"
            f"<div class='verdict {kind}'>{text}</div>"
            f"<p style='margin:.8rem 0 0'><a href='{item['link']}' target='_blank'>Open on Airbnb ↗</a></p></div>"
        )
        nearby = df[(abs(df["latitude"] - item["latitude"]) < 0.008) & (abs(df["longitude"] - item["longitude"]) < 0.011)]
        fig = px.scatter_map(nearby, lat="latitude", lon="longitude", hover_name="name",
                             hover_data={"price": ":.0f", "latitude": False, "longitude": False},
                             center=dict(lat=item["latitude"], lon=item["longitude"]), zoom=14.6,
                             map_style="carto-positron", opacity=0.5, color_discrete_sequence=[GREY])
        fig.update_traces(marker=dict(size=7), name="Nearby listings", showlegend=False)
        fig.add_trace(go.Scattermap(lat=[item["latitude"]], lon=[item["longitude"]], mode="markers",
                                    marker=dict(size=18, color=CORAL), name="This listing",
                                    hovertext=[item["name"]], hoverinfo="text"))
        html("<div style='height:.8rem'></div>")
        with st.container(key="card_explore_map"):
            chart(style(fig, height=260))


# ------------------------------------------------------------------ 🔮 Predict
NB_KM = df.groupby("neighbourhood")["km_to_centre"].median()
PREDICT_DEFAULTS = {"p_nb": "Santo Stefano", "p_room": "Entire home/apt", "p_nights": 2, "p_reviews": 20,
                    "p_reviews_12m": 8, "p_avail": 180, "p_host": 1, "p_price": None}
for key, value in PREDICT_DEFAULTS.items():
    st.session_state.setdefault(key, value)
st.session_state.setdefault("p_km", round(float(NB_KM[PREDICT_DEFAULTS["p_nb"]]), 1))


def on_predict_area():
    """When the neighbourhood changes, move the distance slider to that area's typical distance."""
    st.session_state["p_km"] = round(float(NB_KM[st.session_state["p_nb"]]), 1)


def reset_predictor():
    for key, value in PREDICT_DEFAULTS.items():
        st.session_state[key] = value
    on_predict_area()


def predictor():
    section("Price predictor",
            "Describe a listing and a Random Forest model trained on all 4,530 listings estimates its price. "
            "Hosts can price a new listing; guests can check if a price is fair.")
    model, scores, test, importance = train_model()

    left, right = st.columns([1, 1], gap="large")
    with left, card("predict_form", "Describe the listing", "The estimate updates as you change anything"):
        a, b = st.columns(2)
        a.selectbox("Neighbourhood", AREAS, key="p_nb", on_change=on_predict_area)
        b.selectbox("Room type", ROOM_ORDER, key="p_room")
        st.slider("Distance to Piazza Maggiore", 0.0, 10.0, step=0.1, format="%.1f km", key="p_km",
                  help="Jumps to the typical distance of the chosen neighbourhood; adjust it if you like.")
        st.slider("Available days in the next year", 0, 365, step=5, format="%d days", key="p_avail")
        a, b = st.columns(2)
        a.number_input("Minimum nights", 1, 365, step=1, key="p_nights")
        b.number_input("Host's number of listings", 1, 150, step=1, key="p_host")
        a, b = st.columns(2)
        a.number_input("Total reviews", 0, 1500, step=5, key="p_reviews")
        b.number_input("Reviews in the last 12 months", 0, 200, step=1, key="p_reviews_12m")
        st.button("Reset to an example listing", on_click=reset_predictor, icon=":material/restart_alt:",
                  type="tertiary")

    listing = pd.DataFrame([{
        "neighbourhood": st.session_state["p_nb"], "room_type": st.session_state["p_room"],
        "km_to_centre": st.session_state["p_km"], "minimum_nights": st.session_state["p_nights"],
        "number_of_reviews": st.session_state["p_reviews"], "reviews_last_12m": st.session_state["p_reviews_12m"],
        "availability_365": st.session_state["p_avail"], "host_listings_count": st.session_state["p_host"],
    }])
    estimate = float(predict(model, listing)[0])
    similar = df[(df["neighbourhood"] == st.session_state["p_nb"]) & (df["room_type"] == st.session_state["p_room"])]

    with right:
        if len(similar) >= 5:
            q25, med, q75 = similar["price"].quantile([.25, .5, .75])
            scale = max(similar["price"].quantile(.9), estimate) * 1.12

            def pos(value):
                return f"{min(value / scale, 1) * 100:.1f}%"

            gauge = (f"<div class='range'><div class='range-track'>"
                     f"<div class='range-band' style='left:{pos(q25)};width:calc({pos(q75)} - {pos(q25)})'></div>"
                     f"<div class='range-mark med' style='left:{pos(med)}'><span>Median €{med:.0f}</span></div>"
                     f"<div class='range-mark est' style='left:{pos(estimate)}'><span>Estimate €{estimate:.0f}</span></div>"
                     f"</div></div><div class='range-legend'>Shaded: the middle 50% of the {len(similar):,} real "
                     f"{st.session_state['p_room'].lower()} listings in {st.session_state['p_nb']} "
                     f"(€{q25:.0f}–€{q75:.0f}).</div>")
        else:
            gauge = (f"<div class='range-legend' style='margin-top:1rem'>⚠️ Only {len(similar)} real listings like "
                     f"this exist, so treat the estimate with care.</div>")
        html(f"<div class='result'><div class='label'>Estimated price</div>"
             f"<div class='price'><span class='grad'>€{estimate:.0f}</span> <span class='per'>/ night</span></div>"
             f"<div class='meta'>Typical error of the model: ±€{scores['mae']:.0f}</div>{gauge}</div>")

        small_title("Is a price fair?")
        st.number_input("Price to check (€ per night)", 0, 2000, step=5, key="p_price", placeholder="e.g. 150",
                        label_visibility="collapsed")
        if st.session_state["p_price"]:
            kind, text = verdict(st.session_state["p_price"], estimate, scores["mae"])
            html(f"<div class='verdict {kind}'>{text}</div>")
        else:
            st.caption("Type a nightly price to compare it with the estimate.")

    small_title("What moves the price?")
    left, right = st.columns(2, gap="medium")
    with left, card("pred_distance", "Distance to the centre", "Same listing, moved closer or further away"):
        distances = np.round(np.arange(0, 6.01, 0.25), 2)
        curve = price_curve(model, listing, distances)
        fig = go.Figure(go.Scatter(x=distances, y=curve, mode="lines", line=dict(color=CORAL, width=3),
                                   hovertemplate="%{x:.2f} km: €%{y:.0f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=[st.session_state["p_km"]], y=[estimate], mode="markers",
                                 marker=dict(size=14, color=INK, line=dict(color="white", width=3)),
                                 hovertemplate="Your listing: €%{y:.0f}<extra></extra>"))
        chart(style(fig, height=300).update_layout(xaxis_title="Km to Piazza Maggiore", yaxis_title="Estimated €"))
    with right, card("pred_rooms", "Room type", "Same listing, as each room type"):
        prices = room_prices(model, listing).reset_index().set_axis(["room_type", "price"], axis=1)
        fig = px.bar(prices, x="room_type", y="price", text="price", labels={"room_type": "", "price": "Estimated €"})
        fig.update_traces(texttemplate="€%{text:.0f}", textposition="outside",
                          marker_color=[CORAL if r == st.session_state["p_room"] else SILVER for r in prices["room_type"]],
                          hovertemplate="%{x}: €%{y:.0f}<extra></extra>")
        chart(bar_room(style(fig, height=300), prices["price"]))

    small_title("For hosts: a rough yearly income estimate")
    nights, occupancy, income = income_estimate(estimate, st.session_state["p_reviews_12m"], st.session_state["p_nights"])
    if nights:
        kpis([
            ("Estimated nights booked / year", f"{nights:.0f}", "Based on reviews in the last 12 months", "neutral"),
            ("Estimated occupancy", pct(occupancy), f"Capped at {pct(MAX_OCCUPANCY)}", "neutral"),
            ("Estimated yearly income", f"€{income:,.0f}", "Rough estimate before costs and fees", "coral"),
        ])
    else:
        st.info("With 0 reviews in the last 12 months, there is no booking activity to base an income estimate on.",
                icon=":material/info:")
    with st.expander("How is the income estimated?"):
        st.markdown(
            "This follows **Inside Airbnb's occupancy model**:\n"
            f"- About **{pct(REVIEW_RATE)}** of guests leave a review, so bookings ≈ reviews ÷ {REVIEW_RATE}.\n"
            f"- Each booking lasts **{MIN_STAY} nights**, or the minimum stay if that is longer.\n"
            f"- Occupancy is capped at **{pct(MAX_OCCUPANCY)}** of the year.\n"
            "- Income = nights booked × the model's estimated price.\n\n"
            "It is only a rough guide: real income depends on seasons, discounts, fees and costs."
        )

    html("<div class='section-title' style='margin-top:1.8rem'>How good is the model?</div>"
         "<div class='section-sub'>Tested on listings the model never saw during training.</div>")
    improvement = 1 - scores["mae"] / scores["baseline_mae"]
    kpis([
        ("Average error (MAE)", f"€{scores['mae']:.0f}", f"{improvement:.0%} better than guessing", "up"),
        ("Guessing the median", f"€{scores['baseline_mae']:.0f}", "Baseline error", "neutral"),
        ("R² score", f"{scores['r2']:.2f}", "Share of price differences explained", "neutral"),
        ("Train / test listings", f"{scores['n_train']:,} / {scores['n_test']:,}", "80% / 20% split", "neutral"),
    ])
    left, right = st.columns(2, gap="medium")
    with left, card("model_fit", "Predicted vs actual price", "Test listings · the dashed line is a perfect prediction"):
        fig = px.scatter(test, x="Actual price", y="Predicted price", color="Room type", opacity=0.55,
                         color_discrete_map=ROOM_COLORS, category_orders={"Room type": ROOM_ORDER})
        fig.update_traces(marker=dict(size=6, line=dict(width=0)))
        fig.add_trace(go.Scatter(x=[0, 1000], y=[0, 1000], mode="lines", name="Perfect prediction",
                                 line=dict(color=INK, dash="dash", width=1.5)))
        chart(style(fig, height=380, legend=True))
    with right, card("model_importance", "What matters most for the price?", "Feature importance"):
        fig = px.bar(importance, x="importance", y="feature", orientation="h", text="importance",
                     color_discrete_sequence=[TEAL], labels={"importance": "Importance", "feature": ""})
        fig.update_traces(texttemplate="%{text:.0%}", textposition="outside",
                          hovertemplate="%{y}: %{x:.1%}<extra></extra>")
        chart(bar_room(style(fig, height=380), importance["importance"], axis="x"))

    insights([
        f"Average error <b>€{scores['mae']:.0f}</b> vs <b>€{scores['baseline_mae']:.0f}</b> when always guessing the "
        f"median: <b>{improvement:.0%} better</b>.",
        f"R² is <b>{scores['r2']:.2f}</b>: the file has no size, bedrooms, amenities or photos, which drive much of "
        "an Airbnb price.",
        f"The most important feature is <b>{importance.iloc[-1]['feature']}</b>, then "
        f"<b>{importance.iloc[-2]['feature']}</b>.",
    ], "model")
    with st.expander("How does the model work?"):
        st.markdown(
            "1. **Data:** the 4,530 cleaned listings, split into 80% for training and 20% for testing.\n"
            "2. **Features:** neighbourhood and room type (turned into 0/1 columns with one-hot encoding), "
            "plus distance to Piazza Maggiore, minimum nights, reviews, available days and the host's listings.\n"
            "3. **Target:** the logarithm of the price, because prices are right-skewed.\n"
            "4. **Model:** a Random Forest, which averages 300 decision trees.\n"
            "5. **Evaluation:** prices are predicted for the 20% test listings the model has never seen, "
            "and compared with their real prices."
        )


# ------------------------------------------------------------------ Data view
def data_view():
    section("The data", "Every listing that matches your filters. Click a column header to sort.")
    html(f"<span class='pill ink'>{len(f):,} listings</span>")
    st.dataframe(
        f, hide_index=True, height=440, column_config=COLUMNS,
        column_order=["name", "neighbourhood", "room_type", "price", "price_category", "host_type",
                      "minimum_nights", "stay_type", "number_of_reviews", "reviews_last_12m",
                      "availability_365", "km_to_centre", "has_license", "last_review", "link"],
    )
    parts = ["bologna"]
    if selected != ALL:
        parts.append(re.sub(r"[^a-z]+", "-", selected.lower()).strip("-"))
    if max_price < 1000:
        parts.append(f"under-{max_price}")
    st.download_button("Download these listings (CSV)", f.drop(columns="link").to_csv(index=False).encode("utf-8"),
                       file_name="_".join(parts) + ".csv", mime="text/csv", icon=":material/download:")
    small_title("Summary statistics")
    st.dataframe(
        f[["price", "minimum_nights", "number_of_reviews", "reviews_per_month",
           "host_listings_count", "availability_365", "reviews_last_12m", "km_to_centre"]].describe().round(1)
    )


# ------------------------------------------------------------------ Draw the chosen view
{"Story": story, "Overview": overview, "Host": host_view, "Guest": guest_view, "Compare": compare_view,
 "Explore": explore_view, "Predict": predictor, "Data": data_view}[view]()

html("<div style='height:1.5rem'></div>")
st.caption(f"Built by {AUTHOR} · Data: [Inside Airbnb]({SOURCE_URL}), Bologna snapshot, 19 September 2026 · "
           "Independent student project, not affiliated with Airbnb.")
