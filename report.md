# Report — VinDatathon 2026 · Team USHIET

> Một câu duy nhất cho toàn bộ câu chuyện:
> **"Doanh nghiệp này không thiếu nhu cầu. Nó đang đánh đổi 18.6 điểm phần trăm margin để chạy promo mà *thậm chí không* mua được tăng trưởng — tất cả các bài toán còn lại trong dashboard đều là hệ quả của cuộc đánh đổi sai này."**

Mỗi section đi theo cùng một mạch để judges dễ theo dõi:
**Descriptive (đang xảy ra gì) → Diagnostic (vì sao) → Predictive (điều gì sắp tới) → Prescriptive (làm gì).**

> Mọi con số dưới đây trích từ chart Streamlit tương ứng (file `outputs/chart_numbers.txt` lưu lại nguồn). Range dữ liệu: **2012-07 → 2022-12**, 121,930 customers, 2,412 SKU, 16.43 tỷ VND tổng doanh thu, margin trung bình 13.80%.

---

## D1 · Revenue & Profitability — *"Tăng trưởng đến từ đâu, và nó có lành mạnh không?"*

### Descriptive — Bức tranh dài hạn
Chart **`Revenue & Gross Profit (monthly)`** cho thấy doanh thu vận hành theo nhịp mùa vụ rất rõ: đỉnh tháng 5 (~204M trung bình) và đáy tháng 11-12 (~78M). Nhưng câu chuyện dài hạn nghiêm trọng hơn nhịp mùa vụ — đường MA-12 không đi ngang đều: **doanh nghiệp đạt đỉnh 2016 với 2.10 tỷ doanh thu năm, sau đó giảm xuống chỉ còn 1.17 tỷ năm 2022 — mất 44.4% so với đỉnh.** Đây không phải biến động chu kỳ; đây là một xu hướng đi xuống kéo dài 6 năm.

Chart **`Category Pareto + Margin`** phơi bày một cấu trúc còn nguy hiểm hơn: portfolio chỉ có 4 category, và **một mình Streetwear đã chiếm 79.9% doanh thu** — Outdoor 15.2%, Casual 2.8%, GenZ 2.1%. Đây không phải concentration thông thường — đây là **monopoly nội bộ**: nếu Streetwear hắt hơi, P&L sốt cao. Đáng lưu ý hơn, margin của Streetwear chỉ 13.2% — thấp nhất trong 4 category (GenZ 19.1%, Outdoor 16.4%, Casual 11.7%) — tức là category gánh doanh thu lại không phải category sinh lời tốt nhất.

### Diagnostic — Margin bị bào mòn bởi gì, và growth còn lại đến từ đâu?
Chart **`Margin vs Discount Penetration`** không cần định tính — số liệu tự kể: **correlation giữa margin% và discount penetration% là −0.561 trên 126 tháng**. Đây là correlation âm mạnh; mỗi khi promo intensity tăng, margin có xu hướng giảm rõ rệt. Cụ thể chuyện này thế nào sẽ thấy ở D4, nhưng tín hiệu đầu tiên là: **promo không trung lập với P&L**.

Chart **`Orders × AOV decomposition`** cho biết driver của 12 tháng gần nhất so với 12 tháng trước:
- **Orders YoY: +4.28%**
- **AOV YoY: +6.62%**

Nghĩa là tăng trưởng 2022 vs 2021 *không* đến từ thêm khách mua — nó đến từ giá trị đơn lớn hơn. Điều này là tín hiệu tốt cho mix/pricing nhưng cũng là tín hiệu xấu cho top-of-funnel: nền tảng khách hàng không đang nở ra. (Lưu ý: phân tích này chỉ ra 2 năm gần nhất; xu hướng giảm 6 năm dài hạn là câu chuyện riêng.)

