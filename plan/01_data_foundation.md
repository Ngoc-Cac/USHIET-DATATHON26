# Section 1 — Data Foundation (Khám phá & Kiểm tra Dữ liệu)

## Mục tiêu

Hiểu rõ toàn bộ bộ dữ liệu trước khi phân tích. Đây là bước nền tảng bắt buộc — mọi section sau đều phụ thuộc vào kết quả ở đây.

## Output

- `notebooks/01_data_exploration.ipynb`
- `outputs/data_summary.csv` — tóm tắt schema từng bảng
- `src/data_loader.py` — module load & parse data chuẩn

---

## Các bước thực hiện

### Bước 1.1 — Load tất cả 14 file CSV

```python
import pandas as pd

files = [
    'products.csv', 'customers.csv', 'promotions.csv', 'geography.csv',
    'orders.csv', 'order_items.csv', 'payments.csv', 'shipments.csv',
    'returns.csv', 'reviews.csv', 'sales.csv', 'sample_submission.csv',
    'inventory.csv', 'web_traffic.csv'
]
```

Với mỗi file:
- `df.shape` — số dòng, số cột
- `df.dtypes` — kiểu dữ liệu
- `df.head(5)` — xem mẫu
- `df.describe()` — thống kê cơ bản

### Bước 1.2 — Kiểm tra chất lượng dữ liệu

Cho mỗi bảng, kiểm tra:

| Kiểm tra | Cách |
|----------|------|
| **Null values** | `df.isnull().sum()` — ghi nhận cột nào nullable |
| **Duplicate keys** | `df[key_col].duplicated().sum()` — phải = 0 cho primary key |
| **Date range** | `df[date_col].min()`, `.max()` — xác nhận khớp với đề bài |
| **Data types** | Parse đúng: date → `datetime64`, int/float → numeric |
| **Outliers** | Box plot hoặc percentile cho numeric columns |
| **Cardinality** | `df[col].nunique()` — số giá trị unique |

### Bước 1.3 — Xác nhận khóa và quan hệ bảng

Theo đề bài, xác nhận:

```text
orders.customer_id → customers.customer_id
orders.zip → geography.zip
order_items.order_id → orders.order_id
order_items.product_id → products.product_id
order_items.promo_id → promotions.promo_id
payments.order_id → orders.order_id (1:1)
shipments.order_id → orders.order_id (1:0..1)
returns.order_id → orders.order_id (1:0..n)
returns.product_id → products.product_id
reviews.order_id → orders.order_id (1:0..n)
reviews.product_id → products.product_id
reviews.customer_id → customers.customer_id
inventory.product_id → products.product_id
```

Kiểm tra bằng anti-join:
```python
# Ví dụ: tìm order_id trong order_items mà không có trong orders
missing = order_items[~order_items['order_id'].isin(orders['order_id'])]
assert len(missing) == 0, f"Found {len(missing)} orphan order_items"
```

### Bước 1.4 — Tạo data_loader.py

Tạo module `src/data_loader.py` để các notebook sau dùng chung:

```python
"""Unified data loading with correct dtypes and parsing."""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

def load_products():
    return pd.read_csv(DATA_DIR / 'products.csv')

def load_customers():
    df = pd.read_csv(DATA_DIR / 'customers.csv', parse_dates=['signup_date'])
    return df

def load_orders():
    df = pd.read_csv(DATA_DIR / 'orders.csv', parse_dates=['order_date'])
    return df

def load_sales():
    df = pd.read_csv(DATA_DIR / 'sales.csv', parse_dates=['Date'])
    return df

# ... tương tự cho tất cả bảng
```

### Bước 1.5 — Ghi nhận business definitions

Ghi rõ các định nghĩa quan trọng:

| Khái niệm | Định nghĩa |
|-----------|-----------|
| **Revenue** | Tổng doanh thu thuần (cột `Revenue` trong `sales.csv`) |
| **COGS** | Giá vốn hàng bán |
| **Gross Margin** | `(price - cogs) / price` |
| **Discount Amount** | `quantity × unit_price × (discount_value/100)` nếu percentage, `quantity × discount_value` nếu fixed |
| **Return Rate** | `count(returns) / count(order_items)` theo product/size |
| **Inter-order Gap** | Khoảng cách ngày giữa 2 đơn liên tiếp của cùng 1 khách |

### Bước 1.6 — Tóm tắt phát hiện ban đầu

Ghi vào cuối notebook:
- Tổng số records mỗi bảng
- Khoảng thời gian dữ liệu thực tế
- Cột nào có null nhiều
- Anomalies phát hiện
- Kết luận: dữ liệu sạch hay cần xử lý thêm

---

## Verify checklist

- [ ] Tất cả 14 CSV load thành công, không lỗi encoding
- [ ] Primary keys không có duplicate
- [ ] Foreign keys khớp nhau (anti-join rỗng)
- [ ] Date columns parse đúng kiểu datetime
- [ ] Khoảng thời gian sales.csv = 04/07/2012 → 31/12/2022
- [ ] sample_submission.csv = 01/01/2023 → 01/07/2024
- [ ] `data_loader.py` hoạt động khi import từ notebook
- [ ] Ghi nhận đủ null patterns cho các cột nullable
- [ ] Không có data leakage rõ ràng

---

## Ghi chú

> Bước này **không tạo biểu đồ phân tích** — chỉ kiểm tra, xác nhận, và chuẩn bị nền tảng.
> Biểu đồ EDA thuộc Section 3.
