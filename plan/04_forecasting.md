# Section 4 — Phần 3: Mô hình Dự báo Doanh thu (20 điểm)

## Mục tiêu

Xây dựng pipeline dự báo `Revenue` (và `COGS`) hàng ngày cho giai đoạn 01/01/2023 – 01/07/2024.
Submit lên Kaggle và viết phần giải thích mô hình cho report.

## Output

- `notebooks/04_forecasting.ipynb` — pipeline chính
- `src/features.py` — module feature engineering
- `submission/submission.csv` — file nộp Kaggle
- `figures/` — SHAP plots, feature importance cho report
- `outputs/validation_results.csv` — kết quả cross-validation

---

## Phân bổ điểm

| Thành phần | Điểm | Yêu cầu |
|-----------|------|---------|
| Hiệu suất mô hình (Kaggle) | 12đ | MAE, RMSE thấp; R² cao; xếp hạng leaderboard |
| Báo cáo kỹ thuật | 8đ | Pipeline rõ ràng, time-series CV, SHAP/feature importance |

---

## Ràng buộc BẮT BUỘC

> [!CAUTION]
> Vi phạm bất kỳ điều nào → **BỊ LOẠI TOÀN BỘ PHẦN 3**

1. ❌ KHÔNG dùng Revenue/COGS từ tập test làm feature
2. ❌ KHÔNG dùng dữ liệu ngoài bộ CSV được cung cấp
3. ✅ PHẢI đính kèm toàn bộ mã nguồn
4. ✅ PHẢI reproducible (random seed = 42)
5. ✅ PHẢI có giải thích mô hình (SHAP/feature importance)

---

## Pipeline thực hiện

### Bước 4.1 — Khám phá dữ liệu target

```python
import pandas as pd
import matplotlib.pyplot as plt

sales = pd.read_csv('data/sales.csv', parse_dates=['Date'])
sample_sub = pd.read_csv('data/sample_submission.csv', parse_dates=['Date'])

print(f"Train: {sales['Date'].min()} → {sales['Date'].max()}")
print(f"Test:  {sample_sub['Date'].min()} → {sample_sub['Date'].max()}")
print(f"Train rows: {len(sales)}, Test rows: {len(sample_sub)}")

# Visualize
fig, axes = plt.subplots(3, 1, figsize=(14, 10))
axes[0].plot(sales['Date'], sales['Revenue'])
axes[0].set_title('Daily Revenue')
axes[1].plot(sales['Date'], sales['COGS'])
axes[1].set_title('Daily COGS')
axes[2].plot(sales['Date'], sales['Revenue'] - sales['COGS'])
axes[2].set_title('Daily Gross Profit')
plt.tight_layout()
```

Kiểm tra:
- Trend tổng thể (tăng/giảm/ổn định)
- Seasonality (weekly, monthly, yearly)
- Outliers / anomalies (ngày Revenue = 0?, spike bất thường?)
- Missing dates

---

### Bước 4.2 — Feature Engineering

Tạo `src/features.py` với các nhóm features:

#### Nhóm 1: Calendar Features
```python
def add_calendar_features(df):
    df['day_of_week'] = df['Date'].dt.dayofweek      # 0=Mon, 6=Sun
    df['day_of_month'] = df['Date'].dt.day
    df['month'] = df['Date'].dt.month
    df['quarter'] = df['Date'].dt.quarter
    df['year'] = df['Date'].dt.year
    df['week_of_year'] = df['Date'].dt.isocalendar().week.astype(int)
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_month_start'] = df['Date'].dt.is_month_start.astype(int)
    df['is_month_end'] = df['Date'].dt.is_month_end.astype(int)
    df['day_of_year'] = df['Date'].dt.dayofyear
    return df
```

#### Nhóm 2: Lag Features (từ sales history)
```python
def add_lag_features(df, target='Revenue', lags=[1, 7, 14, 28, 365]):
    for lag in lags:
        df[f'{target}_lag_{lag}'] = df[target].shift(lag)
    return df
```

#### Nhóm 3: Rolling Window Features
```python
def add_rolling_features(df, target='Revenue', windows=[7, 14, 28, 90]):
    for w in windows:
        df[f'{target}_roll_mean_{w}'] = df[target].shift(1).rolling(w).mean()
        df[f'{target}_roll_std_{w}'] = df[target].shift(1).rolling(w).std()
        df[f'{target}_roll_max_{w}'] = df[target].shift(1).rolling(w).max()
        df[f'{target}_roll_min_{w}'] = df[target].shift(1).rolling(w).min()
    return df
```

