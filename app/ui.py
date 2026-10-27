"""Look and feel: colours, CSS, and small helpers that draw the title, KPI strip, cards, findings and charts."""
import streamlit as st

from data import HOST_ORDER, PRICE_ORDER, ROOM_ORDER

# Colours: Airbnb coral on the data, warm neutrals everywhere else
CORAL = "#FF5A5F"        # the one data hue
CORAL_PALE = "#FFC2C4"
CORAL_DARK = "#A3202B"
CORAL_TEXT = "#C8303D"   # coral that is readable as text on white
INK = "#222222"
GREY = "#6A6A6A"         # secondary text
MID = "#B0B0B0"          # data that is not the answer
SILVER = "#DDDDDD"
LINE = "#EBEBEB"
FONT = "'DM Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"

# One subject keeps one colour on every screen
HOST_COLORS = dict(zip(HOST_ORDER, [INK, MID, CORAL]))
PRICE_COLORS = dict(zip(PRICE_ORDER, [CORAL_PALE, CORAL, CORAL_DARK]))
ROOM_COLORS = dict(zip(ROOM_ORDER, [CORAL, INK, MID, SILVER]))

PLOTLY_CONFIG = {"displaylogo": False, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["autoScale2d", "toImage", "lasso2d"]}

# The product mark: one of Bologna's porticoes, drawn as an arch
MARK = ("<svg viewBox='0 0 24 24' width='30' height='30' aria-hidden='true'>"
        "<path d='M3 22V10.5a9 9 0 0 1 18 0V22h-4.5V10.5a4.5 4.5 0 0 0-9 0V22z' fill='#FF5A5F'/></svg>")

