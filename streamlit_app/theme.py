"""Brand palette + plotly styling + CSS injection for the Streamlit app."""
from __future__ import annotations
import plotly.graph_objects as go
import streamlit as st

# Match template.jpg
LIME = "#B8E835"
LIME_STRONG = "#9DCB1F"
LIME_DARK = "#6FA82B"
LIME_SOFT = "#E8F5C8"
DARK = "#1A1F14"
GREY = "#6B7280"
AMBER = "#F59E0B"
RED = "#DC2626"
BG = "#F5F6F0"
CARD = "#FFFFFF"
BORDER = "#E5E7E0"
CAT_PALETTE = ["#9DCB1F", "#6FA82B", "#3F6B17", "#C9E866", "#7C9F2C",
               "#BFD877", "#4F7A1B", "#A8C940", "#5C8222", "#D9EE99"]

SEGMENT_COLORS = {
    "Champions": "#6FA82B",
    "Loyal Customers": "#9DCB1F",
    "Potential Loyalists": "#B8E835",
    "New Customers": "#C9E866",
    "Promising": "#D9EE99",
    "Need Attention": "#F59E0B",
    "About to Sleep": "#F97316",
    "At Risk": "#EF4444",
    "Cannot Lose Them": "#B91C1C",
    "Hibernating": "#6B7280",
    "Lost": "#374151",
}


def style(fig: go.Figure, height: int | None = None,
          show_legend: bool = True, compact: bool = True) -> go.Figure:
    """Apply unified theme. compact=True trims margins for grid layout."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, sans-serif", color=DARK, size=11),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=13, color=DARK, family="Inter"),
        margin=dict(l=32, r=12, t=32, b=24) if compact else dict(l=44, r=24, t=56, b=44),
        legend=dict(bgcolor="rgba(255,255,255,0.6)",
                    bordercolor=BORDER, borderwidth=1,
                    font=dict(size=9),
                    orientation="h", y=-0.22, x=0),
        showlegend=show_legend,
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(gridcolor="#EEF1E5", linecolor="#D1D5C8",
                     zerolinecolor="#EEF1E5",
                     tickfont=dict(color=GREY, size=10))
    fig.update_yaxes(gridcolor="#EEF1E5", linecolor="#D1D5C8",
                     zerolinecolor="#EEF1E5",
                     tickfont=dict(color=GREY, size=10))
    return fig


_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="st-"], .stApp { font-family: 'Inter', sans-serif !important; }

.stApp { background: #F5F6F0 !important; }

/* Hide Streamlit chrome */
header[data-testid="stHeader"] { background: transparent; height: 0; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 0.4rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 1600px;
}
/* Tighten gaps between rows so 2x2 grid fits */
[data-testid="stVerticalBlock"] { gap: 0.45rem !important; }
[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }

/* ---- Sidebar (dark olive like template) ---- */
section[data-testid="stSidebar"] {
    background: #1A1F14 !important;
    border-right: 1px solid #232818;
}
section[data-testid="stSidebar"] * { color: #E8EDD8 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #B8E835 !important; }
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: #8E9379 !important;
    font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] a {
    color: #E8EDD8 !important;
    border-radius: 8px;
    padding: 6px 10px;
}
section[data-testid="stSidebar"] a:hover { background: #2A301F !important; }
section[data-testid="stSidebar"] [aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: #B8E835 !important;
}
section[data-testid="stSidebar"] [aria-current="page"] * { color: #1A1F14 !important; font-weight: 600; }

/* Sidebar inputs */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="popover"] {
    background: #2A301F !important; color: #E8EDD8 !important;
    border-color: #3A4129 !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: #B8E835 !important; color: #1A1F14 !important;
}
section[data-testid="stSidebar"] [role="slider"] { background: #B8E835 !important; }

/* ---- Main content ---- */
h1, h2, h3 { color: #1A1F14 !important; letter-spacing: -0.01em; }
.stCaption, [data-testid="stCaptionContainer"] { color: #6B7280 !important; }

/* Accent tag (used inside markdown) */
.accent-tag {
    display: inline-block; background: #B8E835; color: #1A1F14;
    padding: 2px 12px; border-radius: 4px; font-weight: 700;
    margin-right: 4px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #FFFFFF; border: 1px solid #E5E7E0;
    border-radius: 12px; padding: 8px 12px;
    box-shadow: 0 1px 2px rgba(20,30,10,0.04);
    margin-bottom: 4px;
}
[data-testid="stMetricLabel"] {
    color: #6B7280 !important;
    font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px;
}
[data-testid="stMetricLabel"]::before {
    content: ""; display: inline-block;
    width: 6px; height: 6px; background: #B8E835;
    border-radius: 50%; margin-right: 6px; vertical-align: middle;
}
[data-testid="stMetricValue"] {
    color: #1A1F14 !important; font-weight: 700 !important;
    font-size: 20px !important; letter-spacing: -0.01em;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* Plotly chart containers — give them card shell like HTML */
div[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid #E5E7E0;
    border-radius: 12px;
    padding: 4px 6px 0;
    box-shadow: 0 1px 2px rgba(20,30,10,0.04);
}

/* Narrative box — compact 1-2 line */
.narrative {
    background: #E8F5C8;
    border-left: 3px solid #9DCB1F;
    padding: 4px 10px; border-radius: 0 6px 6px 0;
    font-size: 11.5px; line-height: 1.35;
    color: #1A1F14;
    margin-top: 2px;
    overflow: hidden;
}
.narrative b { color: #1A1F14; }

/* Containers (st.container border=True) — match card style */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF; border: 1px solid #E5E7E0;
    border-radius: 14px; padding: 14px 16px;
    box-shadow: 0 1px 2px rgba(20,30,10,0.04);
}

/* Buttons */
.stButton > button {
    background: #B8E835; color: #1A1F14;
    border: 1px solid #9DCB1F; border-radius: 8px;
    font-weight: 600; padding: 6px 14px;
}
.stButton > button:hover {
    background: #9DCB1F; border-color: #6FA82B;
}

/* Expanders */
[data-testid="stExpander"] {
    background: #FFFFFF; border: 1px solid #E5E7E0;
    border-radius: 12px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #E5E7E0; border-radius: 10px; overflow: hidden;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: #FFFFFF; border: 1px solid #E5E7E0;
    border-radius: 8px 8px 0 0; padding: 8px 14px;
}
.stTabs [aria-selected="true"] {
    background: #B8E835 !important; color: #1A1F14 !important;
    font-weight: 600;
}
</style>
"""


def inject_css() -> None:
    """Call once at the top of every page (right after set_page_config)."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def page_header(tag: str, title: str, subtitle: str = "") -> None:
    """Branded header bar with lime accent tag — call after inject_css."""
    st.markdown(
        f"## <span class='accent-tag'>{tag}</span> {title}",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.caption(subtitle)


def fmt_money(v: float) -> str:
    if abs(v) >= 1e9:
        return f"{v/1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"{v/1e6:.2f}M"
    if abs(v) >= 1e3:
        return f"{v/1e3:.1f}K"
    return f"{v:.0f}"
