"""D4 — Marketing & Channel Effectiveness."""
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
from theme import (PLOTLY_CONFIG, style, fmt_money, inject_css, page_header_inline, filter_label, sidebar_notes_panel,
                   LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, RED, GREY, CAT_PALETTE)
from filters import single_select, year_select

st.set_page_config(page_title="D4 · Marketing", page_icon="📣", layout="wide")
inject_css()
sidebar_notes_panel("D4 notes", "Large blank area for channel insights, experiment notes, and optimization actions.")

wt = load("fact_web_traffic")
rfm = load("dim_customers_rfm", columns=(
    "customer_id", "frequency", "monetary", "acquisition_channel"))
orders_promo = load("fact_orders_enriched", columns=(
    "category", "line_revenue", "line_gross_profit", "line_cost",
    "quantity", "has_promo", "discount_pct", "order_year", "order_ym",
    "order_month", "promo_id"))
monthly_summary = load("agg_monthly_summary")
promotions = load("dim_promotions")

# Campaign family = promo_name with trailing year stripped
# (e.g. "Spring Sale 2013" -> "Spring Sale")
promotions["campaign_family"] = (promotions["promo_name"]
                                 .str.replace(r"\s+\d{4}$", "", regex=True))
campaign_families = sorted(promotions["campaign_family"].unique().tolist())

# Pre-join campaign info onto promo orders so all charts can use it
orders_promo = orders_promo.merge(
    promotions[["promo_id", "campaign_family", "promo_name", "promo_type",
                "discount_value", "promo_channel"]],
    on="promo_id", how="left")

sources = sorted(wt["traffic_source"].dropna().unique().tolist())
min_year = int(wt["year"].min())
max_year = int(wt["year"].max())

title_col, filter_col = st.columns([1.7, 2.3], gap="medium")
with title_col:
    page_header_inline("D4", "Marketing & Channel Effectiveness",
                       "Web traffic · Channel mix · Conversion · CAC vs LTV")
with filter_col:
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        filter_label("From year")
        yr_from = year_select("From year", list(range(min_year, max_year + 1)), key="d4_year_from")
    with f2:
        filter_label("To year")
        yr_to = year_select("To year", list(range(yr_from, max_year + 1)), key="d4_year_to", default="last")
    with f3:
        filter_label("Traffic source")
        sel_sources = single_select("Traffic source", sources, key="d4_src")
    with f4:
        filter_label("Campaign")
        sel_campaigns = single_select("Campaign", campaign_families, key="d4_campaign")
yr = (yr_from, yr_to)

wt_f = wt[wt["traffic_source"].isin(sel_sources) & wt["year"].between(yr[0], yr[1])]

total_sessions = wt_f["sessions"].sum()
total_visitors = wt_f["unique_visitors"].sum()
avg_bounce = wt_f["bounce_rate"].mean() * 100 if len(wt_f) else 0
avg_pps = wt_f["pages_per_session"].mean() if len(wt_f) else 0

charts_col, kpi_col = st.columns([4, 1], gap="medium")
with kpi_col:
    st.markdown("##### KPIs")
    st.metric("Total Sessions", fmt_money(total_sessions))
    st.metric("Unique Visitors", fmt_money(total_visitors))
    st.metric("Avg Bounce", f"{avg_bounce:.2f}%")
    st.metric("Pages/Session", f"{avg_pps:.2f}")

with charts_col:
    row1c1, row1c2 = st.columns(2)
    row2c1, row2c2 = st.columns(2)

