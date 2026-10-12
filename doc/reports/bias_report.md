# Đánh giá LLM Judge Phase B

Nhóm: Nhóm 1 - AITC K4

Người phụ trách: Phùng Quốc Việt (MSSV: K4-PQV-02)

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T14:35:05.300086+00:00.
Models generation/judge: generation: gpt-4o-mini-2024-07-18; judge: gpt-4o-mini.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ
fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

| ID | Candidate A | Candidate B | Winner Pass 1 | Winner Pass 2 (quy về gốc) | Final Winner | Position Consistent | Scores Pass 1 (A/B) | Scores Pass 2 (A/B) | Reasoning Tóm tắt |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc khi kết hôn. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | B | B | B | True | A: 0.8, B: 1.0 | A: 0.8, B: 1.0 | Answer B đầy đủ hơn vì chỉ rõ 3 ngày nghỉ là 'có lương' theo đúng chính sách tham chiếu. |
| 5 | Cần thêm phê duyệt Kế toán trưởng. | Cần Giám đốc phòng ban phê duyệt. | B | A | tie | False | A: 0.3, B: 0.7 | A: 0.5, B: 0.0 | Đảo vị trí làm thay đổi góc nhìn đánh giá giữa hai đáp án đều chưa chuẩn xác (cần CEO phê duyệt). Bất đồng nên trả tie. |
| 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là **1 tháng lương**. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | A | A | A | True | A: 1.0, B: 0.7 | A: 1.0, B: 0.8 | Answer A nêu trọn vẹn điều kiện 'từ 6 tháng trở lên' và nhấn mạnh chuẩn xác mức 1 tháng lương. |
| 21 | Nhân viên có 9 năm thâm niên sẽ được 18 ngày phép... Về lương, nhân viên sẽ được hưởng lương trong thời gian nghỉ phép... | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | A | B | tie | False | A: 0.9, B: 0.7 | A: 0.7, B: 1.0 | Khi đảo thứ tự, LLM ưu tiên tính súc tích của B ở lượt sau thay vì giải thích chi tiết của A ở lượt đầu. Bất đồng nên trả tie. |
| 41 | Nhân viên được nghỉ **15 ngày phép năm**. | Nhân viên được nghỉ 12 ngày phép năm. | A | A | A | True | A: 1.0, B: 0.0 | A: 1.0, B: 0.2 | Answer A chính xác theo phiên bản chính sách v2024 hiện hành (15 ngày), Answer B sai do theo quy định cũ v2023 (12 ngày). |

Position bias count/rate: 2 / 0.400 (40.0%).
Verbosity win rate: 1.000 (100.0%); decisive cases: 3.

**Phân tích các case không nhất quán và thiên lệch độ dài (Verbosity):**
- **Về Position Bias (2/5 cases = 40%)**: Hai câu hỏi ID 5 và ID 21 bị ảnh hưởng mạnh bởi vị trí xuất hiện của câu trả lời. 
  - Tại câu ID 5, cả hai candidate đều không trích xuất đúng thẩm quyền CEO (A đề cập Kế toán trưởng, B đề cập Giám đốc phòng ban). Khi đặt B ở vị trí thứ hai ở Pass 1, model thiên vị B; nhưng khi hoán đổi ở Pass 2, model lại thiên vị A.
  - Tại câu ID 21, câu hỏi bao gồm 2 vế (ngày phép và khoảng lương). Candidate A trả lời chi tiết cách tính ngày phép nhưng diễn giải dài dòng về lương khi nghỉ phép; Candidate B súc tích và nêu đúng khoảng lương Senior (20-35 triệu). Sự giằng co giữa tiêu chí 'đầy đủ' và 'súc tích' khiến thứ tự xuất hiện quyết định kết quả. Cơ chế Swap-and-Average đã kịp thời triệt tiêu thiên lệch này bằng cách gán nhãn an toàn `tie`.
