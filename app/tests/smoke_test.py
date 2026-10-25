"""
Smoke test: opens every view of the dashboard without a browser and checks that nothing crashes.

Run it from the app folder with:
    py tests/smoke_test.py
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
VIEWS = ["Story", "Overview", "Host", "Guest", "Compare", "Explore", "Predict", "Data"]


def fresh_app(**state):
    app = AppTest.from_file(APP, default_timeout=120)
    app.session_state["welcomed"] = True  # skip the welcome dialog
    for key, value in state.items():
        app.session_state[key] = value
    return app.run()


def check(name, app):
    assert not app.exception, f"{name}: {[e.message for e in app.exception]}"
    print(f"ok  {name}")


for view in VIEWS:
    check(f"view {view}", fresh_app(seg_nav=view))

for chapter in range(1, 6):
    check(f"story chapter {chapter}", fresh_app(seg_nav="Story", seg_story=chapter))

app = fresh_app(seg_nav="Overview", f_rooms=[])
check("empty filter", app)
assert any("No listings match" in w.value for w in app.warning), "empty filter should show a warning"
print("ok  empty filter shows a warning")

app = fresh_app(seg_nav="Predict")
assert any("€206" in m.value for m in app.markdown), "default predictor estimate should be €206"
print("ok  predictor estimate for the example listing is €206")

check("compare same area", fresh_app(seg_nav="Compare", c_a="Navile", c_b="Navile"))
check("focused area + low price", fresh_app(seg_nav="Host", f_nb="Savena", f_max_price=150))
check("explore search", fresh_app(seg_nav="Explore", x_search="terrace", x_sort="Cheapest first"))
check("guest heat map", fresh_app(seg_nav="Guest", seg_maptype="Heat"))
print("\nAll smoke tests passed.")
