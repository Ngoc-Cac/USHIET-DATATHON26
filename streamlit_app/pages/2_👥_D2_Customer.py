"""D2 — Customer Segmentation & Lifecycle."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from data import load
from theme import (style, fmt_money, inject_css, page_header_inline, filter_label, sidebar_notes_panel,
                   LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, SEGMENT_COLORS)
from filters import single_select

st.set_page_config(page_title="D2 · Customer", page_icon="👥", layout="wide")
inject_css()
sidebar_notes_panel("D2 notes", "Large blank area for customer behavior notes, hypotheses, and next actions.")

rfm = load("dim_customers_rfm", columns=(
    "customer_id", "frequency", "monetary", "rfm_segment",
    "acquisition_channel", "recency_days", "region"))
cohort = load("agg_cohort_retention")

regions = sorted(rfm["region"].dropna().unique().tolist())
channels = sorted(rfm["acquisition_channel"].dropna().unique().tolist())

title_col, filter_col = st.columns([1.8, 2.2], gap="medium")
with title_col:
    page_header_inline("D2", "Customer Segmentation & Lifecycle",
                       "RFM · Cohort · Acquisition channel · LTV distribution")
with filter_col:
    f1, f2 = st.columns(2)
    with f1:
        filter_label("Region")
        sel_regions = single_select("Region", regions, key="d2_region")
    with f2:
        filter_label("Channel")
        sel_channels = single_select("Channel", channels, key="d2_ch")

rfm_f = rfm[rfm["region"].isin(sel_regions) & rfm["acquisition_channel"].isin(sel_channels)]
active = rfm_f[rfm_f["frequency"] > 0]

# KPIs
champions = (active["rfm_segment"] == "Champions").sum()
at_risk = active["rfm_segment"].isin(["At Risk", "Cannot Lose Them"]).sum()
avg_ltv = active["monetary"].mean() if len(active) else 0

charts_col, kpi_col = st.columns([4, 1], gap="medium")
with kpi_col:
    st.markdown("##### KPIs")
    st.metric("Total Customers", f"{len(rfm_f):,}", f"{len(active):,} active")
    st.metric("Champions", f"{champions:,}",
              f"{champions/len(active)*100:.1f}% of active" if len(active) else "")
    st.metric("Win-back targets", f"{at_risk:,}", "At Risk + Cannot Lose")
    st.metric("Avg Lifetime Value", fmt_money(avg_ltv))

with charts_col:
    row1c1, row1c2 = st.columns(2)
    row2c1, row2c2 = st.columns(2)

# C1 — RFM segment bar
with row1c1:
    seg = (active.groupby("rfm_segment")
           .agg(customers=("customer_id", "count"),
                revenue=("monetary", "sum"),
                avg_value=("monetary", "mean"))
           .reset_index().sort_values("customers", ascending=False))
    colors = [SEGMENT_COLORS.get(s, LIME) for s in seg["rfm_segment"]]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=seg["rfm_segment"], y=seg["customers"],
                         marker_color=colors, name="Customers"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=seg["rfm_segment"], y=seg["avg_value"],
                             name="Avg LTV", mode="lines+markers",
                             line=dict(color=DARK, width=2)),
                  secondary_y=True)
    fig.update_layout(title="RFM Segments — count + avg LTV", hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Descriptive.</b> Số đông không = giá trị cao. "
        "Top tier (Champions/Loyal) đem revenue lớn dù ít khách.</div>",
        unsafe_allow_html=True)

# C2 — Cohort heatmap
with row1c2:
    df = cohort[cohort["period_number"] <= 24].copy()
    pivot = df.pivot(index="cohort_month", columns="period_number", values="retention_rate")
    pivot.index = pd.to_datetime(pivot.index + "-01")
    yearly = pivot.groupby(pivot.index.year).mean()
    fig = go.Figure(go.Heatmap(
        z=yearly.values,
        x=[f"M{int(c)}" for c in yearly.columns],
        y=yearly.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.3, "#D9EE99"], [0.7, LIME], [1, LIME_DARK]],
        zmin=0, zmax=30,
        colorbar=dict(thickness=10, outlinewidth=0),
        hovertemplate="Cohort %{y} · %{x}<br>%{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(title="Cohort Retention (avg %, 0–24m)")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Diagnostic.</b> Sụt mạnh M1–M3, ổn định M6+. "
        "Trigger nurture trong 30/60/90 ngày sau lần mua đầu.</div>",
        unsafe_allow_html=True)

# C3 — Acquisition channel
with row2c1:
    ch = (active.groupby("acquisition_channel")
          .agg(customers=("customer_id", "count"),
               revenue=("monetary", "sum"),
               avg_value=("monetary", "mean"))
          .reset_index().sort_values("revenue"))
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                        column_widths=[0.55, 0.45], horizontal_spacing=0.04,
                        subplot_titles=("Revenue", "Avg LTV"))
    fig.add_trace(go.Bar(y=ch["acquisition_channel"], x=ch["revenue"],
                         orientation="h", marker_color=LIME,
                         marker_line_color=LIME_STRONG, name="Revenue"),
                  row=1, col=1)
    fig.add_trace(go.Bar(y=ch["acquisition_channel"], x=ch["avg_value"],
                         orientation="h", marker_color=DARK, name="Avg"),
                  row=1, col=2)
    fig.update_layout(title="Acquisition Channel", showlegend=False)
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Predictive.</b> CAC giống nhưng LTV khác — "
        "chuyển budget sang kênh avg value cao.</div>",
        unsafe_allow_html=True)

# C4 — Treemap
with row2c2:
    seg2 = (active.groupby("rfm_segment").agg(revenue=("monetary", "sum")).reset_index())
    colors = [SEGMENT_COLORS.get(s, LIME) for s in seg2["rfm_segment"]]
    fig = go.Figure(go.Treemap(
        labels=seg2["rfm_segment"], parents=[""]*len(seg2),
        values=seg2["revenue"],
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent root",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(title="Revenue by RFM Segment")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Prescriptive.</b> Ưu tiên retention budget: "
        "Champions > Cannot Lose > Potential Loyalists.</div>",
        unsafe_allow_html=True)