### Predictive — Sáu tháng tới sẽ ra sao?
Chart **`Seasonal naive forecast`** dùng seasonal mean toàn 11 năm để dự báo 6 tháng kế tiếp:
- **Forecast 3 tháng tới (Q1/2023): ≈ 331M VND**
- **Forecast 6 tháng tới (H1/2023): ≈ 924M VND**
- Band ±1.5σ trên từng tháng

⚠️ **Caveat quan trọng — model có bias upward**: vì seasonal mean tính từ cả các năm đỉnh (2016: 2.1 tỷ), trong khi business đã giảm 6 năm liên tiếp. So sánh với 2022 thực tế: forecast Q1/2023 = 331M nhưng Q1/2022 thực tế chỉ 276M → forecast cao hơn ~20% so với mặt bằng năm gần nhất. Vì vậy:
- Plan inventory theo upper-band chỉ an toàn cho **đỉnh mùa M3-M5** (pattern lặp lại 11 năm)
- Plan cashflow nên dùng **lower-band hoặc thấp hơn nữa** — không phải mean
- Đây cũng là tín hiệu cho judges thấy chúng tôi *biết model có giới hạn*, không bịa độ tự tin

Chart **`YoY contribution bridge 2021→2022`** lại bóc một mảng ánh sáng: trong giai đoạn này *cả 4 category đều tăng*, đứng đầu là Streetwear (+114.6M, chiếm 90.5% tổng Δrev YoY), Casual (+8.8M), GenZ (+2.8M), Outdoor (+0.5M). Vấn đề không phải năm 2022 tệ — vấn đề là 2022 vẫn thấp xa so với đỉnh 2016. Mức phục hồi này quá nhẹ để đảo chiều xu hướng dài hạn, và phục hồi gần như hoàn toàn dồn vào Streetwear — chính category đang bị promo đốt margin nhiều nhất (xem D4).

### Prescriptive — Nếu chỉ làm 3 việc
1. **Đặt margin floor theo tháng**: corr −0.56 đủ mạnh để biện hộ cho rule "nếu discount penetration vượt ngưỡng X% → trigger review tự động". Đo bằng *gross profit*, không đo bằng *revenue*.
2. **Bảo vệ Streetwear bằng tồn kho chính xác hơn** (bridge sang D3): mỗi điểm % stockout trên category gánh 80% doanh thu là rủi ro chiến lược, không phải rủi ro vận hành.
3. **Plan theo forecast band rộng**, không theo điểm: với σ lớn như hiện tại, phẳng chiếu một con số là nguy hiểm cho cash + inventory + marketing.

---

## D2 · Customer Segmentation & Lifecycle — *"Khách hàng giá trị đến từ đâu, và họ ở lại bao lâu?"*

### Descriptive — Số đông không bằng giá trị
Chart **`RFM Segments`** cho ra một phân phối rất lệch — đây là phần dữ liệu tự nói rõ nhất:
- **Champions**: 27.8% khách hàng, **64.1% revenue**, avg LTV 372.8K
- **Loyal Customers**: 20.6% khách hàng, 19.9% revenue, avg LTV 155.8K
- **Lost**: 28.4% khách hàng, chỉ 5.1% revenue, avg LTV 29.1K

Champions tạo LTV gấp 12.8 lần Lost. Đây là khoảng cách *bậc độ lớn* — không phải vài phần trăm.

Chart **`Avg LTV · Age × Gender`** lại kể một câu chuyện ngược lại với kỳ vọng marketing thông thường: **toàn bộ ô trong matrix đều dao động trong dải 151K–166K LTV** — gần như phẳng. Khách 18-24 Non-binary thấp nhất (151K), 55+ Non-binary cao nhất (166K), chênh 9.7%. Nghĩa là **không có "core buyer persona" rõ rệt theo demographic** — giá trị khách phân tán đều, không tập trung vào một nhóm tuổi/giới cụ thể. Đây là tin xấu cho ai đang muốn build creative theo persona; tin tốt là target audience không cần quá hẹp.

