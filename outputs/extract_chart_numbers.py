"""Extract real numbers from data, replicating exact Streamlit chart logic.
Run: python outputs/extract_chart_numbers.py > outputs/chart_numbers.txt
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "streamlit_app"))

import numpy as np
import pandas as pd
from data import load


def section(title):
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


# =====================================================================
# D1 · Revenue
# =====================================================================
section("D1 · Revenue & Profitability")

monthly = load("agg_monthly_summary")
monthly["year"] = monthly["year_month"].str[:4].astype(int)
monthly["date"] = pd.to_datetime(monthly["year_month"] + "-01")
monthly = monthly.sort_values("date")

print(f"\n[Period] {monthly['year_month'].min()} → {monthly['year_month'].max()}")
print(f"[Total Revenue] {monthly['revenue'].sum():,.0f}")
print(f"[Total GP]      {monthly['gross_profit'].sum():,.0f}")
print(f"[Avg Margin %]  {(monthly['gross_profit'].sum()/monthly['revenue'].sum()*100):.2f}%")

# Peak / trough month
print(f"\n[Peak month]   {monthly.loc[monthly['revenue'].idxmax(), 'year_month']} "
      f"= {monthly['revenue'].max():,.0f}")
print(f"[Trough month] {monthly.loc[monthly['revenue'].idxmin(), 'year_month']} "
      f"= {monthly['revenue'].min():,.0f}")

# Long-run shape
y_rev = monthly.groupby("year")["revenue"].sum()
print("\n[Yearly revenue]")
for y, v in y_rev.items():
    print(f"  {y}: {v:,.0f}")
peak_year = y_rev.idxmax()
last_year = y_rev.index.max()
print(f"\n[Peak year] {peak_year}: {y_rev.max():,.0f}")
print(f"[Last year] {last_year}: {y_rev.iloc[-1]:,.0f} "
      f"(vs peak: {(y_rev.iloc[-1]/y_rev.max()-1)*100:+.1f}%)")

# Margin vs Discount correlation (uses orders for discount penetration)
orders = load("fact_orders_enriched", columns=("order_ym", "has_promo",
                                                "line_revenue", "line_gross_profit",
                                                "line_cost", "category", "order_year",
                                                "quantity", "product_id", "size"))
promo = (orders.groupby("order_ym")
         .agg(lines=("has_promo", "size"), promoted=("has_promo", "sum"))
         .assign(discount_pen=lambda d: d["promoted"]/d["lines"]*100)
         .reset_index().rename(columns={"order_ym": "year_month"}))
df = monthly.merge(promo[["year_month", "discount_pen"]], on="year_month", how="left")
corr_md = df["gross_margin_pct"].corr(df["discount_pen"])
print(f"\n[Margin% ↔ Discount penetration%] corr = {corr_md:.3f}  "
      f"(N={df['discount_pen'].notna().sum()})")

# Pareto category
cat = (orders.groupby("category")
       .agg(revenue=("line_revenue", "sum"),
            gp=("line_gross_profit", "sum"))
       .assign(margin_pct=lambda d: d["gp"]/d["revenue"]*100)
       .sort_values("revenue", ascending=False).reset_index())
cat["share"] = cat["revenue"] / cat["revenue"].sum() * 100
cat["cum"] = cat["share"].cumsum()
print("\n[Category Pareto]")
print(cat[["category", "revenue", "share", "cum", "margin_pct"]].to_string(index=False))
print(f"\n[Top-3 share] {cat.head(3)['share'].sum():.1f}%")

# Orders × AOV decomposition (last 12 vs prev 12 months)
if len(monthly) >= 24:
    last12 = monthly.tail(12)
    prev12 = monthly.iloc[-24:-12]
    do = last12["total_orders"].sum() / prev12["total_orders"].sum() - 1
    da = last12["aov"].mean() / prev12["aov"].mean() - 1
    print(f"\n[Last 12 vs Prev 12]")
    print(f"  Orders YoY: {do*100:+.2f}%")
    print(f"  AOV YoY:    {da*100:+.2f}%")
    print(f"  Driver: {'Orders (volume)' if abs(do) > abs(da) else 'AOV (price/mix)'}")

# Forecast band
season = monthly.groupby(monthly["date"].dt.month)["revenue"].agg(["mean", "std"])
print(f"\n[Seasonal mean by month]")
print(season.round(0).to_string())
next_3_mean = season.head(3)["mean"].sum()  # placeholder; depends on last_date
last_month = monthly["date"].max().month
next_months = [(last_month + i - 1) % 12 + 1 for i in range(1, 7)]
fc = season.loc[next_months]
print(f"\n[Forecast next 6 months · mean sum] {fc['mean'].sum():,.0f}")
print(f"[Forecast band ±1.5σ width] {(2*1.5*fc['std'].fillna(0)).sum():,.0f}")

# YoY bridge
years = sorted(orders["order_year"].unique())
if len(years) >= 2:
    cur_y, prv_y = years[-1], years[-2]
    cur = orders[orders["order_year"] == cur_y].groupby("category")["line_revenue"].sum()
    prv = orders[orders["order_year"] == prv_y].groupby("category")["line_revenue"].sum()
    bridge = (pd.concat([prv.rename("prev"), cur.rename("curr")], axis=1)
              .fillna(0).assign(delta=lambda d: d["curr"] - d["prev"])
              .sort_values("delta"))
    print(f"\n[YoY bridge {prv_y}→{cur_y}]")
    print(bridge.to_string())


# =====================================================================
# D2 · Customer
# =====================================================================
section("D2 · Customer")

rfm = load("dim_customers_rfm", columns=(
    "customer_id", "frequency", "monetary", "rfm_segment",
    "acquisition_channel", "recency_days", "region", "age_group", "gender"))
cohort = load("agg_cohort_retention")

active = rfm[rfm["frequency"] > 0]
print(f"\n[Total customers] {len(rfm):,}")
print(f"[Active customers (≥1 order)] {len(active):,}")

# RFM segment distribution
seg = (active.groupby("rfm_segment")
       .agg(customers=("customer_id", "count"),
            revenue=("monetary", "sum"),
            avg_ltv=("monetary", "mean"))
       .reset_index().sort_values("customers", ascending=False))
seg["cust_share"] = seg["customers"] / seg["customers"].sum() * 100
seg["rev_share"] = seg["revenue"] / seg["revenue"].sum() * 100
print("\n[RFM segment]")
print(seg.to_string(index=False))

# Cohort retention M1-M3
df = cohort[cohort["period_number"] <= 24].copy()
pivot = df.pivot(index="cohort_month", columns="period_number", values="retention_rate")
m_avg = pivot.mean(axis=0)
print(f"\n[Avg cohort retention by period (months after first order)]")
for m in [0, 1, 2, 3, 6, 12, 24]:
    if m in m_avg.index:
        print(f"  M{m:02d}: {m_avg[m]:.2f}%")

# Customer Journey Funnel
f1 = (rfm["frequency"] >= 1).sum()
f2 = (rfm["frequency"] >= 2).sum()
f3 = (rfm["frequency"] >= 3).sum()
f5 = (rfm["frequency"] >= 5).sum()
print(f"\n[Customer Journey Funnel]")
print(f"  ≥1 purchase: {f1:,}  (100.0%)")
print(f"  ≥2 purchase: {f2:,}  ({f2/f1*100:.1f}% of base)")
print(f"  ≥3 purchase: {f3:,}  ({f3/f1*100:.1f}% of base)")
print(f"  ≥5 (loyal):  {f5:,}  ({f5/f1*100:.1f}% of base)")
print(f"\n[Drop-off 1st→2nd] {(1-f2/f1)*100:.1f}%")
print(f"[Drop-off 2nd→3rd] {(1-f3/f2)*100:.1f}%")
print(f"[Drop-off 3rd→5th] {(1-f5/f3)*100:.1f}%")

# Channel quality
ch = (rfm.groupby("acquisition_channel")
      .agg(total=("customer_id", "count"),
           repeat=("frequency", lambda s: (s >= 2).sum()),
           loyal=("frequency", lambda s: (s >= 5).sum()),
           avg_ltv=("monetary", "mean"))
      .assign(repeat_rate=lambda d: d["repeat"] / d["total"] * 100,
              loyal_rate=lambda d: d["loyal"] / d["total"] * 100)
      .reset_index().sort_values("repeat_rate", ascending=False))
print(f"\n[Channel quality]")
print(ch.to_string(index=False))

# Age × Gender LTV
ag = (active.dropna(subset=["age_group", "gender"])
      .groupby(["age_group", "gender"])
      .agg(avg_ltv=("monetary", "mean"),
           customers=("customer_id", "count"))
      .reset_index())
print(f"\n[Avg LTV by age × gender]")
print(ag.to_string(index=False))


# =====================================================================
# D3 · Product
# =====================================================================
section("D3 · Product")

products = load("dim_products")
returns = load("fact_returns_enriched", columns=(
    "category", "return_reason", "refund_amount", "return_quantity",
    "return_year", "size", "product_id"))
inv = load("fact_inventory", columns=(
    "category", "inventory_health", "inventory_value_cost",
    "stockout_flag", "overstock_flag", "year",
    "stockout_days", "units_sold", "product_price", "product_id"))

print(f"\n[SKU count] {len(products):,}")
print(f"[Total returned units] {returns['return_quantity'].sum():,}")

# Top SKU revenue gap
prod_rev = orders.groupby("product_id")["line_revenue"].sum().sort_values(ascending=False)
print(f"\n[Top SKU revenue]")
print(f"  #1:  {prod_rev.iloc[0]:,.0f}")
print(f"  #5:  {prod_rev.iloc[4]:,.0f}")
print(f"  #15: {prod_rev.iloc[14]:,.0f}")
print(f"  Ratio #1/#15: {prod_rev.iloc[0]/prod_rev.iloc[14]:.1f}x")

# Pareto SKU: % SKU = 80% revenue
pr = prod_rev.reset_index()
pr["cum_pct"] = pr["line_revenue"].cumsum() / pr["line_revenue"].sum() * 100
pr["sku_pct"] = (np.arange(len(pr)) + 1) / len(pr) * 100
sku_at_80 = pr.loc[pr["cum_pct"] >= 80, "sku_pct"].min() if (pr["cum_pct"] >= 80).any() else 100
print(f"\n[Pareto] {sku_at_80:.1f}% SKU đầu tạo 80% revenue")
print(f"[Top 20% SKU contribute] {pr.loc[pr['sku_pct'] <= 20, 'line_revenue'].sum() / pr['line_revenue'].sum() * 100:.1f}% revenue")

# Return reasons
rs = returns.groupby("return_reason")["return_quantity"].sum().sort_values(ascending=False)
total_r = rs.sum()
print(f"\n[Return reasons (units)]")
for reason, qty in rs.items():
    print(f"  {reason}: {qty:,} ({qty/total_r*100:.1f}%)")

# Return rate by category × size
sold = (orders.groupby(["category", "size"])["quantity"].sum()
        .rename("sold").reset_index())
ret = (returns.groupby(["category", "size"])["return_quantity"].sum()
       .rename("returned").reset_index())
rs2 = sold.merge(ret, on=["category", "size"], how="left").fillna(0)
rs2["return_rate"] = rs2["returned"] / rs2["sold"].replace(0, np.nan) * 100
print(f"\n[Return rate · category × size]")
print(rs2.sort_values("return_rate", ascending=False).head(10).to_string(index=False))
print(f"\n[Min] {rs2['return_rate'].min():.2f}%  [Max] {rs2['return_rate'].max():.2f}%")

# Rating → return risk
prods = products[["product_id", "avg_rating", "total_return_qty",
                  "review_count", "category"]].copy()
sold_p = orders.groupby("product_id")["quantity"].sum().rename("sold")
prods = prods.merge(sold_p, on="product_id", how="left").fillna({"sold": 0})
prods = prods[(prods["sold"] > 0) & prods["avg_rating"].notna()]
prods["return_rate"] = prods["total_return_qty"] / prods["sold"] * 100
prods["rating_bin"] = pd.cut(prods["avg_rating"],
                              bins=[0, 3.0, 3.5, 4.0, 4.5, 5.0],
                              labels=["≤3.0", "3.0–3.5", "3.5–4.0", "4.0–4.5", "4.5–5.0"])
binned = (prods.groupby("rating_bin", observed=True)
          .agg(avg_return_rate=("return_rate", "mean"),
               skus=("product_id", "count"),
               avg_reviews=("review_count", "mean"))
          .reset_index())
print(f"\n[Rating bin → return rate]")
print(binned.to_string(index=False))

# Inventory health
ih = inv["inventory_health"].value_counts()
total_snap = ih.sum()
print(f"\n[Inventory health snapshots]")
for k, v in ih.items():
    print(f"  {k}: {v:,} ({v/total_snap*100:.1f}%)")

# Stockout impact
iv = (inv.groupby("product_id")
      .agg(stockout_days=("stockout_days", "sum"),
           units_sold=("units_sold", "sum"),
           price=("product_price", "mean"))
      .reset_index())
iv = iv[(iv["units_sold"] > 0) & (iv["stockout_days"] > 0)]
iv["lost_rev_proxy"] = (iv["units_sold"] / 365.0) * iv["stockout_days"] * iv["price"]
top80 = iv.nlargest(80, "lost_rev_proxy")
print(f"\n[Stockout lost-rev proxy · top 80 SKU] {top80['lost_rev_proxy'].sum():,.0f}")
print(f"[Stockout lost-rev proxy · all SKU]    {iv['lost_rev_proxy'].sum():,.0f}")


# =====================================================================
# D4 · Marketing
# =====================================================================
section("D4 · Marketing")

wt = load("fact_web_traffic")
print(f"\n[Total sessions] {wt['sessions'].sum():,}")
print(f"[Sources] {sorted(wt['traffic_source'].unique())}")

# Promo with vs without
op = orders.copy()
grp = op.groupby("has_promo").agg(
    revenue=("line_revenue", "sum"),
    gp=("line_gross_profit", "sum"),
    orders_n=("line_revenue", "size"),
    units=("quantity", "sum"),
).reset_index()
grp["margin_pct"] = grp["gp"] / grp["revenue"] * 100
grp["aov"] = grp["revenue"] / grp["orders_n"]
print(f"\n[Promo vs No-promo]")
print(grp.to_string(index=False))
if len(grp) == 2:
    w = grp[grp["has_promo"] == 1].iloc[0]
    n = grp[grp["has_promo"] == 0].iloc[0]
    print(f"\n[Margin gap] No-promo {n['margin_pct']:.2f}% vs With-promo {w['margin_pct']:.2f}% "
          f"= {n['margin_pct'] - w['margin_pct']:.2f}pp drop")
    print(f"[Revenue share with promo] {w['revenue']/(w['revenue']+n['revenue'])*100:.1f}%")

# Promo penetration heatmap
pen = (op.groupby(["category", "order_year"])
       .agg(lines=("line_revenue", "size"),
            promoted=("has_promo", "sum"))
       .assign(pen_pct=lambda d: d["promoted"] / d["lines"] * 100)
       .reset_index())
pivot = pen.pivot(index="category", columns="order_year", values="pen_pct")
latest_y = pivot.columns.max()
print(f"\n[Promo penetration · latest year {latest_y}]")
print(pivot[latest_y].sort_values(ascending=False).to_string())

# Promo ROI by category
ps = (op.groupby(["category", "has_promo"])
      .agg(rev=("line_revenue", "sum"),
           gp=("line_gross_profit", "sum"))
      .reset_index())
piv = ps.pivot(index="category", columns="has_promo", values=["rev", "gp"]).fillna(0)
recs = []
for c in piv.index:
    rw = piv.loc[c, ("rev", 1)]
    rn = piv.loc[c, ("rev", 0)]
    gw = piv.loc[c, ("gp", 1)]
    gn = piv.loc[c, ("gp", 0)]
    mw = gw/rw*100 if rw else 0
    mn = gn/rn*100 if rn else 0
    recs.append({
        "category": c,
        "margin_with_promo": mw,
        "margin_no_promo": mn,
        "drop_pp": mn - mw,
        "promo_share_pct": rw/(rw+rn)*100 if (rw+rn) else 0,
    })
df_roi = pd.DataFrame(recs).sort_values("drop_pp", ascending=False)
print(f"\n[Promo ROI · margin drop pp by category]")
print(df_roi.to_string(index=False))

# Cross-functional correlation
rev_m = monthly[["year_month", "revenue"]].copy()
sess_m = wt.groupby("year_month")["sessions"].sum().reset_index()
promo_m = (op.groupby("order_ym")
           .agg(lines=("has_promo", "size"),
                promoted=("has_promo", "sum"))
           .assign(pen=lambda d: d["promoted"] / d["lines"] * 100)
           .reset_index().rename(columns={"order_ym": "year_month"}))
xf = (rev_m.merge(sess_m, on="year_month", how="inner")
      .merge(promo_m[["year_month", "pen"]], on="year_month", how="left"))
print(f"\n[Cross-functional correlation · N={len(xf)}]")
print(f"  Corr(Revenue, Sessions): {xf['revenue'].corr(xf['sessions']):.3f}")
print(f"  Corr(Revenue, Promo%):   {xf['revenue'].corr(xf['pen']):.3f}")
print(f"  Corr(Sessions, Promo%):  {xf['sessions'].corr(xf['pen']):.3f}")

# Channel scale vs LTV
ch2 = (rfm[rfm["frequency"] > 0].groupby("acquisition_channel")
       .agg(customers=("customer_id", "count"),
            total_rev=("monetary", "sum"),
            avg_ltv=("monetary", "mean"))
       .reset_index())
median_ltv = ch2["avg_ltv"].median()
print(f"\n[Channel scale vs LTV · median LTV = {median_ltv:,.0f}]")
print(ch2.sort_values("avg_ltv", ascending=False).to_string(index=False))
above = ch2[ch2["avg_ltv"] > median_ltv]["acquisition_channel"].tolist()
below = ch2[ch2["avg_ltv"] <= median_ltv]["acquisition_channel"].tolist()
print(f"\n[Above median] {above}")
print(f"[At/below median] {below}")
