"""Lazy loader for prepared Tableau-ready CSVs.

Caches large facts as parquet on first read for ~10x faster subsequent loads.
"""
from __future__ import annotations

from pathlib import Path
from functools import lru_cache
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "code-data" / "tableau_data"
CACHE_DIR = ROOT / ".cache" / "tableau_parquet"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Files large enough to benefit from parquet caching
LARGE_FILES = {"fact_orders_enriched", "fact_shipments_enriched", "dim_customers_rfm"}

DATE_COLS = {
    "fact_orders_enriched": ["order_date"],
    "fact_returns_enriched": ["return_date", "order_date"],
    "fact_shipments_enriched": ["ship_date", "delivery_date", "order_date"],
    "fact_sales_daily": ["Date"],
    "fact_inventory": ["snapshot_date"],
    "fact_web_traffic": ["date"],
}


@lru_cache(maxsize=None)
def load(name: str, columns: tuple[str, ...] | None = None) -> pd.DataFrame:
    """Load a prepared table by name (e.g. 'agg_monthly_summary').

    For large facts, builds a parquet cache on first call.
    """
    csv_path = DATA_DIR / f"{name}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    parse_dates = DATE_COLS.get(name)

    if name in LARGE_FILES:
        pq_path = CACHE_DIR / f"{name}.parquet"
        if not pq_path.exists():
            df = pd.read_csv(csv_path, parse_dates=parse_dates)
            df.to_parquet(pq_path, index=False)
        df = pd.read_parquet(pq_path, columns=list(columns) if columns else None)
    else:
        df = pd.read_csv(csv_path, parse_dates=parse_dates,
                         usecols=list(columns) if columns else None)
    return df


def available() -> list[str]:
    return sorted(p.stem for p in DATA_DIR.glob("*.csv"))
