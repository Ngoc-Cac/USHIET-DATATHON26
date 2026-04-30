"""D2 — Customer Segmentation & Lifecycle."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

from data import load
from theme import (PLOTLY_CONFIG, style, fmt_money, inject_css, page_header_inline, filter_label, sidebar_notes_panel,
                   LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, GREY, SEGMENT_COLORS, CAT_PALETTE)
from filters import single_select

st.set_page_config(page_title="D2 · Customer", page_icon="👥", layout="wide")
inject_css()
sidebar_notes_panel("D2 notes", "Large blank area for customer behavior notes, hypotheses, and next actions.")

from rfm import apply_segment as apply_rfm_segment

rfm = load("dim_customers_rfm", columns=(
    "customer_id", "frequency", "monetary", "rfm_segment",
    "acquisition_channel", "recency_days", "region",
    "age_group", "gender",
    "R_score", "F_score", "M_score"))
# Re-apply RFM segmentation rule that fixes "Cant Lose Them" ordering
rfm = apply_rfm_segment(rfm)
cohort = load("agg_cohort_retention")
orders = load("fact_orders_enriched", columns=(
    "customer_id", "order_id", "line_revenue", "order_ym", "order_year"))

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
at_risk = active["rfm_segment"].isin(["At Risk", "Cant Lose Them", "About To Sleep"]).sum()
avg_ltv = active["monetary"].mean() if len(active) else 0

charts_col, kpi_col = st.columns([4, 1], gap="medium")
with kpi_col:
    st.markdown("##### KPIs")
    st.metric("Total Customers", f"{len(rfm_f):,}", f"{len(active):,} active")
    st.metric("Champions", f"{champions:,}",
              f"{champions/len(active)*100:.1f}% of active" if len(active) else "")
    st.metric("Win-back targets", f"{at_risk:,}", "At Risk + Cant Lose + Sleep")
    st.metric("Avg Lifetime Value", fmt_money(avg_ltv))

with charts_col:
    row1c1, row1c2 = st.columns(2)
    row2c1, row2c2 = st.columns(2)

# C1 — Customer Journey Funnel (lifetime cumulative repeat)
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
    fig.update_layout(title="Customer Journey Funnel")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# C2 — Cohort Retention heatmap (weighted, M1–M24)
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
    z_max = float(yearly.stack().max())
    fig = go.Figure(go.Heatmap(
        z=yearly.values,
        x=[f"M{int(c)}" for c in yearly.columns],
        y=yearly.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.3, "#D9EE99"], [0.7, LIME], [1, LIME_DARK]],
        zmin=0, zmax=max(z_max, 5),
        colorbar=dict(thickness=10, outlinewidth=0),
        hovertemplate="Cohort %{y} · %{x}<br>Retention: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(title="Cohort Retention · weighted %, M1–M24 (M0=100% omitted)")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# C3 — RFM Segments (count + avg LTV combo)
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
    fig.update_layout(title="RFM Segments — count + avg LTV", hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# C4 — Revenue by RFM Segment (Treemap)
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
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

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
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        # find best cell
        idx = np.unravel_index(np.nanargmax(pivot.values), pivot.shape)
        best = f"{pivot.index[idx[0]]} · {pivot.columns[idx[1]]}"
        st.markdown(
            f"<div class='narrative'><b>Descriptive.</b> Core buyer giá trị cao nhất: "
            f"<b>{best}</b>. Đây là persona để build creative & product line.</div>",
            unsafe_allow_html=True)
    else:
        st.info("Thiếu cột age_group/gender.")

# E2 — Acquisition Channel · Revenue + Avg LTV (combo)
with ext2:
    ch = (active.groupby("acquisition_channel")
          .agg(customers=("customer_id", "count"),
               revenue=("monetary", "sum"),
               avg_value=("monetary", "mean"))
          .reset_index().sort_values("revenue", ascending=False))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ch["acquisition_channel"], y=ch["revenue"],
                         name="Revenue", marker_color=LIME,
                         marker_line_color=LIME_STRONG,
                         text=[fmt_money(v) for v in ch["revenue"]],
                         textposition="outside"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=ch["acquisition_channel"], y=ch["avg_value"],
                             name="Avg LTV", mode="lines+markers",
                             line=dict(color=DARK, width=2.5),
                             marker=dict(size=10, line=dict(color="white", width=1.5))),
                  secondary_y=True)
    fig.update_yaxes(title_text="Revenue", secondary_y=False)
    fig.update_yaxes(title_text="Avg LTV", secondary_y=True)
    fig.update_layout(title="Acquisition Channel · Revenue (bar) + Avg LTV (line)",
                      hovermode="x unified")
    style(fig, height=260)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    spread = (ch["avg_value"].max() - ch["avg_value"].min()) / ch["avg_value"].mean() * 100
    st.markdown(
        f"<div class='narrative'><b>Predictive.</b> Bar (revenue) chênh nhau theo scale, "
        f"nhưng line LTV gần như phẳng — spread chỉ <b>{spread:.1f}%</b> giữa kênh cao "
        "và thấp. Channels gần như identical về chất lượng khách.</div>",
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
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    best_ch = ch.iloc[-1]["acquisition_channel"] if len(ch) else "—"
    worst_ch = ch.iloc[0]["acquisition_channel"] if len(ch) else "—"
    st.markdown(
        f"<div class='narrative'><b>Predictive + Prescriptive.</b> Kênh "
        f"<b>{best_ch}</b> nuôi khách quay lại tốt nhất; <b>{worst_ch}</b> chỉ "
        "mang khách one-shot. Re-allocate budget theo repeat-rate, không chỉ CAC.</div>",
        unsafe_allow_html=True)

# =====================================================================
# Extra row 2 — Channel revenue evolution over time
# =====================================================================
st.markdown("---")
st.markdown("##### Channel revenue · evolution over time")

# Join orders to customer's acquisition channel; apply existing region/channel filters
rfm_subset = rfm[rfm["region"].isin(sel_regions)
                 & rfm["acquisition_channel"].isin(sel_channels)]
orders_ch = orders.merge(
    rfm_subset[["customer_id", "acquisition_channel"]],
    on="customer_id", how="inner")

ext4, ext5 = st.columns(2)

# E4 — Absolute revenue per channel over time (multi-line)
with ext4:
    yearly = (orders_ch.groupby(["order_year", "acquisition_channel"])["line_revenue"]
              .sum().reset_index())
    fig = px.line(yearly.sort_values("order_year"),
                  x="order_year", y="line_revenue",
                  color="acquisition_channel",
                  color_discrete_sequence=CAT_PALETTE,
                  markers=True,
                  labels={"line_revenue": "Revenue", "order_year": "Year"})
    fig.update_traces(line=dict(width=2), marker=dict(size=7))
    # Annotate peak year
    peak_total = yearly.groupby("order_year")["line_revenue"].sum().idxmax()
    fig.add_vline(x=peak_total, line_dash="dot", line_color=GREY, opacity=0.5,
                  annotation_text=f"Peak {peak_total}", annotation_position="top")
    fig.update_layout(title="Revenue by acquisition channel · over time",
                      hovermode="x unified",
                      legend=dict(orientation="h", y=-0.25, x=0,
                                  font=dict(size=9)))
    style(fig, height=300)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    # Compute peak vs latest comparison
    yr_peak = yearly[yearly["order_year"] == peak_total]["line_revenue"].sum()
    last_y = yearly["order_year"].max()
    yr_last = yearly[yearly["order_year"] == last_y]["line_revenue"].sum()
    st.markdown(
        f"<div class='narrative'><b>Descriptive.</b> Tất cả 6 channels follow cùng "
        f"shape: peak <b>{peak_total}</b> ({fmt_money(yr_peak)}), giảm về "
        f"{fmt_money(yr_last)} năm {last_y} (−{(1-yr_last/yr_peak)*100:.1f}%). "
        "Không có channel nào outlier — declining trend là vấn đề tổng thể.</div>",
        unsafe_allow_html=True)

# E5 — Channel mix % over time (100% stacked area) — show stability of mix
with ext5:
    pivot = (orders_ch.groupby(["order_year", "acquisition_channel"])["line_revenue"]
             .sum().unstack(fill_value=0))
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    fig = go.Figure()
    for i, col in enumerate(pivot_pct.columns):
        fig.add_trace(go.Scatter(
            x=pivot_pct.index, y=pivot_pct[col],
            name=col, mode="lines",
            stackgroup="one", line=dict(width=0.5),
            fillcolor=CAT_PALETTE[i % len(CAT_PALETTE)],
            hovertemplate="<b>" + col + "</b><br>%{x}: %{y:.1f}%<extra></extra>",
        ))
    fig.update_layout(title="Channel mix % · stacked over time",
                      hovermode="x unified",
                      yaxis_ticksuffix="%",
                      legend=dict(orientation="h", y=-0.25, x=0,
                                  font=dict(size=9)))
    style(fig, height=300)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    # Variance of share over years (max - min for each channel)
    share_var = (pivot_pct.max() - pivot_pct.min()).max()
    st.markdown(
        f"<div class='narrative'><b>Diagnostic.</b> Mix channel cực ổn định — "
        f"channel biến thiên nhiều nhất chỉ <b>±{share_var:.1f}pp</b> qua 11 năm. "
        "Bands stack gần như parallel = mix lock-in. Củng cố insight ở C3/E3: "
        "channel allocation không phải lever growth.</div>",
        unsafe_allow_html=True)

# =====================================================================
# Extra row 3 — Channel AOV ranked vs overall mean
# =====================================================================
st.markdown("---")
st.markdown("##### Channel AOV · ranked vs overall mean")

# Compute AOV per channel (revenue / unique orders) using filtered customer base
orders_aov = orders.merge(
    rfm_subset[["customer_id", "acquisition_channel"]],
    on="customer_id", how="inner")
if {"order_id"}.issubset(orders_aov.columns):
    aov_df = (orders_aov.groupby("acquisition_channel")
              .agg(revenue=("line_revenue", "sum"),
                   orders=("order_id", "nunique"))
              .assign(aov=lambda d: d["revenue"] / d["orders"])
              .reset_index().sort_values("aov", ascending=True))
    overall_aov = orders_aov["line_revenue"].sum() / orders_aov["order_id"].nunique()
else:
    # order_id not loaded yet → load it
    o2 = load("fact_orders_enriched", columns=("customer_id", "order_id", "line_revenue"))
    o2 = o2.merge(rfm_subset[["customer_id", "acquisition_channel"]],
                  on="customer_id", how="inner")
    aov_df = (o2.groupby("acquisition_channel")
              .agg(revenue=("line_revenue", "sum"),
                   orders=("order_id", "nunique"))
              .assign(aov=lambda d: d["revenue"] / d["orders"])
              .reset_index().sort_values("aov", ascending=True))
    overall_aov = o2["line_revenue"].sum() / o2["order_id"].nunique()

# Color bars: green if above overall, amber if below
bar_colors = [LIME_DARK if v >= overall_aov else AMBER for v in aov_df["aov"]]

fig = go.Figure()
fig.add_trace(go.Bar(
    y=aov_df["acquisition_channel"], x=aov_df["aov"],
    orientation="h",
    marker_color=bar_colors,
    marker_line_color=DARK, marker_line_width=0.5,
    text=[fmt_money(v) for v in aov_df["aov"]],
    textposition="outside",
    name="AOV per channel",
    hovertemplate="<b>%{y}</b><br>AOV: %{x:,.0f} VND<extra></extra>",
))
fig.add_vline(
    x=overall_aov, line_dash="dash", line_color=DARK, line_width=2,
    annotation_text=f"Overall AOV {fmt_money(overall_aov)}",
    annotation_position="top",
)
fig.update_layout(
    title="AOV by channel · ranked vs overall benchmark",
    xaxis_title="Avg Order Value (VND)",
    showlegend=False,
)
style(fig, height=320, show_legend=False)
st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

above = aov_df[aov_df["aov"] >= overall_aov]["acquisition_channel"].tolist()
below = aov_df[aov_df["aov"] < overall_aov]["acquisition_channel"].tolist()
spread = aov_df["aov"].max() - aov_df["aov"].min()
spread_pct = (aov_df["aov"].max() / aov_df["aov"].min() - 1) * 100
st.markdown(
    f"<div class='narrative'><b>Predictive.</b> Channels trên benchmark "
    f"(<b>{fmt_money(overall_aov)}</b>): {', '.join(above) or '—'}. "
    f"Dưới: {', '.join(below) or '—'}. "
    f"Nhưng spread max-min chỉ <b>{fmt_money(spread)} ({spread_pct:.1f}%)</b> — "
    "tất cả channels mang basket size gần như identical. "
    "AOV không phải lever phân biệt channel quality.</div>",
    unsafe_allow_html=True)