#### Nhóm 4: Trend Features
```python
def add_trend_features(df, target='Revenue'):
    # EWM
    df[f'{target}_ewm_7'] = df[target].shift(1).ewm(span=7).mean()
    df[f'{target}_ewm_30'] = df[target].shift(1).ewm(span=30).mean()
    
    # Ratio / momentum
    df[f'{target}_mom_7'] = df[target].shift(1) / df[target].shift(8)
    df[f'{target}_mom_30'] = df[target].shift(1) / df[target].shift(31)
    return df
```

#### Nhóm 5: Features từ bảng khác (aggregate lên daily)

```python
def add_external_features(df):
    """
    Join features từ các bảng khác, aggregate lên mức daily.
    CHỈ dùng dữ liệu TRƯỚC ngày dự báo (shift hoặc lag).
    """
    # Web traffic: sessions, bounce_rate, page_views (daily)
    traffic = pd.read_csv('data/web_traffic.csv', parse_dates=['date'])
    daily_traffic = traffic.groupby('date').agg({
        'sessions': 'sum',
        'unique_visitors': 'sum',
        'page_views': 'sum',
        'bounce_rate': 'mean',
        'avg_session_duration_sec': 'mean'
    }).reset_index()
    df = df.merge(daily_traffic, left_on='Date', right_on='date', how='left')
    
    # Orders: daily order count, cancel rate
    orders = pd.read_csv('data/orders.csv', parse_dates=['order_date'])
    daily_orders = orders.groupby('order_date').agg(
        order_count=('order_id', 'count'),
        cancel_count=('order_status', lambda x: (x == 'cancelled').sum())
    ).reset_index()
    daily_orders['cancel_rate'] = daily_orders['cancel_count'] / daily_orders['order_count']
    df = df.merge(daily_orders, left_on='Date', right_on='order_date', how='left')
    
    # Promotions: count active promos per day
    promos = pd.read_csv('data/promotions.csv', parse_dates=['start_date', 'end_date'])
    # ... expand date ranges and count
    
    # Inventory: monthly → broadcast to daily (lagged 1 month)
    # ...
    
    return df
```

> [!WARNING]
> **Leakage check:** Mọi feature từ bảng khác phải dùng dữ liệu **trước** ngày dự báo.
> Ví dụ: web_traffic ngày t-1 dùng cho dự báo ngày t.
> Orders ngày t KHÔNG được dùng (vì revenue ngày t phụ thuộc vào orders ngày t).

---

### Bước 4.3 — Train/Validation Split (Time-based)

```python
# KHÔNG dùng random split!
# Dùng rolling/expanding window

# Ví dụ: 5-fold time-based CV
folds = [
    ('2012-07-04', '2020-12-31', '2021-01-01', '2021-06-30'),
    ('2012-07-04', '2021-06-30', '2021-07-01', '2021-12-31'),
    ('2012-07-04', '2021-12-31', '2022-01-01', '2022-06-30'),
    ('2012-07-04', '2022-06-30', '2022-07-01', '2022-12-31'),
]

for i, (train_start, train_end, val_start, val_end) in enumerate(folds):
    train = df[(df['Date'] >= train_start) & (df['Date'] <= train_end)]
    val = df[(df['Date'] >= val_start) & (df['Date'] <= val_end)]
    # Train and evaluate
```

---

### Bước 4.4 — Baseline Models

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate(y_true, y_pred, name=''):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print(f"{name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.4f}")
    return {'name': name, 'MAE': mae, 'RMSE': rmse, 'R2': r2}
```

**Baselines:**
1. **Naive lag-7**: Dùng Revenue 7 ngày trước
2. **Rolling mean 28d**: Trung bình 28 ngày gần nhất
3. **Seasonal naive**: Cùng ngày tuần trước

---

### Bước 4.5 — Candidate Models

| Model | Thư viện | Ghi chú |
|-------|---------|---------|
| **Ridge Regression** | scikit-learn | Baseline linear |
| **LightGBM** | lightgbm | Tree-based, fast |
| **XGBoost** | xgboost | Tree-based, robust |
| **CatBoost** | catboost | Handles categoricals |
| **Prophet** | prophet | Facebook time-series |
| **Ensemble** | manual | Weighted average of top models |

```python
import lightgbm as lgb

