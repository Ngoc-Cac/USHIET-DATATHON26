# CHANGELOG

Ghi lại các thay đổi quan trọng theo thứ tự thời gian.

---

## 2026-04-29 — Streamlit Filter UX + D3 Loader Fix

### Đã hoàn thành

#### 1. `streamlit_app/filters.py` — đổi filter sang dropdown kiểu Power BI ✅
- Thêm `All` option cho filter đơn chọn.
- Thêm helper `single_select()` dùng `st.sidebar.selectbox`.
- Đổi `year_range()` từ slider sang 2 dropdown `From year` / `To year`.
- Giữ khả năng truyền `key` riêng để state từng page không bị đè nhau.

#### 2. `streamlit_app/pages/` — áp dụng dropdown filter cho D1-D4 ✅
- `1_📈_D1_Revenue.py` dùng dropdown year/region/category qua helper chung.
- `2_👥_D2_Customer.py` đổi `Region` và `Channel` sang dropdown.
- `3_📦_D3_Product.py` đổi `Category` và `Year` sang dropdown.
- `4_📣_D4_Marketing.py` đổi `Traffic source` và `Year` sang dropdown.
- `app.py` cập nhật mô tả sidebar filter trong trang chủ.

#### 3. `streamlit_app/data.py` — fix loader cho D3 ✅
- Thêm `available_parse_dates()` để chỉ parse các cột ngày thực sự nằm trong `usecols`.
- Sửa lỗi `fact_returns_enriched` làm D3 crash khi page chỉ load subset cột không chứa `return_date` / `order_date`.

#### 4. `tests/test_streamlit_helpers.py` — thêm regression tests ✅
- Test option list có prepend `All`.
- Test logic `All` / single-value filter mapping.
- Test `available_parse_dates()` bỏ qua date column không được chọn và giữ lại date column hợp lệ.

### Verification
- `python -m unittest discover -s tests -p "test_streamlit_helpers.py" -v` chạy pass 5/5 tests.
- `streamlit.testing.v1.AppTest` cho toàn bộ `streamlit_app/pages/*.py`:
  - `1_📈_D1_Revenue.py` → OK
  - `2_👥_D2_Customer.py` → OK
  - `3_📦_D3_Product.py` → OK
  - `4_📣_D4_Marketing.py` → OK
  - `5_🧬_Data_Model.py` → OK

---

## 2026-04-29 — Section 03: Dashboard D1 (Plotly + Jinja2)

### Đã hoàn thành

#### 1. `dashboard_builder/` — Python pipeline render HTML dashboard ✅
- `data_loader.py` — lazy load 13 bảng từ `code-data/tableau_data/` với cache parquet cho fact lớn (`fact_orders_enriched` 183MB).
- `insights/d1_revenue.py` — build 4 KPI (Revenue, Gross Profit, Margin %, AOV) + 5 plotly figures:
  - C1 Descriptive · Line Revenue/Gross Profit + MA-12
  - C2 Diagnostic · Dual-axis Margin % vs Discount Penetration %
  - C3 Predictive · Heatmap MoM growth (year × month)
  - C4 Prescriptive · Pareto category revenue + margin %
  - C5 Diagnostic · Scatter price–margin, bubble = revenue
- `templates/` — Jinja2 (`base.html` + `index.html` + `dashboard.html`).
- `static/style.css` — dark theme, KPI grid, narrative blocks.
- `build_dashboard.py` — entrypoint, render ra `dashboard/index.html` + `dashboard/d1_revenue.html`.

#### 2. `requirements.txt` ✅
- Thêm `plotly`, `jinja2`, `pyarrow`.

### Verification
- `python -m dashboard_builder.build_dashboard` chạy ok.
- `dashboard/d1_revenue.html` (~191 KB) chứa Plotly CDN, 4 KPI, 5 chart div, narrative đủ 4 levels.
- `dashboard/index.html` có link D1.

### Chưa hoàn thành
- D2 (Customer RFM/Cohort) và D4 (Marketing/Channel) — phase sau.
- Browser smoke test thủ công (Playwright bridge unavailable).

---

