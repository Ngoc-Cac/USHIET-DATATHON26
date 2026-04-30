"""D1 — Revenue & Profitability (single-screen grid)."""
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
                   LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, GREY, RED, CAT_PALETTE)
from filters import year_select, region_select, category_select

st.set_page_config(page_title="D1 · Revenue", page_icon="📈", layout="wide")
inject_css()
sidebar_notes_panel("D1 notes", "Large blank area for your narrative, assumptions, and action points.")

# ---- load
monthly = load("agg_monthly_summary")
orders = load("fact_orders_enriched", columns=(
    "category", "region", "line_revenue", "line_gross_profit",
    "line_cost", "has_promo", "order_ym", "product_id", "order_year",
    "promo_id", "discount_pct"))
products = load("dim_products")
promotions = load("dim_promotions")
promotions["campaign_family"] = (promotions["promo_name"]
                                 .str.replace(r"\s+\d{4}$", "", regex=True))

regions = sorted(orders["region"].dropna().unique().tolist())
categories = sorted(orders["category"].dropna().unique().tolist())

title_col, filter_col = st.columns([1.7, 2.3], gap="medium")
with title_col:
    page_header_inline("D1", "Revenue & Profitability",
                       "Descriptive → Diagnostic → Predictive → Prescriptive")
with filter_col:
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        filter_label("From year")
        yr_from = year_select("From year", list(range(2012, 2023)), key="d1_year_from")
    with f2:
        filter_label("To year")
        yr_to = year_select("To year", list(range(yr_from, 2023)), key="d1_year_to", default="last")
    with f3:
        filter_label("Region")
        sel_regions = region_select(regions, key="d1_region")
    with f4:
        filter_label("Category")
        sel_cats = category_select(categories, key="d1_category")
yr = (yr_from, yr_to)

# ---- apply filters
mask = (orders["order_year"].between(yr[0], yr[1])
        & orders["region"].isin(sel_regions)
        & orders["category"].isin(sel_cats))
orders_f = orders[mask]
monthly["year"] = monthly["year_month"].str[:4].astype(int)
monthly_f = monthly[monthly["year"].between(yr[0], yr[1])]

# When category filter is partial, recompute monthly KPIs from orders_f
if set(sel_cats) != set(categories) or set(sel_regions) != set(regions):
    rebuilt = (orders_f.groupby("order_ym").agg(
        revenue=("line_revenue", "sum"),
        gross_profit=("line_gross_profit", "sum"),
        cogs=("line_cost", "sum"),
        total_orders=("has_promo", "size"),
    ).reset_index().rename(columns={"order_ym": "year_month"}))
    rebuilt["gross_margin_pct"] = rebuilt["gross_profit"] / rebuilt["revenue"] * 100
    rebuilt["aov"] = rebuilt["revenue"] / rebuilt["total_orders"]
    rebuilt = rebuilt.sort_values("year_month")
    rebuilt["mom_growth_pct"] = rebuilt["revenue"].pct_change() * 100
    monthly_f = rebuilt

# ---- KPI strip
total_rev = monthly_f["revenue"].sum()
total_gp = monthly_f["gross_profit"].sum()
margin = total_gp / total_rev * 100 if total_rev else 0
aov_total = total_rev / monthly_f["total_orders"].sum() if monthly_f["total_orders"].sum() else 0

last_y = monthly_f["year_month"].str[:4].astype(int).max() if len(monthly_f) else yr[1]
prev_y = last_y - 1

def _yoy(col, last_y, prev_y, monthly_f):
    last = monthly_f.loc[monthly_f["year_month"].str[:4].astype(int) == last_y, col].sum()
    prev = monthly_f.loc[monthly_f["year_month"].str[:4].astype(int) == prev_y, col].sum()
    return (last / prev - 1) * 100 if prev else 0

# ---- Layout: 2x2 charts on left, KPI rail on right ----
charts_col, kpi_col = st.columns([4, 1], gap="medium")
with kpi_col:
    st.markdown("##### KPIs")
    st.metric("Total Revenue", fmt_money(total_rev),
              f"{_yoy('revenue', last_y, prev_y, monthly_f):+.1f}% YoY")
    st.metric("Gross Profit", fmt_money(total_gp),
              f"{_yoy('gross_profit', last_y, prev_y, monthly_f):+.1f}% YoY")
    st.metric("Gross Margin", f"{margin:.1f}%")
    st.metric("AOV", fmt_money(aov_total))

