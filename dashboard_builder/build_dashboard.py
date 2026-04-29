"""Entrypoint: build all dashboards as static HTML pages.

Usage:
    python -m dashboard_builder.build_dashboard
"""
from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from plotly.offline import get_plotlyjs

from .insights import d1_revenue, d2_customer

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"
OUT_DIR = ROOT / "dashboard"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
    plotly_js = get_plotlyjs()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    # Dashboard D1
    print("[D1] Building Revenue & Profitability...")
    d1_data = d1_revenue.build()
    d1_html = env.get_template("dashboard.html").render(
        page_title=f"{d1_data['title']} — VinDatathon 2026",
        page_subtitle=f"{d1_data['title']} · {d1_data['subtitle']}",
        active_nav="d1",
        css=css, plotly_js=plotly_js, data=d1_data,
    )
    (OUT_DIR / "d1_revenue.html").write_text(d1_html, encoding="utf-8")
    print(f"  -> {OUT_DIR / 'd1_revenue.html'}")

    # Dashboard D2
    print("[D2] Building Customer Segmentation...")
    d2_data = d2_customer.build()
    d2_html = env.get_template("dashboard.html").render(
        page_title=f"{d2_data['title']} — VinDatathon 2026",
        page_subtitle=f"{d2_data['title']} · {d2_data['subtitle']}",
        active_nav="d2",
        css=css, plotly_js=plotly_js, data=d2_data,
    )
    (OUT_DIR / "d2_customer.html").write_text(d2_html, encoding="utf-8")
    print(f"  -> {OUT_DIR / 'd2_customer.html'}")

    # Index
    dashboards = [
        {"tag": "D1", "title": "Revenue & Profitability",
         "desc": "Doanh thu, gross margin, seasonality, category Pareto.",
         "href": "d1_revenue.html", "live": True},
        {"tag": "D2", "title": "Customer Segmentation",
         "desc": "RFM, cohort retention, customer lifetime value.",
         "href": "d2_customer.html", "live": True},
        {"tag": "D4", "title": "Marketing & Channel",
         "desc": "Traffic source, conversion, CAC vs LTV.",
         "href": "#", "live": False},
    ]
    index_html = env.get_template("index.html").render(
        page_title="VinDatathon 2026 — EDA Dashboards",
        page_subtitle="EDA Dashboards · Synthetic fashion e-commerce · 2012–2022 · 2.96M records",
        active_nav="home",
        css=css, dashboards=dashboards,
    )
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  -> {OUT_DIR / 'index.html'}")
    print("Done.")


if __name__ == "__main__":
    main()
