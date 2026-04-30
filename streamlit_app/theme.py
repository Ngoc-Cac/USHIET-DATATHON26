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


PLOTLY_CONFIG = {
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "png", "scale": 2,
        "filename": "datathon-2026-chart",
    },
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@700;800&display=swap');

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
section[data-testid="stSidebar"] > div {
    background: #1A1F14 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #B8E835 !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #E8EDD8;
}
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: #8E9379 !important;
    font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    display: block;
    background: transparent !important;
    border: 1px solid transparent;
    margin-bottom: 4px;
}
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] a {
    color: #E8EDD8 !important;
    border-radius: 10px;
    padding: 8px 10px;
    text-decoration: none !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover,
section[data-testid="stSidebar"] a:hover { background: #2A301F !important; }
section[data-testid="stSidebar"] [aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: #B8E835 !important;
    border-color: #9DCB1F !important;
}
section[data-testid="stSidebar"] [aria-current="page"] * { color: #1A1F14 !important; font-weight: 600; }

/* Sidebar inputs */
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="input"] > div {
    background: #242A1B !important;
    border: 1px solid #39402B !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="input"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] input {
    color: #F3F6E9 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] svg,
section[data-testid="stSidebar"] [data-baseweb="input"] svg {
    fill: #B8E835 !important;
}
section[data-testid="stSidebar"] [data-baseweb="menu"],
section[data-testid="stSidebar"] [role="listbox"] {
    background: #242A1B !important;
    border: 1px solid #39402B !important;
}
section[data-testid="stSidebar"] [role="option"] {
    color: #E8EDD8 !important;
    background: transparent !important;
}
section[data-testid="stSidebar"] [role="option"][aria-selected="true"],
section[data-testid="stSidebar"] [role="option"]:hover {
    background: #313823 !important;
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
.top-nav {
    margin-bottom: 8px;
}
.top-nav a {
    display: block;
    text-align: center;
    text-decoration: none !important;
    color: #4F5842 !important;
    font-size: 0.92rem;
    font-weight: 600;
    padding: 8px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.55);
}
.top-nav a:hover {
    background: rgba(184,232,53,0.18);
    color: #1A1F14 !important;
}
.top-nav [aria-current="page"] {
    background: #B8E835 !important;
    color: #1A1F14 !important;
}

.home-hero {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 20px;
    padding: 6px 0 10px;
}
.home-hero-title {
    line-height: 0.94;
    margin: 0;
}
.home-hero-main,
.home-hero-sub {
    display: block;
    font-family: 'Orbitron', 'Inter', sans-serif !important;
    font-weight: 800;
    letter-spacing: -0.06em;
    color: #11150F;
}
.home-hero-main {
    font-size: 3.3rem;
}
.home-hero-sub {
    font-size: 3rem;
    text-transform: lowercase;
}
.home-year-chip,
.home-tagline {
    display: inline-block;
    background: #9DCB1F;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 1px 8px 2px;
    margin-left: 6px;
}
.home-tagline {
    color: #1A1F14;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-left: 0;
    margin-top: 8px;
}
.team-shell {
    background: linear-gradient(180deg, #FFFFFF 0%, #FBFCF7 100%);
    border: none;
    border-radius: 16px;
    padding: 18px;
    box-shadow: none;
}
.team-eyebrow {
    color: #6B7280 !important;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    margin-bottom: 6px;
}
.team-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #11150F;
    margin-bottom: 8px;
    letter-spacing: -0.03em;
}
.team-copy {
    color: #4A5142 !important;
    font-size: 0.98rem;
    line-height: 1.55;
    margin-bottom: 14px;
}
.member-card {
    background: #F8FAF2;
    border: none;
    border-radius: 14px;
    padding: 14px;
    min-height: 116px;
    box-shadow: none;
}
.member-role {
    color: #6FA82B !important;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 800;
    margin-bottom: 8px;
}
.member-name {
    color: #11150F;
    font-size: 1.05rem;
    font-weight: 800;
    margin-bottom: 6px;
}
.member-note {
    color: #697160 !important;
    font-size: 0.92rem;
    line-height: 1.45;
}

.page-header-inline {
    padding-top: 2px;
    padding-bottom: 4px;
}
.page-header-title {
    color: #1A1F14 !important;
    font-size: 1.95rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin-bottom: 4px;
}
.page-header-subtitle {
    color: #6B7280 !important;
    font-size: 0.98rem;
    line-height: 1.35;
}
.filter-label {
    color: #7B8370 !important;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    margin-bottom: 4px;
}
.sidebar-notes {
    background: linear-gradient(180deg, #212719 0%, #1A1F14 100%);
    border: none;
    border-radius: 16px;
    padding: 16px 14px;
    min-height: 420px;
    margin-top: 16px;
    box-shadow: none;
}
.sidebar-notes-title {
    color: #B8E835 !important;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 800;
    margin-bottom: 10px;
}
.sidebar-notes-copy {
    color: #9EA58E !important;
    font-size: 0.92rem;
    line-height: 1.5;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #FFFFFF; border: none;
    border-radius: 12px; padding: 8px 12px;
    box-shadow: none;
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
    border: none;
    border-radius: 12px;
    padding: 4px 6px 0;
    box-shadow: none;
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
    background: #FFFFFF; border: none;
    border-radius: 14px; padding: 14px 16px;
    box-shadow: none;
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
    background: #FFFFFF; border: none;
    border-radius: 12px;
    box-shadow: none;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: none; border-radius: 10px; overflow: hidden;
    box-shadow: none;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: #FFFFFF; border: none;
    border-radius: 8px 8px 0 0; padding: 8px 14px;
    box-shadow: none;
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


def page_header_inline(tag: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="page-header-inline">
          <div class="page-header-title"><span class="accent-tag">{tag}</span> {title}</div>
          <div class="page-header-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_nav(current: str) -> None:
    pages = [
        ("D1 Revenue", "1_📈_D1_Revenue.py", "d1"),
        ("D2 Customer", "2_👥_D2_Customer.py", "d2"),
        ("D3 Product", "3_📦_D3_Product.py", "d3"),
        ("D4 Marketing", "4_📣_D4_Marketing.py", "d4"),
        ("Data Model", "5_🧬_Data_Model.py", "dm"),
    ]
    cols = st.columns(len(pages), gap="small")
    for col, (label, path, key) in zip(cols, pages):
        with col:
            st.markdown("<div class='top-nav'>", unsafe_allow_html=True)
            try:
                st.page_link(path, label=label)
            except Exception:
                st.markdown(label)
            st.markdown("</div>", unsafe_allow_html=True)


def filter_label(text: str) -> None:
    st.markdown(f"<div class='filter-label'>{text}</div>", unsafe_allow_html=True)


def sidebar_notes_panel(title: str = "Notes / Insights",
                        note: str = "") -> None:
    """No-op (notes panel removed from sidebar). Kept for API compatibility."""
    return


def fmt_money(v: float) -> str:
    if abs(v) >= 1e9:
        return f"{v/1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"{v/1e6:.2f}M"
    if abs(v) >= 1e3:
        return f"{v/1e3:.1f}K"
    return f"{v:.0f}"
