"""D2 — Customer Segmentation & Lifecycle."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from data import load
from theme import (PLOTLY_CONFIG, style, fmt_money, inject_css, page_header_inline,
                   filter_label, sidebar_notes_panel, insight_panel,
                   LIME, LIME_STRONG, LIME_DARK, DARK, SEGMENT_COLORS)
from filters import single_select
from rfm import apply_segment as apply_rfm_segment

st.set_page_config(page_title="D2 · Customer", page_icon="👥", layout="wide")
inject_css()
sidebar_notes_panel("D2 notes", "Large blank area for customer behavior notes, hypotheses, and next actions.")

rfm = load("dim_customers_rfm", columns=(
    "customer_id", "frequency", "monetary", "rfm_segment",
    "acquisition_channel", "recency_days", "region",
    "age_group", "gender",
    "R_score", "F_score", "M_score"))
rfm = apply_rfm_segment(rfm)
cohort = load("agg_cohort_retention")

regions = sorted(rfm["region"].dropna().unique().tolist())
channels = sorted(rfm["acquisition_channel"].dropna().unique().tolist())

title_col, filter_col = st.columns([1.8, 2.2], gap="medium")
with title_col:
    page_header_inline("D2", "Customer Segmentation & Lifecycle",
                       "Repeat funnel · Cohort decay · Segment value · Win-back focus")
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

champions = (active["rfm_segment"] == "Champions").sum()
at_risk = active["rfm_segment"].isin(["At Risk", "Cant Lose Them", "About To Sleep"]).sum()
avg_ltv = active["monetary"].mean() if len(active) else 0
repeat_rate = (rfm_f["frequency"] >= 2).mean() * 100 if len(rfm_f) else 0
champion_share = champions / len(active) * 100 if len(active) else 0
best_channel = "N/A"
best_channel_repeat = 0.0
if len(rfm_f):
    channel_repeat = (rfm_f.assign(is_repeat=rfm_f["frequency"] >= 2)
                      .groupby("acquisition_channel")["is_repeat"]
                      .mean()
                      .sort_values(ascending=False))
    if len(channel_repeat):
        best_channel = channel_repeat.index[0]
        best_channel_repeat = channel_repeat.iloc[0] * 100

charts_col, kpi_col = st.columns([4, 1], gap="medium")
with kpi_col:
    st.markdown("##### KPIs")
    st.metric("Total Customers", f"{len(rfm_f):,}", f"{len(active):,} active")
    st.metric("Champions", f"{champions:,}",
              f"{champion_share:.1f}% of active" if len(active) else "")
    st.metric("Win-back targets", f"{at_risk:,}", "At Risk + Cant Lose + Sleep")
    st.metric("Avg Lifetime Value", fmt_money(avg_ltv))
    insight_panel(
        "Customer insight",
        f"Repeat rate is {repeat_rate:.1f}%, Champions are only {champion_share:.1f}% of active customers, and {best_channel} has the strongest repeat quality at {best_channel_repeat:.1f}%."
    )

with charts_col:
    row1c1, row1c2 = st.columns(2)
    row2c1, row2c2 = st.columns(2)

with row1c1:
    f1 = (rfm_f["frequency"] >= 1).sum()
    f2 = (rfm_f["frequency"] >= 2).sum()
    f3 = (rfm_f["frequency"] >= 3).sum()
    f5 = (rfm_f["frequency"] >= 5).sum()
    fig = go.Figure(go.Funnel(
        y=["1st purchase", "2nd purchase", "3rd purchase", "Loyal (5+)"],
        x=[f1, f2, f3, f5],
        marker=dict(color=[LIME_STRONG, LIME, LIME_DARK, DARK]),
        textposition="inside",
        textinfo="value+percent initial",
    ))
    fig.update_layout(title="Lifetime Purchase Funnel (cumulative)")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with row1c2:
    df = cohort[(cohort["period_number"] >= 1) & (cohort["period_number"] <= 24)].copy()
    df["cohort_dt"] = pd.to_datetime(df["cohort_month"] + "-01")
    df["year"] = df["cohort_dt"].dt.year
    agg = (df.groupby(["year", "period_number"])
             .agg(active=("active_customers", "sum"),
                  size=("cohort_size", "sum"))
             .reset_index())
    agg["retention"] = agg["active"] / agg["size"] * 100
    yearly = agg.pivot(index="year", columns="period_number", values="retention")
    z_max = float(yearly.stack().max()) if len(yearly.stack()) else 5
    fig = go.Figure(go.Heatmap(
        z=yearly.values,
        x=[f"M{int(c)}" for c in yearly.columns],
        y=yearly.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.3, "#D9EE99"], [0.7, LIME], [1, LIME_DARK]],
        zmin=0, zmax=max(z_max, 5),
        colorbar=dict(thickness=10, outlinewidth=0),
        hovertemplate="Cohort %{y} · %{x}<br>Retention: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(title="Cohort Retention Heatmap (weighted, M1–M24)")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with row2c1:
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
    fig.update_layout(title="RFM Segments: Customer Count & Avg LTV", hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with row2c2:
    seg2 = (active.groupby("rfm_segment").agg(revenue=("monetary", "sum")).reset_index())
    colors = [SEGMENT_COLORS.get(s, LIME) for s in seg2["rfm_segment"]]
    fig = go.Figure(go.Treemap(
        labels=seg2["rfm_segment"], parents=[""] * len(seg2),
        values=seg2["revenue"],
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent root",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(title="Revenue Contribution by RFM Segment")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