CSS = """
<style>
:root {--ground: #F7F7F7; --surface: #FFFFFF; --border: #EBEBEB; --rule: #F2F2F2; --control: #DDDDDD;
       --text: #222222; --muted: #6A6A6A; --coral: #FF5A5F; --coral-text: #C8303D;}
.block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1240px;}
[data-testid="stHeader"] {background: var(--ground);}
[data-testid="stAppDeployButton"] {display: none;}
.st-key-ltr_fix {position: absolute; width: 0; height: 0; overflow: hidden;}

/* Always left-to-right, even if the browser is in Arabic or translates the page */
html, body, .stApp, [data-testid="stSidebar"], [data-testid="stSlider"], [data-testid="stSlider"] * {
    direction: ltr !important;}
[data-testid="stSlider"] [role="slider"] {background: #FFFFFF !important; border: 1px solid var(--control) !important;
                                          box-shadow: 0 1px 2px rgba(0,0,0,.12) !important;}

/* Figures line up digit for digit */
.kpi-value, .vs-val, .result .price, .facts b, .chapter .big, .findings b {font-variant-numeric: tabular-nums;}

/* Chosen room types and stay types are neutral chips in ink, not coral blocks: colour stays on the data */
[data-testid="stMultiSelectTagsContainer"] > span > span {background: #F2F2F2 !important; color: var(--text) !important;}
[data-testid="stMultiSelectTagsContainer"] > span > span * {color: var(--text) !important; fill: var(--muted) !important;}
button[data-variant="pills"] {border-color: var(--control) !important; color: var(--text) !important;
                              background: var(--surface) !important;}
button[data-variant="pills"][data-selected="true"] {border-color: var(--text) !important; background: #F2F2F2 !important;
                                                    font-weight: 600;}

/* Sidebar: the product's mark, name and scope */
.brand {display: flex; align-items: center; gap: 10px; margin: -.4rem 0 .9rem;}
.brand .name {font-weight: 700; font-size: 1.08rem; letter-spacing: -0.01em; color: var(--text); line-height: 1.2;}
.brand .scope {font-size: .8rem; color: var(--muted);}
.brand.phone-only {display: none;}

/* View tabs: a quiet track with a white pill on the open view */
[class*="st-key-seg_"] [role="radiogroup"] {background: #EFEFEF; padding: 3px; border-radius: 999px; gap: 2px;}
[class*="st-key-seg_"] button {border: none !important; background: transparent !important; box-shadow: none !important;
                              border-radius: 999px !important; padding: 6px 14px !important; color: var(--text) !important;
                              transition: background .15s ease;}
[class*="st-key-seg_"] button:hover {background: rgba(255,255,255,.6) !important;}
[class*="st-key-seg_"] button[aria-checked="true"] {background: #FFFFFF !important; font-weight: 600;
                              box-shadow: 0 1px 2px rgba(0,0,0,.1) !important;}

/* Page title and its finding */
h1.page-title {font-size: 2rem !important; font-weight: 700 !important; letter-spacing: -0.02em; line-height: 1.2;
               color: var(--text); margin: .9rem 0 .25rem !important; padding: 0 !important;}
.page-sub {font-size: 1rem; color: var(--muted); line-height: 1.5; max-width: 820px; margin: 0 0 .2rem;}
.page-sub b {color: var(--text); font-weight: 600;}
.small-title {font-size: 1.1rem; font-weight: 700; letter-spacing: -0.01em; color: var(--text); margin: 1.6rem 0 .5rem;}

/* The scope row: how many listings are shown and which filters are on */
.scope-line {color: var(--muted); font-size: .95rem;}
.scope-line b {color: var(--text); font-weight: 600;}

/* KPI strip: one white container split by thin lines */
.kpis {display: grid; gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 16px;
       overflow: hidden; margin: .3rem 0 1rem;}
.kpi {background: var(--surface); padding: 16px 20px 15px;}
.kpi-label {color: var(--muted); font-size: .84rem;}
.kpi-value {font-size: 1.65rem; font-weight: 600; letter-spacing: -0.02em; color: var(--text); line-height: 1.25;
            margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.kpi-note {color: var(--muted); font-size: .8rem; margin-top: 2px;}
.kpi.lead .kpi-value {color: var(--coral-text);}

/* Cards (containers with key "card_...") */
[class*="st-key-card_"] {background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
                         padding: 18px 20px 8px;}
.card-title {font-size: 1rem; font-weight: 600; color: var(--text);}
.card-sub {font-size: .84rem; color: var(--muted); margin-top: 1px;}

/* Findings: one panel of ruled rows */
.findings {background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 6px 20px;
           margin: .2rem 0 .6rem;}
.findings .f-title {font-size: 1rem; font-weight: 600; color: var(--text); padding: 12px 0 6px;}
.findings ul {list-style: none; margin: 0; padding: 0;}
.findings li {padding: 11px 0; border-top: 1px solid var(--rule); font-size: .97rem; line-height: 1.5; color: var(--text);
              margin: 0;}
.findings b {font-weight: 600;}

/* Story: one finding at a time, read like a page */
.chapter {display: flex; flex-direction: column; gap: .5rem; padding: .2rem 0 .8rem;}
.chapter .side {font-size: .9rem; color: var(--muted);}
.chapter .side b {color: var(--text); font-weight: 600;}
.chapter .big {font-size: clamp(3rem, 5.4vw, 4.4rem); font-weight: 700; letter-spacing: -0.04em; line-height: 1;
               color: var(--coral);}
.chapter .title {font-size: 1.55rem; font-weight: 700; letter-spacing: -0.02em; color: var(--text); line-height: 1.2;}
.chapter .text {font-size: 1.02rem; color: var(--text); line-height: 1.55;}
.progress-text {text-align: center; color: var(--muted); font-size: .9rem;}

/* Compare areas */
.vs {background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 4px 20px;
     margin-bottom: .4rem;}
.vs-row {display: grid; grid-template-columns: 1.3fr 1fr 1fr; gap: 12px; align-items: center; padding: 11px 0;
         border-top: 1px solid var(--rule);}
.vs-row:first-child {border-top: none;}
.vs-head {font-weight: 600; font-size: 1rem; text-align: right;}
.vs-head.a {color: var(--coral-text);}
.vs-label {color: var(--muted); font-size: .9rem;}
.vs-val {font-size: 1.2rem; font-weight: 500; color: var(--text); text-align: right;}
.vs-val.win {color: var(--coral-text); font-weight: 700;}

/* Result and detail cards */
.result {background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 22px 24px;}
.result .label {color: var(--muted); font-size: .9rem;}
.result .price {font-size: 2.5rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1.1; color: var(--text);}
.result .per {font-size: 1rem; color: var(--muted); font-weight: 500; letter-spacing: 0;}
.result .meta {color: var(--muted); font-size: .9rem; margin-top: .25rem;}
.result .name {font-size: 1.2rem; font-weight: 600; color: var(--text); line-height: 1.3;}
.pill {display: inline-block; margin-top: 10px; font-size: .8rem; font-weight: 500; padding: 3px 10px; border-radius: 999px;
       background: #F2F2F2; color: var(--muted);}
.pill.up {background: #DCFAE5; color: #04250E;}
.pill.down {background: #FFEDEA; color: #831C1E;}
.facts {display: grid; grid-template-columns: repeat(2, 1fr); gap: 1px; background: var(--border); border: 1px solid var(--border);
        border-radius: 12px; overflow: hidden; margin-top: 1rem;}
.facts div {background: var(--surface); padding: 10px 12px; font-size: .8rem; color: var(--muted);}
.facts b {display: block; font-size: 1.02rem; font-weight: 600; color: var(--text);}
.range {position: relative; margin: 2.6rem 4px 1.9rem;}
.range-track {position: relative; height: 8px; border-radius: 999px; background: #F2F2F2;}
.range-band {position: absolute; top: 0; bottom: 0; border-radius: 999px; background: var(--coral-pale, #FFD6D7);}
.range-mark {position: absolute; top: 50%; width: 14px; height: 14px; border-radius: 50%; transform: translate(-50%, -50%);
             border: 2px solid #FFFFFF;}
.range-mark.est {background: var(--coral);}
.range-mark.med {background: var(--text);}
.range-mark span {position: absolute; left: 50%; transform: translateX(-50%); white-space: nowrap; font-size: .8rem; font-weight: 600;}
.range-mark.est span {bottom: 17px; color: var(--coral-text);}
.range-mark.med span {top: 17px; color: var(--text);}
.range-legend {color: var(--muted); font-size: .84rem;}
.verdict {border-radius: 12px; padding: 11px 15px; font-weight: 500; margin-top: .5rem;}
.verdict.good {background: #DCFAE5; color: #04250E;}
.verdict.fair {background: #F2F2F2; color: var(--text);}
.verdict.high {background: #FFEDEA; color: #831C1E;}

@media (max-width: 640px) {
  .block-container {padding-top: 1.2rem;}
  .brand.phone-only {display: flex; margin: 1.6rem 0 .6rem;}
  h1.page-title {font-size: 1.5rem !important;}
  /* Tabs scroll sideways in one row instead of wrapping into a block */
  [class*="st-key-seg_"] [role="radiogroup"] {flex-wrap: nowrap !important; overflow-x: auto; scrollbar-width: none;}
  [class*="st-key-seg_"] button {flex: none !important; white-space: nowrap;}
  .kpis {grid-template-columns: repeat(2, 1fr) !important;}
  .kpi:last-child:nth-child(odd) {grid-column: span 2;}
  .kpi-value {font-size: 1.35rem;}
  .facts {grid-template-columns: repeat(2, 1fr);}
  .vs {padding: 4px 14px;}
  .vs-val {font-size: 1.02rem;}
  .result .price {font-size: 2.1rem;}
}
</style>
"""