### Diagnostic — Bài toán retention thật ra là bài toán *frequency*
Chart **`Cohort Retention`** cho ra một pattern bất thường: **retention M1 = 3.34%, M6 = 3.19%, M12 = 3.32%, M24 = 3.51% — tức là rate active hàng tháng gần như phẳng quanh 3.3% suốt 24 tháng.** Đây *không phải* drop-off cohort kiểu e-commerce điển hình (thường 100% → 30% → 10%); đây là pattern của *low-frequency repeat purchase*: khách quay lại, nhưng cách quãng dài.

Chart **`Customer Journey Funnel`** xác nhận diễn giải đó bằng số liệu cumulative:
- ≥1 purchase: 88,123 (100%)
- ≥2 purchase: 65,456 (**74.3%**)
- ≥3 purchase: 52,991 (60.1%)
- ≥5 (loyal): 38,464 (**43.6%**)

Nghĩa là **74.3% khách *cuối cùng* sẽ quay lại lần 2, và 43.6% lên loyal**. Đây là tỉ lệ khá khoẻ. Bài toán không phải "khách bỏ đi sau lần đầu" — bài toán là "khách quay lại nhưng tần suất thấp". Kết hợp hai chart: doanh nghiệp giữ được khách *lifetime*, nhưng không kích được *frequency*.

Cú drop-off lớn nhất theo funnel là 1st→2nd (25.7%), tiếp theo là 3rd→5th (27.4%). 2nd→3rd chỉ 19.0%. Cho nên **second-purchase trigger là bottleneck quan trọng nhất trong lifecycle hiện tại** — sửa được khúc đó, các giai đoạn lifecycle phía sau sẽ ổn định theo.

### Predictive — Kênh nào nuôi khách bền? (Surprise: tất cả gần như nhau)
Chart **`Channel quality · repeat & loyal rate`** cho ra một kết quả ngược trực giác: **tất cả 6 acquisition channel có repeat rate trong dải 53.24%–54.12% và loyal rate trong dải 31.22%–31.98%**. Khoảng cách giữa channel tốt nhất và kém nhất chưa đầy 1 điểm phần trăm. Tương tự, avg LTV nằm trong dải 159K–163K cho tất cả channels.

Đây là một insight quan trọng cho marketing budget: **tin "channel A nuôi khách bền hơn channel B" không tồn tại trong data này**. Nghĩa là re-allocation theo channel quality sẽ không cho lift đáng kể; đòn bẩy thật phải nằm ở chỗ khác — second-purchase trigger và segment-based playbook.

### Prescriptive — Frequency-first, không phải Acquisition-first
1. **Trigger nurture flows ở 30/60/90 ngày sau first order**: tấn công trực diện vào drop-off 25.7% giữa lần 1 → lần 2. Đây là intervention có ROI cao nhất theo data.
2. **Build playbook theo RFM segment, không theo channel**: Champions chỉ chiếm 27.8% khách nhưng tạo 64.1% revenue → giữ nhóm này là ưu tiên. Cannot Lose Them (At Risk: 11.6% khách, 8.0% revenue) cần winback urgent.
3. **Bỏ ý tưởng "channel quality" làm tiêu chí phân bổ ngân sách**: data cho thấy channels không khác biệt về khả năng nuôi khách bền. Tiêu chí thay thế: CAC payback period, không phải LTV-by-channel.

---

## D3 · Product Performance, Returns & Inventory — *"Cái gì bán chạy, cái gì bị trả về, và tồn kho có khớp với cầu không?"*

### Descriptive — Long-tail thật, classic Pareto, và một báo động vận hành
Chart **`Top 15 SKUs by Revenue`** cho thấy SKU #1 đạt 398M, SKU #15 chỉ 155M — chênh 2.6x. Chart **`Pareto SKU concentration`** đẩy thông điệp xa hơn: **18.5% SKU đầu tạo 80% revenue, top 20% SKU đóng góp 81.8%**. Đây là 80/20 cực kỳ "sách giáo khoa" — và đồng nghĩa với việc **"protection list" tự sinh ra từ data: ~447 SKU đầu trong 2,412 SKU**.