# C1 — Sessions trend by source
with row1c1:
    monthly = (wt_f.groupby(["year_month", "traffic_source"])["sessions"]
               .sum().reset_index())
    monthly["date"] = pd.to_datetime(monthly["year_month"] + "-01")
    fig = px.line(monthly.sort_values("date"), x="date", y="sessions",
                  color="traffic_source",
                  color_discrete_sequence=CAT_PALETTE,
                  labels={"sessions": "Sessions", "date": "Month"})
    fig.update_traces(line=dict(width=1.6))
    fig.update_layout(title="Sessions by Traffic Source", hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# C2 — Bounce vs Pages/Session per source
with row1c2:
    src = (wt_f.groupby("traffic_source")
           .agg(sessions=("sessions", "sum"),
                bounce=("bounce_rate", "mean"),
                pps=("pages_per_session", "mean"),
                duration=("avg_session_duration_sec", "mean"))
           .reset_index())
    fig = px.scatter(src, x="bounce", y="pps", size="sessions",
                     color="traffic_source",
                     color_discrete_sequence=CAT_PALETTE,
                     hover_name="traffic_source", size_max=50,
                     labels={"bounce": "Bounce rate", "pps": "Pages / session"})
    fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
    fig.update_layout(title="Engagement by Source (size = sessions)")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# C3 — Channel LTV (from RFM)
with row2c1:
    ch = (rfm[rfm["frequency"] > 0].groupby("acquisition_channel")
          .agg(customers=("customer_id", "count"),
               revenue=("monetary", "sum"),
               avg_ltv=("monetary", "mean"))
          .reset_index().sort_values("avg_ltv"))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ch["acquisition_channel"], y=ch["customers"],
                         name="Customers", marker_color=LIME,
                         marker_line_color=LIME_STRONG), secondary_y=False)
    fig.add_trace(go.Scatter(x=ch["acquisition_channel"], y=ch["avg_ltv"],
                             name="Avg LTV", mode="lines+markers",
                             line=dict(color=DARK, width=2)),
                  secondary_y=True)
    fig.update_layout(title="Acquisition Channel — Customers + LTV")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# C4 — Bounce rate trend (monthly avg)
with row2c2:
    bm = (wt_f.groupby(["year_month", "traffic_source"])["bounce_rate"]
          .mean().reset_index())
    bm["date"] = pd.to_datetime(bm["year_month"] + "-01")
    fig = px.line(bm.sort_values("date"), x="date", y="bounce_rate",
                  color="traffic_source",
                  color_discrete_sequence=CAT_PALETTE)
    fig.update_traces(line=dict(width=1.6))
    fig.update_layout(title="Bounce Rate Trend", hovermode="x unified")
    style(fig, height=240)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# =====================================================================
# Extra brainstorm row 1 — Promo effectiveness (refocus on marketing economics)
# =====================================================================
st.markdown("---")
st.markdown("##### Extra analyses · promotion economics")

# Apply year filter; campaign filter applies ONLY to promo orders
# (no-promo orders have no campaign by definition; we keep them for fair comparison
#  but mark which ones belong to selected campaign vs all-other-promo)
op_year = orders_promo[orders_promo["order_year"].between(yr[0], yr[1])]
campaign_active = (set(sel_campaigns) != set(campaign_families))
if campaign_active:
    # When a single campaign is chosen, drop other promo orders so charts focus
    # on "this campaign vs no-promo baseline"
    op = op_year[(op_year["campaign_family"].isin(sel_campaigns))
                 | (op_year["has_promo"] == 0)]
    st.caption(f"🎯 Campaign filter active: **{', '.join(sel_campaigns)}** · "
               f"non-promo orders kept as baseline")
else:
    op = op_year

ext1, ext2, ext3 = st.columns(3)

# E1 — Promo with vs without (revenue, margin, AOV)
with ext1:
    grp = op.groupby("has_promo").agg(
        revenue=("line_revenue", "sum"),
        gp=("line_gross_profit", "sum"),
        units=("quantity", "sum"),
        orders=("line_revenue", "size"),
    ).reset_index()
    grp["label"] = grp["has_promo"].map({True: "With promo", False: "No promo",
                                          1: "With promo", 0: "No promo"})
    grp["margin_pct"] = grp["gp"] / grp["revenue"] * 100
    grp["aov_proxy"] = grp["revenue"] / grp["orders"]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=False,
                        column_widths=[0.5, 0.5], horizontal_spacing=0.18,
                        subplot_titles=("Revenue", "Margin %"))
    fig.add_trace(go.Bar(x=grp["label"], y=grp["revenue"],
                         marker_color=[LIME_DARK, AMBER],
                         text=[fmt_money(v) for v in grp["revenue"]],
                         textposition="outside", showlegend=False),
                  row=1, col=1)
    fig.add_trace(go.Bar(x=grp["label"], y=grp["margin_pct"],
                         marker_color=[LIME_DARK, AMBER],
                         text=[f"{v:.1f}%" for v in grp["margin_pct"]],
                         textposition="outside", showlegend=False),
                  row=1, col=2)
    fig.update_layout(title="Promo vs No-promo · revenue & margin")
    style(fig, height=280, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) == 2:
        with_p = grp[grp["has_promo"].isin([True, 1])].iloc[0]
        no_p = grp[grp["has_promo"].isin([False, 0])].iloc[0]
        margin_drop = no_p["margin_pct"] - with_p["margin_pct"]
        st.markdown(
            f"<div class='narrative'><b>Diagnostic.</b> Promo kéo volume "
            f"nhưng margin <b>−{margin_drop:.1f}pp</b> so với no-promo. "
            "Mỗi $1 promo doanh thu kèm $X margin bị đốt → cần ROI gate.</div>",
            unsafe_allow_html=True)

