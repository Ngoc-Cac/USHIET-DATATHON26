"""Export all main dashboard charts to figures/ as PNG.

Run:
    python export_figures.py

Output: figures/{D1,D2,D3,D4}/<chart>.png — one subfolder per dashboard.
Requires: pip install kaleido
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "streamlit_app"))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from data import load
from theme import (style, LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, RED,
                   GREY, CAT_PALETTE, SEGMENT_COLORS)

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

CURRENT_DASH = {"name": "D1"}

def set_dash(name: str) -> Path:
    CURRENT_DASH["name"] = name
    sub = OUT / name
    sub.mkdir(parents=True, exist_ok=True)
    return sub

# Larger margins for standalone PNG (don't use compact)
def styled(fig, height=520, show_legend=True):
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, sans-serif", color=DARK, size=13),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        title_font=dict(size=18, color=DARK, family="Inter"),
        margin=dict(l=70, r=40, t=70, b=70),
        legend=dict(bgcolor="rgba(255,255,255,0.6)",
                    bordercolor="#E5E7E0", borderwidth=1, font=dict(size=11)),
        showlegend=show_legend, height=height, width=960,
    )
    fig.update_xaxes(gridcolor="#EEF1E5", linecolor="#D1D5C8",
                     zerolinecolor="#EEF1E5", tickfont=dict(color=GREY, size=11))
    fig.update_yaxes(gridcolor="#EEF1E5", linecolor="#D1D5C8",
                     zerolinecolor="#EEF1E5", tickfont=dict(color=GREY, size=11))
    return fig


def save(fig, name):
    sub = OUT / CURRENT_DASH["name"]
    sub.mkdir(parents=True, exist_ok=True)
    path = sub / f"{name}.png"
    fig.write_image(str(path), scale=2)
    print(f"  ✓ {CURRENT_DASH['name']}/{path.name}  ({fig.layout.width}×{fig.layout.height})")


# =====================================================================
# D1 — Revenue & Profitability
# =====================================================================
def export_d1():
    print("[D1] Revenue & Profitability")
    set_dash("D1")
    monthly = load("agg_monthly_summary")
    orders = load("fact_orders_enriched", columns=(
        "category", "line_revenue", "line_gross_profit", "has_promo",
        "order_ym", "product_id"))
    products = load("dim_products")

    # C1 Revenue trend
    df = monthly.copy()
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.sort_values("date")
    df["rev_ma12"] = df["revenue"].rolling(12, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["revenue"], name="Revenue",
                             line=dict(color=LIME_STRONG, width=1.6),
                             fill="tozeroy", fillcolor="rgba(184,232,53,0.15)"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["gross_profit"], name="Gross Profit",
                             line=dict(color=LIME_DARK, width=1.6)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["rev_ma12"], name="MA-12",
                             line=dict(color=DARK, width=2.2, dash="dot")))
    fig.update_layout(title="D1 · Revenue & Gross Profit (monthly)",
                      hovermode="x unified",
                      xaxis_title="Month", yaxis_title="VND")
    save(styled(fig), "C1_revenue_trend")

    # C2 MoM heatmap
    df = monthly.copy()
    df["year"] = df["year_month"].str[:4].astype(int)
    df["month"] = df["year_month"].str[5:7].astype(int)
    pivot = df.pivot_table(index="year", columns="month", values="mom_growth_pct").reindex(columns=range(1, 13))
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=[f"M{m:02d}" for m in pivot.columns],
        y=pivot.index.astype(str),
        colorscale=[[0, "#DC2626"], [0.5, "#F5F6F0"], [1, LIME_DARK]], zmid=0,
        colorbar=dict(title="MoM %", thickness=12),
    ))
    fig.update_layout(title="D1 · Month-over-Month Growth Heatmap",
                      xaxis_title="Month", yaxis_title="Year")
    save(styled(fig, show_legend=False), "C2_mom_heatmap")

    # C3 Margin vs discount
    promo = (orders.groupby("order_ym")
             .agg(lines=("has_promo", "size"), promoted=("has_promo", "sum"))
             .assign(discount_pen=lambda d: d["promoted"]/d["lines"]*100)
             .reset_index().rename(columns={"order_ym": "year_month"}))
    df = monthly.merge(promo[["year_month", "discount_pen"]], on="year_month", how="left")
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.sort_values("date")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df["date"], y=df["gross_margin_pct"],
                             name="Margin %", line=dict(color=LIME_DARK, width=2.2)),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=df["date"], y=df["discount_pen"],
                             name="Discount %", line=dict(color=AMBER, width=2, dash="dash")),
                  secondary_y=True)
    fig.update_yaxes(title_text="Margin %", secondary_y=False)
    fig.update_yaxes(title_text="Discount %", secondary_y=True)
    fig.update_layout(title="D1 · Margin vs Discount Penetration",
                      hovermode="x unified", xaxis_title="Month")
    save(styled(fig), "C3_margin_vs_discount")

    # C4 Category Pareto
    cat = (orders.groupby("category")
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
                             mode="lines+markers", line=dict(color=DARK, width=2.2)),
                  secondary_y=True)
    fig.add_trace(go.Scatter(x=cat["category"], y=cat["margin_pct"], name="Margin %",
                             mode="lines+markers",
                             line=dict(color=AMBER, width=2.2, dash="dot")),
                  secondary_y=True)
    fig.update_yaxes(title_text="Revenue", secondary_y=False)
    fig.update_yaxes(title_text="Cum % / Margin %", range=[0, 105], secondary_y=True)
    fig.update_layout(title="D1 · Category Pareto + Margin",
                      hovermode="x unified")
    save(styled(fig), "C4_category_pareto")


# =====================================================================
# D2 — Customer
# =====================================================================
def export_d2():
    print("[D2] Customer Segmentation")
    set_dash("D2")
    rfm = load("dim_customers_rfm", columns=(
        "customer_id", "frequency", "monetary", "rfm_segment",
        "acquisition_channel"))
    cohort = load("agg_cohort_retention")
    active = rfm[rfm["frequency"] > 0]

    # C1 RFM Segments
    seg = (active.groupby("rfm_segment")
           .agg(customers=("customer_id", "count"),
                avg_value=("monetary", "mean"))
           .reset_index().sort_values("customers", ascending=False))
    colors = [SEGMENT_COLORS.get(s, LIME) for s in seg["rfm_segment"]]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=seg["rfm_segment"], y=seg["customers"],
                         marker_color=colors, name="Customers"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=seg["rfm_segment"], y=seg["avg_value"],
                             name="Avg LTV", mode="lines+markers",
                             line=dict(color=DARK, width=2.2)),
                  secondary_y=True)
    fig.update_yaxes(title_text="# Customers", secondary_y=False)
    fig.update_yaxes(title_text="Avg LTV (VND)", secondary_y=True)
    fig.update_layout(title="D2 · RFM Segments — count + avg LTV",
                      hovermode="x unified")
    save(styled(fig), "C1_rfm_segments")

    # C2 Customer Journey Funnel
    f1 = (rfm["frequency"] >= 1).sum()
    f2 = (rfm["frequency"] >= 2).sum()
    f3 = (rfm["frequency"] >= 3).sum()
    f5 = (rfm["frequency"] >= 5).sum()
    fig = go.Figure(go.Funnel(
        y=["1st purchase", "2nd purchase", "3rd purchase", "Loyal (5+)"],
        x=[f1, f2, f3, f5],
        marker=dict(color=[LIME_STRONG, LIME, LIME_DARK, DARK]),
        textposition="inside", textinfo="value+percent initial",
    ))
    fig.update_layout(title="D2 · Customer Journey Funnel")
    save(styled(fig, show_legend=False), "C2_journey_funnel")

    # C3 Acquisition Channel
    ch = (active.groupby("acquisition_channel")
          .agg(customers=("customer_id", "count"),
               revenue=("monetary", "sum"),
               avg_value=("monetary", "mean"))
          .reset_index().sort_values("revenue", ascending=False))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ch["acquisition_channel"], y=ch["revenue"],
                         marker_color=LIME, marker_line_color=LIME_STRONG,
                         name="Revenue"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=ch["acquisition_channel"], y=ch["avg_value"],
                             mode="lines+markers", name="Avg LTV",
                             line=dict(color=DARK, width=2.5),
                             marker=dict(size=10)),
                  secondary_y=True)
    fig.update_yaxes(title_text="Revenue (VND)", secondary_y=False)
    fig.update_yaxes(title_text="Avg LTV", secondary_y=True)
    fig.update_layout(title="D2 · Acquisition Channel — Revenue + LTV",
                      hovermode="x unified")
    save(styled(fig), "C3_acquisition_channel")

    # C4 Treemap
    seg2 = (active.groupby("rfm_segment").agg(revenue=("monetary", "sum")).reset_index())
    colors = [SEGMENT_COLORS.get(s, LIME) for s in seg2["rfm_segment"]]
    fig = go.Figure(go.Treemap(
        labels=seg2["rfm_segment"], parents=[""]*len(seg2),
        values=seg2["revenue"],
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent root",
    ))
    fig.update_layout(title="D2 · Revenue by RFM Segment")
    save(styled(fig, show_legend=False), "C4_revenue_treemap")

    # C5 Cohort retention (weighted, M1-M24)
    df = cohort[(cohort["period_number"] >= 1) & (cohort["period_number"] <= 24)].copy()
    df["cohort_dt"] = pd.to_datetime(df["cohort_month"] + "-01")
    df["year"] = df["cohort_dt"].dt.year
    agg = (df.groupby(["year", "period_number"])
             .agg(active=("active_customers", "sum"),
                  size=("cohort_size", "sum")).reset_index())
    agg["retention"] = agg["active"] / agg["size"] * 100
    yearly = agg.pivot(index="year", columns="period_number", values="retention")
    z_max = float(yearly.stack().max())
    fig = go.Figure(go.Heatmap(
        z=yearly.values,
        x=[f"M{int(c)}" for c in yearly.columns],
        y=yearly.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.3, "#D9EE99"], [0.7, LIME], [1, LIME_DARK]],
        zmin=0, zmax=max(z_max, 5),
        colorbar=dict(title="Retention %", thickness=12),
    ))
    fig.update_layout(title="D2 · Cohort Retention (weighted, M1–M24)",
                      xaxis_title="Months since first purchase",
                      yaxis_title="Cohort year")
    save(styled(fig, show_legend=False), "C5_cohort_retention")


# =====================================================================
# D3 — Product
# =====================================================================
def export_d3():
    print("[D3] Product Performance")
    set_dash("D3")
    products = load("dim_products")
    orders = load("fact_orders_enriched", columns=(
        "category", "line_revenue", "line_gross_profit", "quantity",
        "product_id", "size"))
    returns = load("fact_returns_enriched", columns=(
        "category", "return_reason", "refund_amount", "return_quantity", "size"))
    inv = load("fact_inventory", columns=(
        "category", "inventory_health", "inventory_value_cost"))

    # C1 Top 15 SKUs
    prod_rev = (orders.groupby("product_id")
                .agg(revenue=("line_revenue", "sum"),
                     gp=("line_gross_profit", "sum")).reset_index())
    top = (prod_rev.merge(products[["product_id", "product_name", "category"]], on="product_id")
           .nlargest(15, "revenue").sort_values("revenue"))
    fig = go.Figure(go.Bar(
        y=top["product_name"], x=top["revenue"], orientation="h",
        marker_color=LIME, marker_line_color=LIME_STRONG,
    ))
    fig.update_layout(title="D3 · Top 15 SKUs by Revenue",
                      xaxis_title="Revenue (VND)")
    save(styled(fig, show_legend=False), "C1_top_skus")

    # C2 Return reasons
    rs = (returns.groupby("return_reason")
          .agg(count=("return_quantity", "sum"))
          .reset_index().sort_values("count", ascending=True))
    fig = go.Figure(go.Bar(y=rs["return_reason"], x=rs["count"],
                           orientation="h", marker_color=AMBER))
    fig.update_layout(title="D3 · Return Reasons (units returned)",
                      xaxis_title="Units returned")
    save(styled(fig, show_legend=False), "C2_return_reasons")

    # C3 Inventory health
    inv_health = inv["inventory_health"].value_counts().reset_index()
    inv_health.columns = ["status", "snapshots"]
    color_map = {"Healthy": LIME_DARK, "Reorder": AMBER,
                 "Overstock": "#7C9F2C", "Stockout": RED}
    fig = go.Figure(go.Bar(
        x=inv_health["status"], y=inv_health["snapshots"],
        marker_color=[color_map.get(s, LIME) for s in inv_health["status"]],
        text=inv_health["snapshots"], textposition="outside",
    ))
    fig.update_layout(title="D3 · Inventory Health Snapshots",
                      yaxis_title="Snapshots")
    save(styled(fig, show_legend=False), "C3_inventory_health")

    # C4 Price vs margin scatter
    prod_rev = (orders.groupby("product_id")["line_revenue"].sum()
                .rename("product_revenue").reset_index())
    df = products.merge(prod_rev, on="product_id", how="left")
    df = df[df["product_revenue"].fillna(0) > 0]
    fig = px.scatter(df, x="price", y="gross_margin_pct",
                     size="product_revenue", color="category",
                     color_discrete_sequence=CAT_PALETTE,
                     hover_name="product_name", size_max=40,
                     labels={"price": "Unit Price", "gross_margin_pct": "Margin %"})
    fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
    fig.update_layout(title="D3 · Price vs Margin (size = revenue)")
    save(styled(fig), "C4_price_vs_margin")


# =====================================================================
# D4 — Marketing
# =====================================================================
def export_d4():
    print("[D4] Marketing & Channel")
    set_dash("D4")
    wt = load("fact_web_traffic")
    rfm = load("dim_customers_rfm", columns=(
        "customer_id", "frequency", "monetary", "acquisition_channel"))

    # C1 Sessions trend
    monthly = (wt.groupby(["year_month", "traffic_source"])["sessions"]
               .sum().reset_index())
    monthly["date"] = pd.to_datetime(monthly["year_month"] + "-01")
    fig = px.line(monthly.sort_values("date"), x="date", y="sessions",
                  color="traffic_source",
                  color_discrete_sequence=CAT_PALETTE)
    fig.update_traces(line=dict(width=1.8))
    fig.update_layout(title="D4 · Sessions by Traffic Source",
                      xaxis_title="Month", yaxis_title="Sessions",
                      hovermode="x unified")
    save(styled(fig), "C1_sessions_trend")

    # C2 Engagement scatter
    src = (wt.groupby("traffic_source")
           .agg(sessions=("sessions", "sum"),
                bounce=("bounce_rate", "mean"),
                pps=("pages_per_session", "mean")).reset_index())
    fig = px.scatter(src, x="bounce", y="pps", size="sessions",
                     color="traffic_source",
                     color_discrete_sequence=CAT_PALETTE,
                     hover_name="traffic_source", size_max=70,
                     labels={"bounce": "Bounce rate", "pps": "Pages / session"})
    fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
    fig.update_layout(title="D4 · Engagement by Source (size = sessions)")
    save(styled(fig), "C2_engagement_scatter")

    # C3 Channel LTV
    ch = (rfm[rfm["frequency"] > 0].groupby("acquisition_channel")
          .agg(customers=("customer_id", "count"),
               avg_ltv=("monetary", "mean"))
          .reset_index().sort_values("avg_ltv"))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ch["acquisition_channel"], y=ch["customers"],
                         name="Customers", marker_color=LIME,
                         marker_line_color=LIME_STRONG),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=ch["acquisition_channel"], y=ch["avg_ltv"],
                             name="Avg LTV", mode="lines+markers",
                             line=dict(color=DARK, width=2.2)),
                  secondary_y=True)
    fig.update_yaxes(title_text="# Customers", secondary_y=False)
    fig.update_yaxes(title_text="Avg LTV (VND)", secondary_y=True)
    fig.update_layout(title="D4 · Acquisition Channel — Customers + LTV",
                      hovermode="x unified")
    save(styled(fig), "C3_channel_ltv")

    # C4 Bounce rate trend
    bm = (wt.groupby(["year_month", "traffic_source"])["bounce_rate"]
          .mean().reset_index())
    bm["date"] = pd.to_datetime(bm["year_month"] + "-01")
    fig = px.line(bm.sort_values("date"), x="date", y="bounce_rate",
                  color="traffic_source",
                  color_discrete_sequence=CAT_PALETTE)
    fig.update_traces(line=dict(width=1.8))
    fig.update_layout(title="D4 · Bounce Rate Trend",
                      xaxis_title="Month", yaxis_title="Bounce rate",
                      hovermode="x unified")
    save(styled(fig), "C4_bounce_trend")


def main():
    print(f"Exporting to {OUT}\n")
    export_d1()
    export_d2()
    export_d3()
    export_d4()
    n = len(list(OUT.rglob("*.png")))
    print(f"\nDone. {n} PNG files in {OUT}")


if __name__ == "__main__":
    main()
