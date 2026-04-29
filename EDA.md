# EDA Storytelling Review

## 1. Executive summary

Dashboard hiện tại đã có nền tảng tốt cho phần **Descriptive** và một phần **Diagnostic**, nhưng chưa thật sự đủ mạnh để đạt trọn rubric về **Predictive** và **Prescriptive** nếu chỉ dựa vào các chart đang lên app Streamlit.

Đánh giá nhanh:

- Chất lượng visual: khá ổn, sạch, dễ đọc, có cấu trúc theo section.
- Chiều sâu phân tích: đang ở mức trung bình khá; một số insight mới dừng ở caption, chưa được chứng minh bằng visual riêng.
- Storytelling: đã có mạch `Revenue -> Customer -> Product -> Marketing`, nhưng phần nối nguyên nhân - hệ quả - hành động còn thiếu một số cầu nối.
- Mức sẵn sàng để thuyết trình: khoảng `70/100` cho phần dashboard storytelling; có thể lên `85+/100` nếu bổ sung vài visual rất trúng rubric.

Thông điệp kinh doanh lớn nhất đọc ra từ các chart hiện có là:

1. Doanh thu tăng trưởng theo mùa vụ rất rõ, nhưng chất lượng tăng trưởng không đồng đều vì margin bị bào mòn khi promo tăng mạnh.
2. Doanh thu đang tập trung mạnh vào một số category/SKU, đặc biệt là Streetwear, tạo tăng trưởng nhưng kéo theo rủi ro tập trung.
3. Giá trị khách hàng theo channel không chênh lệch quá lớn ở mặt bằng chung, nên lợi thế cạnh tranh nằm ở retention và CRM hơn là chỉ đổ thêm acquisition.
4. Vấn đề vận hành lớn nhất không phải một lỗi đơn lẻ mà là nghịch lý kép: vừa stockout cao vừa overstock cao.
5. Returns hiện không bùng nổ theo category tổng thể, nhưng cấu trúc lý do trả hàng cho thấy bài toán sizing và chất lượng sản phẩm là đáng ưu tiên hơn delivery.

## 2. Có đọc được visual không?

Có. Mình đã đọc trực tiếp các PNG trong `figures/` và đối chiếu với nội dung dashboard hiện tại, gồm:

- `A1/A2/A3` cho revenue
- `B1/B2/B3` cho customer
- `C1/C2/C3` cho product
- `D1/D2/D3` cho promotion
- `E1/E2` cho operations
- `F1/F2/F3` cho returns
- `X1/X2` cho cross-functional story
- `executive_summary_dashboard.png`

Vì vậy phần nhận xét dưới đây không chỉ dựa vào tên chart hay code, mà dựa trên chính visual đã render.

## 3. Review theo từng section

### D1. Revenue & Profitability

#### Những gì đang làm tốt

- `Revenue & Gross Profit (monthly)` cho thấy seasonality rõ và có baseline MA-12.
- `MoM Growth Heatmap` giúp nhìn chu kỳ tháng/quý tốt hơn line chart.
- `Margin vs Discount Penetration` là chart chẩn đoán tốt vì nối được tăng trưởng với chất lượng lợi nhuận.
- `Category Pareto + Margin` tạo được góc nhìn ưu tiên danh mục.

#### Story business có thể kể

- Giai đoạn 2013-2018 là pha mở rộng mạnh, với đỉnh doanh thu quanh các tháng cao điểm.
- Sau đó doanh thu giảm về mặt bằng thấp hơn, cho thấy tăng trưởng không tuyến tính mà phụ thuộc mùa vụ và chất lượng demand.
- Promo xuất hiện như một cần gạt ngắn hạn cho volume, nhưng mỗi đợt discount mạnh thường kéo margin xuống.
- Kết luận CEO-level: bài toán không còn là “làm sao bán nhiều hơn”, mà là “bán đúng mùa, đúng category, đúng mức discount”.

#### Còn thiếu gì

