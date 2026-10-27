# Bologna Airbnb: Host vs Guest

Unit 3 final project at Tuwaiq Academy by Khalid Alotaibi.

I analysed all Airbnb listings in Bologna, Italy from two sides: what a host should know before listing a
place, and what a guest should know before booking one.

- Dashboard: https://bologna-airbnb.streamlit.app
- Presentation: https://xkh11.github.io/tuwaiq-academy-EDA-project/
- Dataset: [listings.csv from Inside Airbnb](https://data.insideairbnb.com/italy/emilia-romagna/bologna/2026-09-19/visualisations/listings.csv)

## The dataset

The data comes from Inside Airbnb, which collects public Airbnb listings city by city. This file is a snapshot
of Bologna on 19 September 2026. Each row is one listing, with its price, room type, neighbourhood, location,
host, minimum nights, availability and reviews.

- 5,094 rows and 19 columns
- 6 neighbourhoods and 4 room types
- Real problems to clean: missing prices, duplicates and prices up to €10,000

I chose it because it is recent, it needs real cleaning, and hosts and guests look at the same data in
different ways.

## Questions

For hosts:
- Who controls the market, single hosts or professionals?
- Do professional hosts charge more?
- Which price range gets the most demand?
- Where is the competition strongest?

For guests:
- What does a typical night cost?
- Which neighbourhoods are cheapest?
- How much do you save with a private room?
- Where are the listings on the map?

The data has no booking numbers, so I used reviews in the last 12 months as a measure of demand.

## Cleaning

| Step | Rows left |
|---|---|
| Raw data | 5,094 |
| Removed 2 duplicate listings | 5,092 |
| Removed 518 listings with no price | 4,574 |
| Removed 44 prices above €1,000 | 4,530 |

I also dropped 3 columns I did not need, filled missing review values with 0, changed `last_review` to a date,
renamed 2 columns and added 4 new ones: `host_type`, `has_license`, `price_category` and `stay_type`.
The cleaned data is saved in `app/clean_listings.csv`.

## Main findings

- A typical night costs €176 (median). The mean is €206 because a few listings are very expensive.
- 48 professional hosts run 28% of all listings. They charge €31 more a night, but single hosts get 35% more reviews.
- Mid-range listings (€100 to €199) get the most reviews: a median of 10 a year, against 3 for budget listings.
- Price and demand are barely related (correlation -0.09).
- A private room is about €55 cheaper than an entire home (€134 against €189).
- Savena is about €70 cheaper than Santo Stefano (€125 against €195), but 69% of listings are in the two central areas.

## Dashboard

The Streamlit dashboard has 8 views: Story, Overview, Host, Guest, Compare, Explore, Predict and Data.
You can filter by neighbourhood, room type, max price and stay type, compare two neighbourhoods, open any
listing, and download the filtered data as CSV.

The Predict view uses a Random Forest model to estimate the price of a listing. Its average error is €73,
against €88 when always guessing the median price. It explains only 16% of the price differences (R² 0.16),
because the data has no size, bedrooms or photos.

## Limitations

- One snapshot (September 2026), so no seasons.
- Listed prices, not what guests actually paid.
- Reviews only approximate demand.

## Run it

```bash
pip install -r app/requirements.txt
cd app
streamlit run app.py
```

The notebook runs in Google Colab or Jupyter and loads the data from the Inside Airbnb link.

## Folders

- `notebook/` the analysis notebook (cleaning, 19 charts, model and insights)
- `app/` the Streamlit dashboard and the cleaned data
- `data/` the raw data
- `docs/` the presentation

## Tools

Python, pandas, NumPy, Matplotlib, Seaborn, scikit-learn, Plotly, Streamlit.

Photos in the presentation are from Wikimedia Commons (CC BY-SA 4.0) by Isabella.Mileti, FrancescoLama and Zairon.