params = {
    'objective': 'regression',
    'metric': 'mae',
    'learning_rate': 0.05,
    'num_leaves': 31,
    'max_depth': -1,
    'min_child_samples': 20,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    'random_state': 42,
    'verbose': -1
}

# Train
dtrain = lgb.Dataset(X_train, y_train)
dval = lgb.Dataset(X_val, y_val, reference=dtrain)
model = lgb.train(params, dtrain, num_boost_round=1000,
                  valid_sets=[dval], callbacks=[lgb.early_stopping(50)])
```

---

### Bước 4.6 — Hyperparameter Tuning

```python
from sklearn.model_selection import TimeSeriesSplit
import optuna

def objective(trial):
    params = {
        'learning_rate': trial.suggest_float('lr', 0.01, 0.3, log=True),
        'num_leaves': trial.suggest_int('num_leaves', 15, 127),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'min_child_samples': trial.suggest_int('min_child', 5, 50),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample', 0.5, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-4, 10, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-4, 10, log=True),
    }
    # Time-series CV evaluation
    scores = []
    for train_idx, val_idx in tscv.split(X):
        # ... train and eval
        scores.append(mae)
    return np.mean(scores)

study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=100)
```

---

### Bước 4.7 — COGS Prediction

`submission.csv` yêu cầu cả Revenue và COGS. Hai cách:

**Cách 1:** Train 2 model riêng (Revenue model + COGS model)
**Cách 2:** Dự đoán Revenue, rồi tính COGS = Revenue × (historical COGS/Revenue ratio)

```python
# Cách 2: dùng historical ratio
cogs_ratio = sales['COGS'].sum() / sales['Revenue'].sum()
submission['COGS'] = submission['Revenue'] * cogs_ratio
```

---

### Bước 4.8 — Explainability (SHAP)

```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_val)

# Summary plot
shap.summary_plot(shap_values, X_val, show=False)
plt.savefig('figures/shap_summary.png', dpi=300, bbox_inches='tight')

# Feature importance bar
shap.summary_plot(shap_values, X_val, plot_type='bar', show=False)
plt.savefig('figures/feature_importance.png', dpi=300, bbox_inches='tight')

# Top features partial dependence
for feat in top_5_features:
    shap.dependence_plot(feat, shap_values, X_val, show=False)
    plt.savefig(f'figures/pdp_{feat}.png', dpi=300, bbox_inches='tight')
```

Giải thích bằng ngôn ngữ kinh doanh:
- "Lượng visitor tuần trước giải thích ~25% biến động doanh thu"
- "Ngày cuối tháng có doanh thu cao hơn 15% do hiệu ứng phát lương"
- "Số chương trình khuyến mãi active tương quan dương với revenue nhưng âm với margin"

---

### Bước 4.9 — Generate Submission

```python
# Predict
test_features = build_features(test_df)  # dùng cùng pipeline
predictions = model.predict(test_features)

# Format submission
submission = sample_sub.copy()
submission['Revenue'] = predictions
submission['COGS'] = predictions * cogs_ratio  # hoặc model COGS riêng

# Kiểm tra
assert len(submission) == len(sample_sub), "Row count mismatch!"
assert list(submission.columns) == list(sample_sub.columns), "Column mismatch!"
assert submission['Date'].equals(sample_sub['Date']), "Date order mismatch!"

# Save
submission.to_csv('submission/submission.csv', index=False)
print("Submission saved!")
```

---

## Verify checklist

- [ ] Không dùng Revenue/COGS test làm feature (leakage check)
- [ ] Không dùng dữ liệu ngoài
- [ ] Random seed = 42 ở mọi nơi
- [ ] Time-based CV, KHÔNG random split
- [ ] Baseline models có kết quả để so sánh
- [ ] Ít nhất 2 model families được thử (ví dụ: LightGBM + XGBoost)
- [ ] SHAP summary plot đã xuất
- [ ] Feature importance đã xuất
- [ ] `submission.csv` có đúng số dòng & thứ tự như `sample_submission.csv`
- [ ] `submission.csv` có 3 cột: Date, Revenue, COGS
- [ ] Kết quả validation được ghi lại trong `outputs/validation_results.csv`
- [ ] Pipeline chạy end-to-end reproducible
- [ ] Giải thích mô hình bằng ngôn ngữ kinh doanh (cho report)
