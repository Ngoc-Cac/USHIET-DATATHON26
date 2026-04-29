"""D4 — Marketing & Channel Effectiveness."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

from data import load
from theme import (style, fmt_money, inject_css, page_header,
                   LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, CAT_PALETTE)
from filters import single_select, year_range

st.set_page_config(page_title="D4 · Marketing", page_icon="📣", layout="wide")
inject_css()
page_header("D4", "Marketing & Channel Effectiveness",
            "Web traffic · Channel mix · Conversion · CAC vs LTV")

wt = load("fact_web_traffic")
rfm = load("dim_customers_rfm", columns=(
    "customer_id", "frequency", "monetary", "acquisition_channel"))

sources = sorted(wt["traffic_source"].dropna().unique().tolist())
sel_sources = single_select("Traffic source", sources, key="d4_src")
yr = year_range(int(wt["year"].min()), int(wt["year"].max()), key_prefix="d4_year")

wt_f = wt[wt["traffic_source"].isin(sel_sources) & wt["year"].between(yr[0], yr[1])]

total_sessions = wt_f["sessions"].sum()
total_visitors = wt_f["unique_visitors"].sum()
avg_bounce = wt_f["bounce_rate"].mean() * 100 if len(wt_f) else 0
avg_pps = wt_f["pages_per_session"].mean() if len(wt_f) else 0

charts_col, kpi_col = st.columns([4, 1], gap="medium")
with kpi_col:
    st.markdown("##### KPIs")
    st.metric("Total Sessions", fmt_money(total_sessions))
    st.metric("Unique Visitors", fmt_money(total_visitors))
    st.metric("Avg Bounce", f"{avg_bounce:.2f}%")
    st.metric("Pages/Session", f"{avg_pps:.2f}")

with charts_col:
    row1c1, row1c2 = st.columns(2)
    row2c1, row2c2 = st.columns(2)

# C1 — Sessions trend by source
with row1c1:
    monthly = (wt_f.groupby(["year_month", "traffic_source"])["sessions"]
               .sum().reset_index())
    monthly["date"] = pd.to_datetime(monthly["year_month"] + "-01")
    fig = px.line(monthly.sort_values("date"), x="date", y="sessions",
                  color="traffic_source",
                  color_discrete_sequence=CAT_PALETTE,
                  labels={"sessions": "Sessions", "date": "Month"})
    fig.update_traces(line=dict(width=1.6))
    fig.update_layout(title="Sessions by Traffic Source", hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Descriptive.</b> Mix kênh thay đổi theo thời gian — "
        "kênh nào đang tăng, kênh nào suy giảm.</div>",
        unsafe_allow_html=True)

# C2 — Bounce vs Pages/Session per source
with row1c2:
    src = (wt_f.groupby("traffic_source")
           .agg(sessions=("sessions", "sum"),
                bounce=("bounce_rate", "mean"),
                pps=("pages_per_session", "mean"),
                duration=("avg_session_duration_sec", "mean"))
           .reset_index())
    fig = px.scatter(src, x="bounce", y="pps", size="sessions",
                     color="traffic_source",
                     color_discrete_sequence=CAT_PALETTE,
                     hover_name="traffic_source", size_max=50,
                     labels={"bounce": "Bounce rate", "pps": "Pages / session"})
    fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
    fig.update_layout(title="Engagement by Source (size = sessions)")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Diagnostic.</b> Quadrant tốt = bounce thấp + "
        "pages/session cao. Tập trung kênh nằm ở quadrant đó.</div>",
        unsafe_allow_html=True)

# C3 — Channel LTV (from RFM)
with row2c1:
    ch = (rfm[rfm["frequency"] > 0].groupby("acquisition_channel")
          .agg(customers=("customer_id", "count"),
               revenue=("monetary", "sum"),
               avg_ltv=("monetary", "mean"))
          .reset_index().sort_values("avg_ltv"))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ch["acquisition_channel"], y=ch["customers"],
                         name="Customers", marker_color=LIME,
                         marker_line_color=LIME_STRONG), secondary_y=False)
    fig.add_trace(go.Scatter(x=ch["acquisition_channel"], y=ch["avg_ltv"],
                             name="Avg LTV", mode="lines+markers",
                             line=dict(color=DARK, width=2)),
                  secondary_y=True)
    fig.update_layout(title="Acquisition Channel — Customers + LTV")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Predictive.</b> Customers cao chưa chắc LTV "
        "cao — re-allocate sang kênh LTV cao.</div>",
        unsafe_allow_html=True)

# C4 — Bounce rate trend (monthly avg)
with row2c2:
    bm = (wt_f.groupby(["year_month", "traffic_source"])["bounce_rate"]
          .mean().reset_index())
    bm["date"] = pd.to_datetime(bm["year_month"] + "-01")
    fig = px.line(bm.sort_values("date"), x="date", y="bounce_rate",
                  color="traffic_source",
                  color_discrete_sequence=CAT_PALETTE)
    fig.update_traces(line=dict(width=1.6))
    fig.update_layout(title="Bounce Rate Trend", hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Prescriptive.</b> Spike bounce báo hiệu "
        "vấn đề landing page hoặc traffic xấu — investigate.</div>",
        unsafe_allow_html=True)
