"""Dashboard D2 — Customer Segmentation & Lifecycle.

KPI + 5 plotly figures: RFM segment distribution, cohort retention heatmap,
acquisition channel performance, monetary distribution, customer LTV by segment.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from ..data_loader import load
from .d1_revenue import (
    style_fig, _fmt_money,
    LIME, LIME_STRONG, LIME_DARK, DARK, GREY, AMBER, RED, CAT_PALETTE,
)

SEGMENT_ORDER = [
    "Champions", "Loyal Customers", "Potential Loyalists",
    "New Customers", "Promising", "Need Attention",
    "About to Sleep", "At Risk", "Cannot Lose Them",
    "Hibernating", "Lost",
]
SEGMENT_COLORS = {
    "Champions": "#6FA82B",
    "Loyal Customers": "#9DCB1F",
    "Potential Loyalists": "#B8E835",
    "New Customers": "#C9E866",
    "Promising": "#D9EE99",
    "Need Attention": "#F59E0B",
    "About to Sleep": "#F97316",
    "At Risk": "#EF4444",
    "Cannot Lose Them": "#B91C1C",
    "Hibernating": "#6B7280",
    "Lost": "#374151",
}


def build_kpis(rfm: pd.DataFrame) -> list[dict]:
    active = rfm[rfm["frequency"] > 0]
    total = len(rfm)
    n_active = len(active)
    champions = (active["rfm_segment"] == "Champions").sum()
    at_risk = active["rfm_segment"].isin(["At Risk", "Cannot Lose Them"]).sum()
    avg_ltv = active["monetary"].mean()
    return [
        {"label": "Total Customers", "value": f"{total:,}",
         "delta": f"{n_active:,} active ({n_active/total*100:.1f}%)",
         "positive": True},
        {"label": "Champions", "value": f"{champions:,}",
         "delta": f"{champions/n_active*100:.1f}% of active",
         "positive": True},
        {"label": "At Risk + Cannot Lose", "value": f"{at_risk:,}",
         "delta": f"{at_risk/n_active*100:.1f}% need win-back",
         "positive": False},
        {"label": "Avg Customer Value", "value": _fmt_money(avg_ltv),
         "delta": "Lifetime monetary",
         "positive": True},
    ]


def chart_rfm_segments(rfm: pd.DataFrame) -> go.Figure:
    active = rfm[rfm["frequency"] > 0]
    seg = (active.groupby("rfm_segment")
           .agg(customers=("customer_id", "count"),
                revenue=("monetary", "sum"),
                avg_value=("monetary", "mean"))
           .reset_index())
    order = [s for s in SEGMENT_ORDER if s in seg["rfm_segment"].values]
    extra = [s for s in seg["rfm_segment"] if s not in SEGMENT_ORDER]
    seg["rfm_segment"] = pd.Categorical(seg["rfm_segment"], categories=order + extra, ordered=True)
    seg = seg.sort_values("rfm_segment")
    colors = [SEGMENT_COLORS.get(s, LIME) for s in seg["rfm_segment"]]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=seg["rfm_segment"], y=seg["customers"],
                         name="Customers", marker_color=colors,
                         customdata=seg[["revenue", "avg_value"]],
                         hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<br>"
                                       "Revenue: %{customdata[0]:,.0f}<br>"
                                       "Avg value: %{customdata[1]:,.0f}<extra></extra>"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=seg["rfm_segment"], y=seg["avg_value"],
                             name="Avg value (VND)",
                             mode="lines+markers",
                             line=dict(color=DARK, width=2),
                             marker=dict(color=DARK, size=8)),
                  secondary_y=True)
    fig.update_layout(title="RFM Segment Distribution + Avg Customer Value",
                      hovermode="x unified", barmode="group")
    fig.update_yaxes(title_text="# Customers", secondary_y=False)
    fig.update_yaxes(title_text="Avg Monetary (VND)", secondary_y=True)
    return style_fig(fig, height=460), seg


def chart_cohort_heatmap(cohort: pd.DataFrame) -> go.Figure:
    df = cohort[cohort["period_number"] <= 24].copy()
    pivot = df.pivot(index="cohort_month", columns="period_number",
                     values="retention_rate")
    pivot = pivot.sort_index()
    yearly = pivot.copy()
    yearly.index = pd.to_datetime(yearly.index + "-01")
    yearly = yearly.groupby(yearly.index.year).mean()

    fig = go.Figure(go.Heatmap(
        z=yearly.values,
        x=[f"M{int(c)}" for c in yearly.columns],
        y=yearly.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.3, "#D9EE99"], [0.7, LIME], [1, LIME_DARK]],
        zmin=0, zmax=30,
        colorbar=dict(title="Retention %", thickness=12, outlinewidth=0),
        hovertemplate="Cohort year %{y} · Period %{x}<br>"
                      "Retention: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(title="Cohort Retention by Year (avg %, periods 0–24 months)",
                      xaxis_title="Months since first purchase",
                      yaxis_title="Cohort Year")
    return style_fig(fig, height=460)


def chart_acquisition_channel(rfm: pd.DataFrame) -> go.Figure:
    active = rfm[rfm["frequency"] > 0]
    ch = (active.groupby("acquisition_channel")
          .agg(customers=("customer_id", "count"),
               revenue=("monetary", "sum"),
               avg_freq=("frequency", "mean"),
               avg_value=("monetary", "mean"))
          .reset_index()
          .sort_values("revenue", ascending=True))

    fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                        column_widths=[0.55, 0.45], horizontal_spacing=0.04,
                        subplot_titles=("Total Revenue (VND)", "Avg Customer Value"))
    fig.add_trace(go.Bar(y=ch["acquisition_channel"], x=ch["revenue"],
                         orientation="h", marker_color=LIME,
                         marker_line_color=LIME_STRONG, marker_line_width=1,
                         name="Revenue",
                         hovertemplate="<b>%{y}</b><br>Revenue: %{x:,.0f}<extra></extra>"),
                  row=1, col=1)
    fig.add_trace(go.Bar(y=ch["acquisition_channel"], x=ch["avg_value"],
                         orientation="h", marker_color=DARK,
                         name="Avg value",
                         hovertemplate="<b>%{y}</b><br>Avg value: %{x:,.0f}<extra></extra>"),
                  row=1, col=2)
    fig.update_layout(title="Acquisition Channel Performance",
                      showlegend=False)
    return style_fig(fig, height=420), ch


def chart_monetary_distribution(rfm: pd.DataFrame) -> go.Figure:
    active = rfm[rfm["frequency"] > 0].copy()
    active["monetary_log"] = np.log10(active["monetary"].clip(lower=1))

    fig = go.Figure(go.Histogram(
        x=active["monetary_log"], nbinsx=60,
        marker_color=LIME, marker_line_color=LIME_STRONG, marker_line_width=0.5,
        hovertemplate="log10 monetary: %{x:.2f}<br>Count: %{y:,}<extra></extra>",
    ))
    p50 = active["monetary"].median()
    p90 = active["monetary"].quantile(0.9)
    fig.add_vline(x=np.log10(p50), line_dash="dash", line_color=DARK,
                  annotation_text=f"P50: {_fmt_money(p50)}",
                  annotation_position="top")
    fig.add_vline(x=np.log10(p90), line_dash="dash", line_color=AMBER,
                  annotation_text=f"P90: {_fmt_money(p90)}",
                  annotation_position="top")
    fig.update_layout(title="Customer Lifetime Monetary Distribution (log10)",
                      xaxis_title="log10(Monetary VND)",
                      yaxis_title="# Customers", bargap=0.05)
    return style_fig(fig, height=400), p50, p90


def chart_segment_value_treemap(seg: pd.DataFrame) -> go.Figure:
    seg = seg.copy()
    seg["color_val"] = [SEGMENT_COLORS.get(s, LIME) for s in seg["rfm_segment"]]
    fig = go.Figure(go.Treemap(
        labels=seg["rfm_segment"].astype(str),
        parents=[""] * len(seg),
        values=seg["revenue"],
        marker=dict(colors=seg["color_val"], line=dict(color="#FFFFFF", width=2)),
        textinfo="label+value+percent root",
        texttemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percentRoot:.1%}",
        hovertemplate="<b>%{label}</b><br>Revenue: %{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(title="Revenue Contribution by RFM Segment",
                      margin=dict(l=10, r=10, t=56, b=10))
    return style_fig(fig, height=440)


def build() -> dict:
    rfm = load("dim_customers_rfm", columns=(
        "customer_id", "frequency", "monetary", "rfm_segment",
        "acquisition_channel", "recency_days"))
    cohort = load("agg_cohort_retention")

    kpis = build_kpis(rfm)

    fig_seg, seg_df = chart_rfm_segments(rfm)
    fig_cohort = chart_cohort_heatmap(cohort)
    fig_ch, ch_df = chart_acquisition_channel(rfm)
    fig_mon, p50, p90 = chart_monetary_distribution(rfm)
    fig_tree = chart_segment_value_treemap(seg_df)

    active = rfm[rfm["frequency"] > 0]
    top_seg_rev = seg_df.iloc[seg_df["revenue"].argmax()]
    biggest_seg_cnt = seg_df.iloc[seg_df["customers"].argmax()]
    best_channel = ch_df.iloc[ch_df["avg_value"].argmax()]
    worst_channel = ch_df.iloc[ch_df["avg_value"].argmin()]

    charts = [
        {
            "id": "d2-c1", "level": "Descriptive",
            "html": fig_seg.to_html(include_plotlyjs=False, full_html=False, div_id="d2c1"),
            "narrative": (
                f"<b>What:</b> Segment đông nhất là <b>{biggest_seg_cnt['rfm_segment']}</b> "
                f"({biggest_seg_cnt['customers']:,} khách), nhưng "
                f"<b>{top_seg_rev['rfm_segment']}</b> đem về doanh thu lớn nhất "
                f"({_fmt_money(top_seg_rev['revenue'])}).<br>"
                "<b>Why:</b> RFM phân tách rõ giá trị — số lượng khách không đồng nghĩa "
                "với giá trị mang lại.<br>"
                "<b>Action:</b> Đầu tư retention cho Champions/Loyal; nurture Potential "
                "Loyalists để chuyển lên top tier."
            ),
        },
        {
            "id": "d2-c2", "level": "Diagnostic",
            "html": fig_cohort.to_html(include_plotlyjs=False, full_html=False, div_id="d2c2"),
            "narrative": (
                "<b>What:</b> Heatmap retention theo cohort year × period number cho "
                "thấy retention sụt mạnh ngay sau M1, ổn định dần ở M6+.<br>"
                "<b>Why:</b> Khoảng trống M1–M3 là vùng churn cao nhất — onboarding "
                "và lần mua thứ 2 là điểm cần can thiệp.<br>"
                "<b>Action:</b> Trigger email/promo trong 30/60/90 ngày sau lần mua "
                "đầu để kéo retention M1–M3 lên."
            ),
        },
        {
            "id": "d2-c3", "level": "Predictive",
            "html": fig_ch.to_html(include_plotlyjs=False, full_html=False, div_id="d2c3"),
            "narrative": (
                f"<b>What:</b> Kênh <b>{best_channel['acquisition_channel']}</b> có "
                f"avg customer value cao nhất ({_fmt_money(best_channel['avg_value'])}); "
                f"<b>{worst_channel['acquisition_channel']}</b> thấp nhất "
                f"({_fmt_money(worst_channel['avg_value'])}).<br>"
                "<b>Why:</b> Cùng 1 đồng CAC, kênh khác nhau cho ra LTV khác nhau "
                "rõ rệt.<br>"
                "<b>Action:</b> Reallocate marketing budget sang kênh avg value cao; "
                "đo CAC theo kênh để tính ROI thực."
            ),
        },
        {
            "id": "d2-c4", "level": "Diagnostic",
            "html": fig_mon.to_html(include_plotlyjs=False, full_html=False, div_id="d2c4"),
            "narrative": (
                f"<b>What:</b> Phân phối monetary lệch phải mạnh — P50 {_fmt_money(p50)}, "
                f"P90 {_fmt_money(p90)} (chênh ~{p90/p50:.1f}×).<br>"
                "<b>Why:</b> Một số ít khách hàng top 10% đóng góp phần lớn doanh thu "
                "(nguyên tắc Pareto).<br>"
                "<b>Action:</b> Xây tier VIP cho top 10%; chương trình loyalty bậc thang "
                "để giữ chân và mở rộng tier."
            ),
        },
        {
            "id": "d2-c5", "level": "Prescriptive",
            "html": fig_tree.to_html(include_plotlyjs=False, full_html=False, div_id="d2c5"),
            "narrative": (
                f"<b>What:</b> Treemap doanh thu theo segment — top 3 segment "
                f"chiếm phần lớn revenue.<br>"
                "<b>Why:</b> Tổng revenue tập trung ở nhóm Champions/Loyal/Potential — "
                "đầu tư cho nhóm này có ROI cao nhất.<br>"
                "<b>Action:</b> Ngân sách retention nên ưu tiên Champions (giữ chân) > "
                "Cannot Lose Them (win-back) > Potential Loyalists (nurture)."
            ),
        },
    ]

    return {
        "title": "D2 — Customer Segmentation & Lifecycle",
        "subtitle": "RFM · Cohort retention · Acquisition channel · LTV distribution",
        "kpis": kpis,
        "charts": charts,
    }
