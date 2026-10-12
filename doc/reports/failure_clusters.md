# Phân tích lỗi Phase A

Nhóm: Soul

Người phụ trách: Nguyễn Công Duẩn (MSSV: 2A202602716) - Trưởng nhóm

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T07:34:36.114455+00:00.
Generation mode/fallback và điều kiện chạy: Thực nghiệm live trên 50 câu hỏi từ `fixtures/test_set_50q.json`, vector store Qdrant container v1.9.7 (port 6333), embedding BAAI/bge-m3, reranker BAAI/bge-reranker-v2-m3, generation mode LLM gpt-4o-mini-2024-07-18 không fallback.
Models generation/evaluator: Generation: gpt-4o-mini-2024-07-18; Evaluator (m4 RAGAS): gpt-4o-mini, text-embedding-ada-002.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9150 | 0.4767 | 0.5667 |
| answer_relevancy | 0.7518 | 0.6210 | 0.4224 |
| context_precision | 0.9583 | 0.9083 | 0.9417 |
| context_recall | 0.8417 | 0.7250 | 0.6167 |
| avg_score | 0.8667 | 0.6828 | 0.6369 |

## Bottom 10 và nguyên nhân

Bảng tổng hợp 10 câu hỏi có điểm trung bình RAGAS thấp nhất (Task 3):

| Rank | ID | Distribution | Câu hỏi | avg_score | worst_metric | Diagnosis | Suggested Fix |
|---|---|---|---|---|---|---|---|
| 1 | 39 | multi_hop | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 33 | multi_hop | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | 0.2500 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 3 | 40 | multi_hop | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? | 0.3333 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 4 | 50 | adversarial | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | 0.3750 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 5 | 44 | adversarial | Bao lâu phải đổi mật khẩu một lần? | 0.3958 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 6 | 42 | adversarial | Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? | 0.4167 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 7 | 48 | adversarial | Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không? | 0.4167 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 8 | 5 | factual | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | 0.5000 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 9 | 9 | factual | Nam nhân viên được nghỉ bao nhiêu ngày khi vợ sinh con? | 0.5000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 10 | 29 | multi_hop | Nhân viên tạm ứng 8 triệu, chưa thanh toán sau 30 ngày (quá hạn 15 ngày). Ai phê duyệt khoản này và phí phạt là bao nhiêu? | 0.5000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |

### Đối chiếu bằng chứng và phân loại nguyên nhân lỗi

1. **Lỗi thế hệ do đa văn bản và suy luận phức hợp (Multi-hop Synthesis Failure)**:
   - **Đại diện: Câu ID 39 (Rank 1, avg = 0.0000)**:
     - *Question*: So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA.
     - *Ground Truth*: v1.0 (hết hiệu lực): tối thiểu 8 ký tự, đổi mỗi 90 ngày, không MFA. v2.0 (hiện hành): tối thiểu 12 ký tự, đổi mỗi 120 ngày, MFA bắt buộc cho tất cả.
     - *Answer sinh ra*: "Không tìm thấy."
     - *Bằng chứng Contexts*: Retriever tìm được đúng các đoạn từ cả tài liệu v1.0 và v2.0, nhưng vì nội dung hai phiên bản mâu thuẫn trực tiếp (8 ký tự vs 12 ký tự, 90 ngày vs 120 ngày), prompt tạo sinh quá thận trọng dẫn tới việc LLM kết luận "Không tìm thấy" thay vì thực hiện bảng so sánh lịch sử phiên bản. Cả 4 chỉ số RAGAS đều rơi về 0.0000.
   - **Đại diện: Câu ID 33 (Rank 2, avg = 0.2500)**:
     - *Question*: Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp và số ngày phép năm theo v2024?
     - *Ground Truth*: Phụ cấp: ăn trưa 1.000.000 + điện thoại Manager 500.000 = 1.500.000 VNĐ. Phép năm v2024: 15 ngày cơ bản + 4 ngày thâm niên = 19 ngày.
     - *Answer*: "Không tìm thấy."
     - *Nguyên nhân*: Context Precision = 1.0000 (retriever đã kéo trúng các chunk chứa công thức thâm niên và bảng phụ cấp chức danh), nhưng LLM thất bại trong khâu tính toán số học đa bước (multi-step arithmetic reasoning), dẫn đến Context Recall = 0 và Faithfulness = 0.

