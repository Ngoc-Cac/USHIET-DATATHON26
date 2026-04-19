# Plan Overview — Datathon 2026 Round 1

## Cấu trúc kế hoạch

Mỗi section được tách thành một file `.md` riêng. Khi thực hiện, chỉ implement **một section tại một thời điểm**, hoàn thành xong mới chuyển sang section tiếp theo.

## Thứ tự thực hiện

| # | File | Section | Điểm | Ưu tiên |
|---|------|---------|------|---------|
| 0 | `00_overview.md` | Tổng quan & quy tắc chung | — | — |
| 1 | `01_data_foundation.md` | Khám phá & kiểm tra dữ liệu | — | Bắt buộc trước |
| 2 | `02_mcq.md` | Phần 1 — 10 câu trắc nghiệm | 20đ | Cao (điểm dễ) |
| 3 | `03_eda.md` | Phần 2 — Trực quan hoá & phân tích | 60đ | **Cao nhất** |
| 4 | `04_forecasting.md` | Phần 3 — Mô hình dự báo doanh thu | 20đ | Cao |
| 5 | `05_report.md` | Báo cáo NeurIPS (4 trang) | — | Cuối cùng |
| 6 | `06_submission.md` | Nộp bài & checklist | — | Cuối cùng |

## Quy tắc thực hiện

1. **Một section / lần**: Hoàn thành section hiện tại trước khi bắt đầu section tiếp theo
2. **Verify trước khi chuyển**: Mỗi section có checklist kiểm tra ở cuối — phải pass hết
3. **Output rõ ràng**: Mỗi section ghi rõ file output và vị trí lưu
4. **Không dùng dữ liệu ngoài**: Tất cả features và phân tích chỉ từ 14 CSV được cung cấp
5. **Reproducibility**: Đặt `random_seed = 42` ở mọi nơi cần thiết
6. **Ghi CHANGELOG.md**: Sau mỗi thay đổi quan trọng

## Cấu trúc thư mục output

```text
USHIET-DATATHON26/
├── data/               # Raw CSV (không chỉnh sửa)
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_mcq_answers.ipynb
│   ├── 03_eda_analysis.ipynb
│   └── 04_forecasting.ipynb
├── src/                # Reusable Python modules
│   ├── data_loader.py
│   ├── features.py
│   └── utils.py
├── figures/            # Biểu đồ xuất cho report
├── outputs/            # Kết quả trung gian
├── submission/         # submission.csv cuối cùng
├── docs/report/        # LaTeX report
└── plan/               # Các file kế hoạch này
```
