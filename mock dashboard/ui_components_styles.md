# UI Components - Fonts and Colors Documentation

## Tổng quan
File này chứa thông tin về font chữ và mã màu được sử dụng trong tất cả các component của ứng dụng dashboard.

## Fonts
### Font chính
- **Font Family**: 'Inter', sans-serif
- **Áp dụng cho**: Toàn bộ body của ứng dụng
- **Ghi chú**: Font chữ hiện đại, dễ đọc, được sử dụng cho tất cả text trong ứng dụng

## Màu sắc (Color Palette)

### Brand Colors (Màu thương hiệu)
- **Brand Neon**: #90FF00
  - Màu xanh lá neon sáng
  - Sử dụng cho: Logo, accent, highlights, borders active, text brand
- **Brand Deep**: #050505
  - Màu đen sâu
  - Sử dụng cho: Background dark theme, text dark

### Status Colors (Màu trạng thái)
- **Success**: #90FF00
  - Màu xanh lá sáng
  - Sử dụng cho: Icons success, text positive trends, bars positive
- **Error**: #FF3B3B
  - Màu đỏ
  - Sử dụng cho: Icons error, text negative trends, bars negative, borders error
- **Warning**: #FFB800
  - Màu vàng cam
  - Sử dụng cho: Icons warning, lines warning, highlights warning

### Theme Colors (Màu theme - Light Mode)
- **Background Main**: #FFFFFF
  - Màu trắng
  - Sử dụng cho: Background chính light mode
- **Background Card**: #FFFFFF
  - Màu trắng
  - Sử dụng cho: Background cards light mode
- **Text Main**: #0B1F3B
  - Màu xanh đen
  - Sử dụng cho: Text chính light mode
- **Text Sub**: #64748B
  - Màu xám xanh
  - Sử dụng cho: Text phụ, labels light mode
- **Border UI**: #E2E8F0
  - Màu xám nhạt
  - Sử dụng cho: Borders, dividers light mode

### Theme Colors (Màu theme - Dark Mode)
- **Background Main**: #050505
  - Màu đen sâu
  - Sử dụng cho: Background chính dark mode
- **Background Card**: #0A0A0A
  - Màu đen nhạt hơn
  - Sử dụng cho: Background cards dark mode
- **Text Main**: #FFFFFF
  - Màu trắng
  - Sử dụng cho: Text chính dark mode
- **Text Sub**: #94A3B8
  - Màu xám xanh nhạt
  - Sử dụng cho: Text phụ, labels dark mode
- **Border UI**: #FFFFFF10 (rgba(255,255,255,0.1))
  - Màu trắng trong suốt 10%
  - Sử dụng cho: Borders, dividers dark mode

## Components và Styles

### Dashboard Card (.dashboard-card)
- **Background**: var(--bg-card) (#FFFFFF light, #0A0A0A dark)
- **Border**: var(--border-ui) (#E2E8F0 light, #FFFFFF10 dark)
- **Hover Border**: rgba(144, 255, 0, 0.3) (#90FF0033)
- **Hover Shadow**: shadow-md

### KPI Card (KPICard component)
- **Label (.kpi-label)**: var(--text-sub), font-bold, uppercase, tracking-widest, text-[10px]
- **Value (.kpi-value)**: var(--text-main), text-2xl, font-bold, tracking-tight
- **Trend Text**: text-status-success (#90FF00) cho positive, text-status-error (#FF3B3B) cho negative

### Slicer Dropdown (.slicer-dropdown)
- **Background**: var(--bg-card)
- **Border**: var(--border-ui)
- **Text**: var(--text-sub), text-[11px], font-semibold
- **Active State**: border-brand-neon (#90FF00), bg-brand-neon/10 (rgba(144,255,0,0.1)), color: #90FF00
- **Hover**: border-brand-neon

### Sidebar (.sidebar-link)
- **Text**: text-slate-500, text-xs, font-bold, uppercase, tracking-widest
- **Active**: text-brand-neon (#90FF00), border-r-4 border-brand-neon, background: rgba(144, 255, 0, 0.05)
- **Hover**: text-brand-neon, transition-colors duration-200

### Insight Box (.insight-box)
- **Border Left**: 4px solid #90FF00
- **Background**: rgba(144, 255, 0, 0.05)

### Section Title (SectionTitle component)
- **Title**: text-xs, font-black, uppercase, tracking-widest, border-l-3 border-brand-neon (#90FF00), pl-2
- **Subtitle**: text-[9px], text-slate-400, font-bold, italic

### Charts
- **Grid Color**: #00000008 (light), #ffffff10 (dark)
- **Text Color**: #64748b (light), #94a3b8 (dark)
- **Primary Fill**: #90FF00 (brand neon)
- **Secondary Fill**: #0B1F3B (light), #fff (dark)
- **Error Fill**: #FF3B3B
- **Warning Fill**: #FFB800

### Tables
- **Header Background**: bg-slate-50 text-slate-500 (light), bg-white/5 text-slate-500 (dark)
- **Row Hover**: bg-brand-neon/5
- **Text**: text-slate-900 (light), text-white (dark)

### Buttons
- **Theme Toggle**: bg-white/5 border-white/10 text-white (dark), bg-slate-50 border-slate-200 text-slate-600 (light)
- **Hover**: bg-white/10 (dark), bg-slate-100 (light)

### Loading Spinner
- **Border**: border-slate-800 border-t-brand-neon (#90FF00)

## Ghi chú bổ sung
- Ứng dụng hỗ trợ 2 theme: Light và Dark
- Tất cả màu sắc sử dụng CSS custom properties (variables) để dễ dàng thay đổi theme
- Font chữ duy nhất là Inter, được áp dụng globally
- Màu brand neon (#90FF00) là màu chủ đạo, xuất hiện trong logo, accents, và highlights
- Các component sử dụng Tailwind CSS classes kết hợp với custom CSS variables