# E2 — Promo penetration heatmap by category × year
with ext2:
    pen = (op.groupby(["category", "order_year"])
           .agg(lines=("line_revenue", "size"),
                promoted=("has_promo", "sum"))
           .assign(pen_pct=lambda d: d["promoted"] / d["lines"] * 100)
           .reset_index())
    pivot = pen.pivot(index="category", columns="order_year", values="pen_pct")
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.astype(str),
        y=pivot.index.astype(str),
        colorscale=[[0, "#F5F6F0"], [0.5, AMBER], [1, RED]],
        colorbar=dict(thickness=10, outlinewidth=0, title="%"),
        hovertemplate="%{y} · %{x}<br>Promo penetration: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(title="Promo penetration · Category × Year")
    style(fig, height=280, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    if pivot.size and pivot.notna().any().any():
        latest_y = pivot.columns.max()
        col = pivot[latest_y].dropna()
        hottest = col.idxmax() if len(col) else "—"
        st.markdown(
            f"<div class='narrative'><b>Descriptive.</b> {latest_y}: "
            f"<b>{hottest}</b> đang bị promo nhiều nhất "
            f"({col.max():.1f}%). Soi xem có đáng đốt margin không.</div>",
            unsafe_allow_html=True)

# E3 — Promo ROI by category (revenue lift vs margin loss)
with ext3:
    promo_split = (op.groupby(["category", "has_promo"])
                   .agg(rev=("line_revenue", "sum"),
                        gp=("line_gross_profit", "sum"),
                        units=("quantity", "sum"))
                   .reset_index())
    pivot = promo_split.pivot(index="category", columns="has_promo",
                              values=["rev", "gp", "units"]).fillna(0)
    # margin pct with vs without
    rec = []
    for cat in pivot.index:
        try:
            rev_w = pivot.loc[cat, ("rev", True)] if ("rev", True) in pivot.columns else pivot.loc[cat, ("rev", 1)]
            rev_n = pivot.loc[cat, ("rev", False)] if ("rev", False) in pivot.columns else pivot.loc[cat, ("rev", 0)]
            gp_w = pivot.loc[cat, ("gp", True)] if ("gp", True) in pivot.columns else pivot.loc[cat, ("gp", 1)]
            gp_n = pivot.loc[cat, ("gp", False)] if ("gp", False) in pivot.columns else pivot.loc[cat, ("gp", 0)]
        except Exception:
            continue
        m_w = gp_w / rev_w * 100 if rev_w else 0
        m_n = gp_n / rev_n * 100 if rev_n else 0
        rec.append({"category": cat,
                    "margin_drop_pp": m_n - m_w,
                    "promo_share_pct": rev_w / max(rev_w + rev_n, 1) * 100,
                    "promo_revenue": rev_w})
    df_roi = pd.DataFrame(rec).sort_values("margin_drop_pp", ascending=False)
    if len(df_roi):
        fig = px.scatter(df_roi, x="promo_share_pct", y="margin_drop_pp",
                         size="promo_revenue", color="category",
                         color_discrete_sequence=CAT_PALETTE,
                         hover_name="category", size_max=40,
                         labels={"promo_share_pct": "Promo revenue share %",
                                 "margin_drop_pp": "Margin drop (pp)"})
        fig.add_hline(y=0, line_dash="dot", line_color=GREY)
        fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
        fig.update_layout(title="Promo ROI · margin drop vs promo share")
        style(fig, height=280)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        worst = df_roi.iloc[0]
        st.markdown(
            f"<div class='narrative'><b>Prescriptive.</b> <b>{worst['category']}</b>: "
            f"promo chiếm {worst['promo_share_pct']:.1f}% rev nhưng đốt "
            f"{worst['margin_drop_pp']:.1f}pp margin → ưu tiên cắt promo đại trà ở đây. "
            "Categories có margin_drop âm = promo healthy.</div>",
            unsafe_allow_html=True)

# =====================================================================
# Extra brainstorm row 2 — Cross-functional: Revenue × Traffic × Promo
# =====================================================================
ext4, ext5 = st.columns(2)

# E4 — Revenue + Sessions + Promo intensity over time
with ext4:
    # monthly: revenue from monthly_summary, sessions from wt, promo_pen from op
    rev_m = monthly_summary[["year_month", "revenue"]].copy()
    sess_m = wt.groupby("year_month")["sessions"].sum().reset_index()
    promo_m = (op.groupby("order_ym")
               .agg(lines=("has_promo", "size"),
                    promoted=("has_promo", "sum"))
               .assign(pen=lambda d: d["promoted"] / d["lines"] * 100)
               .reset_index().rename(columns={"order_ym": "year_month"}))
    df = (rev_m.merge(sess_m, on="year_month", how="inner")
          .merge(promo_m[["year_month", "pen"]], on="year_month", how="left"))
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.sort_values("date")
    df = df[df["year_month"].str[:4].astype(int).between(yr[0], yr[1])]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df["date"], y=df["revenue"], name="Revenue",
                             line=dict(color=LIME_DARK, width=2)),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=df["date"], y=df["sessions"], name="Sessions",
                             line=dict(color=DARK, width=1.5, dash="dot")),
                  secondary_y=True)
    fig.add_trace(go.Bar(x=df["date"], y=df["pen"], name="Promo %",
                         marker_color=AMBER, opacity=0.4),
                  secondary_y=True)
    fig.update_yaxes(title_text="Revenue", secondary_y=False)
    fig.update_yaxes(title_text="Sessions / Promo %", secondary_y=True)
    fig.update_layout(title="Revenue × Sessions × Promo intensity",
                      hovermode="x unified")
    style(fig, height=280)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    # correlations
    if len(df) > 6:
        c_rs = df["revenue"].corr(df["sessions"])
        c_rp = df["revenue"].corr(df["pen"])
        st.markdown(
            f"<div class='narrative'><b>Diagnostic.</b> Corr(Revenue, Sessions) = "
            f"<b>{c_rs:.2f}</b>; Corr(Revenue, Promo%) = <b>{c_rp:.2f}</b>. "
            "Nếu corr promo cao mà margin giảm → tăng trưởng \"vay\" từ margin.</div>",
            unsafe_allow_html=True)

