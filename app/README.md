# Bologna Airbnb: Host vs Guest dashboard

Interactive Streamlit dashboard for the Unit 3 Final Project by **Khalid Alotaibi**. It uses
`clean_listings.csv` (4,530 listings), the cleaned data produced by the notebook in the `bologna-airbnb-python` folder.

## How to run

Open a terminal in this folder and run:

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

The dashboard opens in your browser at http://localhost:8501.

To check that every view works without opening a browser:

```bash
py tests/smoke_test.py
```

## Files

| File | What it does |
|---|---|
| `app.py` | Page layout, sidebar filters and the 8 views |
| `ui.py` | Colours, CSS and drawing helpers (cards, KPI tiles, insights, chart style) |
| `data.py` | Loads the cleaned data and applies the filters |
| `model.py` | The Random Forest price model and its helpers |
| `tests/smoke_test.py` | Opens every view headless and checks nothing breaks |
| `.streamlit/config.toml` | Theme: colours, Inter font, rounded corners |

## The 8 views

- **Story:** the 5 key findings, one chapter at a time, with Previous / Next.
- **Overview:** KPIs compared with the whole city, price and area charts, a data preview and summary statistics.
- **Host:** host types, price by host type, competition per neighbourhood (click a bar to focus the dashboard),
  demand by price, and a price-vs-demand chart where you can box-select listings to analyse them.
- **Guest:** price distribution, cheapest areas, price by room type, a map (dots or heat), best-value picks.
- **Compare:** two neighbourhoods side by side with winner badges and comparison charts.
- **Explore:** search and sort every listing, then click one to see its details, the model's estimate and a fair-price verdict.
- **Predict:** describe a listing to get an estimated price, how distance and room type change it, and a rough
  yearly income estimate for hosts (Inside Airbnb's occupancy model). The model's accuracy is shown openly:
  MAE €73 vs €88 for guessing the median, R² 0.16.
- **Data:** the filtered table, a CSV download and summary statistics.

The sidebar has the dataset description and the filters: neighbourhood (dropdown), room type (multiselect),
max price per night (slider), stay type (pills).

Data: [Inside Airbnb](https://insideairbnb.com/get-the-data/), Bologna snapshot of 19 September 2026.
