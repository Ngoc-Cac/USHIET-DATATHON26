# Section 6 — Nộp bài & Checklist cuối cùng

## Mục tiêu

Đảm bảo tất cả deliverables được nộp đầy đủ, đúng format, đúng hạn.

---

## Checklist nộp bài

### 1. Kaggle Submission

- [ ] File `submission/submission.csv` đã tạo
- [ ] Đúng số dòng với `sample_submission.csv`
- [ ] Giữ nguyên thứ tự dòng (KHÔNG sắp xếp lại)
- [ ] 3 cột: `Date`, `Revenue`, `COGS`
- [ ] Đã upload lên: https://www.kaggle.com/competitions/datathon-2026-round-1
- [ ] Kaggle chấp nhận file (không bị rejected)
- [ ] Ghi lại link submission Kaggle

### 2. GitHub Repository

- [ ] Repository ở chế độ **public** (hoặc cấp quyền cho BTC)
- [ ] Cấu trúc thư mục rõ ràng:
  ```
  ├── data/           # Raw data (hoặc .gitignore nếu quá lớn)
  ├── notebooks/      # Jupyter notebooks
  ├── src/            # Python modules
  ├── figures/        # Biểu đồ xuất
  ├── submission/     # submission.csv
  ├── docs/report/    # LaTeX report
  ├── requirements.txt
  └── README.md
  ```
- [ ] `README.md` có:
  - [ ] Mô tả dự án
  - [ ] Cấu trúc thư mục
  - [ ] Hướng dẫn cài đặt dependencies
  - [ ] Hướng dẫn chạy lại kết quả (reproduce)
  - [ ] Tên thành viên nhóm
- [ ] `requirements.txt` đầy đủ tất cả thư viện
- [ ] Code chạy được từ đầu đến cuối
- [ ] Ghi lại link GitHub

### 3. Báo cáo (Report)

- [ ] File PDF đã xuất từ LaTeX
- [ ] Dùng template NeurIPS
- [ ] Tối đa 4 trang (không tính refs + appendix)
- [ ] Có phần EDA + visualizations
- [ ] Có phần pipeline mô hình + kết quả
- [ ] Có link GitHub trong báo cáo
- [ ] PDF readable, figures rõ ràng

### 4. Form nộp bài chính thức

Form yêu cầu (link sẽ được BTC cung cấp):

- [ ] **Đáp án 10 câu MCQ** — chọn đáp án đúng
- [ ] **Upload báo cáo PDF**
- [ ] **Link GitHub repository**
- [ ] **Link Kaggle submission**
- [ ] **Ảnh thẻ sinh viên** của TẤT CẢ thành viên
- [ ] **Xác nhận tham dự**: Ít nhất 1 thành viên có thể đến VinUni ngày 23/05/2026

> [!CAUTION]
> **Điều kiện loại:**
> - Không xác nhận tham gia trực tiếp Vòng Chung kết → **không đủ điều kiện**
> - Không cung cấp ảnh thẻ sinh viên → **không đủ điều kiện**

---

## Checklist kỹ thuật cuối cùng

### Reproducibility

- [ ] `random_seed = 42` trong mọi model/sampling
- [ ] Notebook chạy top-to-bottom không lỗi
- [ ] Kết quả giống nhau khi chạy lại

### Leakage

- [ ] ❌ Không dùng Revenue/COGS test
- [ ] ❌ Không dùng dữ liệu ngoài
- [ ] ✅ Features chỉ dùng thông tin trước ngày dự báo

### Code Quality

- [ ] Không có hardcoded paths (dùng relative paths)
- [ ] Import sạch, không có unused imports
- [ ] Có comment giải thích logic quan trọng

---

## Timeline gợi ý

| Giai đoạn | Việc | Deadline gợi ý |
|-----------|------|----------------|
| 1 | Data Foundation | Ngày 1 |
| 2 | MCQ Answers | Ngày 1–2 |
| 3 | EDA Analysis | Ngày 2–4 |
| 4 | Forecasting Pipeline | Ngày 3–5 |
| 5 | Report Writing | Ngày 5–6 |
| 6 | Final Review & Submit | Ngày 6–7 |

> [!IMPORTANT]
> Dành ít nhất **1 ngày cuối** chỉ để review, kiểm tra lại toàn bộ, và nộp bài.
> Không code thêm feature mới vào ngày cuối.

---

## Sau khi nộp

- [ ] Double-check Kaggle submission status
- [ ] Verify GitHub repo accessible
- [ ] Confirm form submission received
- [ ] Screenshot confirmation page