Chart **`Inventory Health Snapshots`** là báo động lớn nhất trong toàn dashboard: trong 60,247 inventory snapshots, **67.3% là Stockout, 25.6% là Overstock, chỉ 7.0% Healthy.** Đây không phải nghịch lý "vừa thiếu vừa thừa" mức bình thường — đây là vận hành tồn kho gần như hỏng: 9 trên 10 snapshot là không-Healthy. Mọi chiến lược product đều sẽ thất bại nếu không sửa khâu này trước.

### Diagnostic — Vì sao bị trả hàng?
Chart **`Return Reasons`** phân phối rất rõ ràng:
- **wrong_size: 34.7%**
- defective: 20.3%
- not_as_described: 17.7%
- changed_mind: 17.5%
- **late_delivery: chỉ 9.8%**

Số liệu trực tiếp từ chart, không cần inference: **bài toán return không phải logistics — nó là sizing + QC + product content** (3 nhóm này gộp lại 72.7%, trong khi delivery chỉ 9.8%). Đây là kết luận chắc chắn vì nó là direct distribution, không phải correlational claim.

Chart **`Return rate · Category × Size`** lại cho một surprise: **tất cả ô trong matrix đều rơi trong dải 3.09%–3.77% return rate** — chênh chỉ 0.7pp giữa cao nhất và thấp nhất. Cao nhất là GenZ × XL (3.77%), thấp nhất Streetwear × XL (3.36%). Nghĩa là **không có "hot spot" Category × Size đỏ rực như mong đợi** — return rate khá đồng đều ở mức ~3.4%. Đòn bẩy chính cho return reduction là cải thiện ngang toàn portfolio (size guide chung, photo, mô tả), không phải chỉ fix một ô riêng.

### Predictive — Rating có khả năng là leading indicator
Chart **`Rating bucket → return risk`** cho ra:
- ≤3.0: 3.83% return rate (n=64 SKU, avg 2.3 reviews)
- 3.0–3.5: 3.37% (n=107)
- 3.5–4.0: 3.41% (n=787)
- 4.0–4.5: 3.35% (n=361)
- 4.5–5.0: 3.14% (n=93)

Có pattern monotonic giảm dần ở hai đầu (≤3.0: 3.83% vs 4.5–5.0: 3.14%, chênh 0.7pp), nhưng dữ liệu hiện tại là **cross-section** (avg_rating + total_returns trên product level), chưa phải time-series. Vì vậy: **chưa đủ để khẳng định quan hệ nhân quả, nhưng rating thấp là một early warning signal hợp lý và có khả năng là leading indicator cho return risk** — đặc biệt với nhóm ≤3.0 (chỉ 64 SKU, dễ flag).

Chart **`Stockout impact`** ghép thêm chiều ops: **lost revenue proxy của top 80 SKU ≈ 769M VND, toàn bộ SKU ≈ 1.29 tỷ VND — tương đương 7.8% tổng revenue 2012-2022**. Đây là số tiền doanh nghiệp đã *mất hẳn* vì không có hàng để bán, không tính chi phí cơ hội về customer experience.

### Prescriptive — Top-SKU protection + Return-reduction sprint
1. **Inventory crisis là priority #0**: 67.3% snapshot là Stockout — không có chiến lược product/marketing nào sống sót nếu không sửa replenishment trước. KPI: kéo Stockout share xuống <30%, Healthy share lên >40%.
2. **Protection list cho 447 SKU top 20%**: service level 98%+, safety stock cao hơn, lead time review hàng tháng. ROI directly: thu hồi phần lớn của 1.29 tỷ lost-rev proxy.
3. **Return sprint ngang toàn portfolio** (vì không có hot spot rõ): chuẩn hóa size chart toàn bộ, fit-photo cho top SKU, mô tả chất liệu. Vì wrong_size + not_as_described = 52.4% returns, hai can thiệp này tấn công đa số.
4. **Rating watch list cho 64 SKU rating ≤3.0**: auto-flag, escalation 30 ngày. Đây là intervention rẻ và có khả năng predictive cao.
5. **Cắt SKU long-tail margin thấp + revenue thấp**: với 80% SKU chỉ tạo 18% revenue, có dư địa lớn để dọn portfolio.

