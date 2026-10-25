"""Look and feel: colours, CSS, and small helpers that draw cards, KPI tiles, insights and charts."""
import streamlit as st

from data import HOST_ORDER, PRICE_ORDER, ROOM_ORDER

# Colours: Airbnb coral + Apple-style neutrals
CORAL = "#FF5A5F"
CORAL_LIGHT = "#FFB3B5"
INK = "#1D1D1F"
GREY = "#86868B"
SILVER = "#D2D2D7"
GREEN = "#34C759"
TEAL = "#30B0C7"
FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

HOST_COLORS = dict(zip(HOST_ORDER, [CORAL, CORAL_LIGHT, INK]))
PRICE_COLORS = dict(zip(PRICE_ORDER, [GREEN, CORAL, INK]))
ROOM_COLORS = dict(zip(ROOM_ORDER, [CORAL, INK, GREY, SILVER]))

PLOTLY_CONFIG = {"displaylogo": False, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["autoScale2d", "toImage"]}

CSS = """
<style>
.block-container {padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1280px;}
[data-testid="stHeader"] {background: rgba(245,245,247,.72); backdrop-filter: saturate(180%) blur(20px);}
[data-testid="stAppDeployButton"] {display: none;}
.st-key-ltr_fix {position: absolute; width: 0; height: 0; overflow: hidden;}
@keyframes rise {from {opacity: 0; transform: translateY(8px);} to {opacity: 1; transform: none;}}

/* Always left-to-right, even if the browser is in Arabic or translates the page */
html, body, .stApp, [data-testid="stSidebar"], [data-testid="stSlider"], [data-testid="stSlider"] * {
    direction: ltr !important;}
[data-testid="stSlider"] [role="slider"] {background: #FFFFFF !important; box-shadow: 0 1px 4px rgba(0,0,0,.3) !important;}

/* Hero */
.eyebrow {color: #FF5A5F; font-weight: 600; font-size: .92rem; margin-bottom: .4rem;}
.headline {font-size: clamp(2.2rem, 4.4vw, 3.7rem); font-weight: 800; line-height: 1.04; letter-spacing: -0.04em;
           color: #1D1D1F; margin: 0;}
.grad {background: linear-gradient(90deg, #FF5A5F 0%, #FF7A59 45%, #E0457B 100%);
       -webkit-background-clip: text; background-clip: text; color: transparent;}
.subhead {font-size: 1.14rem; color: #6E6E73; max-width: 800px; margin: .85rem 0 0; line-height: 1.5;}
.count {color: #6E6E73; font-size: .92rem; margin: 1.1rem 0 .35rem;}
.count b {color: #1D1D1F;}

/* Headings */
.section-title {font-size: 1.75rem; font-weight: 800; letter-spacing: -0.035em; color: #1D1D1F; margin: .6rem 0 .15rem;}
.section-sub {color: #6E6E73; font-size: 1.02rem; margin-bottom: 1rem;}
.small-title {font-size: 1.2rem; font-weight: 700; letter-spacing: -0.02em; color: #1D1D1F; margin: 1.4rem 0 .6rem;}

/* KPI tiles */
.kpis {display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin: .2rem 0 1.1rem;}
.kpi {background: #FFFFFF; border-radius: 20px; padding: 18px 20px; animation: rise .45s ease both;
      box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 6px 20px rgba(0,0,0,.04); transition: transform .2s ease, box-shadow .2s ease;}
.kpi:hover {transform: translateY(-2px); box-shadow: 0 2px 4px rgba(0,0,0,.05), 0 14px 30px rgba(0,0,0,.08);}
.kpi-label {color: #6E6E73; font-size: .86rem; font-weight: 500;}
.kpi-value {font-size: 2rem; font-weight: 700; letter-spacing: -0.035em; color: #1D1D1F; line-height: 1.2;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.pill {display: inline-block; margin-top: 8px; font-size: .76rem; font-weight: 600; padding: 3px 9px;
       border-radius: 999px; background: #F2F2F7; color: #6E6E73;}
.pill.up {background: #E9F8EE; color: #1E8E3E;}
.pill.down {background: #FFECEC; color: #D70015;}
.pill.coral {background: #FFE3E4; color: #D9363B;}
.pill.ink {background: #1D1D1F; color: #FFFFFF;}

/* White cards (containers with key "card_...") */
[class*="st-key-card_"] {background: #FFFFFF; border-radius: 22px; padding: 20px 22px 10px;
                         box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 6px 20px rgba(0,0,0,.04); animation: rise .5s ease both;}
.card-title {font-size: 1.06rem; font-weight: 700; letter-spacing: -0.015em; color: #1D1D1F;}
.card-sub {font-size: .85rem; color: #86868B; margin-top: 1px;}

/* Insight cards */
.insights {display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 14px; margin-bottom: .6rem;}
.insight {background: #FFFFFF; border-radius: 18px; padding: 16px 18px; display: flex; gap: 12px; animation: rise .5s ease both;
          box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 6px 20px rgba(0,0,0,.04); font-size: .95rem; line-height: 1.45; color: #1D1D1F;}
.insight .dot {flex: none; width: 10px; height: 10px; border-radius: 50%; margin-top: 7px; background: #FF5A5F;}
.insight.guest .dot {background: #1D1D1F;}
.insight.model .dot {background: #30B0C7;}

/* Segmented controls (keys starting with "seg_") look like iOS */
[class*="st-key-seg_"] [role="radiogroup"] {background: #E8E8ED; padding: 3px; border-radius: 20px; gap: 2px;}
[class*="st-key-seg_"] button {border: none !important; background: transparent !important; box-shadow: none !important;
                              border-radius: 999px !important; padding: 6px 14px !important; color: #1D1D1F !important;
                              transition: background .2s ease, box-shadow .2s ease;}
[class*="st-key-seg_"] button[aria-checked="true"] {background: #FFFFFF !important; font-weight: 600;
                              box-shadow: 0 1px 3px rgba(0,0,0,.14), 0 1px 1px rgba(0,0,0,.04) !important;}

/* Filter tokens under the header */
.st-key-tokens button {background: #FFFFFF !important; border: 1px solid #E5E5EA !important; min-height: 32px;
                       padding: 2px 12px !important; font-size: .85rem;}
.st-key-tokens button:hover {border-color: #FF5A5F !important; color: #E0484D !important;}

/* Sidebar brand */
.brand {display: flex; align-items: center; gap: 12px; margin-bottom: .6rem;}
.brand .logo {width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, #FF5A5F, #E0457B);
              display: grid; place-items: center; color: #FFFFFF; font-size: 1.25rem;}
.brand .name {font-weight: 700; font-size: 1.05rem; letter-spacing: -0.01em; color: #1D1D1F;}
.brand .sub {font-size: .8rem; color: #86868B;}

/* Story mode */
.chapter {display: flex; flex-direction: column; gap: .6rem; padding: .4rem 0 1rem; animation: rise .45s ease both;}
.chapter .tag {align-self: flex-start; font-size: .78rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
               padding: 4px 10px; border-radius: 999px; background: #FFE3E4; color: #D9363B;}
.chapter .tag.guest {background: #1D1D1F; color: #FFFFFF;}
.chapter .tag.model {background: #E3F6FA; color: #1B7F92;}
.chapter .big {font-size: clamp(3.2rem, 6vw, 5.2rem); font-weight: 800; letter-spacing: -0.05em; line-height: 1;}
.chapter .title {font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; color: #1D1D1F; line-height: 1.15;}
.chapter .text {font-size: 1.05rem; color: #3A3A3C; line-height: 1.55;}
.dots {display: flex; gap: 8px; align-items: center; margin: .2rem 0 .8rem;}
.dots span {width: 8px; height: 8px; border-radius: 999px; background: #D2D2D7; transition: all .3s ease;}
.dots span.on {width: 26px; background: #FF5A5F;}

/* Compare areas */
.vs {background: #FFFFFF; border-radius: 22px; padding: 8px 22px; margin-bottom: 1rem; animation: rise .45s ease both;
     box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 6px 20px rgba(0,0,0,.04);}
.vs-row {display: grid; grid-template-columns: 1.3fr 1fr 1fr; gap: 12px; align-items: center; padding: 12px 0;
         border-bottom: 1px solid #F2F2F7;}
.vs-row:last-child {border-bottom: none;}
.vs-head {font-weight: 700; font-size: 1.02rem;}
.vs-head.a {color: #E0484D;}
.vs-label {color: #6E6E73; font-size: .9rem;}
.vs-val {font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; color: #1D1D1F;}
.vs-val.win::after {content: " 🏆"; font-size: 1rem;}

/* Result and detail cards */
.result {background: #FFFFFF; border-radius: 24px; padding: 24px 26px; animation: rise .45s ease both;
         box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 10px 30px rgba(0,0,0,.06);}
.result .label {color: #6E6E73; font-weight: 500;}
.result .price {font-size: 4rem; font-weight: 800; letter-spacing: -0.05em; line-height: 1.05;}
.result .per {font-size: 1.1rem; color: #86868B; font-weight: 600; letter-spacing: 0;}
.result .meta {color: #6E6E73; font-size: .9rem; margin-top: .3rem;}
.result .name {font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; color: #1D1D1F; line-height: 1.25;}
.facts {display: grid; grid-template-columns: repeat(auto-fit, minmax(118px, 1fr)); gap: 10px; margin-top: 1rem;}
.facts div {background: #F5F5F7; border-radius: 14px; padding: 10px 12px; font-size: .8rem; color: #6E6E73;}
.facts b {display: block; font-size: 1.05rem; color: #1D1D1F;}
.range {position: relative; margin: 2.6rem 4px 1.9rem;}
.range-track {position: relative; height: 8px; border-radius: 999px; background: #F2F2F7;}
.range-band {position: absolute; top: 0; bottom: 0; border-radius: 999px; background: #FFD6D7;}
.range-mark {position: absolute; top: 50%; width: 16px; height: 16px; border-radius: 50%; transform: translate(-50%, -50%);
             border: 3px solid #FFFFFF; box-shadow: 0 1px 4px rgba(0,0,0,.3);}
.range-mark.est {background: #FF5A5F;}
.range-mark.med {background: #1D1D1F;}
.range-mark span {position: absolute; left: 50%; transform: translateX(-50%); white-space: nowrap; font-size: .78rem; font-weight: 600;}
.range-mark.est span {bottom: 18px; color: #E0484D;}
.range-mark.med span {top: 18px; color: #1D1D1F;}
.range-legend {color: #86868B; font-size: .82rem;}
.verdict {border-radius: 14px; padding: 12px 16px; font-weight: 600; margin-top: .4rem; animation: rise .3s ease both;}
.verdict.good {background: #E9F8EE; color: #1E8E3E;}
.verdict.fair {background: #F2F2F7; color: #1D1D1F;}
.verdict.high {background: #FFECEC; color: #D70015;}

@media (max-width: 640px) {
  .facts {grid-template-columns: repeat(2, 1fr);}
  .vs-val {font-size: 1.1rem;}
  .result .price {font-size: 3rem;}
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
    "last_review": st.column_config.DateColumn("Last review", format="DD MMM YYYY"),
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


def style(fig, height=340, legend=False):
    """Clean, Apple-like look for every chart."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=4, r=12, t=12, b=4),
        font=dict(family=FONT, size=13, color="#3A3A3C"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="top", y=-0.16, x=0, title_text="", font=dict(size=12)),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E5E5EA", font=dict(family=FONT, size=13, color=INK)),
        bargap=0.32,
        title_text="",
    )
    for update in (fig.update_xaxes, fig.update_yaxes):
        update(gridcolor="#F0F0F3", zeroline=False, showline=False, ticks="", tickfont=dict(color=GREY),
               title_font=dict(color=GREY, size=12))
    fig.update_traces(selector=dict(type="bar"), marker_cornerradius=8, marker_line_width=0)
    return fig


