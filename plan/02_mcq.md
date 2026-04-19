# Section 2 — Phần 1: Câu hỏi Trắc nghiệm (20 điểm)

## Mục tiêu

Tính toán đáp án chính xác cho 10 câu MCQ. Mỗi câu 2 điểm, không trừ điểm sai.
Đây là **điểm dễ nhất** — mục tiêu 20/20.

## Output

- `notebooks/02_mcq_answers.ipynb` — code tính toán + đáp án
- `outputs/mcq_results.md` — tóm tắt đáp án cuối cùng

---

## Các câu hỏi và cách giải

### Q1 — Trung vị inter-order gap (2đ)

**Đề:** Khách hàng có >1 đơn, trung vị số ngày giữa 2 lần mua liên tiếp?
**Đáp án:** A) 30 / B) 90 / C) 180 / D) 365

```python
# Dữ liệu: orders.csv
orders = load_orders()  # cần cột: customer_id, order_date

# Lọc khách có > 1 đơn
multi = orders.groupby('customer_id').filter(lambda x: len(x) > 1)

# Sắp xếp theo customer + date
multi = multi.sort_values(['customer_id', 'order_date'])

# Tính gap
multi['prev_date'] = multi.groupby('customer_id')['order_date'].shift(1)
multi['gap_days'] = (multi['order_date'] - multi['prev_date']).dt.days

# Trung vị
median_gap = multi['gap_days'].dropna().median()
print(f"Median inter-order gap: {median_gap} days")
# → Chọn đáp án gần nhất
```

**Lưu ý:** "inter-order gap" = khoảng cách giữa mỗi cặp đơn liên tiếp, không phải trung bình gap per customer.

---

### Q2 — Segment có gross margin TB cao nhất (2đ)

**Đề:** Segment nào có `(price - cogs) / price` trung bình cao nhất?
**Đáp án:** A) Premium / B) Performance / C) Activewear / D) Standard

```python
# Dữ liệu: products.csv
products = load_products()

products['gross_margin'] = (products['price'] - products['cogs']) / products['price']
result = products.groupby('segment')['gross_margin'].mean().sort_values(ascending=False)
print(result)
# → Segment đầu tiên là đáp án
```

---

### Q3 — Lý do trả hàng phổ biến nhất cho Streetwear (2đ)

**Đề:** Category Streetwear, return_reason nào xuất hiện nhiều nhất?
**Đáp án:** A) defective / B) wrong_size / C) changed_mind / D) not_as_described

```python
# Dữ liệu: returns.csv + products.csv
returns = load_returns()
products = load_products()

merged = returns.merge(products[['product_id', 'category']], on='product_id')
streetwear_returns = merged[merged['category'] == 'Streetwear']
result = streetwear_returns['return_reason'].value_counts()
print(result)
# → Giá trị đầu tiên là đáp án
```

---

### Q4 — Traffic source có bounce_rate TB thấp nhất (2đ)

**Đề:** Trong web_traffic.csv, source nào bounce_rate TB thấp nhất?
**Đáp án:** A) organic_search / B) paid_search / C) email_campaign / D) social_media

```python
# Dữ liệu: web_traffic.csv
traffic = load_web_traffic()

result = traffic.groupby('traffic_source')['bounce_rate'].mean().sort_values()
print(result)
# → Source đầu tiên (thấp nhất) là đáp án
```

---

### Q5 — % order_items có promo (2đ)

**Đề:** Tỷ lệ dòng order_items có promo_id != null?
**Đáp án:** A) 12% / B) 25% / C) 39% / D) 54%

```python
# Dữ liệu: order_items.csv
items = load_order_items()

pct = items['promo_id'].notna().mean() * 100
print(f"% with promo: {pct:.1f}%")
# → Chọn đáp án gần nhất
```

---

### Q6 — Age_group có số đơn TB/khách cao nhất (2đ)

**Đề:** Nhóm tuổi (age_group != null) nào có `tổng đơn / số khách` cao nhất?
**Đáp án:** A) 55+ / B) 25–34 / C) 35–44 / D) 45–54

