"""D3 — Product Performance, Returns, Inventory."""
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
                   LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, RED, CAT_PALETTE)
from filters import category_select, year_range

st.set_page_config(page_title="D3 · Product", page_icon="📦", layout="wide")
inject_css()
page_header("D3", "Product Performance & Inventory",
            "Top SKUs · Returns · Inventory health · Pricing vs margin")

products = load("dim_products")
orders = load("fact_orders_enriched", columns=(
    "category", "segment", "line_revenue", "line_gross_profit", "quantity",
    "product_id", "order_year"))
returns = load("fact_returns_enriched", columns=(
    "category", "return_reason", "refund_amount", "return_quantity", "return_year"))
inv = load("fact_inventory", columns=(
    "category", "inventory_health", "inventory_value_cost",
    "stockout_flag", "overstock_flag", "year"))

categories = sorted(products["category"].dropna().unique().tolist())
sel_cats = category_select(categories, key="d3_cat")
yr = year_range(2012, 2022, key_prefix="d3_year")

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
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
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
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
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
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
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
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown(
        "<div class='narrative'><b>Prescriptive.</b> Bubble lớn ở margin thấp = "
        "ứng viên tăng giá; bubble nhỏ ở margin cao = ứng viên đẩy marketing.</div>",
        unsafe_allow_html=True)