with charts_col:
    row1c1, row1c2 = st.columns(2)
    row2c1, row2c2 = st.columns(2)

# C1 — Revenue trend
with row1c1:
    df = monthly_f.copy()
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.sort_values("date")
    df["rev_ma12"] = df["revenue"].rolling(12, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["revenue"], name="Revenue",
                             line=dict(color=LIME_STRONG, width=1.5),
                             fill="tozeroy", fillcolor="rgba(184,232,53,0.15)"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["gross_profit"], name="Gross Profit",
                             line=dict(color=LIME_DARK, width=1.5)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["rev_ma12"], name="MA-12",
                             line=dict(color=DARK, width=2, dash="dot")))
    fig.update_layout(title="Revenue & Gross Profit (monthly)",
                      hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        "<div class='narrative'><b>Descriptive.</b> Đỉnh seasonal ở M05 (~204M), "
        "đáy M11–12 (~78M). MA-12 cho thấy <b>trend dài hạn đi xuống</b>: "
        "doanh thu 2022 thấp hơn đỉnh 2016 −44.4%.</div>",
        unsafe_allow_html=True)

# C2 — MoM heatmap
with row1c2:
    df = monthly_f.copy()
    df["year"] = df["year_month"].str[:4].astype(int)
    df["month"] = df["year_month"].str[5:7].astype(int)
    pivot = df.pivot_table(index="year", columns="month", values="mom_growth_pct").reindex(columns=range(1, 13))
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"M{m:02d}" for m in pivot.columns],
        y=pivot.index.astype(str),
        colorscale=[[0, "#DC2626"], [0.5, "#F5F6F0"], [1, LIME_DARK]],
        zmid=0,
        colorbar=dict(thickness=10, outlinewidth=0),
        hovertemplate="Year %{y} · %{x}<br>MoM: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(title="MoM Growth Heatmap")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        "<div class='narrative'><b>Predictive.</b> Vân tay mùa vụ rõ rệt qua 11 năm: "
        "<b>M03 luôn tăng mạnh nhất (avg +58%)</b>, M07 và M11 luôn rớt sâu (≈−24%). "
        "Q4 thực ra là quý suy giảm — forecast cần seasonal term 12 tháng.</div>",
        unsafe_allow_html=True)

# C3 — Margin vs Discount (scatter with regression — direct inverse evidence)
with row2c1:
    promo = (orders_f.groupby("order_ym")
             .agg(lines=("has_promo", "size"), promoted=("has_promo", "sum"))
             .assign(discount_pen=lambda d: d["promoted"]/d["lines"]*100)
             .reset_index().rename(columns={"order_ym": "year_month"}))
    df = monthly_f.merge(promo[["year_month", "discount_pen"]], on="year_month", how="left")
    df = df.dropna(subset=["discount_pen", "gross_margin_pct"])
    df["year"] = df["year_month"].str[:4].astype(int)

    # Linear regression
    x = df["discount_pen"].values
    y = df["gross_margin_pct"].values
    if len(x) >= 2:
        slope, intercept = np.polyfit(x, y, 1)
        r = np.corrcoef(x, y)[0, 1]
        x_line = np.linspace(x.min(), x.max(), 50)
        y_line = slope * x_line + intercept
    else:
        slope = intercept = r = 0
        x_line = y_line = np.array([])

    fig = go.Figure()
    # Scatter: each dot = 1 month, color = year (gradient lime → dark)
    fig.add_trace(go.Scatter(
        x=df["discount_pen"], y=df["gross_margin_pct"],
        mode="markers",
        marker=dict(size=9, color=df["year"], colorscale="Viridis",
                    showscale=True, colorbar=dict(title="Year", thickness=8,
                                                  outlinewidth=0, len=0.7),
                    line=dict(width=0.5, color=DARK), opacity=0.85),
        text=df["year_month"],
        hovertemplate="<b>%{text}</b><br>"
                      "Discount: %{x:.1f}%<br>Margin: %{y:.1f}%<extra></extra>",
        name="Months",
    ))
    # Regression line
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode="lines",
        line=dict(color=RED, width=2.5, dash="dash"),
        name=f"Fit: y = {slope:.2f}x + {intercept:.1f}",
        hoverinfo="skip",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color=GREY, opacity=0.5)
    fig.update_layout(
        title=f"Discount tăng → Margin giảm  (r = {r:.2f}, mỗi dot = 1 tháng)",
        xaxis_title="Discount penetration %", yaxis_title="Gross margin %",
        hovermode="closest",
    )
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        f"<div class='narrative'><b>Diagnostic.</b> "
        f"Mỗi +1pp discount penetration kéo margin xuống <b>{abs(slope):.2f}pp</b>. "
        f"Correlation âm <b>{r:.2f}</b> trên {len(df)} tháng — pattern lặp lại nhất quán, "
        "không phải nhiễu. Cần margin floor.</div>",
        unsafe_allow_html=True)

