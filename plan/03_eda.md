# Section 3 — Phần 2: Trực quan hoá & Phân tích EDA (60 điểm)

## Mục tiêu

Tạo bộ phân tích dữ liệu có chiều sâu, biểu đồ chất lượng cao, và insight kinh doanh có thể hành động.
Đây là **phần chiếm 60% tổng điểm** — quyết định kết quả cuộc thi.

## Output

- `notebooks/03_eda_analysis.ipynb` — notebook phân tích chính
- `figures/` — tất cả biểu đồ xuất PNG/SVG cho report
- Nội dung cho 2 trang đầu của report NeurIPS

---

## Rubric chấm điểm (nhắc lại)

| Tiêu chí | Điểm | Chiến lược ghi điểm cao |
|----------|------|------------------------|
| Chất lượng trực quan hoá | 15đ | Tiêu đề, nhãn trục, legend, loại biểu đồ tối ưu |
| Chiều sâu phân tích | **25đ** | Đạt cả 4 cấp: Descriptive → Diagnostic → Predictive → Prescriptive |
| Insight kinh doanh | 15đ | Đề xuất cụ thể, định lượng, áp dụng ngay |
| Sáng tạo & kể chuyện | 5đ | Góc nhìn độc đáo, kết nối nhiều bảng, mạch coherent |

---

## Chiến lược tổng thể

### Nguyên tắc 1: Kể chuyện, không dump chart

Mỗi phân tích phải theo flow:
```
Observation → Evidence → Explanation → Recommendation
(Descriptive)  (Diagnostic)  (Predictive)  (Prescriptive)
```

### Nguyên tắc 2: Chọn 6–8 phân tích chất lượng, không phải 20 phân tích nông

Judges đánh giá chiều sâu, không phải số lượng.

### Nguyên tắc 3: Kết nối nhiều bảng

Join products + orders + returns + promotions + inventory → tạo insights cross-functional.

---

## Storyline đề xuất (6 mảng phân tích)

### Mảng A — Xu hướng doanh thu & tăng trưởng

**Bảng cần:** `sales.csv`, `orders.csv`, `order_items.csv`

| Cấp độ | Nội dung |
|--------|---------|
| Descriptive | Revenue theo tháng/quý/năm, tốc độ tăng trưởng YoY |
| Diagnostic | Phân rã doanh thu: số đơn × AOV. Nguyên nhân biến động |
| Predictive | Xu hướng seasonality lặp lại, dự đoán peak/trough |
| Prescriptive | Khuyến nghị lập kế hoạch inventory & marketing theo mùa |

**Biểu đồ gợi ý:**
1. Line chart: Revenue monthly trend + COGS + Gross Profit
2. Decomposition: Trend + Seasonality + Residual
3. Heatmap: Revenue theo day-of-week × month

```python
# Ví dụ code
sales = load_sales()
sales['month'] = sales['Date'].dt.to_period('M')
monthly = sales.groupby('month').agg({'Revenue': 'sum', 'COGS': 'sum'})
monthly['Gross_Profit'] = monthly['Revenue'] - monthly['COGS']
monthly['Margin_%'] = monthly['Gross_Profit'] / monthly['Revenue'] * 100
```

---

### Mảng B — Khách hàng & kênh tiếp cận

**Bảng cần:** `customers.csv`, `orders.csv`, `order_items.csv`, `geography.csv`

| Cấp độ | Nội dung |
|--------|---------|
| Descriptive | Phân bố khách theo age_group, gender, acquisition_channel |
| Diagnostic | Channel nào mang lại khách repeat nhiều nhất? AOV theo segment? |
| Predictive | Customer lifetime value ước tính theo cohort |
| Prescriptive | Tập trung chi tiêu acquisition vào channel có ROI cao nhất |

**Biểu đồ gợi ý:**
1. Bar chart: Số khách & số đơn TB theo acquisition_channel
2. Cohort analysis: Retention rate theo signup month
3. RFM distribution hoặc customer segment scatter