```python
# Dữ liệu: customers.csv + orders.csv
customers = load_customers()
orders = load_orders()

# Lọc age_group != null
valid_cust = customers[customers['age_group'].notna()]

# Join
merged = orders.merge(valid_cust[['customer_id', 'age_group']], on='customer_id')

# Tính: tổng đơn / số khách duy nhất trong mỗi nhóm
orders_per_group = merged.groupby('age_group')['order_id'].count()
customers_per_group = valid_cust.groupby('age_group')['customer_id'].nunique()

avg_orders = (orders_per_group / customers_per_group).sort_values(ascending=False)
print(avg_orders)
```

**Lưu ý:** Mẫu số là **số khách trong nhóm tuổi** (từ customers.csv), không phải số khách có đơn.

---

### Q7 — Region có tổng doanh thu cao nhất (2đ)

**Đề:** Region nào tạo ra tổng doanh thu cao nhất?
**Đáp án:** A) West / B) Central / C) East / D) Cả ba xấp xỉ bằng nhau

```python
# Dữ liệu: orders.csv + order_items.csv + geography.csv
# HOẶC: orders.csv + payments.csv + geography.csv
orders = load_orders()
items = load_order_items()
geo = load_geography()

# Tính revenue per order từ order_items
order_revenue = items.groupby('order_id').apply(
    lambda x: (x['quantity'] * x['unit_price']).sum()
).reset_index(name='revenue')

# Join orders → geography để lấy region
orders_geo = orders.merge(geo[['zip', 'region']], on='zip')
orders_geo = orders_geo.merge(order_revenue, on='order_id')

result = orders_geo.groupby('region')['revenue'].sum().sort_values(ascending=False)
print(result)
```

**Lưu ý:** Đề nói "sales_train.csv" nhưng bảng sales chỉ có Date/Revenue/COGS, không có region. Cần tính từ order_items hoặc payments.

---

### Q8 — Payment method phổ biến nhất cho đơn cancelled (2đ)

**Đề:** Đơn cancelled dùng payment_method nào nhiều nhất?
**Đáp án:** A) credit_card / B) cod / C) paypal / D) bank_transfer

```python
# Dữ liệu: orders.csv
orders = load_orders()

cancelled = orders[orders['order_status'] == 'cancelled']
result = cancelled['payment_method'].value_counts()
print(result)
```

---

### Q9 — Size có tỷ lệ trả hàng cao nhất (2đ)

**Đề:** Size (S/M/L/XL) nào có return rate cao nhất = `count(returns) / count(order_items)` theo product?
**Đáp án:** A) S / B) M / C) L / D) XL

```python
# Dữ liệu: returns.csv + order_items.csv + products.csv
returns = load_returns()
items = load_order_items()
products = load_products()

# Số returns theo size
ret_with_size = returns.merge(products[['product_id', 'size']], on='product_id')
ret_count = ret_with_size.groupby('size').size()

# Số order_items theo size
items_with_size = items.merge(products[['product_id', 'size']], on='product_id')
items_count = items_with_size.groupby('size').size()

# Return rate
return_rate = (ret_count / items_count).sort_values(ascending=False)
print(return_rate)
```

---

### Q10 — Installment plan có payment value TB cao nhất (2đ)

**Đề:** Kế hoạch trả góp nào có payment_value trung bình cao nhất?
**Đáp án:** A) 1 kỳ / B) 3 kỳ / C) 6 kỳ / D) 12 kỳ

```python
# Dữ liệu: payments.csv
payments = load_payments()

result = payments.groupby('installments')['payment_value'].mean().sort_values(ascending=False)
print(result)
```

---

## Verify checklist

- [ ] Tất cả 10 câu đều có code tính toán rõ ràng
- [ ] Kết quả mỗi câu khớp với 1 trong 4 đáp án cho sẵn
- [ ] Không có edge case bỏ sót (null handling, duplicates)
- [ ] Q6: mẫu số đúng = số khách trong nhóm tuổi, không phải số khách có đơn
- [ ] Q7: cách tính revenue nhất quán (từ order_items hoặc payments)
- [ ] Q9: cách tính return rate đúng = returns / order_items (không phải / orders)
- [ ] Code reproducible — chạy lại notebook cho cùng kết quả
- [ ] Ghi đáp án cuối cùng vào `outputs/mcq_results.md`

---

## Ghi chú

> Kết quả Q7 có thể cần kiểm tra lại nếu "doanh thu" ở đây là từ sales.csv (aggregated daily)
> hay từ order_items. Đề nói "sales_train.csv" nhưng bảng này không có region.
> Cần thử cả hai cách và chọn cách hợp lý nhất.
