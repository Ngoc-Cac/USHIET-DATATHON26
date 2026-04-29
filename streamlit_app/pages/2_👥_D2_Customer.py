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
    "acquisition_channel", "recency_days", "region",
    "age_group", "gender"))
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

# =====================================================================
# Extra brainstorm row — additional D2 visuals (do NOT remove existing)
# =====================================================================
st.markdown("---")
st.markdown("##### Extra analyses · brainstorm board")
ext1, ext2, ext3 = st.columns(3)

# E1 — Avg LTV by age_group × gender (heatmap)
with ext1:
    if {"age_group", "gender"}.issubset(active.columns):
        ag = (active.dropna(subset=["age_group", "gender"])
              .groupby(["age_group", "gender"])
              .agg(avg_ltv=("monetary", "mean"),
                   customers=("customer_id", "count"))
              .reset_index())
        pivot = ag.pivot(index="age_group", columns="gender", values="avg_ltv")
        # order age groups naturally if possible
        try:
            order = sorted(pivot.index, key=lambda s: int(str(s).split("-")[0].replace("+", "")))
            pivot = pivot.loc[order]
        except Exception:
            pass
        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.astype(str),
            y=pivot.index.astype(str),
            colorscale=[[0, "#F5F6F0"], [0.5, LIME], [1, LIME_DARK]],
            colorbar=dict(thickness=10, outlinewidth=0),
            hovertemplate="Age %{y} · %{x}<br>Avg LTV: %{z:,.0f}<extra></extra>",
        ))
        fig.update_layout(title="Avg LTV · Age group × Gender")
        style(fig, height=260, show_legend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        # find best cell
        idx = np.unravel_index(np.nanargmax(pivot.values), pivot.shape)
        best = f"{pivot.index[idx[0]]} · {pivot.columns[idx[1]]}"
        st.markdown(
            f"<div class='narrative'><b>Descriptive.</b> Core buyer giá trị cao nhất: "
            f"<b>{best}</b>. Đây là persona để build creative & product line.</div>",
            unsafe_allow_html=True)
    else:
        st.info("Thiếu cột age_group/gender.")

# E2 — Customer Journey Funnel: 1st → 2nd → 3rd → loyal (5+)
with ext2:
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
    fig.update_layout(title="Customer Journey Funnel")
    style(fig, height=260, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    drop_2 = (1 - f2 / f1) * 100 if f1 else 0
    drop_loyal = (1 - f5 / f1) * 100 if f1 else 0
    st.markdown(
        f"<div class='narrative'><b>Diagnostic.</b> {drop_2:.1f}% khách không "
        f"quay lại sau lần đầu; chỉ {100 - drop_loyal:.1f}% lên loyal. "
        "Bottleneck rõ nhất nằm ở second-purchase trigger.</div>",
        unsafe_allow_html=True)

# E3 — Channel × second-order conversion (predictive: kênh nào nuôi khách tốt)
with ext3:
    ch = (rfm_f.groupby("acquisition_channel")
          .agg(total=("customer_id", "count"),
               repeat=("frequency", lambda s: (s >= 2).sum()),
               loyal=("frequency", lambda s: (s >= 5).sum()),
               avg_ltv=("monetary", "mean"))
          .assign(repeat_rate=lambda d: d["repeat"] / d["total"] * 100,
                  loyal_rate=lambda d: d["loyal"] / d["total"] * 100)
          .reset_index().sort_values("repeat_rate"))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ch["acquisition_channel"], y=ch["repeat_rate"],
                         name="2nd-order rate %",
                         marker_color=LIME, marker_line_color=LIME_STRONG),
                  secondary_y=False)
    fig.add_trace(go.Bar(x=ch["acquisition_channel"], y=ch["loyal_rate"],
                         name="Loyal rate %", marker_color=LIME_DARK),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=ch["acquisition_channel"], y=ch["avg_ltv"],
                             name="Avg LTV", mode="lines+markers",
                             line=dict(color=DARK, width=2)),
                  secondary_y=True)
    fig.update_layout(title="Channel quality · repeat & loyal rate",
                      barmode="group", hovermode="x unified")
    style(fig, height=260)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    best_ch = ch.iloc[-1]["acquisition_channel"] if len(ch) else "—"
    worst_ch = ch.iloc[0]["acquisition_channel"] if len(ch) else "—"
    st.markdown(
        f"<div class='narrative'><b>Predictive + Prescriptive.</b> Kênh "
        f"<b>{best_ch}</b> nuôi khách quay lại tốt nhất; <b>{worst_ch}</b> chỉ "
        "mang khách one-shot. Re-allocate budget theo repeat-rate, không chỉ CAC.</div>",
        unsafe_allow_html=True)