```python
# Cohort analysis
orders_cust = orders.merge(customers[['customer_id', 'signup_date']], on='customer_id')
orders_cust['signup_month'] = orders_cust['signup_date'].dt.to_period('M')
orders_cust['order_month'] = orders_cust['order_date'].dt.to_period('M')
orders_cust['month_offset'] = (orders_cust['order_month'] - orders_cust['signup_month']).apply(lambda x: x.n)
```

---

### Mảng C — Sản phẩm, giá & lợi nhuận

**Bảng cần:** `products.csv`, `order_items.csv`, `returns.csv`

| Cấp độ | Nội dung |
|--------|---------|
| Descriptive | Revenue & margin theo category, segment |
| Diagnostic | Sản phẩm nào revenue cao nhưng margin thấp? Return rate theo category? |
| Predictive | Category nào đang tăng trưởng vs suy giảm? |
| Prescriptive | Điều chỉnh portfolio: cắt sản phẩm margin âm, đẩy mạnh segment có margin cao |

**Biểu đồ gợi ý:**
1. Scatter: Revenue vs Gross Margin theo category (bubble size = volume)
2. Pareto chart: Top 20% sản phẩm chiếm bao nhiêu % revenue
3. Stacked bar: Revenue composition theo segment qua các năm

```python
# Revenue vs Margin analysis
items_products = items.merge(products, on='product_id')
items_products['line_revenue'] = items_products['quantity'] * items_products['unit_price']
items_products['line_cost'] = items_products['quantity'] * items_products['cogs']
items_products['line_margin'] = items_products['line_revenue'] - items_products['line_cost']

category_perf = items_products.groupby('category').agg({
    'line_revenue': 'sum',
    'line_margin': 'sum',
    'quantity': 'sum'
})
category_perf['margin_pct'] = category_perf['line_margin'] / category_perf['line_revenue'] * 100
```

---

### Mảng D — Khuyến mãi & hiệu quả giảm giá

**Bảng cần:** `promotions.csv`, `order_items.csv`, `orders.csv`

| Cấp độ | Nội dung |
|--------|---------|
| Descriptive | Tần suất sử dụng promo, loại promo phổ biến |
| Diagnostic | Promo nào tăng volume hiệu quả nhất? Promo nào "đốt margin"? |
| Predictive | Mối liên hệ giữa số promo active và revenue spike |
| Prescriptive | Giảm cường độ promo cho sản phẩm low-margin, tập trung promo vào high-elasticity items |

**Biểu đồ gợi ý:**
1. Timeline: Số promo active theo thời gian vs Revenue
2. Bar chart: Discount amount vs revenue lift theo promo_type
3. Heatmap: % đơn có promo theo category × quarter

```python
# Promo effectiveness
promo_items = items[items['promo_id'].notna()]
no_promo_items = items[items['promo_id'].isna()]

promo_aov = promo_items.groupby('order_id')['quantity'].sum().mean()
no_promo_aov = no_promo_items.groupby('order_id')['quantity'].sum().mean()
print(f"Avg items/order - with promo: {promo_aov:.1f}, without: {no_promo_aov:.1f}")
```

---

### Mảng E — Vận hành: Tồn kho & logistics

**Bảng cần:** `inventory.csv`, `shipments.csv`, `web_traffic.csv`

| Cấp độ | Nội dung |
|--------|---------|
| Descriptive | Stockout frequency, overstock rate, shipping delay phân bố |
| Diagnostic | Stockouts có liên quan đến doanh thu giảm? Shipping delay → returns tăng? |
| Predictive | Trend stockout → dự đoán lost sales |
| Prescriptive | Tối ưu reorder point cho sản phẩm hay stockout; giảm inventory cho overstock |

