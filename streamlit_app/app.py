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
    """
    <div class="home-hero">
      <div>
        <div class="home-hero-title">
          <span class="home-hero-main">DATATHON <span class="home-year-chip">2026</span></span>
          <span class="home-hero-sub">the gridbreakers</span>
        </div>
        <div class="home-tagline">Breaking Business Boundaries</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="team-shell">
      <div class="team-eyebrow">Team Introduction</div>
      <div class="team-title">USHIET</div>
      <div class="team-copy">
        We are a 4-member team focused on turning data into business actions.
        You can fill in the final introduction and positioning text here later.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
members = [
    ("Member 01", "Role / expertise placeholder", "Fill in name, role, and what this member contributed."),
    ("Member 02", "Role / expertise placeholder", "Fill in name, role, and what this member contributed."),
    ("Member 03", "Role / expertise placeholder", "Fill in name, role, and what this member contributed."),
    ("Member 04", "Role / expertise placeholder", "Fill in name, role, and what this member contributed."),
]
for col, (name, role, note) in zip([m1, m2, m3, m4], members):
    with col:
        st.markdown(
            f"""
            <div class="member-card">
              <div class="member-role">{role}</div>
              <div class="member-name">{name}</div>
              <div class="member-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