- Chưa có **chart decomposition thật sự** cho `Revenue = Orders x AOV`. File `A2_revenue_decomposition.png` làm việc này tốt hơn chart D1 hiện tại.
- Chưa có **seasonality forecast view** hoặc band dự báo theo tháng/quý. Caption “predictive” hiện vẫn là text, chưa phải evidence.
- Chưa có **bridge chart / contribution chart** để trả lời revenue giảm là do volume, giá trị đơn, hay mix category.

#### Visual nên bổ sung

- Ưu tiên cao: `Orders vs AOV decomposition`.
- Ưu tiên cao: `Seasonality calendar / forecast next-quarter`.
- Ưu tiên vừa: `Year-over-year bridge` cho revenue change.

### D2. Customer Segmentation & Lifecycle

#### Những gì đang làm tốt

- RFM + avg LTV giúp phân biệt “đông khách” và “khách giá trị cao”.
- Cohort heatmap là một trong những visual mạnh nhất vì bám sát retention.
- Acquisition channel revenue/LTV tạo nền cho quyết định phân bổ ngân sách.

#### Story business có thể kể

- Chảy máu khách hàng diễn ra sớm, đặc biệt trong các tháng đầu sau mua đầu tiên.
- Không phải mọi channel đều mang khách hàng có cùng giá trị dài hạn.
- Trọng tâm tăng trưởng bền vững nên chuyển từ acquisition thuần sang lifecycle management: onboarding, repeat purchase, win-back.

#### Còn thiếu gì

- Chưa có visual thể hiện **demographic composition** rõ ràng trên dashboard, trong khi `B3_customer_value.png` cho thấy age/gender có thể kể thêm câu chuyện ai là core buyer.
- Chưa có **scatter frequency vs monetary vs recency** để thấy trực quan cụm khách hàng.
- Chưa có **channel x cohort**: kênh nào giữ khách tốt hơn theo thời gian, không chỉ LTV snapshot.
- Chưa có **funnel retention action view**: new -> second order -> loyal.

#### Visual nên bổ sung

- Ưu tiên cao: `Customer value by age_group x gender`.
- Ưu tiên cao: `Repeat purchase / second-order conversion by channel`.
- Ưu tiên vừa: `RFM scatter` hoặc `segment migration`.

### D3. Product Performance, Returns, Inventory

#### Những gì đang làm tốt

- Top SKU revenue giúp chốt nhóm sản phẩm cần bảo vệ doanh thu.
- Return reasons chart có tác dụng định hướng root cause.
- Inventory health + price-margin scatter tạo được cầu nối giữa product strategy và operations.

#### Story business có thể kể

- Doanh thu tập trung vào một nhóm SKU nhỏ, nên bất kỳ lỗi stockout hay pricing sai trên top SKU đều có tác động lớn.
- Có những cụm sản phẩm bán tốt nhưng margin chưa tối ưu, trong khi một số cụm nhỏ hơn lại có economics lành mạnh hơn.
- Returns theo category tổng thể khá gần nhau, nghĩa là vấn đề không nằm ở “category nào tệ nhất” mà nằm ở mix size, quality, và mô tả sản phẩm.

#### Còn thiếu gì

- Dashboard hiện tại **chưa có Pareto chart sản phẩm**, trong khi `C2_pareto_segment.png` là một visual kể chuyện rất mạnh.
- Chưa có `Category growth trajectory`, nên phần predictive ở D3 còn yếu.
- Chưa có `Return rate by category x size`, trong khi `F2` cho thấy sizing là một insight rõ.
- Chưa có `Rating vs Return` hay `rating bucket vs return rate`, trong khi `F3` tạo được góc predictive tốt.
- Chưa có visual nối trực tiếp `stockout -> lost sales / units sold`, dù `E2` đã có scatter khá mạnh.

#### Visual nên bổ sung

- Ưu tiên rất cao: `Pareto Analysis: Product Revenue Concentration`.
- Ưu tiên rất cao: `Return Rate by Category x Size`.
- Ưu tiên cao: `Rating as predictor of return risk`.
- Ưu tiên cao: `Category growth trajectory`.
- Ưu tiên vừa: `Stockout days vs units sold / lost revenue proxy`.

