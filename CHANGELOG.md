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