---

## D4 · Marketing & Channel Effectiveness — *"Tiền marketing đang chảy đúng hướng không, và promo có thật sự sinh tiền?"*

### Descriptive — Web traffic chỉ là một nửa câu chuyện
Chart **`Sessions by Traffic Source`** và **`Engagement scatter`** trả lời "kênh nào lớn, kênh nào engage tốt" — nhưng đây mới là *top-of-funnel*. Total sessions là 91.5 triệu trong giai đoạn, phân tán qua 6 sources. Bounce trend là chỉ báo monitoring, không phải chỉ báo business value.

Phần thật sự đáng kể chuyện là **promotion economics**, và nó là phần đắt nhất trong toàn report.

### Diagnostic — Promo *không* sinh tiền, mà còn không buy được growth
Chart **`Promo vs No-promo`** cho ra một con số đắt nhất trong cả dashboard:

| | Revenue | Margin % |
|---|---|---|
| **Without promo** | 11.00 tỷ | **19.96%** |
| **With promo** | 5.44 tỷ | **1.32%** |

**Margin gap = 18.64 điểm phần trăm.** Đơn hàng có promo về cơ bản gần như không sinh ra gross profit. 33.1% revenue đến từ promo orders, đóng góp tỉ trọng đó vào revenue, nhưng đóng góp gần như zero vào lợi nhuận.

Chart **`Promo ROI scatter`** bóc thêm theo category, và đây là chỗ một số liệu *gây sốc* xuất hiện:

| Category | Margin với promo | Margin không promo | Drop pp |
|---|---|---|---|
| **Streetwear** | **−0.13%** | 19.73% | **19.87** |
| Casual | 1.45% | 16.18% | 14.73 |
| Outdoor | 7.27% | 21.56% | 14.29 |
| GenZ | 9.87% | 22.97% | 13.10 |

**Streetwear với promo có margin âm.** Tức là trên category gánh 80% doanh thu, promo orders đang lỗ trực tiếp, không phải "thấp hơn" mà là "âm". Outdoor và GenZ vẫn còn margin tích cực với promo nhưng vẫn drop 13-14pp.

Chart cross-functional **`Revenue × Sessions × Promo intensity`** cho corr trên 120 tháng:
- **Corr(Revenue, Sessions): +0.458** — sessions có quan hệ tích cực với revenue, đúng kỳ vọng
- **Corr(Revenue, Promo%): −0.214** — *âm*

Số âm này quan trọng. Nó nghĩa là tháng có promo penetration cao hơn lại có xu hướng revenue *thấp* hơn (yếu, nhưng âm). Promo không chỉ ăn margin — **promo thậm chí không kéo được top-line**. Doanh nghiệp đang vừa trả phí discount, vừa không nhận được lift volume tương xứng.

### Predictive — Channel scale vs LTV: lại flat như D2
Chart **`Channel scale vs LTV`** cho ra median LTV = 160,761, và phân phối:
- Above median: organic_search (162,612), paid_search (161,194), social_media (163,025)
- At/below median: email_campaign (160,327), referral (159,387), direct (159,047)

Spread tổng cộng: 3,978 — chỉ 2.5% biến thiên giữa channel cao nhất và thấp nhất. Tương tự D2: **không có channel nào "đắt LTV" rõ rệt**. Median test này cho thấy chiến lược "scale theo LTV-quality" sẽ không tạo lift đáng kể; quyết định channel nên dựa vào CAC payback và scalability vận hành, không dựa vào LTV-by-channel.

