"""VinDatathon 2026 — EDA Dashboards (Streamlit, Power BI-style).

Run:
    streamlit run streamlit_app/app.py
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from theme import inject_css

st.set_page_config(
    page_title="VinDatathon 2026 — the gridbreakers",
    page_icon="🟩",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

st.markdown(
    "## <span class='accent-tag'>DATATHON 2026</span> the gridbreakers",
    unsafe_allow_html=True,
)
st.caption("Synthetic Vietnamese fashion e-commerce · 2012–2022 · 2.96M records")

st.write("")
col1, col2, col3, col4, col5 = st.columns(5)
cards = [
    ("📈 D1 Revenue", "Doanh thu, gross margin, seasonality, category Pareto.", "pages/1_📈_D1_Revenue.py"),
    ("👥 D2 Customer", "RFM, cohort retention, customer lifetime value.", "pages/2_👥_D2_Customer.py"),
    ("📦 D3 Product", "Product performance, returns, inventory health.", "pages/3_📦_D3_Product.py"),
    ("📣 D4 Marketing", "Web traffic, channel effectiveness, conversion.", "pages/4_📣_D4_Marketing.py"),
    ("🧬 Data Model", "Schema graph, table joins, modeling playground.", "pages/5_🧬_Data_Model.py"),
]
for col, (title, desc, page) in zip([col1, col2, col3, col4, col5], cards):
    with col:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(desc)
            try:
                st.page_link(page, label="Open →")
            except Exception:
                st.write(page)

st.markdown("---")
with st.expander("ℹ️ Tương tác như Power BI?"):
    st.markdown("""
- **Hover/Zoom/Pan** trên mọi chart (Plotly built-in).
- **Click legend** để toggle series.
- **Sidebar dropdown filter** (year, region/category/source) áp lên tất cả charts của trang đang xem.
- **Cross-filter click bar → filter chart khác**: chưa có (cần custom callback). Streamlit re-run page khi filter thay đổi nên dùng filter sidebar thay thế.
- **Data Model page** cho phép xem schema graph + chạy join thử giữa 2 bảng.
""")
