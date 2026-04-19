# CHANGELOG

Ghi lại các thay đổi quan trọng theo thứ tự thời gian.

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