def bar_room(fig, values, axis="y"):
    """Leave 20% space after the longest bar so its label is not cut off."""
    top = max(values.max(), 1) * 1.2
    return fig.update_yaxes(range=[0, top]) if axis == "y" else fig.update_xaxes(range=[0, top])


def chart(fig, **kwargs):
    return st.plotly_chart(fig, config=PLOTLY_CONFIG, **kwargs)


def card(key, title, subtitle=None):
    """A white rounded card with a title; use it with `with card(...):`."""
    box = st.container(key=f"card_{key}")
    box.markdown(f"<div class='card-title'>{title}</div>"
                 + (f"<div class='card-sub'>{subtitle}</div>" if subtitle else ""), unsafe_allow_html=True)
    return box


def section(title, subtitle):
    html(f"<div class='section-title'>{title}</div><div class='section-sub'>{subtitle}</div>")


def small_title(text):
    html(f"<div class='small-title'>{text}</div>")


def kpis(items):
    """Row of KPI tiles. Each item: (label, value, note or None, tone: up / down / neutral / coral / ink)."""
    tiles = "".join(
        f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div>"
        + (f"<div class='pill {tone}'>{note}</div>" if note else "") + "</div>"
        for label, value, note, tone in items
    )
    html(f"<div class='kpis'>{tiles}</div>")


def insights(lines, kind=""):
    cards = "".join(f"<div class='insight {kind}'><div class='dot'></div><div>{line}</div></div>" for line in lines)
    html(f"<div class='insights'>{cards}</div>")


def verdict(price, estimate, mae):
    """Good deal / fair / expensive, compared with the model's estimate and its typical error."""
    diff = price - estimate
    if diff < -mae:
        return "good", f"Good deal: €{-diff:.0f} below the model's estimate."
    if diff > mae:
        return "high", f"Expensive: €{diff:.0f} above the model's estimate."
    return "fair", f"Fair price: within the model's typical error (±€{mae:.0f})."
