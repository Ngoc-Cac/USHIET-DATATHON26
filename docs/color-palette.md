# Color Palette — VinDatathon 2026 Streamlit App

Bảng mã màu sử dụng trong toàn bộ Streamlit dashboard (`streamlit_app/theme.py`).
Phong cách: light theme, accent lime/olive khớp template `template.jpg`.

---

## Brand · Lime / Olive (chủ đạo)

| Token | Hex | Preview | Dùng cho |
|---|---|---|---|
| `LIME` | `#B8E835` | ![](https://placehold.co/20x20/B8E835/B8E835.png) | Accent chính: tag header, button, slider, KPI dot, sidebar active |
| `LIME_STRONG` | `#9DCB1F` | ![](https://placehold.co/20x20/9DCB1F/9DCB1F.png) | Border của bar lime, đường viền active state |
| `LIME_DARK` | `#6FA82B` | ![](https://placehold.co/20x20/6FA82B/6FA82B.png) | Line chart, secondary bar, healthy state |
| `LIME_SOFT` | `#E8F5C8` | ![](https://placehold.co/20x20/E8F5C8/E8F5C8.png) | Narrative box background, chart-level badge |

---

## Background & Surface

| Token | Hex | Preview | Dùng cho |
|---|---|---|---|
| `BG` | `#F5F6F0` | ![](https://placehold.co/20x20/F5F6F0/F5F6F0.png) | Background tổng app, neutral cell trong heatmap divergent |
| `CARD` | `#FFFFFF` | ![](https://placehold.co/20x20/FFFFFF/FFFFFF.png) | Card / container background (KPI card, chart wrapper) |
| `BORDER` | `#E5E7E0` | ![](https://placehold.co/20x20/E5E7E0/E5E7E0.png) | Border 1px của card + chart container |

---

## Text

| Token | Hex | Preview | Dùng cho |
|---|---|---|---|
| `DARK` | `#1A1F14` | ![](https://placehold.co/20x20/1A1F14/1A1F14.png) | Text chính, sidebar background, KPI value |
| `GREY` | `#6B7280` | ![](https://placehold.co/20x20/6B7280/6B7280.png) | Caption, muted text, axis tick label |

---

## Status / Semantic

| Token | Hex | Preview | Dùng cho |
|---|---|---|---|
| `AMBER` | `#F59E0B` | ![](https://placehold.co/20x20/F59E0B/F59E0B.png) | Warning (Reorder, discount line, return rate giữa) |
| `RED` | `#DC2626` | ![](https://placehold.co/20x20/DC2626/DC2626.png) | Danger (Stockout, negative margin, cảnh báo) |

---

## Sidebar (dark olive)

| Hex | Preview | Dùng cho |
|---|---|---|
| `#1A1F14` | ![](https://placehold.co/20x20/1A1F14/1A1F14.png) | Sidebar background (= `DARK`) |
| `#2A301F` | ![](https://placehold.co/20x20/2A301F/2A301F.png) | Sidebar nav hover state |
| `#242A1B` | ![](https://placehold.co/20x20/242A1B/242A1B.png) | Sidebar input background |
| `#39402B` | ![](https://placehold.co/20x20/39402B/39402B.png) | Sidebar input border |
| `#E8EDD8` | ![](https://placehold.co/20x20/E8EDD8/E8EDD8.png) | Sidebar text on dark |
| `#8E9379` | ![](https://placehold.co/20x20/8E9379/8E9379.png) | Sidebar muted label |

---

## Category Palette `CAT_PALETTE` (10 màu)

Dùng cho `color_discrete_sequence` khi chart cần phân biệt nhiều category/source/segment.

| # | Hex | Preview |
|---|---|---|
| 1 | `#9DCB1F` | ![](https://placehold.co/20x20/9DCB1F/9DCB1F.png) |
| 2 | `#6FA82B` | ![](https://placehold.co/20x20/6FA82B/6FA82B.png) |
| 3 | `#3F6B17` | ![](https://placehold.co/20x20/3F6B17/3F6B17.png) |
| 4 | `#C9E866` | ![](https://placehold.co/20x20/C9E866/C9E866.png) |
| 5 | `#7C9F2C` | ![](https://placehold.co/20x20/7C9F2C/7C9F2C.png) |
| 6 | `#BFD877` | ![](https://placehold.co/20x20/BFD877/BFD877.png) |
| 7 | `#4F7A1B` | ![](https://placehold.co/20x20/4F7A1B/4F7A1B.png) |
| 8 | `#A8C940` | ![](https://placehold.co/20x20/A8C940/A8C940.png) |
| 9 | `#5C8222` | ![](https://placehold.co/20x20/5C8222/5C8222.png) |
| 10 | `#D9EE99` | ![](https://placehold.co/20x20/D9EE99/D9EE99.png) |

---

## RFM Segment Colors `SEGMENT_COLORS`

Mapping cố định cho 11 RFM segment, dùng ở D2 RFM bar + treemap.

| Segment | Hex | Preview | Ý nghĩa |
|---|---|---|---|
| Champions | `#6FA82B` | ![](https://placehold.co/20x20/6FA82B/6FA82B.png) | Top tier — giữ chân |
| Loyal Customers | `#9DCB1F` | ![](https://placehold.co/20x20/9DCB1F/9DCB1F.png) | Khách trung thành |
| Potential Loyalists | `#B8E835` | ![](https://placehold.co/20x20/B8E835/B8E835.png) | Tiềm năng nâng cấp |
| New Customers | `#C9E866` | ![](https://placehold.co/20x20/C9E866/C9E866.png) | Khách mới |
| Promising | `#D9EE99` | ![](https://placehold.co/20x20/D9EE99/D9EE99.png) | Hứa hẹn |
| Need Attention | `#F59E0B` | ![](https://placehold.co/20x20/F59E0B/F59E0B.png) | Cần can thiệp |
| About to Sleep | `#F97316` | ![](https://placehold.co/20x20/F97316/F97316.png) | Sắp ngủ |
| At Risk | `#EF4444` | ![](https://placehold.co/20x20/EF4444/EF4444.png) | Rủi ro mất |
| Cannot Lose Them | `#B91C1C` | ![](https://placehold.co/20x20/B91C1C/B91C1C.png) | Win-back ngay |
| Hibernating | `#6B7280` | ![](https://placehold.co/20x20/6B7280/6B7280.png) | Ngủ đông |
| Lost | `#374151` | ![](https://placehold.co/20x20/374151/374151.png) | Mất khách |

---

## Inventory Health (D3)

| Status | Hex | Preview |
|---|---|---|
| Healthy | `#6FA82B` (= `LIME_DARK`) | ![](https://placehold.co/20x20/6FA82B/6FA82B.png) |
| Reorder | `#F59E0B` (= `AMBER`) | ![](https://placehold.co/20x20/F59E0B/F59E0B.png) |
| Overstock | `#7C9F2C` | ![](https://placehold.co/20x20/7C9F2C/7C9F2C.png) |
| Stockout | `#DC2626` (= `RED`) | ![](https://placehold.co/20x20/DC2626/DC2626.png) |

---

## Heatmap Colorscales

### Diverging (margin / MoM growth)
Đỏ ↔ Trắng-be ↔ Xanh: `[[0, '#DC2626'], [0.5, '#F5F6F0'], [1, '#6FA82B']]` với `zmid=0`.

### Sequential (return rate / promo penetration)
Trắng-be → Amber → Đỏ: `[[0, '#F5F6F0'], [0.5, '#F59E0B'], [1, '#DC2626']]`.

### Sequential lime (cohort retention)
Trắng-be → Light lime → Lime → Olive: `[[0, '#F5F6F0'], [0.3, '#D9EE99'], [0.7, '#B8E835'], [1, '#6FA82B']]`.

---

## Phụ trợ (text màu trắng tươi)

| Hex | Preview | Ngữ cảnh |
|---|---|---|
| `#11150F` | ![](https://placehold.co/20x20/11150F/11150F.png) | Hero title đậm hơn `DARK` |
| `#F3F6E9` | ![](https://placehold.co/20x20/F3F6E9/F3F6E9.png) | Sidebar input text (sáng hơn `E8EDD8`) |

---

## Source

Toàn bộ tokens định nghĩa ở `streamlit_app/theme.py` (top of file). Khi sửa palette, update file này song song.

`.streamlit/config.toml` cũng có theme native:
```toml
primaryColor = "#9DCB1F"
backgroundColor = "#F5F6F0"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1A1F14"
```