# E5 — Channel CAC vs LTV (proxy: customers vs avg LTV)
with ext5:
    ch = (rfm[rfm["frequency"] > 0].groupby("acquisition_channel")
          .agg(customers=("customer_id", "count"),
               total_rev=("monetary", "sum"),
               avg_ltv=("monetary", "mean"))
          .reset_index())
    # CAC proxy: assume budget proportional to customer count → invert to acquisition cost per customer (placeholder)
    # Better: just plot avg_ltv vs customer count, size = total revenue, label channels
    fig = px.scatter(ch, x="customers", y="avg_ltv", size="total_rev",
                     color="acquisition_channel",
                     color_discrete_sequence=CAT_PALETTE,
                     hover_name="acquisition_channel", size_max=50,
                     labels={"customers": "Customers acquired",
                             "avg_ltv": "Avg LTV"})
    median_ltv = ch["avg_ltv"].median()
    fig.add_hline(y=median_ltv, line_dash="dot", line_color=GREY,
                  annotation_text=f"Median LTV = {fmt_money(median_ltv)}")
    fig.update_traces(marker=dict(line=dict(width=0.5, color=DARK), opacity=0.85))
    fig.update_layout(title="Acquisition channel · scale vs value")
    style(fig, height=280)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    above = ch[ch["avg_ltv"] > median_ltv]["acquisition_channel"].tolist()
    st.markdown(
        f"<div class='narrative'><b>Prescriptive.</b> Channels trên median LTV: "
        f"<b>{', '.join(above) or '—'}</b>. Đây là nhóm nên scale ngân sách. "
        "Channels dưới median: tối ưu CAC trước khi scale.</div>",
        unsafe_allow_html=True)

