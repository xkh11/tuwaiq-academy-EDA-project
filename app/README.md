# Bologna Airbnb dashboard

Streamlit dashboard for my Unit 3 final project (Khalid Alotaibi). It uses `clean_listings.csv`,
the 4,530 listings left after cleaning the data in the notebook.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

It opens at http://localhost:8501. To check that every view loads without errors:

```bash
python tests/smoke_test.py
```

## Files

- `app.py` the layout, the filters and the 8 views
- `ui.py` colours, styles and small drawing helpers
- `data.py` loads the data and applies the filters
- `model.py` the Random Forest price model
- `tests/smoke_test.py` opens every view and checks nothing breaks

## Views

- Story: the 5 main findings, one at a time
- Overview: key numbers, price and area charts, data preview and statistics
- Host: host types, prices, competition per area and demand by price
- Guest: prices per area, room types, a map and good-value listings
- Compare: two neighbourhoods side by side
- Explore: search any listing and see if its price is fair
- Predict: estimate the price of a listing (average error €73, R² 0.16)
- Data: the filtered table and a CSV download

The filters are in the sidebar (neighbourhood, room type, max price, stay type) and also in the Filters
button on each view.

Data: [Inside Airbnb](https://insideairbnb.com/get-the-data/), Bologna, 19 September 2026.