## 2026-04-19 — Section 01: Data Foundation

### Branch: `first-exp` (tạo mới từ `main`)

### Đã hoàn thành

#### 1. `src/data_loader.py` — Module load dữ liệu chuẩn ✅
- Tạo 14 hàm `load_*()` cho tất cả bảng CSV
- Parse đúng kiểu `datetime64` cho các cột date: `signup_date`, `order_date`, `ship_date`, `delivery_date`, `return_date`, `review_date`, `snapshot_date`, `start_date`, `end_date`, `Date`, `date`
- `DATA_DIR` resolve relative path từ vị trí file (`src/` → `data/`)
- Hàm tiện ích `load_all()` trả về dict toàn bộ 14 bảng
- Dict `ALL_LOADERS` cho phép iterate qua tất cả loaders

#### 2. `notebooks/01_data_exploration.ipynb` — Notebook khám phá dữ liệu ✅
- **Bước 1.1**: Load tất cả 14 CSV, in shape/dtypes/head/describe
- **Bước 1.2**: Kiểm tra chất lượng dữ liệu
  - Null values report cho từng bảng
  - Primary key duplicate check (10 bảng có single PK + composite key cho order_items)
  - Date range validation (xác nhận sales = 2012-07-04 → 2022-12-31, submission = 2023-01-01 → 2024-07-01)
  - Data type verification (datetime64 cho date cols, numeric cho price/revenue/etc.)
  - Cardinality analysis cho categorical columns
  - Outlier detection (IQR method) cho 13 numeric columns chính
- **Bước 1.3**: Foreign key integrity — anti-join check cho 13 quan hệ FK
  - Phát hiện `promo_id_2` trong `order_items.csv` (không có trong plan gốc) — investigate stacked promotions
- **Bước 1.4**: Verify `data_loader.py` import thành công từ notebook
- **Bước 1.5**: Business definitions tính toán từ dữ liệu thực
  - Revenue, COGS, Gross Margin tổng
  - Gross margin per product (price - cogs) / price
  - Discount amount stats
  - Return rate = returns / order_items
  - Median inter-order gap
- **Bước 1.6**: Tóm tắt phát hiện + export `outputs/data_summary.csv`

### Phát hiện chính
- `order_items.csv` có cột `promo_id_2` ngoài plan — khả năng là stacked promotions
- `promotions.applicable_category` là float64 (chứa NaN thay vì text category)
- `web_traffic.csv` có 3,652 rows = daily × traffic_source (không phải pure daily)
- Dữ liệu sạch, không cần cleaning lớn

### Chưa hoàn thành
- Notebook chưa chạy end-to-end verify (execution timeout) — cần chạy manual trong VS Code

---

## 2026-04-19 — Section 02: MCQ Answers (20 điểm)

### Đã hoàn thành

#### 1. `notebooks/02_mcq_answers.ipynb` — Notebook tính 10 câu MCQ ✅
- Tất cả 10 câu có code tính toán rõ ràng, sử dụng `data_loader.py`
- Mỗi câu có: đề bài, code, kết quả, mapping đáp án tự động
- Cross-validation Q7 bằng 2 phương pháp (order_items vs payments)
- Bảng tổng hợp đáp án cuối notebook
- Export kết quả ra `outputs/mcq_results.md`
- Notebook đã chạy end-to-end thành công qua `nbconvert --execute`

#### 2. `outputs/mcq_results.md` — Tóm tắt đáp án ✅

### Đáp án
| Q | Ans | Mô tả |
|---|-----|-------|
| Q1 | C | 180 (median gap = 144 ngày) |
| Q2 | D | Standard (margin = 0.3134) |
| Q3 | B | wrong_size (7,626 returns) |
| Q4 | C | email_campaign (bounce = 0.00446) |
| Q5 | C | 39% (actual = 38.7%) |
| Q6 | A | 55+ (5.407 đơn/khách) |
| Q7 | C | East (7.64B revenue) |
| Q8 | A | credit_card (28,452 đơn cancelled) |
| Q9 | A | S (return rate = 5.65%) |
| Q10 | C | 6 kỳ (avg = 24,447) |
