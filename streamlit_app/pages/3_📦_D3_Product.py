"""D3 — Product Performance, Returns, Inventory."""
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
                   LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, RED, CAT_PALETTE)
from filters import category_select, year_select

st.set_page_config(page_title="D3 · Product", page_icon="📦", layout="wide")
inject_css()
sidebar_notes_panel("D3 notes", "Large blank area for product findings, return-risk commentary, and recommended actions.")

products = load("dim_products")
orders = load("fact_orders_enriched", columns=(
    "category", "segment", "line_revenue", "line_gross_profit", "quantity",
    "product_id", "order_year", "size"))
returns = load("fact_returns_enriched", columns=(
    "category", "return_reason", "refund_amount", "return_quantity",
    "return_year", "size", "product_id"))
inv = load("fact_inventory", columns=(
    "category", "inventory_health", "inventory_value_cost",
    "stockout_flag", "overstock_flag", "year",
    "stockout_days", "units_sold", "product_price", "product_id"))

categories = sorted(products["category"].dropna().unique().tolist())

title_col, filter_col = st.columns([1.7, 2.3], gap="medium")
with title_col:
    page_header_inline("D3", "Product Performance & Inventory",
                       "Top SKUs · Returns · Inventory health · Pricing vs margin")
with filter_col:
    f1, f2, f3 = st.columns(3)
    with f1:
        filter_label("From year")
        yr_from = year_select("From year", list(range(2012, 2023)), key="d3_year_from")
    with f2:
        filter_label("To year")
        yr_to = year_select("To year", list(range(yr_from, 2023)), key="d3_year_to", default="last")
    with f3:
        filter_label("Category")
        sel_cats = category_select(categories, key="d3_cat")
yr = (yr_from, yr_to)

orders_f = orders[(orders["category"].isin(sel_cats))
                  & orders["order_year"].between(yr[0], yr[1])]
returns_f = returns[(returns["category"].isin(sel_cats))
                    & returns["return_year"].between(yr[0], yr[1])]
inv_f = inv[(inv["category"].isin(sel_cats)) & inv["year"].between(yr[0], yr[1])]
products_f = products[products["category"].isin(sel_cats)]

# KPIs
n_skus = len(products_f)
total_returns = returns_f["return_quantity"].sum()
ordered_units = orders_f["quantity"].sum()
return_rate = total_returns / ordered_units * 100 if ordered_units else 0
inv_value = inv_f["inventory_value_cost"].sum()

charts_col, kpi_col = st.columns([4, 1], gap="medium")
with kpi_col:
    st.markdown("##### KPIs")
    st.metric("SKUs", f"{n_skus:,}")
    st.metric("Returned units", f"{total_returns:,}")
    st.metric("Return rate", f"{return_rate:.2f}%")
    st.metric("Inventory value", fmt_money(inv_value))

with charts_col:
    row1c1, row1c2 = st.columns(2)
    row2c1, row2c2 = st.columns(2)

# C1 — Top 15 SKUs by revenue
with row1c1:
    prod_rev = (orders_f.groupby("product_id")
                .agg(revenue=("line_revenue", "sum"),
                     gp=("line_gross_profit", "sum"))
                .reset_index())
    top = (prod_rev.merge(products_f[["product_id", "product_name", "category"]], on="product_id")
           .nlargest(15, "revenue").sort_values("revenue"))
    fig = go.Figure(go.Bar(
        y=top["product_name"], x=top["revenue"], orientation="h",
        marker_color=LIME, marker_line_color=LIME_STRONG,
        customdata=top[["category", "gp"]],
        hovertemplate="<b>%{y}</b><br>%{customdata[0]}<br>"
                      "Revenue: %{x:,.0f}<br>GP: %{customdata[1]:,.0f}<extra></extra>",
    ))
    fig.update_layout(title="Top 15 SKUs by Revenue")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        "<div class='narrative'><b>Descriptive.</b> Long-tail rõ — số ít SKU "
        "đóng góp phần lớn revenue. Phải đảm bảo tồn kho đủ cho top SKU.</div>",
        unsafe_allow_html=True)