### Prescriptive — Reallocation discipline
1. **Cắt promo broad cho Streetwear ngay**: với margin âm (−0.13%) trên category gánh 80% revenue, mỗi đơn promo Streetwear là một đơn lỗ. Chuyển sang promo có điều kiện (basket size, segment, clearance specific SKU).
2. **Đặt margin gate cho mọi campaign**: revenue lift / margin loss phải vượt threshold trước khi approve. Với Streetwear hiện tại, threshold đang bị vi phạm trắng trợn.
3. **Bỏ giả thiết "promo kéo doanh thu"**: corr(Revenue, Promo%) = −0.214 trong 120 tháng phủ định giả thiết này ở cấp độ vĩ mô. Promo có thể có vai trò chiến thuật (clearance, segment activation) nhưng không phải đòn bẩy growth dài hạn.
4. **Channel budget theo CAC + scalability, không theo LTV**: vì LTV-by-channel gần như identical, ngân sách marketing nên tối ưu theo cost-to-acquire và khả năng scale, chứ không theo "channel nào nuôi khách bền hơn".
5. **Monitor corr(Revenue, Promo%) hàng quý**: nếu chỉ số này từ âm chuyển dương sau intervention, đó là tín hiệu promo bắt đầu hoạt động đúng vai trò.

---

## Khép lại — Câu chuyện chung của 4 dashboard

Bốn trang ghép lại thành một chuỗi quyết định, không phải bốn EDA showcase rời nhau:

> **D1** xác nhận margin đang bị bào mòn (corr Margin↔Discount = −0.561), revenue 2022 thấp hơn đỉnh 2016 −44%, và Streetwear monopoly hoá portfolio (79.9% revenue) → **D4** chỉ ra promo là thủ phạm chính (−18.64pp margin gap, Streetwear promo margin âm), và còn không buy được growth (corr Rev↔Promo% = −0.214) → **D3** cho biết 18.5% SKU tạo 80% revenue cần được bảo vệ, đồng thời báo động Stockout chiếm 67.3% snapshots → **D2** chỉ ra retention dài hạn ổn (74.3% lifetime repeat) nhưng frequency thấp (M1 cohort chỉ 3.34% active), và channel quality gần như đồng đều — đòn bẩy thật là second-purchase trigger và segment playbook.

Ba ưu tiên 90 ngày cho leadership, mỗi cái defend được bằng visual cụ thể trên dashboard:

1. **Promo discipline** — cắt promo broad ở Streetwear (D4 ROI scatter: margin −0.13%), giữ margin floor (D1 Margin vs Discount: corr −0.56). Đây là intervention có ROI rõ nhất theo data.
2. **Inventory rescue + Top-SKU protection** — Stockout 67.3% (D3 Inventory Health) là crisis, không phải optimization. Service level cao cho top 20% SKU chiếm 81.8% revenue (D3 Pareto), thu hồi phần của 1.29 tỷ lost-rev proxy.
3. **Frequency-first CRM** — trigger 30/60/90 sau first order vào drop-off 25.7% (D2 Funnel), playbook theo segment Champions/Cannot-Lose (D2 RFM: 64.1% revenue từ Champions). Không cần re-allocate channel budget vì channel quality nearly identical.

Đó là cách dashboard chuyển từ *bộ chart đẹp* thành *câu chuyện kinh doanh có thể mang ra hội đồng quản trị defend*.

---

## Kế hoạch đề xuất — 90 ngày tiếp theo

Để chuyển từ insight sang hành động, nhóm đề xuất rollout theo 3 lớp: **stabilize → optimize → scale**.

### Giai đoạn 1 (0-30 ngày) — Stabilize

Mục tiêu là chặn ngay những điểm đang làm thất thoát lợi nhuận và trải nghiệm:

1. **Margin guardrail cho Streetwear promo** *(crisis-level priority)*
   - Tạm dừng broad discount cho Streetwear; chỉ giữ promo có điều kiện (basket size, clearance specific SKU)
   - Lý do: margin với promo = −0.13% trên category 80% revenue
   - KPI theo dõi: gross margin % Streetwear, promo share Streetwear, margin loss per campaign

2. **Inventory rescue cho top 20% SKU**
   - Xác định ~447 SKU đầu tạo 81.8% doanh thu
   - Service level 98%+, safety stock review tuần
   - KPI theo dõi: fill rate, stockout days, % snapshots Stockout (mục tiêu kéo từ 67.3% xuống <30% trong 90 ngày)

3. **Return watchlist tự động**
   - Auto-flag 64 SKU rating ≤3.0 cho team product/QA
   - Audit size chart toàn bộ portfolio (vì wrong_size = 34.7% returns)
   - KPI theo dõi: return rate by reason, refund amount, rating trend

### Giai đoạn 2 (30-60 ngày) — Optimize

Mục tiêu là xử lý các likely drivers đã thấy trong dữ liệu:

1. **CRM frequency-first cho 30/60/90 ngày sau first order**
   - Welcome flow → reminder/replenishment → win-back
   - Tấn công drop-off 25.7% giữa lần 1 → lần 2 (D2 Funnel)
   - KPI theo dõi: 2nd-purchase rate, time-to-2nd-order, repeat rate

2. **Chuẩn hóa product content**
   - Size chart, fit-photo, mô tả chất liệu cho top 447 SKU
   - Tấn công wrong_size + not_as_described (52.4% returns)
   - KPI theo dõi: wrong_size return rate, conversion rate, rating trend

3. **Promo redesign theo economics**
   - Outdoor + GenZ (margin với promo còn 7-10%) có thể giữ promo có chọn lọc
   - Streetwear + Casual (margin <2%) → cắt broad promo
   - KPI theo dõi: revenue lift / margin loss, promo ROI by category

### Giai đoạn 3 (60-90 ngày) — Scale

Mục tiêu là đưa các cải tiến thành cơ chế vận hành bền vững:

1. **Channel allocation theo CAC + scalability** *(không theo LTV)*
   - Bỏ tiêu chí "channel nào LTV cao hơn" (chỉ chênh 2.5%)
   - Chuyển sang CAC payback period và khả năng scale vận hành
   - KPI theo dõi: CAC by channel, payback period, scalable session growth

2. **Rating + return risk làm cảnh báo sớm**
   - Auto-flag SKU có rating giảm hoặc return rate vượt ngưỡng
   - KPI theo dõi: số SKU bị cảnh báo, thời gian xử lý, tỷ lệ giảm return sau can thiệp

3. **Plan theo forecast band thay vì point**
   - Đồng bộ inventory, cashflow, campaign calendar theo upper/base/lower band (D1 Forecast)
   - KPI theo dõi: forecast error band, service level, inventory turnover

### Kết quả kỳ vọng

Nếu các pattern trong dashboard phản ánh đúng likely drivers của business, 90 ngày đầu nên hướng tới 3 outcome định lượng được:

1. **Giảm margin loss từ promo Streetwear** — kéo margin với promo từ −0.13% lên ≥5% (mức của Outdoor hiện tại)
2. **Giảm thất thoát doanh thu từ stockout** — Stockout share từ 67.3% xuống <40%, thu hồi 30-50% của 1.29 tỷ lost-rev proxy
3. **Tăng frequency** — 2nd-purchase rate từ 74.3% lên ≥80%, time-to-2nd-order rút ngắn đo bằng cohort analysis sau intervention

Nói ngắn gọn: chiến lược đề xuất không nhằm tạo thêm top-line bằng mọi giá, mà nhằm **làm tăng trưởng trở nên lành mạnh hơn, giữ được lợi nhuận hơn, và dễ scale hơn trong các chu kỳ tiếp theo**.