**Biểu đồ gợi ý:**
1. Line chart: Days of supply trend + stockout events overlay
2. Scatter: Stockout days vs Lost revenue estimate
3. Bar: Shipping delay distribution + highlight late deliveries

```python
# Stockout impact analysis
inventory_monthly = inventory.groupby('snapshot_date').agg({
    'stockout_days': 'sum',
    'units_sold': 'sum',
    'fill_rate': 'mean'
})
# Correlate with monthly revenue from sales.csv
```

---

### Mảng F — Trải nghiệm khách hàng: Trả hàng & đánh giá

**Bảng cần:** `returns.csv`, `reviews.csv`, `products.csv`, `shipments.csv`

| Cấp độ | Nội dung |
|--------|---------|
| Descriptive | Return rate theo category/size, rating distribution |
| Diagnostic | Size nào return wrong_size nhiều? Shipping delay → rating thấp? |
| Predictive | Products với rating < 3 có return rate tương lai cao hơn? |
| Prescriptive | Fix sizing guide cho category/size có wrong_size cao; cải thiện delivery SLA |

**Biểu đồ gợi ý:**
1. Heatmap: Return rate theo category × size
2. Box plot: Rating distribution theo delivery delay bucket
3. Funnel: Order → Ship → Deliver → Review → Return rates

```python
# Delivery delay vs rating
ship_review = shipments.merge(reviews, on='order_id')
ship_review['delay'] = (ship_review['delivery_date'] - ship_review['ship_date']).dt.days
ship_review['delay_bucket'] = pd.cut(ship_review['delay'], bins=[0, 3, 7, 14, 30, 999])
delay_rating = ship_review.groupby('delay_bucket')['rating'].mean()
```

---

## Yêu cầu kỹ thuật cho biểu đồ

### Chuẩn visualization

Mọi biểu đồ PHẢI có:
- [ ] **Tiêu đề** rõ ràng, mô tả insight chính (không phải tên biến)
- [ ] **Nhãn trục** X, Y với đơn vị
- [ ] **Legend** nếu multi-series
- [ ] **Annotation** cho điểm đáng chú ý (peak, outlier, trend change)
- [ ] **Color palette** nhất quán (dùng 1 palette cho toàn bộ report)
- [ ] **Font size** đọc được khi in A4

### Thư viện khuyến nghị

```python
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Style setup
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')
plt.rcParams.update({
    'figure.figsize': (12, 6),
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
})

# Save cho report
fig.savefig('figures/mang_a_revenue_trend.png', dpi=300, bbox_inches='tight')
```

---

## Cấu trúc notebook `03_eda_analysis.ipynb`

```text
1. Setup & Imports
2. Load Data (dùng data_loader.py)
3. Mảng A — Revenue & Growth
   3.1 Descriptive charts
   3.2 Diagnostic analysis
   3.3 Predictive observations
   3.4 Prescriptive recommendations
   3.5 Summary insight
4. Mảng B — Customer & Channel
   (tương tự)
5. Mảng C — Product & Pricing
6. Mảng D — Promotions
7. Mảng E — Operations
8. Mảng F — Returns & Reviews
9. Cross-cutting insights
10. Executive Summary
```

---

## Verify checklist

- [ ] Ít nhất 6 mảng phân tích, mỗi mảng có đủ 4 cấp độ
- [ ] Mỗi biểu đồ có tiêu đề, nhãn trục, legend (nếu cần)
- [ ] Tổng cộng 10–15 biểu đồ chất lượng cao
- [ ] Mỗi insight có số liệu cụ thể hỗ trợ
- [ ] Có ít nhất 3 prescriptive recommendations với tradeoff định lượng
- [ ] Join ít nhất 3 bảng khác nhau trong 1 phân tích (tính sáng tạo)
- [ ] Biểu đồ xuất ra `figures/` ở dpi 300
- [ ] Narrative mạch lạc, đọc như 1 business report
- [ ] Color palette và style nhất quán