### D4. Marketing & Channel Effectiveness

#### Những gì đang làm tốt

- Sessions by source và engagement scatter giúp nhìn chất lượng traffic.
- Channel LTV đưa được góc nhìn downstream, không chỉ top-of-funnel.
- Bounce trend hữu ích cho monitoring.

#### Story business có thể kể

- Traffic không đồng nghĩa với giá trị; một số nguồn có volume tốt nhưng engagement hoặc quality không tương xứng.
- Nếu chỉ tối ưu sessions, team marketing có thể tăng vanity metrics nhưng không tăng business value.
- Quyết định tốt hơn là tối ưu theo LTV-quality thay vì traffic thuần.

#### Còn thiếu gì

- D4 hiện nghiêng nhiều về **web traffic**, nhưng PDF và figures gợi ý section này nên có trọng tâm **promotion effectiveness** rõ hơn.
- Chưa có visual `with promo vs without promo` trên app, trong khi `D2_promo_effectiveness.png` là evidence rất mạnh rằng promo có thể tăng volume nhưng đốt margin.
- Chưa có `promotion penetration by category x year/quarter`, trong khi `D3_promo_category_heatmap.png` kể được mix promo rất rõ.
- Chưa có visual nối `revenue x traffic x active promotions` như `X1_cross_revenue_web_promo.png`.

#### Visual nên bổ sung

- Ưu tiên rất cao: `Promotion impact: with vs without promo`.
- Ưu tiên cao: `Promotion penetration heatmap by category`.
- Ưu tiên cao: `Revenue x Web Traffic x Active Promotions`.

## 4. Phần storytelling hiện tại đã đủ chưa?

Chưa đủ hẳn nếu mục tiêu là điểm rất cao ở rubric.

### Đã đủ ở đâu

- Có cấu trúc section rõ.
- Có KPI + chart + narrative caption.
- Có một phần logic từ descriptive sang diagnostic.

### Chưa đủ ở đâu

- Phần **Predictive** hiện phần lớn đang nằm trong câu chữ, chưa có visual riêng đủ mạnh.
- Phần **Prescriptive** mới là khuyến nghị chung, chưa có trade-off hoặc mức ưu tiên định lượng.
- Một số chart đang “đúng kỹ thuật” nhưng chưa “đắt business”.
- D3 và D4 chưa nối nhau thành chuỗi quyết định hoàn chỉnh: `promo -> margin -> return -> inventory`.

### Kết luận

Nếu đem dashboard hiện tại đi demo, câu chuyện sẽ nghe ổn nhưng chưa thật sắc.
Muốn lên level “business review” thay vì “EDA showcase”, cần thêm các chart giúp trả lời ba câu:

1. Điều gì đang tạo tăng trưởng thật sự?
2. Điều gì đang phá hủy lợi nhuận hoặc trải nghiệm?
3. Nếu chỉ được làm 3 việc trong quý tới, nên làm gì trước?

## 5. Các visual còn thiếu quan trọng nhất

Nếu chỉ được thêm ít visual, mình đề xuất theo thứ tự này:

1. `Revenue decomposition: Orders vs AOV`
2. `Promotion impact: with promo vs without promo`
3. `Pareto product concentration`
4. `Return rate by category x size`
5. `Stockout impact scatter`
6. `Revenue x traffic x active promos`
7. `Customer value by age/gender`
8. `Customer journey funnel`

## 6. Storyline nên dùng khi thuyết trình

### Mở đầu

Doanh nghiệp thời trang e-commerce này không gặp vấn đề về “thiếu nhu cầu” đơn thuần. Nhu cầu có thật, mùa vụ rõ, và traffic vẫn tăng. Vấn đề nằm ở chất lượng tăng trưởng: margin bị ăn mòn bởi promo, doanh thu tập trung vào ít category/SKU, và vận hành tồn kho chưa cân bằng.

### Chương 1. Growth quality