- **Về Verbosity Bias (3/3 cases quyết định = 100%)**: Trong cả 3 trường hợp có winner rõ ràng (ID 1, 12, 41), câu trả lời dài hơn đều giành chiến thắng. Tuy nhiên, phân tích nội dung chứng minh đây là tương quan hợp lý chứ không phải thiên lệch mù quáng: câu dài hơn thực sự chứa thông tin cốt lõi bắt buộc (ở ID 1 là cụm 'có lương', ở ID 12 là điều kiện 'từ 6 tháng trở lên', ở ID 41 là định dạng nhấn mạnh chính sách mới).

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json;
không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference.
Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| Question ID | Model Answer Gốc | Nhãn Judge | Reasoning | Human Label | Agree |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | Câu trả lời chính xác và đầy đủ theo thông tin trong tài liệu tham khảo, không thiếu ý thiết yếu. | 1 | True |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | Câu trả lời sai vì không nêu đúng người phê duyệt theo chính sách, cần Tổng Giám đốc chứ không phải Giám đốc phòng ban. | 0 | True |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | Câu trả lời chính xác theo thông tin trong reference, nêu rõ điều kiện và mức thưởng cho nhân viên chính thức có từ 6 tháng trở lên. | 1 | True |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | Câu trả lời chính xác theo reference, nêu rõ số ngày phép và khoảng lương cho nhân viên Senior với 9 năm thâm niên. | 1 | True |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | Câu trả lời chính xác theo reference, nêu rõ nhân viên phải hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | True |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | Câu trả lời sai vì chỉ đề cập Trưởng phòng phê duyệt mà không nhắc đến Kế toán trưởng, và phí phạt được tính cho quá hạn 15 ngày chứ không phải 30 ngày như trong câu hỏi. | 0 | True |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | Câu trả lời cung cấp đúng số ngày phép và tổng phụ cấp hàng tháng theo thông tin trong reference. | 1 | True |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | Câu trả lời sai vì nó dựa trên chính sách cũ (v2023) thay vì chính sách hiện hành (v2024), trong đó quy định nhân viên được nghỉ 15 ngày phép năm. | 0 | True |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | Câu trả lời chính xác theo reference, nêu rõ rằng nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần, đồng thời không bỏ qua điều kiện cần có sự phê duyệt của trưởng phòng. | 1 | True |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | Câu trả lời sai vì khẳng định cho phép sử dụng VPN cá nhân, trong khi reference rõ ràng cấm điều này. | 0 | True |

Cohen’s κ: 1.000.
Observed/chance agreement và diễn giải:
- Tỷ lệ đồng thuận quan sát (Observed Agreement): $P_o = \frac{10}{10} = 1.000$ (100.0%).
- Tỷ lệ đồng thuận ngẫu nhiên (Chance Agreement): Với phân bố nhãn 6 nhãn 1 và 4 nhãn 0 từ cả hai phía, $P_e = (0.6 \times 0.6) + (0.4 \times 0.4) = 0.36 + 0.16 = 0.520$.
- Hệ số Cohen's $\kappa = \frac{P_o - P_e}{1 - P_e} = \frac{1.000 - 0.520}{1 - 0.520} = 1.000$.
- Diễn giải: Đạt mức **Almost Perfect Agreement** (Đồng thuận gần như tuyệt đối theo thang đo Landis & Koch, $\kappa > 0.8$). Vượt xa ngưỡng mục tiêu $\kappa > 0.6$ của tiêu chí đề bài, giúp nhóm giành trọn **+3 điểm bonus**.

## Giới hạn và cách dùng judge

- **Quy mô tập mẫu và độ tin cậy thống kê**: Thực nghiệm calibration được thực hiện trên 10 mẫu nhãn người và 5 cặp pairwise. Mặc dù đạt $\kappa = 1.000$ hoàn hảo, kích thước mẫu nhỏ khiến khoảng tin cậy (Confidence Interval) của $\kappa$ còn rộng. Trong môi trường production quy mô lớn, cần mở rộng bộ nhãn kiểm chuẩn lên tối thiểu 100-200 mẫu đa dạng các phòng ban.
- **Hiện tượng Position Bias thực tế**: Tỷ lệ Position Bias lên tới 40% (2/5 cặp) chứng minh rằng LLM (ngay cả mô hình tiên tiến như GPT-4o-mini) vẫn chịu thiên lệch vị trí rõ rệt khi đối mặt với các câu trả lời có độ chính xác tương đương hoặc cùng mắc lỗi nhỏ. Vì vậy, **kỹ thuật Swap-and-Average là yêu cầu bắt buộc**, không thể bỏ qua trong bất kỳ pipeline LLM-as-a-Judge nào.
- **Nguy cơ Hallucination và Alignment**: LLM Judge không được xem là chân lý tuyệt đối (Ground Truth). Judge chỉ là công cụ tự động hóa sàng lọc sơ bộ (pre-screening). Các trường hợp trả về `tie` do bất đồng giữa hai lượt swap hoặc các câu hỏi thuộc chính sách tài chính / nhân sự trọng yếu cần được định tuyến (fallback) về cho con người (Human-in-the-loop) thẩm định lần cuối trước khi ban hành hoặc đưa ra quyết định kinh doanh.
