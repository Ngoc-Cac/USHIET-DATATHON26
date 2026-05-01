"""
Unified data loading with correct dtypes and parsing.
All notebooks should import from here to ensure consistent data types.

Usage:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.getcwd()), 'src'))
    from data_loader import load_products, load_orders, ...
"""

import pandas as pd
from pathlib import Path

# Resolve DATA_DIR relative to this file's location (src/ → project root → data/)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ---------------------------------------------------------------------------
# Dimension tables
# ---------------------------------------------------------------------------

def load_products() -> pd.DataFrame:
    """Load products.csv (2,412 rows).
    Columns: product_id, product_name, category, segment, size, color, price, cogs
    """
    return pd.read_csv(DATA_DIR / "products.csv")


def load_customers() -> pd.DataFrame:
    """Load customers.csv (121,930 rows).
    Columns: customer_id, zip, city, signup_date, gender, age_group, acquisition_channel
    """
    df = pd.read_csv(DATA_DIR / "customers.csv", parse_dates=["signup_date"])
    return df


def load_geography() -> pd.DataFrame:
    """Load geography.csv (39,948 rows).
    Columns: zip, city, region, district
    """
    return pd.read_csv(DATA_DIR / "geography.csv")


def load_promotions() -> pd.DataFrame:
    """Load promotions.csv (50 rows).
    Columns: promo_id, promo_name, promo_type, discount_value,
             start_date, end_date, applicable_category, promo_channel,
             stackable_flag, min_order_value
    """
    df = pd.read_csv(
        DATA_DIR / "promotions.csv",
        parse_dates=["start_date", "end_date"],
    )
    return df


# ---------------------------------------------------------------------------
# Fact / transaction tables
# ---------------------------------------------------------------------------

def load_orders() -> pd.DataFrame:
    """Load orders.csv (646,945 rows).
    Columns: order_id, order_date, customer_id, zip,
             order_status, payment_method, device_type, order_source
    """
    df = pd.read_csv(DATA_DIR / "orders.csv", parse_dates=["order_date"])
    return df


def load_order_items() -> pd.DataFrame:
    """Load order_items.csv (714,669 rows).
    Columns: order_id, product_id, quantity, unit_price,
             discount_amount, promo_id, promo_id_2
    """
    return pd.read_csv(DATA_DIR / "order_items.csv")


def load_payments() -> pd.DataFrame:
    """Load payments.csv (646,945 rows).
    Columns: order_id, payment_method, payment_value, installments
    """
    return pd.read_csv(DATA_DIR / "payments.csv")


def load_shipments() -> pd.DataFrame:
    """Load shipments.csv (566,067 rows).
    Columns: order_id, ship_date, delivery_date, shipping_fee
    """
    df = pd.read_csv(
        DATA_DIR / "shipments.csv",
        parse_dates=["ship_date", "delivery_date"],
    )
    return df


def load_returns() -> pd.DataFrame:
    """Load returns.csv (39,939 rows).
    Columns: return_id, order_id, product_id, return_date,
             return_reason, return_quantity, refund_amount
    """
    df = pd.read_csv(DATA_DIR / "returns.csv", parse_dates=["return_date"])
    return df


def load_reviews() -> pd.DataFrame:
    """Load reviews.csv (113,551 rows).
    Columns: review_id, order_id, product_id, customer_id,
             review_date, rating, review_title
    """
    df = pd.read_csv(DATA_DIR / "reviews.csv", parse_dates=["review_date"])
    return df


# ---------------------------------------------------------------------------
# Aggregated / supporting tables
# ---------------------------------------------------------------------------

def load_sales() -> pd.DataFrame:
    """Load sales.csv (3,833 rows) — daily aggregated revenue.
    Columns: Date, Revenue, COGS
    Train period: 2012-07-04 → 2022-12-31
    """
    df = pd.read_csv(DATA_DIR / "sales.csv", parse_dates=["Date"])
    return df


def load_sample_submission() -> pd.DataFrame:
    """Load sample_submission.csv (548 rows).
    Columns: Date, Revenue, COGS
    Test period: 2023-01-01 → 2024-07-01
    """
    df = pd.read_csv(DATA_DIR / "sample_submission.csv", parse_dates=["Date"])
    return df


def load_inventory() -> pd.DataFrame:
    """Load inventory.csv (60,247 rows).
    Columns: snapshot_date, product_id, stock_on_hand, units_received,
             units_sold, stockout_days, days_of_supply, fill_rate,
             stockout_flag, overstock_flag, reorder_flag, sell_through_rate,
             product_name, category, segment, year, month
    """
    df = pd.read_csv(DATA_DIR / "inventory.csv", parse_dates=["snapshot_date"])
    return df


def load_web_traffic() -> pd.DataFrame:
    """Load web_traffic.csv (3,652 rows).
    Columns: date, sessions, unique_visitors, page_views,
             bounce_rate, avg_session_duration_sec, traffic_source
    """
    df = pd.read_csv(DATA_DIR / "web_traffic.csv", parse_dates=["date"])
    return df


# ---------------------------------------------------------------------------
# Convenience: load everything
# ---------------------------------------------------------------------------

ALL_LOADERS = {
    "products": load_products,
    "customers": load_customers,
    "geography": load_geography,
    "promotions": load_promotions,
    "orders": load_orders,
    "order_items": load_order_items,
    "payments": load_payments,
    "shipments": load_shipments,
    "returns": load_returns,
    "reviews": load_reviews,
    "sales": load_sales,
    "sample_submission": load_sample_submission,
    "inventory": load_inventory,
    "web_traffic": load_web_traffic,
}


def load_all() -> dict[str, pd.DataFrame]:
    """Load all 14 tables into a dict keyed by table name."""
    return {name: loader() for name, loader in ALL_LOADERS.items()}
