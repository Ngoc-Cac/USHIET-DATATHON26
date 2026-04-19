# Section 5 — Báo cáo NeurIPS (4 trang)

## Mục tiêu

Viết báo cáo kỹ thuật theo template NeurIPS LaTeX, tối đa 4 trang (không tính references và appendix).
Báo cáo phải tổng hợp kết quả từ Phần 2 (EDA) và Phần 3 (Forecasting).

## Output

- `docs/report/main.tex` — file LaTeX chính
- `docs/report/main.pdf` — file PDF xuất
- `docs/report/figures/` — biểu đồ chọn lọc cho report
- `docs/report/references.bib` — bibtex nếu cần

---

## Template

Tải NeurIPS LaTeX template tại:
- https://neurips.cc/Conferences/2025/CallForPapers
- Hoặc sử dụng Overleaf template NeurIPS 2025

---

## Phân bổ trang đề xuất

| Trang | Nội dung | Biểu đồ |
|-------|---------|---------|
| **1** | Abstract + Business Context + Top Descriptive/Diagnostic Insights | 2–3 charts |
| **2** | Deep Insights + Prescriptive Recommendations | 2–3 charts |
| **3** | Forecasting: Approach + Features + Validation Design | 1 table + 1 chart |
| **4** | Forecasting Results + Explainability + Conclusion | SHAP plot + results table |

---

## Cấu trúc báo cáo chi tiết

### Abstract (5–6 dòng)
- Bối cảnh: e-commerce thời trang Việt Nam
- Phương pháp: EDA multi-table + ML forecasting
- Kết quả chính: top 2–3 findings + model performance
- Đề xuất: 1–2 business actions chính

### 1. Introduction & Business Context
- Mô tả ngắn gọn bộ dữ liệu
- Mục tiêu phân tích
- Overview cấu trúc 14 bảng dữ liệu

### 2. Exploratory Data Analysis
- Chọn 4–5 insights mạnh nhất từ Section 3 (EDA)
- Mỗi insight: chart + narrative + business implication
- Flow: Descriptive → Diagnostic → Prescriptive
- **Không dump tất cả charts** — chỉ chọn những cái có business impact cao nhất

### 3. Revenue Forecasting
#### 3.1 Problem Definition
- Target: Daily Revenue (+ COGS)
- Train/Test split
- Evaluation metrics: MAE, RMSE, R²

#### 3.2 Feature Engineering
- Bảng tóm tắt các nhóm features
- Lý do chọn từng nhóm

#### 3.3 Model Selection & Validation
- Time-series CV setup
- Models benchmarked
- Bảng so sánh metrics

#### 3.4 Results
- Final model performance
- So sánh với baseline

#### 3.5 Model Explainability
- SHAP summary plot
- Top 5 features và giải thích kinh doanh
- Ví dụ: "Traffic sessions tuần trước giải thích 25% variance"

### 4. Conclusion & Recommendations
- Top 3 business actions từ EDA
- Forecasting utility cho planning
- Limitations & future work

### References
- Thư viện sử dụng (LightGBM, SHAP, etc.)

### Appendix (không giới hạn trang)
- Biểu đồ bổ sung
- Bảng kết quả chi tiết
- Hyperparameter settings

---

## Quy tắc viết

1. **Ngắn gọn**: 4 trang rất hạn chế — mỗi câu phải mang thông tin
2. **Số liệu cụ thể**: "Revenue tăng 23% YoY" thay vì "Revenue tăng đáng kể"
3. **Business language**: Judges không chỉ là data scientist — viết cho cả business stakeholders
4. **Figures > Text**: Một biểu đồ tốt thay thế 1 đoạn văn
5. **Captions chi tiết**: Mỗi figure caption phải tự giải thích được insight mà không cần đọc text

---

## Verify checklist

- [ ] Template NeurIPS đúng format
- [ ] Tối đa 4 trang nội dung chính
- [ ] Có abstract
- [ ] Có phần EDA với ≥ 4 charts chất lượng
- [ ] Có phần Forecasting với pipeline description
- [ ] Có bảng so sánh model metrics
- [ ] Có SHAP / feature importance plot
- [ ] Có business recommendations cụ thể
- [ ] Có link GitHub repository trong báo cáo
- [ ] PDF compile thành công, không lỗi
- [ ] Figure captions rõ ràng
- [ ] Không vượt page limit