# =====================================================================
# Extra brainstorm row 3 — Campaign-family performance (always full data,
# ignores campaign filter so user can see all families to choose from)
# =====================================================================
st.markdown("---")
st.markdown("##### Campaign family · multi-year performance")

cf_orders = orders_promo[(orders_promo["order_year"].between(yr[0], yr[1]))
                         & (orders_promo["campaign_family"].notna())]

ext6, ext7 = st.columns(2)

# E6 — Campaign family · revenue + margin (multi-year aggregate)
with ext6:
    cf = (cf_orders.groupby("campaign_family")
          .agg(orders_n=("line_revenue", "size"),
               revenue=("line_revenue", "sum"),
               gp=("line_gross_profit", "sum"),
               years_active=("order_year", "nunique"))
          .assign(margin_pct=lambda d: d["gp"] / d["revenue"] * 100)
          .reset_index().sort_values("revenue", ascending=False))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    bar_colors = [RED if m < 0 else (AMBER if m < 5 else LIME_DARK)
                  for m in cf["margin_pct"]]
    fig.add_trace(go.Bar(x=cf["campaign_family"], y=cf["revenue"],
                         name="Revenue", marker_color=bar_colors,
                         text=[fmt_money(v) for v in cf["revenue"]],
                         textposition="outside"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=cf["campaign_family"], y=cf["margin_pct"],
                             name="Margin %", mode="lines+markers",
                             line=dict(color=DARK, width=2),
                             marker=dict(size=10)),
                  secondary_y=True)
    fig.add_hline(y=0, line_dash="dot", line_color=RED, secondary_y=True)
    fig.update_yaxes(title_text="Revenue", secondary_y=False)
    fig.update_yaxes(title_text="Margin %", secondary_y=True)
    fig.update_layout(title="Campaign family · revenue & margin (all years)",
                      hovermode="x unified")
    style(fig, height=300)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    worst = cf.loc[cf["margin_pct"].idxmin()]
    best = cf.loc[cf["margin_pct"].idxmax()]
    st.markdown(
        f"<div class='narrative'><b>Diagnostic + Prescriptive.</b> "
        f"<b>{worst['campaign_family']}</b> tệ nhất: margin "
        f"<b>{worst['margin_pct']:+.1f}%</b> trên {worst['orders_n']:,} orders "
        f"qua {worst['years_active']} năm — pattern lặp lại có hệ thống. "
        f"<b>{best['campaign_family']}</b> tốt nhất: {best['margin_pct']:+.1f}% margin. "
        "Cắt hoặc redesign các family margin âm trước khi tối ưu vận hành khác.</div>",
        unsafe_allow_html=True)

# E7 — Campaign family × year heatmap (revenue) — see consistency over time
with ext7:
    cy = (cf_orders.groupby(["campaign_family", "order_year"])
          .agg(revenue=("line_revenue", "sum"),
               gp=("line_gross_profit", "sum"))
          .assign(margin_pct=lambda d: d["gp"] / d["revenue"] * 100)
          .reset_index())
    pivot = cy.pivot(index="campaign_family", columns="order_year",
                     values="margin_pct")
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.astype(str),
        y=pivot.index.astype(str),
        colorscale=[[0, RED], [0.3, AMBER], [0.5, "#F5F6F0"], [1, LIME_DARK]],
        zmid=0,
        colorbar=dict(thickness=10, outlinewidth=0, title="Margin %"),
        hovertemplate="<b>%{y}</b> · %{x}<br>Margin: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(title="Campaign family × year · margin % consistency")
    style(fig, height=300, show_legend=False)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    # Detect pattern: consistently bad campaigns
    consistently_bad = []
    for fam in pivot.index:
        row = pivot.loc[fam].dropna()
        if len(row) >= 3 and (row < 0).sum() / len(row) >= 0.6:
            consistently_bad.append(fam)
    st.markdown(
        f"<div class='narrative'><b>Predictive.</b> "
        f"Family có margin âm ≥ 60% số năm: "
        f"<b>{', '.join(consistently_bad) or 'không có'}</b>. "
        "Đây là pattern lặp lại đa năm — không phải biến cố ngẫu nhiên, "
        "có thể *predict* margin âm cho năm tới nếu giữ format cũ.</div>",
        unsafe_allow_html=True)
