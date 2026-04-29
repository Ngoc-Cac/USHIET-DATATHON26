# CHANGELOG

Ghi lại các thay đổi quan trọng theo thứ tự thời gian.

---

## 2026-04-30 — Report rewrite với số liệu thật từ chart

### Mục tiêu
Apply Option A từ critique GPT review: giữ 2 sửa đúng (rating causal hedge + 90-day plan), revert 4 hedge khác, và **kiểm chứng từng claim bằng số liệu thật**.

### Đã hoàn thành

#### 1. `outputs/extract_chart_numbers.py` — script trích số ✅
- Replicate logic exact của từng chart Streamlit
- Output: `outputs/chart_numbers.txt` (241 dòng số thật)
- Chạy lại bất cứ lúc nào: `python outputs/extract_chart_numbers.py > outputs/chart_numbers.txt`

#### 2. `report.md` — rewrite full với số liệu trích từ chart ✅
Phát hiện **6 sai sót thực tế** trong bản gốc:

| Bản gốc của tôi | Số thật từ data | Hành động |
|---|---|---|
| Top-3 category "trên 60%" | **97.9%** (Streetwear một mình 79.9%) | Sửa số, đổi framing thành "monopoly" |
| "Promo eats margin" định tính | **Corr Margin↔Discount = −0.561** | Cite số → claim mạnh hẳn |
| "Vay tăng trưởng từ promo" | **Corr Rev↔Promo% = −0.214 (âm)** | Đổi framing: promo *không thậm chí buy được growth* |
| "Onboarding fail M1-M3" | Cohort retention phẳng ~3.3% suốt M1-M24, nhưng funnel cho 74.3% lifetime repeat | Sửa lại: đây là *frequency* problem, không phải *retention drop* |
| "Channel nuôi khách lệch 5pp" | All channels 53.24-54.12% repeat (lệch <1pp) | Bỏ claim → "channel quality nearly identical" |
| "Age × gender persona đắt" | LTV 151K-166K (chênh 9.7%) gần phẳng | Bỏ claim |

Đồng thời cite được số đắt hơn:
- Promo vs No-promo margin gap = **18.64pp**
- **Streetwear margin với promo = −0.13% (âm)** — category 80% revenue đang lỗ thuần với promo
- Stockout chiếm **67.3%** inventory snapshots (crisis-level)
- 18.5% SKU = 80% revenue (Pareto cực sách giáo khoa)
- Lost revenue proxy ≈ 1.29 tỷ VND (7.8% tổng revenue)
- Revenue 2022 thấp hơn đỉnh 2016 −44.4%

#### 3. Critique GPT review per Option A ✅
- **Giữ**: hedge causal trên rating→return (data là cross-section, không có time-series)
- **Giữ**: section 90-day rollout (Stabilize → Optimize → Scale)
- **Revert**: 4 chỗ hedge khác về tone confident — mỗi claim bây giờ đều có số trích từ chart kèm theo

### Verification
- Mọi câu khẳng định mạnh trong report đều có **chart name + số cụ thể** kèm theo
- Số liệu reproducible bằng `python outputs/extract_chart_numbers.py`
- Không có số nào "bịa" — tất cả từ load + groupby trên CSV gốc

---

## 2026-04-29 — D-D-P-P Brainstorm Charts (append-only)

### Mục tiêu
Bổ sung các chart còn thiếu theo review ở `EDA.md` mà KHÔNG xoá chart cũ — để brainstorm: vẽ càng nhiều phân tích càng tốt, sau đó chọn ra insights chất lượng.

### Đã hoàn thành

#### D1 Revenue — thêm 3 chart (`pages/1_📈_D1_Revenue.py`)
- **E1 Orders × AOV decomposition** (Diagnostic): tách revenue thành 2 driver, tự động báo driver YoY chính.
- **E2 Seasonal naive forecast band** (Predictive thực sự): forecast 6 tháng tới với band ±1.5σ theo same-month của các năm trước.
- **E3 YoY contribution bridge** (Prescriptive): bar ngang Δrev theo category, tự động list winners/losers.

#### D2 Customer — thêm 3 chart (`pages/2_👥_D2_Customer.py`)
- **E1 LTV heatmap age × gender** (Descriptive persona): xác định core buyer.
- **E2 Customer journey funnel** (Diagnostic): 1st → 2nd → 3rd → loyal (5+); auto tính drop-off.
- **E3 Channel quality · repeat & loyal rate** (Predictive + Prescriptive): grouped bar repeat-rate / loyal-rate + line LTV.
- Mở rộng load thêm `age_group`, `gender` cho `dim_customers_rfm`.