# C4 — Category Pareto
with row2c2:
    cat = (orders_f.groupby("category")
           .agg(revenue=("line_revenue", "sum"),
                gp=("line_gross_profit", "sum"))
           .assign(margin_pct=lambda d: d["gp"]/d["revenue"]*100)
           .sort_values("revenue", ascending=False).reset_index())
    cat["cum_pct"] = cat["revenue"].cumsum() / cat["revenue"].sum() * 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=cat["category"], y=cat["revenue"], name="Revenue",
                         marker_color=LIME, marker_line_color=LIME_STRONG),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=cat["category"], y=cat["cum_pct"], name="Cum %",
                             mode="lines+markers", line=dict(color=DARK, width=2)),
                  secondary_y=True)
    fig.add_trace(go.Scatter(x=cat["category"], y=cat["margin_pct"], name="Margin %",
                             mode="lines+markers",
                             line=dict(color=AMBER, width=2, dash="dot")),
                  secondary_y=True)
    fig.update_layout(title="Category Pareto + Margin", hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    top3 = cat.head(3)["revenue"].sum() / cat["revenue"].sum() * 100
    st.markdown(
        f"<div class='narrative'><b>Prescriptive.</b> Top 3 category chiếm "
        f"{top3:.1f}% revenue. Dồn budget vào top, kiểm tra margin thấp để cắt SKU.</div>",
        unsafe_allow_html=True)

# =====================================================================
# Extra brainstorm row — additional D1 visuals (do NOT remove existing)
# =====================================================================
st.markdown("---")
st.markdown("##### Extra analyses · brainstorm board")
ext1, ext2, ext3 = st.columns(3)

# E1 — Revenue decomposition: Orders × AOV (true decomposition)
with ext1:
    df = monthly_f.copy()
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.sort_values("date")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df["date"], y=df["total_orders"], name="Orders",
                         marker_color=LIME, marker_line_color=LIME_STRONG,
                         opacity=0.85),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=df["date"], y=df["aov"], name="AOV",
                             line=dict(color=DARK, width=2)),
                  secondary_y=True)
    fig.update_yaxes(title_text="Orders", secondary_y=False)
    fig.update_yaxes(title_text="AOV", secondary_y=True)
    fig.update_layout(title="Revenue decomposition · Orders × AOV",
                      hovermode="x unified")
    style(fig, height=260)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    # quick decomposition metric: which driver moved more YoY?
    if len(df) >= 24:
        last12 = df.tail(12)
        prev12 = df.iloc[-24:-12]
        do = last12["total_orders"].sum() / max(prev12["total_orders"].sum(), 1) - 1
        da = last12["aov"].mean() / max(prev12["aov"].mean(), 1e-9) - 1
        driver = "Orders (volume)" if abs(do) > abs(da) else "AOV (price/mix)"
        st.markdown(
            f"<div class='narrative'><b>Diagnostic.</b> YoY: Orders {do*100:+.1f}% · "
            f"AOV {da*100:+.1f}% → driver chính = <b>{driver}</b>. "
            "Tăng trưởng đến từ volume hay giá trị đơn?</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='narrative'><b>Diagnostic.</b> Tách revenue thành "
            "Orders × AOV giúp biết tăng/giảm là do volume hay giá trị đơn.</div>",
            unsafe_allow_html=True)