# Streamlit's sliders take their direction from the browser language. With an Arabic browser they switch to
# right-to-left: the handle is drawn from the right while the coloured bar starts on the left, and dragging goes
# the wrong way. This tiny invisible script tells the dashboard page to use English (left-to-right) layout.
LTR_FIX = """
<script>
(function () {
  const w = window.parent;
  try {
    Object.defineProperty(w.navigator, "language", {get: () => "en-US", configurable: true});
    Object.defineProperty(w.navigator, "languages", {get: () => ["en-US", "en"], configurable: true});
    const html = w.document.documentElement;
    html.setAttribute("lang", "en");
    html.setAttribute("dir", "ltr");
    html.setAttribute("translate", "no");
    w.dispatchEvent(new Event("languagechange"));
  } catch (error) {
    console.warn("Could not switch the page to left-to-right", error);
  }
})();
</script>
"""

# Friendly column titles used by every table
COLUMNS = {
    "name": st.column_config.TextColumn("Listing", width="large"),
    "neighbourhood": "Neighbourhood",
    "room_type": "Room type",
    "price": st.column_config.NumberColumn("Price", format="€%d"),
    "price_category": "Price category",
    "host_type": "Host type",
    "minimum_nights": "Min. nights",
    "stay_type": "Stay type",
    "number_of_reviews": "Total reviews",
    "reviews_last_12m": st.column_config.NumberColumn("Reviews (12 mo)"),
    "has_license": st.column_config.CheckboxColumn("License"),
    "last_review": st.column_config.DateColumn("Last review", format="YYYY-MM-DD"),
    "km_to_centre": st.column_config.NumberColumn("Km to centre", format="%.1f"),
    "availability_365": st.column_config.ProgressColumn("Available days", min_value=0, max_value=365, format="%d"),
    "link": st.column_config.LinkColumn("Airbnb page", display_text="Open ↗"),
}


