# Bologna Airbnb: Host vs Guest

Unit 3 final project at Tuwaiq Academy by Khalid Alotaibi.

I analysed all Airbnb listings in Bologna, Italy (Inside Airbnb, 19 September 2026) from two sides:
what a host should know before listing a place, and what a guest should know before booking one.

- Dashboard: https://bologna-airbnb.streamlit.app
- Presentation: https://xkh11.github.io/tuwaiq-academy-EDA-project/
- Dataset: [listings.csv from Inside Airbnb](https://data.insideairbnb.com/italy/emilia-romagna/bologna/2026-09-19/visualisations/listings.csv)

## What I did

1. Loaded the data (5,094 rows, 19 columns) and checked its structure and missing values.
2. Cleaned it: removed 2 duplicates, 518 listings with no price and 44 prices above €1,000, which left 4,530 listings.
3. Explored it with 19 charts, from the host side and the guest side.
4. Built a Streamlit dashboard with filters, a map and a simple price model (Random Forest).

## Main findings

- A typical night costs €176 (median).
- 48 professional hosts run 28% of all listings.
- Mid-range listings (€100 to €199) get the most reviews, more than cheap ones.
- Price and demand are barely related (correlation -0.09).
- A private room is about €55 cheaper than an entire home.
- Savena is about €70 cheaper than the centre, but 69% of listings are in the two central areas.

Demand is measured with reviews in the last 12 months, because the data has no booking numbers.

## Run it

```bash
pip install -r app/requirements.txt
cd app
streamlit run app.py
```

The notebook runs in Google Colab or Jupyter and loads the data from the Inside Airbnb link.

## Folders

- `notebook/` the analysis notebook
- `app/` the Streamlit dashboard and the cleaned data
- `data/` the raw data
- `docs/` the presentation

## Tools

Python, pandas, NumPy, Matplotlib, Seaborn, scikit-learn, Plotly, Streamlit.

Photos in the presentation are from Wikimedia Commons (CC BY-SA 4.0) by Isabella.Mileti, FrancescoLama and Zairon.