# C2 — Return reason distribution
with row1c2:
    rs = (returns_f.groupby("return_reason")
          .agg(count=("return_quantity", "sum"),
               refund=("refund_amount", "sum"))
          .reset_index().sort_values("count", ascending=True))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(y=rs["return_reason"], x=rs["count"], orientation="h",
                         marker_color=AMBER, name="Units"),
                  secondary_y=False)
    fig.update_layout(title="Return Reasons (units returned)")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        "<div class='narrative'><b>Diagnostic.</b> Top return reason chỉ ra "
        "vấn đề chất lượng/size guide cần sửa.</div>",
        unsafe_allow_html=True)

# C3 — Inventory health distribution
with row2c1:
    inv_health = inv_f["inventory_health"].value_counts().reset_index()
    inv_health.columns = ["status", "snapshots"]
    color_map = {"Healthy": LIME_DARK, "Reorder": AMBER, "Overstock": "#7C9F2C", "Stockout": RED}
    fig = go.Figure(go.Bar(
        x=inv_health["status"], y=inv_health["snapshots"],
        marker_color=[color_map.get(s, LIME) for s in inv_health["status"]],
        text=inv_health["snapshots"], textposition="outside",
    ))
    fig.update_layout(title="Inventory Health Snapshots")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        "<div class='narrative'><b>Predictive.</b> Tỷ lệ Stockout/Reorder cảnh báo "
        "nguy cơ mất doanh thu; Overstock cảnh báo tiền chôn.</div>",
        unsafe_allow_html=True)

# C4 — Price vs margin scatter
with row2c2:
    prod_rev = (orders_f.groupby("product_id")["line_revenue"].sum()
                .rename("product_revenue").reset_index())
    df = products_f.merge(prod_rev, on="product_id", how="left")
    df = df[df["product_revenue"].fillna(0) > 0]
    fig = px.scatter(
        df, x="price", y="gross_margin_pct",
        size="product_revenue", color="category",
        color_discrete_sequence=CAT_PALETTE,
        hover_name="product_name", size_max=30,
        labels={"price": "Price", "gross_margin_pct": "Margin %"},
    )
    fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
    fig.update_layout(title="Price vs Margin (size = revenue)")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        "<div class='narrative'><b>Prescriptive.</b> Bubble lớn ở margin thấp = "
        "ứng viên tăng giá; bubble nhỏ ở margin cao = ứng viên đẩy marketing.</div>",
        unsafe_allow_html=True)

# =====================================================================
# Extra brainstorm row 1 — Pareto + Return×Size
# =====================================================================
st.markdown("---")
st.markdown("##### Extra analyses · brainstorm board")
ext1, ext2 = st.columns(2)

# E1 — Pareto product concentration
with ext1:
    pr = (orders_f.groupby("product_id")["line_revenue"].sum()
          .sort_values(ascending=False).reset_index())
    pr["rank"] = range(1, len(pr) + 1)
    pr["cum_pct"] = pr["line_revenue"].cumsum() / pr["line_revenue"].sum() * 100
    pr["sku_pct"] = pr["rank"] / len(pr) * 100
    # find 80% line
    sku_at_80 = pr.loc[pr["cum_pct"] >= 80, "sku_pct"].min() if (pr["cum_pct"] >= 80).any() else 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=pr["rank"], y=pr["line_revenue"],
                         name="SKU revenue", marker_color=LIME,
                         marker_line_color=LIME_STRONG),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=pr["rank"], y=pr["cum_pct"],
                             name="Cum %", line=dict(color=DARK, width=2)),
                  secondary_y=True)
    fig.add_hline(y=80, line_dash="dot", line_color=AMBER, secondary_y=True,
                  annotation_text="80%", annotation_position="right")
    fig.update_yaxes(title_text="Revenue", secondary_y=False)
    fig.update_yaxes(title_text="Cum %", range=[0, 105], secondary_y=True)
    fig.update_xaxes(title_text="SKU rank")
    fig.update_layout(title="Pareto · SKU revenue concentration",
                      hovermode="x unified")
    style(fig, height=280)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        f"<div class='narrative'><b>Descriptive + Prescriptive.</b> "
        f"<b>{sku_at_80:.1f}%</b> SKU đầu tạo 80% doanh thu. Đây là danh sách "
        "<b>protection list</b>: stock cao, không hết hàng, ưu tiên QA.</div>",
        unsafe_allow_html=True)