2. **Lỗi bẫy xung đột phiên bản (Version Conflict Traps)**:
   - **Đại diện: Câu ID 44 (Rank 5, avg = 0.3958) & ID 42 (Rank 6, avg = 0.4167)**:
     - *Câu 44*: "Bao lâu phải đổi mật khẩu một lần?" — v1.0 quy định 90 ngày, v2.0 sửa thành 120 ngày.
     - *Câu 42*: "Thâm niên bao nhiêu năm thì được cộng thêm ngày phép?" — v2023 yêu cầu 5 năm, v2024 hạ xuống 3 năm.
     - *Bằng chứng*: Top chunks được truy xuất chứa cả chunk cũ và mới do cả hai đều có độ tương đồng ngữ nghĩa cực cao với câu hỏi. Khi prompt không có chỉ dẫn tường minh về việc ưu tiên metadata version/hiệu lực mới nhất (`effective_date`), LLM không thể phân giải xung đột thời gian (temporal conflict), dẫn đến việc từ chối trả lời hoặc chọn nhầm phiên bản cũ.

3. **Lỗi bẫy phủ định và điều kiện loại trừ (Negation & Policy Contradiction Traps)**:
   - **Đại diện: Câu ID 50 (Rank 4, avg = 0.3750) & ID 48 (Rank 7, avg = 0.4167)**:
     - *Câu 50*: "Nhân viên Manager có thể dùng VPN cá nhân khi WFH để tăng bảo mật thêm không?" — Policy v1.3 cấm nghiêm ngặt mọi VPN cá nhân, bắt buộc WireGuard công ty.
     - *Câu 48*: "Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không?" — Quy chế ghi nhận nhân viên thử việc chỉ có BHXH, loại trừ gói PVI tự nguyện.
     - *Bằng chứng*: Trong tài liệu bảo hiểm PVI, thông tin về nhân viên thử việc là thông tin mang tính phủ định (nằm ở tài liệu thử việc, không nằm ở tài liệu bảo hiểm). Pipeline gặp hiện tượng retrieval phân tán, generator không kết nối được mệnh đề phủ định, dẫn đến điểm Faithfulness và Relevancy suy giảm mạnh.

## Matrix và nhóm yếu nhất

| Metric | factual | multi_hop | adversarial | Tổng |
|---|---|---|---|---|
| faithfulness | 2 | 13 | 5 | 20 |
| answer_relevancy | 13 | 2 | 1 | 16 |
| context_precision | 1 | 0 | 0 | 1 |
| context_recall | 4 | 5 | 4 | 13 |
| **Tổng số câu** | 20 | 20 | 10 | 50 |

Nhóm yếu theo mean thấp nhất: `adversarial`; mean: `0.6369` (thấp hơn `multi_hop` 0.6828 và `factual` 0.8667).
Worst metric xuất hiện nhiều nhất: `faithfulness`; số câu: `20` câu (chiếm 40% tổng số câu hỏi benchmark).

### Phân tích nguyên nhân và giải pháp cải tiến

1. **Vì sao nhóm `adversarial` có mean thấp nhất (0.6369)?**
   - Bộ câu hỏi adversarial được thiết kế có chủ đích nhằm tấn công vào điểm mù của RAG: xung đột thời gian giữa các bản cập nhật policy, câu hỏi có tiền giả định sai, và bẫy phủ định.
   - Answer Relevancy của nhóm adversarial chỉ đạt trung bình 0.4224 (so với factual là 0.7518). Lý do chính là khi gặp các bẫy contradiction, LLM sinh ra câu trả lời ngắn ngủn "Không tìm thấy" hoặc vòng vo từ chối, khiến embedding của answer sai lệch rất xa so với embedding của câu hỏi ban đầu.
   - Lưu ý phương pháp luận: Việc xác định nhóm yếu nhất phải dựa vào giá trị kỳ vọng (mean score) của từng distribution, hoàn toàn không phụ thuộc vào kích thước mẫu 20/20/10.

2. **Vì sao `faithfulness` là worst metric xuất hiện nhiều nhất (20 câu)?**
   - Trong 20 câu multi_hop, có tới 13 câu có worst metric là faithfulness. Mô hình LLM khi được yêu cầu tổng hợp từ 3-4 chunks khác nhau thường rơi vào trạng thái suy diễn thêm các con số không có trong context hoặc gộp sai số liệu giữa các phòng ban.
   - Trong nhóm adversarial, có 5/10 câu bị gán worst metric là faithfulness do câu trả lời chứa thông tin từ phiên bản đã hết hiệu lực, vi phạm tính trung thực với context có hiệu lực hiện hành.