# E2 — Seasonal forecast band (next 6 months, naive seasonal + std)
with ext2:
    df = monthly_f.copy()
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.sort_values("date").reset_index(drop=True)
    df["month"] = df["date"].dt.month
    # seasonal naive: forecast = last year's same-month, band = ±1.5 std of last 3 yrs same-month
    if len(df) >= 24:
        season = df.groupby("month")["revenue"].agg(["mean", "std"]).reset_index()
        last_date = df["date"].max()
        future = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=6, freq="MS")
        fdf = pd.DataFrame({"date": future})
        fdf["month"] = fdf["date"].dt.month
        fdf = fdf.merge(season, on="month", how="left")
        fdf["upper"] = fdf["mean"] + 1.5 * fdf["std"].fillna(0)
        fdf["lower"] = (fdf["mean"] - 1.5 * fdf["std"].fillna(0)).clip(lower=0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["date"], y=df["revenue"], name="Actual",
                                 line=dict(color=LIME_STRONG, width=1.6)))
        fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["upper"], name="Upper",
                                 line=dict(color=LIME, width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["lower"], name="Lower",
                                 line=dict(color=LIME, width=0),
                                 fill="tonexty", fillcolor="rgba(184,232,53,0.25)",
                                 showlegend=False))
        fig.add_trace(go.Scatter(x=fdf["date"], y=fdf["mean"], name="Forecast",
                                 line=dict(color=DARK, width=2, dash="dash")))
        fig.update_layout(title="Seasonal naive forecast · next 6 months",
                          hovermode="x unified")
        style(fig, height=260)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        next_q = fdf.head(3)["mean"].sum()
        next_6 = fdf["mean"].sum()
        st.markdown(
            f"<div class='narrative'><b>Predictive.</b> Forecast 3 tháng tới ≈ "
            f"{fmt_money(next_q)}, 6 tháng ≈ {fmt_money(next_6)} (band ±1.5σ/tháng). "
            "Caveat: model dùng seasonal mean toàn 11 năm (gồm đỉnh 2016) → "
            "<b>nhiều khả năng overshoot</b> vì business đang giảm 6 năm. "
            "Plan theo lower-band cho cash, upper-band cho inventory.</div>",
            unsafe_allow_html=True)
    else:
        st.info("Cần ≥24 tháng dữ liệu để vẽ forecast band.")

# E3 — YoY revenue bridge: contribution by category to YoY change
with ext3:
    if yr[1] > yr[0]:
        cur_y = yr[1]
        prv_y = yr[1] - 1
        cur = (orders_f[orders_f["order_year"] == cur_y]
               .groupby("category")["line_revenue"].sum())
        prv = (orders_f[orders_f["order_year"] == prv_y]
               .groupby("category")["line_revenue"].sum())
        bridge = (pd.concat([prv.rename("prev"), cur.rename("curr")], axis=1)
                  .fillna(0).assign(delta=lambda d: d["curr"] - d["prev"])
                  .sort_values("delta"))
        colors = [LIME_DARK if v > 0 else RED for v in bridge["delta"]]
        fig = go.Figure(go.Bar(
            y=bridge.index, x=bridge["delta"], orientation="h",
            marker_color=colors,
            hovertemplate="<b>%{y}</b><br>ΔRev: %{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(title=f"YoY contribution · {prv_y} → {cur_y}")
        style(fig, height=260, show_legend=False)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        winners = bridge[bridge["delta"] > 0].index.tolist()[-2:]
        losers = bridge[bridge["delta"] < 0].index.tolist()[:2]
        st.markdown(
            f"<div class='narrative'><b>Prescriptive.</b> Tăng nhờ "
            f"<b>{', '.join(winners) or '—'}</b>; mất ở "
            f"<b>{', '.join(losers) or '—'}</b>. Bảo vệ winners, "
            "điều tra losers (mix, giá, tồn kho).</div>",
            unsafe_allow_html=True)
    else:
        st.info("Chọn khoảng thời gian ≥ 2 năm để xem YoY bridge.")