#### D3 Product — thêm 4 chart (`pages/3_📦_D3_Product.py`)
- **E1 Pareto SKU concentration** (Descriptive + Prescriptive): bar revenue theo rank + cum% line + ngưỡng 80%, auto tính % SKU tạo 80% rev → protection list.
- **E2 Return rate · Category × Size** (Diagnostic): heatmap, auto tìm hot spot.
- **E3 Rating bucket → return risk** (Predictive thực sự): bins rating, return-rate trung bình từng bin → leading indicator.
- **E4 Stockout days vs lost revenue proxy** (Prescriptive): scatter top-80 SKU bị stockout, tổng lost-rev proxy.
- Mở rộng load thêm `size`, `stockout_days`, `units_sold`, `product_price`.

#### D4 Marketing — thêm 5 chart (`pages/4_📣_D4_Marketing.py`)
Đổi trọng tâm sang promotion economics + cross-functional theo `EDA.md`.
- **E1 Promo vs No-promo** (Diagnostic): 2-panel revenue + margin %, auto tính margin drop pp.
- **E2 Promo penetration · Category × Year** (Descriptive heatmap).
- **E3 Promo ROI scatter** (Prescriptive): margin drop pp vs promo share, size = promo revenue.
- **E4 Revenue × Sessions × Promo intensity** (Diagnostic cross-functional): triple-line + correlation.
- **E5 Channel scale vs LTV** (Prescriptive): scatter + median LTV reference, auto list channels nên scale.
- Mở rộng load `fact_orders_enriched` (promo cols) và `agg_monthly_summary`.

### Verification
- `python -c "ast.parse(...)"` qua sạch cho cả 4 page.
- Smoke test data load: rfm 121k×9, orders 714k×8/10, returns 39k×7, inventory 60k×9.
- Smoke test chart computations: return×size ≈3% range hợp lý; rating bins cho thấy signal predictive thực (≤3.0: 3.8% return vs 4.5–5.0: 3.1%).

### Quy ước
- Mọi chart mới nằm sau marker `# Extra brainstorm row` ở cuối từng page, đặt trong cột full-width dưới grid 2×2 hiện hữu.
- Chart cũ giữ nguyên 100%, không sửa caption / không xoá.
- Mọi chart mới đều có narrative caption gắn nhãn D-D-P-P kèm số liệu auto-extracted.

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

#### 5. `streamlit_app/theme.py` — fix sidebar readability and color layering ✅
- Bỏ rule sidebar quá rộng làm ép cùng một màu lên toàn bộ node con.
- Tách màu riêng cho nền sidebar, nav item, active item, input surface và dropdown menu.
- Tăng tương phản giữa text, selected value và background để sidebar không còn bị chèn màu giữa các component.

#### 6. `streamlit_app/pages/3_📦_D3_Product.py` — đổi KPI Refund amount thành Return rate ✅
- Thêm `quantity` vào dữ liệu orders cho D3.
- KPI thứ ba giờ hiển thị `Return rate = returned units / ordered units` theo đúng filter category và year.

#### 7. `streamlit_app/app.py` + `theme.py` — home hero + team intro block ✅
- Thiết kế lại title `DATATHON 2026 / the gridbreakers` theo hướng gần mẫu hơn với font display và year chip lime.
- Thêm block giới thiệu team `USHIET` trên trang `localhost:8501`.
- Tạo 4 member placeholder cards để điền nội dung sau.

#### 8. `streamlit_app/pages/` + `filters.py` + `theme.py` — move filters to canvas top-right ✅
- `single_select()` và `year_range()` chuyển từ `st.sidebar.selectbox` sang `st.selectbox`.
- D1, D2, D3, D4 đặt filter thành một hàng ngang trên main canvas, phía trên KPI cards.
- Sidebar của các page analytics giờ giữ nav và thêm một notes panel lớn để trống cho nhận xét thủ công.
- Thêm unit tests xác nhận filter helpers không còn render ở sidebar.

#### 9. `streamlit_app/pages/` + `theme.py` — inline page header with filters ✅
- Title/subtitle của D1, D2, D3, D4 giờ nằm cùng hàng với filter controls.
- `From year` và `To year` được tách thành 2 dropdown riêng trên cùng một hàng ngang.
- Thêm helper `page_header_inline()` để header và filter bar bám sát layout mong muốn hơn.

#### 10. `streamlit_app/theme.py` + analytics pages — top navigation + lighter UI shell ✅
- Thêm navigation ngang phía trên header cho D1-D4.
- Bỏ lớp bọc thừa quanh filter controls.
- Giảm mạnh viền/khung bao ở team cards, metric cards, chart containers, expanders, tabs và containers để giao diện thoáng hơn.

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