3. **Đề xuất khắc phục cụ thể và quy trình kiểm chứng**:
   - **Sửa Retrieval (Pre-generation)**: Bổ sung metadata filter cho vector search trong `m2_search.py` (`status == 'active'` hoặc sort theo `effective_date` giảm dần) nhằm loại bỏ chunk của policy cũ trước khi đưa vào context.
   - **Sửa Prompt Template**: Cấu trúc lại prompt yêu cầu rõ: (1) Nếu có nhiều phiên bản tài liệu, luôn lấy thông tin từ phiên bản có số hiệu cao nhất; (2) Trả lời rõ ràng "CÓ" hoặc "KHÔNG" kèm căn cứ điều khoản khi gặp câu hỏi về quyền hạn/nghĩa vụ; (3) Hướng dẫn từng bước chain-of-thought khi cộng trừ các khoản phụ cấp.
   - **Cách chạy lại kiểm chứng**:
     ```bash
     python scripts/setup_answers.py --live
     python scripts/run_experiments.py --phase a --live
     python -m pytest tests/test_phase_a.py -q
     ```
     So sánh file `artifacts/ragas_50q.json` mới với baseline để xác nhận faithfulness của multi_hop tăng từ 0.47 lên trên 0.80 và mean của adversarial tăng từ 0.63 lên trên 0.75.

## Bẫy adversarial và giới hạn

### So sánh với Factual và Multi-hop

- **Độ dốc chất lượng**: Factual đạt 0.8667 -> Multi-hop giảm xuống 0.6828 -> Adversarial chạm đáy 0.6369.
- **Bẫy Version Conflict**: Factual chỉ hỏi về các chính sách cố định không đổi (như hạn mức bảo hiểm PVI 200 triệu, phụ cấp ăn trưa 1 triệu). Ngược lại, Adversarial cố tình nhắm vào chính sách đã trải qua ít nhất 2 lần sửa đổi (mật khẩu v1.0 90 ngày vs v2.0 120 ngày; phép năm v2023 5 năm vs v2024 3 năm). Bộ reranker hiện tại chỉ chấm điểm độ tương đồng ngữ nghĩa câu chữ mà không hiểu ý nghĩa niên đại, dẫn đến việc cả hai phiên bản đều lọt vào top 3 reranked chunks.
- **Bẫy Negation**: Trong Factual, câu hỏi tìm kiếm hành động khẳng định ("Ai phê duyệt", "Được nghỉ bao nhiêu ngày"). Trong Adversarial (câu 48, câu 50), câu hỏi tìm kiếm quyền lợi không được phép ("Có được dùng VPN cá nhân không", "Thử việc có được PVI không"). Retriever dựa trên dense vector thường bị thu hút bởi từ khóa "VPN cá nhân", "bảo hiểm PVI" mà bỏ qua tính chất cấm đoán/ngoại lệ.

### Điểm số và nhận thức thực tế của Pipeline

Cần nhấn mạnh một nguyên lý then chốt trong đánh giá hệ thống: **Điểm số adversarial thấp hơn (0.6369 < 0.8667) không đồng nghĩa với việc pipeline đã tự động nhận biết được bẫy**.
Ngược lại, điểm số sụt giảm chứng minh rằng pipeline ngây thơ (naive RAG pipeline) đã bị bẫy đánh lừa. Pipeline không có cơ chế tự phát hiện xung đột hay kiểm tra tiền giả định (presupposition verification). Nếu không có Guardrails chuyên biệt ở đầu vào (như NeMo Guardrails trong Phase C), hệ thống RAG thuần túy sẽ liên tục mắc bẫy hallucination hoặc silent refusal.

### Giới hạn thực nghiệm

1. **Kích thước mẫu**: Bộ test adversarial gồm 10 câu hỏi, đủ để định tính các dạng bẫy chính nhưng độ bao phủ thống kê còn hẹp so với không gian tấn công thực tế.
2. **Mô hình Generation**: gpt-4o-mini-2024-07-18 là mô hình nhỏ, tối ưu về chi phí và độ trễ nhưng khả năng suy luận logic phủ định và giải quyết mâu thuẫn thời gian kém hơn đáng kể so với gpt-4o đầy đủ.
3. **Môi trường Retrieval**: Sử dụng top-k = 3 sau BGE-reranker. Với k = 3, khi câu hỏi multi-hop trải rộng trên 3-4 văn bản hoặc cần so sánh 2 phiên bản độc lập, ngân sách context bị nghẽn (context bottleneck), trực tiếp gây ra điểm Context Recall thấp (0.6167 ở adversarial và 0.7250 ở multi_hop).
