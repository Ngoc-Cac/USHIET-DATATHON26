"""D3 — Product Performance, Returns, Inventory."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

from data import load
from theme import (PLOTLY_CONFIG, style, fmt_money, inject_css, page_header_inline,
                   filter_label, sidebar_notes_panel, insight_panel,
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
                       "Top SKUs · Return drivers · Inventory health · Margin fit")
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

n_skus = len(products_f)
total_returns = returns_f["return_quantity"].sum()
ordered_units = orders_f["quantity"].sum()
return_rate = total_returns / ordered_units * 100 if ordered_units else 0
inv_value = inv_f["inventory_value_cost"].sum()

top_return_reason = "N/A"
if len(returns_f):
    reason_mix = returns_f.groupby("return_reason")["return_quantity"].sum().sort_values(ascending=False)
    if len(reason_mix):
        top_return_reason = reason_mix.index[0]

inventory_risk_share = 0.0
if len(inv_f):
    risk_states = inv_f["inventory_health"].isin(["Stockout", "Reorder"]).sum()
    inventory_risk_share = risk_states / len(inv_f) * 100

charts_col, kpi_col = st.columns([4, 1], gap="medium")
with kpi_col:
    st.markdown("##### KPIs")
    st.metric("SKUs", f"{n_skus:,}")
    st.metric("Returned units", f"{total_returns:,}")
    st.metric("Return rate", f"{return_rate:.2f}%")
    st.metric("Inventory value", fmt_money(inv_value))
    insight_panel(
        "Product insight",
        f"Return rate is {return_rate:.2f}%, {top_return_reason} is the biggest return driver, and {inventory_risk_share:.1f}% of inventory snapshots sit in reorder or stockout states."
    )

with charts_col:
    row1c1, row1c2 = st.columns(2)
    row2c1, row2c2 = st.columns(2)

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

with row1c2:
    rs = (returns_f.groupby("return_reason")
          .agg(count=("return_quantity", "sum"),
               refund=("refund_amount", "sum"))
          .reset_index().sort_values("count", ascending=True))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(y=rs["return_reason"], x=rs["count"], orientation="h",
                         marker_color=AMBER, name="Units"),
                  secondary_y=False)
    fig.update_layout(title="Top Return Reasons by Units Returned")
    style(fig, height=240, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with row2c1:
    color_map = {"Healthy": LIME_DARK, "Reorder": AMBER,
                 "Overstock": "#7C9F2C", "Stockout": RED}
    by_year = (inv_f.groupby(["year", "inventory_health"])
               .size().rename("snapshots").reset_index())
    pivot = by_year.pivot(index="year", columns="inventory_health",
                          values="snapshots").fillna(0)
    status_order = [s for s in ["Stockout", "Reorder", "Overstock", "Healthy"]
                    if s in pivot.columns]
    fig = go.Figure()
    for status in status_order:
        fig.add_trace(go.Bar(
            x=pivot.index.astype(str), y=pivot[status],
            name=status,
            marker_color=color_map.get(status, LIME),
            hovertemplate="<b>%{x}</b> · " + status +
                          "<br>%{y:,} snapshots<extra></extra>",
        ))
    fig.update_layout(title="Inventory Snapshots by Status & Year",
                      barmode="stack",
                      xaxis_title="Year", yaxis_title="Snapshots")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

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
    fig.update_layout(title="Product Price vs Gross Margin (bubble = revenue)")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