# E2 — Return rate by category × size
with ext2:
    sold = (orders_f.groupby(["category", "size"])["quantity"].sum()
            .rename("sold").reset_index())
    ret = (returns_f.groupby(["category", "size"])["return_quantity"].sum()
           .rename("returned").reset_index())
    rs = sold.merge(ret, on=["category", "size"], how="left").fillna(0)
    rs["return_rate"] = rs["returned"] / rs["sold"].replace(0, np.nan) * 100
    pivot = rs.pivot(index="category", columns="size", values="return_rate")
    # natural size order
    size_order = ["XS", "S", "M", "L", "XL", "XXL"]
    pivot = pivot.reindex(columns=[s for s in size_order if s in pivot.columns])
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.astype(str),
        y=pivot.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.5, AMBER], [1, RED]],
        colorbar=dict(thickness=10, outlinewidth=0, title="%"),
        hovertemplate="%{y} · size %{x}<br>Return rate: %{z:.2f}%<extra></extra>",
    ))
    fig.update_layout(title="Return rate · Category × Size")
    style(fig, height=280, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    if pivot.size and pivot.notna().any().any():
        idx = np.unravel_index(np.nanargmax(pivot.values), pivot.shape)
        worst = f"{pivot.index[idx[0]]} · {pivot.columns[idx[1]]}"
        worst_v = float(pivot.values[idx])
        st.markdown(
            f"<div class='narrative'><b>Diagnostic.</b> Hot spot: "
            f"<b>{worst}</b> · {worst_v:.1f}% return rate. Ưu tiên fix size guide & QC "
            "ở ô đỏ trước khi chạm tới logistics.</div>",
            unsafe_allow_html=True)

# =====================================================================
# Extra brainstorm row 2 — Rating-risk + Stockout-loss
# =====================================================================
ext3, ext4 = st.columns(2)

# E3 — Rating as predictor of return risk (binned)
with ext3:
    pr = products_f[["product_id", "avg_rating", "total_return_qty",
                     "review_count", "category"]].copy()
    sold_p = orders_f.groupby("product_id")["quantity"].sum().rename("sold")
    pr = pr.merge(sold_p, on="product_id", how="left").fillna({"sold": 0})
    pr = pr[(pr["sold"] > 0) & pr["avg_rating"].notna()]
    pr["return_rate"] = pr["total_return_qty"] / pr["sold"] * 100
    pr["rating_bin"] = pd.cut(pr["avg_rating"],
                              bins=[0, 3.0, 3.5, 4.0, 4.5, 5.0],
                              labels=["≤3.0", "3.0–3.5", "3.5–4.0", "4.0–4.5", "4.5–5.0"])
    binned = (pr.groupby("rating_bin", observed=True)
              .agg(avg_return_rate=("return_rate", "mean"),
                   skus=("product_id", "count"),
                   avg_reviews=("review_count", "mean"))
              .reset_index())
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = [RED, AMBER, "#F5C842", LIME, LIME_DARK][:len(binned)]
    fig.add_trace(go.Bar(x=binned["rating_bin"].astype(str),
                         y=binned["avg_return_rate"],
                         name="Avg return rate %",
                         marker_color=colors,
                         text=[f"{v:.1f}%" for v in binned["avg_return_rate"]],
                         textposition="outside"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=binned["rating_bin"].astype(str),
                             y=binned["skus"], name="SKU count",
                             mode="lines+markers",
                             line=dict(color=DARK, width=2)),
                  secondary_y=True)
    fig.update_layout(title="Rating bucket → return risk",
                      hovermode="x unified")
    style(fig, height=280)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    if len(binned) >= 2:
        worst = binned.iloc[0]
        best = binned.iloc[-1]
        st.markdown(
            f"<div class='narrative'><b>Predictive.</b> SKU rating "
            f"<b>{worst['rating_bin']}</b> có return rate ≈ "
            f"<b>{worst['avg_return_rate']:.1f}%</b> vs "
            f"<b>{best['rating_bin']}</b> chỉ {best['avg_return_rate']:.1f}%. "
            "Rating thấp là leading indicator — list để fix mô tả/chất lượng trước.</div>",
            unsafe_allow_html=True)

# E4 — Stockout days vs revenue at risk (scatter)
with ext4:
    iv = (inv_f.groupby("product_id")
          .agg(stockout_days=("stockout_days", "sum"),
               units_sold=("units_sold", "sum"),
               price=("product_price", "mean"))
          .reset_index())
    iv = iv.merge(products_f[["product_id", "product_name", "category"]],
                  on="product_id", how="left")
    iv = iv[(iv["units_sold"] > 0)]
    # daily run-rate based proxy for lost revenue
    iv["daily_rate"] = iv["units_sold"] / 365.0
    iv["lost_rev_proxy"] = iv["daily_rate"] * iv["stockout_days"] * iv["price"]
    iv = iv[iv["stockout_days"] > 0].sort_values("lost_rev_proxy", ascending=False).head(80)
    if len(iv):
        fig = px.scatter(iv, x="stockout_days", y="lost_rev_proxy",
                         size="units_sold", color="category",
                         color_discrete_sequence=CAT_PALETTE,
                         hover_name="product_name", size_max=35,
                         labels={"stockout_days": "Stockout days",
                                 "lost_rev_proxy": "Lost revenue proxy"})
        fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
        fig.update_layout(title="Stockout impact · days vs lost revenue (top 80)")
        style(fig, height=280)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        total_loss = iv["lost_rev_proxy"].sum()
        st.markdown(
            f"<div class='narrative'><b>Prescriptive.</b> Lost revenue proxy ≈ "
            f"<b>{fmt_money(total_loss)}</b> chỉ riêng top-80 SKU. "
            "Tăng safety stock cho góc trên-phải → ROI cao nhất từ ops.</div>",
            unsafe_allow_html=True)
    else:
        st.info("Không đủ dữ liệu stockout để vẽ scatter.")

# =====================================================================
# Extra brainstorm row 3 — Inventory health × Category breakdown
# =====================================================================
ext5, ext6 = st.columns(2)

# E5 — Inventory health share by category (stacked 100%)
with ext5:
    health = (inv_f.groupby(["category", "inventory_health"])
              .size().rename("snapshots").reset_index())
    pivot = (health.pivot(index="category", columns="inventory_health",
                          values="snapshots").fillna(0))
    # Normalize per category to %
    pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    # Order categories by Stockout share desc so worst goes top
    if "Stockout" in pct.columns:
        pct = pct.sort_values("Stockout", ascending=True)
    status_order = ["Stockout", "Reorder", "Overstock", "Healthy"]
    status_order = [s for s in status_order if s in pct.columns]
    color_map = {"Healthy": LIME_DARK, "Reorder": AMBER,
                 "Overstock": "#7C9F2C", "Stockout": RED}
    fig = go.Figure()
    for status in status_order:
        fig.add_trace(go.Bar(
            y=pct.index.astype(str), x=pct[status],
            name=status, orientation="h",
            marker_color=color_map.get(status, LIME),
            text=[f"{v:.0f}%" if v >= 6 else "" for v in pct[status]],
            textposition="inside",
            hovertemplate="<b>%{y}</b> · " + status +
                          "<br>%{x:.1f}% snapshots<extra></extra>",
        ))
    fig.update_layout(
        title="Inventory health share · % per category",
        barmode="stack",
    )
    fig.update_xaxes(title_text="% snapshots", range=[0, 100])
    style(fig, height=300)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    if "Stockout" in pct.columns and not pct["Stockout"].dropna().empty:
        so_min, so_max = pct["Stockout"].min(), pct["Stockout"].max()
        hl_min, hl_max = (pct["Healthy"].min(), pct["Healthy"].max()
                          if "Healthy" in pct.columns else (0, 0))
        st.markdown(
            f"<div class='narrative'><b>Diagnostic.</b> "
            f"<b>Cả 4 categories đều ở Stockout {so_min:.0f}–{so_max:.0f}%</b> "
            f"(spread chỉ {so_max-so_min:.1f}pp), Healthy chỉ {hl_min:.0f}–{hl_max:.0f}%. "
            "Đây là <b>structural crisis của replenishment system</b>, "
            "không phải vấn đề của category cụ thể — fix per-category sẽ vô ích.</div>",
            unsafe_allow_html=True)

# E6 — Inventory value at risk by status × category (heatmap)
with ext6:
    val = (inv_f.groupby(["category", "inventory_health"])["inventory_value_cost"]
           .sum().reset_index())
    pivot_v = val.pivot(index="category", columns="inventory_health",
                        values="inventory_value_cost").fillna(0)
    # Reorder columns
    cols = [c for c in ["Stockout", "Reorder", "Overstock", "Healthy"]
            if c in pivot_v.columns]
    pivot_v = pivot_v[cols]
    # Normalize per row to highlight where each category's $ is concentrated
    pct_v = pivot_v.div(pivot_v.sum(axis=1), axis=0) * 100
    fig = go.Figure(go.Heatmap(
        z=pct_v.values,
        x=pct_v.columns.astype(str),
        y=pct_v.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.5, AMBER], [1, RED]],
        colorbar=dict(thickness=10, outlinewidth=0, title="% of value"),
        hovertemplate="<b>%{y}</b> · %{x}<br>"
                      "%{z:.1f}% inventory value<extra></extra>",
        text=[[f"{v:.0f}%" for v in row] for row in pct_v.values],
        texttemplate="%{text}", textfont=dict(size=11, color=DARK),
    ))
    fig.update_layout(title="Inventory value tied up · % per category × status")
    style(fig, height=300, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    # All 4 categories have nearly identical pattern → uniform crisis
    if {"Overstock", "Stockout", "Healthy"}.issubset(pct_v.columns):
        bad = pct_v["Overstock"] + pct_v["Stockout"]
        hl_min, hl_max = pct_v["Healthy"].min(), pct_v["Healthy"].max()
        st.markdown(
            f"<div class='narrative'><b>Prescriptive.</b> "
            f"<b>{bad.min():.0f}–{bad.max():.0f}% giá trị tồn kho bị kẹt</b> "
            f"(Stockout+Overstock) trên cả 4 categories — "
            f"Healthy chỉ {hl_min:.0f}–{hl_max:.0f}% giá trị. "
            "Replenishment & forecast system cần overhaul ở tầng portfolio, "
            "không phải tweak per-category.</div>",
            unsafe_allow_html=True)

# =====================================================================
# Extra brainstorm row 4 — Return rate × Category × Reason
# =====================================================================
ext7, _ = st.columns([2, 1])

# E7 — Return rate by category × return reason
with ext7:
    sold_cat = (orders_f.groupby("category")["quantity"].sum()
                .rename("sold_total"))
    ret_cr = (returns_f.groupby(["category", "return_reason"])["return_quantity"]
              .sum().rename("returned").reset_index())
    ret_cr = ret_cr.merge(sold_cat, on="category", how="left")
    ret_cr["rate"] = ret_cr["returned"] / ret_cr["sold_total"] * 100
    pivot_r = ret_cr.pivot(index="category", columns="return_reason", values="rate")
    # Sort columns by total impact (mean across categories)
    if not pivot_r.empty:
        pivot_r = pivot_r[pivot_r.mean().sort_values(ascending=False).index]
    fig = go.Figure(go.Heatmap(
        z=pivot_r.values,
        x=pivot_r.columns.astype(str),
        y=pivot_r.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.5, AMBER], [1, RED]],
        colorbar=dict(thickness=10, outlinewidth=0, title="%"),
        hovertemplate="<b>%{y}</b> · %{x}<br>"
                      "Return rate: %{z:.2f}%<extra></extra>",
        text=[[f"{v:.1f}%" if not pd.isna(v) else "" for v in row]
              for row in pivot_r.values],
        texttemplate="%{text}", textfont=dict(size=11, color=DARK),
    ))
    fig.update_layout(title="Return rate · Category × Reason "
                            "(% of category units sold)")
    style(fig, height=320, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    if pivot_r.size and pivot_r.notna().any().any():
        idx = np.unravel_index(np.nanargmax(pivot_r.values), pivot_r.shape)
        worst_cat = pivot_r.index[idx[0]]
        worst_reason = pivot_r.columns[idx[1]]
        worst_rate = float(pivot_r.values[idx])
        # Top reason overall (column with highest mean)
        top_reason = pivot_r.mean().idxmax()
        top_reason_avg = pivot_r.mean().max()
        st.markdown(
            f"<div class='narrative'><b>Diagnostic.</b> Hot spot: "
            f"<b>{worst_cat} · {worst_reason}</b> = {worst_rate:.2f}% return rate. "
            f"Reason hệ thống nhất là <b>{top_reason}</b> "
            f"(avg {top_reason_avg:.2f}% across categories). "
            "Fix root cause của reason đó trước (size guide / mô tả / QC).</div>",
            unsafe_allow_html=True)