Doanh thu tăng theo mùa vụ nhưng không bền nếu phụ thuộc vào discount. Khi promo penetration tăng, margin có xu hướng giảm. Vì vậy tăng trưởng cần được đo bằng `gross profit` chứ không chỉ `revenue`.

### Chương 2. Customer economics

Giá trị khách hàng khác nhau theo channel, nhưng khác biệt không quá cực đoan. Cơ hội lớn hơn nằm ở việc kéo retention sau mua đầu tiên và nuôi nhóm có tiềm năng thành loyal/champions.

### Chương 3. Portfolio concentration

Một số category và SKU đang gánh phần lớn doanh thu. Streetwear tạo scale nhưng không vượt trội về margin; Outdoor có hồ sơ cân bằng hơn; GenZ nhỏ nhưng margin tốt. Cần quản trị portfolio theo cả scale lẫn unit economics.

### Chương 4. Promo discipline

Promo có tác dụng kéo volume nhưng không tự động tạo giá trị. Broad discount làm giảm margin nặng hơn mức tăng sản lượng. Vì vậy cần chuyển sang targeted promotion theo category, margin band, và elasticity.

### Chương 5. Operations and returns

Doanh nghiệp đang cùng lúc stockout cao và overstock cao, cho thấy cơ chế replenishment và assortment chưa tối ưu. Ở chiều trải nghiệm, returns không tăng mạnh do delivery, mà chủ yếu xoay quanh wrong size, defective, và not as described. Điều này chỉ ra ưu tiên là sizing guide, quality control, và product content.

### Kết thúc

Ba ưu tiên kinh doanh nên là:

1. Giảm promo đại trà, chuyển sang promo có điều kiện cho nhóm sản phẩm margin khỏe.
2. Bảo vệ top SKU/category bằng tồn kho chính xác hơn, đặc biệt các nhóm gánh doanh thu.
3. Giảm returns qua cải thiện size guidance, mô tả sản phẩm, và QA thay vì chỉ siết logistics.

## 7. Prescriptive recommendations

### Recommendation 1. Reallocate marketing and promo budget

- Giảm discount breadth trên các category/SKU margin thấp.
- Chỉ giữ promo mạnh cho nhóm có elasticity cao hoặc phục vụ clear inventory.
- KPI theo dõi: gross margin after promo, revenue lift per 1% discount, promo ROI by category.

### Recommendation 2. Build a top-SKU protection list

- Xác định top 20% SKU đóng góp phần lớn doanh thu.
- Đặt service level và safety stock cao hơn cho nhóm này.
- KPI theo dõi: stockout days, fill rate, lost-sales proxy, revenue at risk.

### Recommendation 3. Launch return-reduction sprint

- Ưu tiên category-size có wrong_size cao.
- Chuẩn hóa bảng size, ảnh fit model, và mô tả chất liệu/kích cỡ.
- KPI theo dõi: wrong_size return rate, defective return rate, refund amount, rating uplift.

### Recommendation 4. Retention-first CRM

- Thiết kế flows cho 30/60/90 ngày sau first order.
- Tách playbook cho `Potential Loyalists`, `At Risk`, và `Cannot Lose Them`.
- KPI theo dõi: M1 repeat rate, second-order conversion, win-back conversion, CLV uplift.

## 8. Kết luận cuối

Dashboard hiện tại **đã có xương sống tốt**, nhưng để thật sự “đủ storytelling” theo rubric của PDF thì cần thêm một lớp visual chứng minh cho các luận điểm predictive và prescriptive.

Nếu phải chốt ngắn gọn:

- `D1` ổn nhất về story.
- `D2` ổn nhưng cần thêm customer-value depth.
- `D3` là nơi còn thiếu nhiều visual quan trọng nhất.
- `D4` cần dịch trọng tâm từ web traffic thuần sang promo effectiveness và marketing economics.

Khi bổ sung đúng 5-8 visual trọng điểm, toàn bộ dashboard sẽ chuyển từ một bộ chart đẹp thành một câu chuyện kinh doanh hoàn chỉnh, có thể defend tốt trước judges.
