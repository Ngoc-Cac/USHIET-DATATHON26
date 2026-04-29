"""Dashboard D1 — Revenue & Profitability.

Builds KPI cards + 5 plotly figures across 4 analytical levels:
Descriptive → Diagnostic → Predictive → Prescriptive.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from ..data_loader import load

# Brand palette — match template.jpg
LIME = "#B8E835"
LIME_STRONG = "#9DCB1F"
LIME_DARK = "#6FA82B"
DARK = "#1A1F14"
GREY = "#6B7280"
AMBER = "#F59E0B"
RED = "#DC2626"
CAT_PALETTE = ["#9DCB1F", "#6FA82B", "#3F6B17", "#C9E866", "#7C9F2C",
               "#BFD877", "#4F7A1B", "#A8C940", "#5C8222", "#D9EE99"]

RANGE_SELECTOR = dict(
    buttons=[
        dict(count=1, label="1Y", step="year", stepmode="backward"),
        dict(count=3, label="3Y", step="year", stepmode="backward"),
        dict(count=5, label="5Y", step="year", stepmode="backward"),
        dict(step="all", label="All"),
    ],
    bgcolor="#F5F6F0", activecolor="#B8E835",
    bordercolor="#D1D5C8", borderwidth=1,
    x=0, y=1.16, font=dict(size=11, color="#1A1F14"),
)


def add_rangeslider(fig: go.Figure) -> go.Figure:
    fig.update_xaxes(
        rangeslider=dict(visible=True, thickness=0.06,
                         bgcolor="#EEF1E5", bordercolor="#D1D5C8"),
        rangeselector=RANGE_SELECTOR,
    )
    return fig


def style_fig(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, sans-serif", color=DARK, size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=15, color=DARK, family="Inter"),
        margin=dict(l=48, r=28, t=56, b=44),
        legend=dict(bgcolor="rgba(255,255,255,0.6)",
                    bordercolor="#E5E7E0", borderwidth=1),
        height=height,
    )
    fig.update_xaxes(gridcolor="#EEF1E5", linecolor="#D1D5C8",
                     zerolinecolor="#EEF1E5", tickfont=dict(color=GREY))
    fig.update_yaxes(gridcolor="#EEF1E5", linecolor="#D1D5C8",
                     zerolinecolor="#EEF1E5", tickfont=dict(color=GREY))
    return fig


def _fmt_money(v: float) -> str:
    if abs(v) >= 1e9:
        return f"{v/1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"{v/1e6:.2f}M"
    if abs(v) >= 1e3:
        return f"{v/1e3:.1f}K"
    return f"{v:.0f}"


def build_kpis(monthly: pd.DataFrame) -> list[dict]:
    monthly = monthly.copy()
    monthly["year"] = monthly["year_month"].str[:4].astype(int)

    total_rev = monthly["revenue"].sum()
    total_gp = monthly["gross_profit"].sum()
    margin = total_gp / total_rev * 100
    aov = (monthly["revenue"].sum() / monthly["total_orders"].sum())

    last_year = monthly["year"].max()
    prev_year = last_year - 1
    rev_last = monthly.loc[monthly["year"] == last_year, "revenue"].sum()
    rev_prev = monthly.loc[monthly["year"] == prev_year, "revenue"].sum()
    yoy_rev = (rev_last / rev_prev - 1) * 100 if rev_prev else 0

    gp_last = monthly.loc[monthly["year"] == last_year, "gross_profit"].sum()
    gp_prev = monthly.loc[monthly["year"] == prev_year, "gross_profit"].sum()
    yoy_gp = (gp_last / gp_prev - 1) * 100 if gp_prev else 0

    margin_last = gp_last / rev_last * 100 if rev_last else 0
    margin_prev = gp_prev / rev_prev * 100 if rev_prev else 0
    margin_delta = margin_last - margin_prev

    aov_last = (monthly.loc[monthly["year"] == last_year, "revenue"].sum() /
                monthly.loc[monthly["year"] == last_year, "total_orders"].sum())
    aov_prev = (monthly.loc[monthly["year"] == prev_year, "revenue"].sum() /
                monthly.loc[monthly["year"] == prev_year, "total_orders"].sum())
    yoy_aov = (aov_last / aov_prev - 1) * 100 if aov_prev else 0

    return [
        {"label": "Total Revenue", "value": _fmt_money(total_rev),
         "delta": f"{yoy_rev:+.1f}% YoY", "positive": yoy_rev >= 0},
        {"label": "Gross Profit", "value": _fmt_money(total_gp),
         "delta": f"{yoy_gp:+.1f}% YoY", "positive": yoy_gp >= 0},
        {"label": "Gross Margin", "value": f"{margin:.1f}%",
         "delta": f"{margin_delta:+.2f} pp YoY", "positive": margin_delta >= 0},
        {"label": "AOV", "value": _fmt_money(aov),
         "delta": f"{yoy_aov:+.1f}% YoY", "positive": yoy_aov >= 0},
    ]


# -------- Charts --------

def chart_revenue_trend(monthly: pd.DataFrame) -> go.Figure:
    df = monthly.copy()
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.sort_values("date")
    df["rev_ma12"] = df["revenue"].rolling(12, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["revenue"], name="Revenue",
                             mode="lines", line=dict(color=LIME_STRONG, width=1.6),
                             fill="tozeroy", fillcolor="rgba(184,232,53,0.15)"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["gross_profit"], name="Gross Profit",
                             mode="lines", line=dict(color=LIME_DARK, width=1.6)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["rev_ma12"], name="Revenue MA-12",
                             mode="lines", line=dict(color=DARK, width=2.2, dash="dot")))
    fig.update_layout(
        title="Revenue & Gross Profit by Month (with 12-month MA)",
        xaxis_title="Month", yaxis_title="VND",
        hovermode="x unified",
    )
    style_fig(fig, height=480)
    return add_rangeslider(fig)


def chart_margin_vs_discount(monthly: pd.DataFrame, orders: pd.DataFrame) -> go.Figure:
    promo = (orders.groupby("order_ym")
             .agg(lines=("has_promo", "size"), promoted=("has_promo", "sum"))
             .assign(discount_pen=lambda d: d["promoted"] / d["lines"] * 100)
             .reset_index()
             .rename(columns={"order_ym": "year_month"}))
    df = monthly.merge(promo[["year_month", "discount_pen"]], on="year_month", how="left")
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.sort_values("date")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df["date"], y=df["gross_margin_pct"],
                             name="Gross Margin %",
                             line=dict(color=LIME_DARK, width=2.2)),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=df["date"], y=df["discount_pen"],
                             name="Discount Penetration %",
                             line=dict(color=AMBER, width=2, dash="dash")),
                  secondary_y=True)
    fig.update_layout(
        title="Gross Margin vs. Discount Penetration",
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Gross Margin %", secondary_y=False)
    fig.update_yaxes(title_text="Discount Penetration %", secondary_y=True)
    style_fig(fig, height=480)
    return add_rangeslider(fig)


def chart_mom_heatmap(monthly: pd.DataFrame) -> go.Figure:
    df = monthly.copy()
    df["year"] = df["year_month"].str[:4].astype(int)
    df["month"] = df["year_month"].str[5:7].astype(int)
    pivot = df.pivot(index="year", columns="month", values="mom_growth_pct")
    pivot = pivot.reindex(columns=range(1, 13))

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"M{m:02d}" for m in pivot.columns],
        y=pivot.index.astype(str),
        colorscale=[[0, "#DC2626"], [0.5, "#F5F6F0"], [1, LIME_DARK]],
        zmid=0,
        colorbar=dict(title="MoM %", thickness=12, outlinewidth=0),
        hovertemplate="Year %{y} · %{x}<br>MoM: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title="Month-over-Month Revenue Growth Heatmap",
        xaxis_title="Month", yaxis_title="Year",
    )
    return style_fig(fig, height=460)


def chart_category_pareto(orders: pd.DataFrame) -> go.Figure:
    cat = (orders.groupby("category")
           .agg(revenue=("line_revenue", "sum"),
                gross_profit=("line_gross_profit", "sum"))
           .assign(margin_pct=lambda d: d["gross_profit"] / d["revenue"] * 100)
           .sort_values("revenue", ascending=False)
           .reset_index())
    cat["cum_pct"] = cat["revenue"].cumsum() / cat["revenue"].sum() * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=cat["category"], y=cat["revenue"],
                        name="Revenue",
                        marker_color=LIME, marker_line_color=LIME_STRONG,
                        marker_line_width=1,
                        customdata=cat[["margin_pct", "gross_profit"]],
                        hovertemplate="<b>%{x}</b><br>Revenue: %{y:,.0f}<br>"
                                      "Margin: %{customdata[0]:.1f}%<br>"
                                      "Gross Profit: %{customdata[1]:,.0f}<extra></extra>"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=cat["category"], y=cat["cum_pct"],
                             name="Cumulative %",
                             mode="lines+markers",
                             line=dict(color=DARK, width=2),
                             marker=dict(color=DARK, size=7)),
                  secondary_y=True)
    fig.add_trace(go.Scatter(x=cat["category"], y=cat["margin_pct"],
                             name="Margin %",
                             mode="lines+markers",
                             line=dict(color=AMBER, width=2, dash="dot"),
                             marker=dict(color=AMBER, size=7)),
                  secondary_y=True)
    fig.update_layout(
        title="Category Revenue Pareto + Margin %",
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Revenue (VND)", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative % / Margin %",
                     secondary_y=True, range=[0, 105])
    return style_fig(fig, height=460), cat


def chart_product_scatter(products: pd.DataFrame, orders: pd.DataFrame) -> go.Figure:
    prod_rev = (orders.groupby("product_id")["line_revenue"].sum()
                .rename("product_revenue").reset_index())
    df = products.merge(prod_rev, on="product_id", how="left")
    df = df[df["product_revenue"].fillna(0) > 0].copy()
    df["product_revenue"] = df["product_revenue"].fillna(0)

    fig = px.scatter(
        df, x="price", y="gross_margin_pct",
        size="product_revenue", color="category",
        color_discrete_sequence=CAT_PALETTE,
        hover_name="product_name",
        hover_data={"price": ":.0f", "gross_margin_pct": ":.1f",
                    "product_revenue": ":,.0f", "segment": True},
        size_max=40,
        title="Product Pricing vs. Margin (bubble size = revenue)",
    )
    fig.update_layout(xaxis_title="Unit Price (VND)",
                      yaxis_title="Gross Margin %")
    fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
    return style_fig(fig, height=480)


# -------- Build all --------

def build() -> dict:
    monthly = load("agg_monthly_summary")
    orders = load("fact_orders_enriched", columns=(
        "category", "line_revenue", "line_gross_profit", "has_promo",
        "order_ym", "product_id"))
    products = load("dim_products")

    kpis = build_kpis(monthly)

    fig_trend = chart_revenue_trend(monthly)
    fig_margin = chart_margin_vs_discount(monthly, orders)
    fig_heatmap = chart_mom_heatmap(monthly)
    fig_pareto, cat_df = chart_category_pareto(orders)
    fig_scatter = chart_product_scatter(products, orders)

    # Insights from real data
    last_year = monthly["year_month"].str[:4].astype(int).max()
    peak_row = monthly.loc[monthly["revenue"].idxmax()]
    worst_margin = monthly.loc[monthly["gross_margin_pct"].idxmin()]
    top_cat = cat_df.iloc[0]
    top3_share = cat_df.head(3)["revenue"].sum() / cat_df["revenue"].sum() * 100

    charts = [
        {
            "id": "c1-trend", "level": "Descriptive",
            "html": fig_trend.to_html(include_plotlyjs=False, full_html=False, div_id="c1"),
            "narrative": (
                f"<b>What:</b> Revenue tăng đều từ 2012 đến {last_year}, đỉnh tại "
                f"{peak_row['year_month']} với doanh thu {_fmt_money(peak_row['revenue'])}.<br>"
                f"<b>Why:</b> Đường MA-12 cho thấy xu hướng dài hạn ổn định; biến "
                f"động ngắn hạn phản ánh tính mùa vụ.<br>"
                f"<b>Action:</b> Dự báo capacity và marketing spend theo quỹ đạo MA-12 "
                f"thay vì revenue tuần đơn lẻ."
            ),
        },
        {
            "id": "c2-margin", "level": "Diagnostic",
            "html": fig_margin.to_html(include_plotlyjs=False, full_html=False, div_id="c2"),
            "narrative": (
                f"<b>What:</b> Gross margin thấp nhất {worst_margin['gross_margin_pct']:.1f}% "
                f"vào {worst_margin['year_month']}.<br>"
                f"<b>Why:</b> Các tháng margin sụt thường trùng giai đoạn discount "
                f"penetration cao — khuyến mãi đang ăn vào lợi nhuận.<br>"
                f"<b>Action:</b> Đặt margin floor cho mỗi promo, ưu tiên promo theo "
                f"category có margin gốc cao."
            ),
        },
        {
            "id": "c3-heatmap", "level": "Predictive",
            "html": fig_heatmap.to_html(include_plotlyjs=False, full_html=False, div_id="c3"),
            "narrative": (
                "<b>What:</b> Heatmap MoM growth lộ rõ pattern mùa vụ — Q4 (M10–M12) "
                "thường xanh (tăng), đầu năm (M01–M02) thường đỏ.<br>"
                "<b>Why:</b> Hành vi mua sắm cuối năm + đầu năm chững lại sau Tết.<br>"
                "<b>Action:</b> Forecast Task 3 nên có term seasonal (12 tháng) và "
                "dummy cho tháng Tết."
            ),
        },
        {
            "id": "c4-pareto", "level": "Prescriptive",
            "html": fig_pareto.to_html(include_plotlyjs=False, full_html=False, div_id="c4"),
            "narrative": (
                f"<b>What:</b> Top 3 category chiếm {top3_share:.1f}% doanh thu; "
                f"<b>{top_cat['category']}</b> dẫn đầu với "
                f"{_fmt_money(top_cat['revenue'])} và margin {top_cat['margin_pct']:.1f}%.<br>"
                "<b>Why:</b> Phân bố Pareto rõ — số ít category gánh phần lớn revenue.<br>"
                "<b>Action:</b> Dồn marketing budget và inventory vào top 3, kiểm tra "
                "category margin thấp xem có nên cắt SKU."
            ),
        },
        {
            "id": "c5-scatter", "level": "Diagnostic",
            "html": fig_scatter.to_html(include_plotlyjs=False, full_html=False, div_id="c5"),
            "narrative": (
                "<b>What:</b> Scatter price–margin lộ outlier: SKU bán chạy nhưng "
                "margin thấp và SKU margin cao nhưng ít doanh thu.<br>"
                "<b>Why:</b> Chính sách giá có thể chưa phản ánh đúng cost cấu trúc.<br>"
                "<b>Action:</b> Re-price SKU bubble lớn ở vùng margin thấp; "
                "đẩy marketing cho SKU margin cao chưa scale."
            ),
        },
    ]

    return {
        "title": "D1 — Revenue & Profitability",
        "subtitle": "Descriptive → Diagnostic → Predictive → Prescriptive",
        "kpis": kpis,
        "charts": charts,
    }