def setup_page():
    st.markdown(CSS, unsafe_allow_html=True)
    with st.container(key="ltr_fix"):
        st.iframe(LTR_FIX, height=1)


def pct(x):
    return f"{x:.0%}"


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def brand(scope, phone_only=False):
    """The product's mark and name, with what the data covers. On the page itself it only shows on phones."""
    html(f"<div class='brand{' phone-only' if phone_only else ''}'>{MARK}<div><div class='name'>Bologna Airbnb</div>"
         f"<div class='scope'>{scope}</div></div></div>")


def style(fig, height=340, legend=False):
    """One quiet look for every chart: faint horizontal grid, grey ticks, colour only on the data."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=4, r=12, t=36 if legend else 10, b=4),
        font=dict(family=FONT, size=12, color=GREY),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title_text="", font=dict(size=12, color=INK)),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=SILVER, font=dict(family=FONT, size=13, color=INK)),
        bargap=0.32,
        title_text="",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="", tickfont=dict(color=GREY, size=12),
                     title_font=dict(color=GREY, size=12))
    fig.update_yaxes(gridcolor=LINE, zeroline=False, showline=False, ticks="", tickfont=dict(color=GREY, size=12),
                     title_font=dict(color=GREY, size=12))
    fig.update_traces(selector=dict(type="bar"), marker_cornerradius=4, marker_line_width=0)
    return fig


def bar_room(fig, values, axis="y"):
    """Leave 20% space after the longest bar so its label is not cut off."""
    top = max(values.max(), 1) * 1.2
    return fig.update_yaxes(range=[0, top]) if axis == "y" else fig.update_xaxes(range=[0, top])


def chart(fig, **kwargs):
    return st.plotly_chart(fig, config=PLOTLY_CONFIG, **kwargs)


def card(key, title, subtitle=None):
    """A white card with a title; use it with `with card(...):`."""
    box = st.container(key=f"card_{key}")
    box.markdown(f"<div class='card-title'>{title}</div>"
                 + (f"<div class='card-sub'>{subtitle}</div>" if subtitle else ""), unsafe_allow_html=True)
    return box


def section(title, finding):
    """The view's one title, and under it the finding the data shows."""
    html(f"<h1 class='page-title'>{title}</h1><p class='page-sub'>{finding}</p>")


def small_title(text):
    html(f"<div class='small-title'>{text}</div>")


def kpis(items):
    """One strip of headline figures. Each item: (label, value, note or None, tone); tone "lead" marks the answer."""
    cells = "".join(
        f"<div class='kpi{' lead' if tone == 'lead' else ''}'><div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value'>{value}</div>" + (f"<div class='kpi-note'>{note}</div>" if note else "") + "</div>"
        for label, value, note, tone in items
    )
    html(f"<div class='kpis' style='grid-template-columns: repeat({len(items)}, 1fr)'>{cells}</div>")


def insights(lines, title="What this shows"):
    """The findings of a view, as one panel of ruled rows."""
    rows = "".join(f"<li>{line}</li>" for line in lines)
    html(f"<div class='findings'><div class='f-title'>{title}</div><ul>{rows}</ul></div>")


def verdict(price, estimate, mae):
    """Good deal / fair / expensive, compared with the model's estimate and its typical error."""
    diff = price - estimate
    if diff < -mae:
        return "good", f"Good deal: €{-diff:.0f} below the model's estimate."
    if diff > mae:
        return "high", f"Expensive: €{diff:.0f} above the model's estimate."
    return "fair", f"Fair price: within the model's typical error (±€{mae:.0f})."
