"""Cached data loaders for the Streamlit app.

All loaders are decorated with @st.cache_data so they're loaded once per session.
Reads from code-data/tableau_data/ (prepared CSVs) with parquet cache for facts.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path.cwd()
DATA_DIR = ROOT / "assets" / "tableau_data"
CACHE_DIR = ROOT / ".cache" / "tableau_parquet"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

LARGE = {"fact_orders_enriched", "fact_shipments_enriched", "dim_customers_rfm"}
DATE_COLS = {
    "fact_orders_enriched": ["order_date"],
    "fact_returns_enriched": ["return_date", "order_date"],
    "fact_shipments_enriched": ["ship_date", "delivery_date", "order_date"],
    "fact_sales_daily": ["Date"],
    "fact_inventory": ["snapshot_date"],
    "fact_web_traffic": ["traffic_date"],
}


def available_parse_dates(name: str, columns: tuple[str, ...] | None = None) -> list[str] | None:
    parse_dates = DATE_COLS.get(name)
    if not parse_dates:
        return None
    if columns is None:
        return parse_dates
    selected = set(columns)
    dates = [col for col in parse_dates if col in selected]
    return dates or None


@st.cache_data(show_spinner="Loading data…")
def load(name: str, columns: tuple[str, ...] | None = None) -> pd.DataFrame:
    csv = DATA_DIR / f"{name}.csv"
    parse_dates = available_parse_dates(name, columns)
    if name in LARGE:
        pq = CACHE_DIR / f"{name}.parquet"
        if not pq.exists():
            df = pd.read_csv(csv, parse_dates=DATE_COLS.get(name), low_memory=False)
            df.to_parquet(pq, index=False)
        df = pd.read_parquet(pq, columns=list(columns) if columns else None)
    else:
        df = pd.read_csv(csv, parse_dates=parse_dates,
                         usecols=list(columns) if columns else None)
    return df


def available_tables() -> list[str]:
    return sorted(p.stem for p in DATA_DIR.glob("*.csv"))


# ---- Schema metadata for Data Model page ----
SCHEMA = {
    "dim_customers_rfm": {
        "kind": "dimension", "pk": "customer_id",
        "desc": "Customers + RFM scores & segment",
        "fks": [("zip", "dim_geography", "zip")],
    },
    "dim_products": {
        "kind": "dimension", "pk": "product_id",
        "desc": "Products with margin/rating/return stats",
        "fks": [],
    },
    "dim_geography": {
        "kind": "dimension", "pk": "zip",
        "desc": "Zip → city → region",
        "fks": [],
    },
    "dim_promotions": {
        "kind": "dimension", "pk": "promo_id",
        "desc": "Promotion catalog",
        "fks": [],
    },
    "fact_orders_enriched": {
        "kind": "fact", "pk": "(order_id, product_id)",
        "desc": "Order line items joined to product/geography",
        "fks": [
            ("customer_id", "dim_customers_rfm", "customer_id"),
            ("product_id", "dim_products", "product_id"),
            ("zip", "dim_geography", "zip"),
            ("promo_id", "dim_promotions", "promo_id"),
        ],
    },
    "fact_returns_enriched": {
        "kind": "fact", "pk": "(return_id)",
        "desc": "Returns + reason + days_to_return",
        "fks": [
            ("order_id", "fact_orders_enriched", "order_id"),
            ("product_id", "dim_products", "product_id"),
        ],
    },
    "fact_shipments_enriched": {
        "kind": "fact", "pk": "order_id",
        "desc": "Shipments with delivery_days/lead_time",
        "fks": [("order_id", "fact_orders_enriched", "order_id")],
    },
    "fact_sales_daily": {
        "kind": "fact", "pk": "Date",
        "desc": "Daily revenue + COGS + MA + YoY",
        "fks": [],
    },
    "fact_inventory": {
        "kind": "fact", "pk": "(snapshot_date, product_id)",
        "desc": "Monthly inventory + health labels",
        "fks": [("product_id", "dim_products", "product_id")],
    },
    "fact_web_traffic": {
        "kind": "fact", "pk": "(date, traffic_source)",
        "desc": "Daily web traffic by source",
        "fks": [],
    },
    "agg_monthly_summary": {
        "kind": "agg", "pk": "year_month",
        "desc": "Monthly KPIs (rev, gp, AOV, MoM)",
        "fks": [],
    },
    "agg_cohort_retention": {
        "kind": "agg", "pk": "(cohort_month, period_number)",
        "desc": "Cohort retention matrix",
        "fks": [],
    },
    "agg_reviews_summary": {
        "kind": "agg", "pk": "(year_month, category)",
        "desc": "Monthly review aggregates",
        "fks": [],
    },
}
