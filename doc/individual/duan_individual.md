# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL REPORT)

### NguyenCongDuan-K4-NCD-01

- **Phần được giao và phần thực tế đã làm**:
  - **Trưởng nhóm & Khởi tạo hạ tầng (CP0)**: Tạo repo GitHub nhóm, add Phùng Quốc Việt và Phan Hoàng Vũ làm Collaborators. Chép 5 module RAG từ Day 18 (`m1_chunking.py`, `m2_search.py`, `m3_rerank.py`, `m4_eval.py`, `m5_enrichment.py`) vào `src/`. Khởi động Docker Qdrant v1.9.7 (port 6333), chạy `python scripts/setup_answers.py --live` sinh ra `artifacts/answers_50q.json` với đầy đủ 50 câu trả lời RAG (20 factual, 20 multi_hop, 10 adversarial). Push commit khởi tạo lên `main` làm baseline cho cả nhóm.
  - **Phase A — RAGAS Production Evaluation (CP1)**: Trực tiếp triển khai toàn bộ `src/phase_a_ragas.py`:
    - **Task 1 (`group_by_distribution`)**: Nhóm 50 câu hỏi theo 3 distribution: `factual` (20), `multi_hop` (20), `adversarial` (10).
    - **Task 2 (`run_ragas_50q`)**: Gọi `m4_eval.evaluate_ragas` trả về `RagasEvaluation` chứa 50 `RagasResult` và `evaluator_models` lấy từ metadata của m4 (không hardcode).
    - **Task 3 (`bottom_10`)**: Lọc 10 câu có `avg_score` thấp nhất theo thứ tự tăng dần, gán đầy đủ `rank`, `diagnosis`, `suggested_fix` theo `DIAGNOSTIC_TREE`.
    - **Task 4 (`cluster_analysis`)**: Xây dựng matrix `worst_metric` × `distribution` (4×3), xác định dominant failure distribution bằng mean `avg_score` thấp nhất.
  - **Báo cáo phân tích lỗi Phase A**: Điền toàn bộ `doc/reports/failure_clusters.md` với phân tích chuyên sâu ba dạng bẫy adversarial (version conflict, multi-hop arithmetic failure, negation trap) và đề xuất cải tiến cụ thể nhằm săn **+4 điểm bonus Phase A**.

- **Bằng chứng**:
  - Commit `1a5265b` — CP0: khởi tạo repo, module Day 18 m1–m5, `artifacts/answers_50q.json`.
  - Commit `90ebd59` — CP1: `src/phase_a_ragas.py` hoàn chỉnh không còn TODO, `artifacts/ragas_50q.json`, `doc/reports/failure_clusters.md`.
  - Commit `8197290` — cập nhật `plan.md` đánh dấu CP0 và CP1 hoàn thành.
  - Artifact `artifacts/ragas_50q.json`: faithfulness factual 0.9150, mean adversarial 0.6369 < factual 0.8667 (đáp ứng điều kiện bonus Phase A).
  - Báo cáo `doc/reports/failure_clusters.md`: phân tích 3 dạng bẫy adversarial, matrix 4×3, dominant failure = `adversarial` (mean = 0.6369).

- **Cách kiểm tra**:
  - Unit tests offline:
    ```powershell
    python -m pytest tests/test_phase_a.py -q
    # Kết quả: 6/6 tests passed
    ```
  - Chạy thực nghiệm live gọi OpenAI API và Qdrant:
    ```powershell
    python scripts/run_experiments.py --phase a --live
    # Kết quả: Sinh artifacts/ragas_50q.json thành công
    ```
  - Kiểm định toàn diện qua checker:
    ```powershell
    python scripts/check_lab.py --with-tests
    # Kết quả: 86 passed, 0 failed checks
    ```

- **Điều đã học**:
  - Hiểu sâu 4 metric RAGAS (`faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`) và cách chúng phản ánh từng điểm yếu khác nhau của pipeline RAG: faithfulness đo hallucination, relevancy đo độ khớp câu trả lời với câu hỏi, precision đo độ nhiễu của context được truy xuất, recall đo độ bao phủ thông tin cần thiết.
  - Nhận ra và phân loại được 3 dạng bẫy adversarial điển hình: (1) **Version Conflict** — corpus chứa cả phiên bản cũ và mới với nội dung mâu thuẫn trực tiếp (mật khẩu 90 ngày vs 120 ngày, phép v2023 vs v2024), reranker không thể phân giải theo niên đại; (2) **Multi-hop Arithmetic Failure** — LLM thất bại trong tính toán đa bước khi cộng phụ cấp theo chức danh và thâm niên từ nhiều chunk; (3) **Negation Trap** — pipeline bị thu hút bởi từ khóa chính sách nhưng bỏ qua tính chất cấm đoán trong câu hỏi (VPN cá nhân, bảo hiểm thử việc).
  - Quy tắc chọn dominant failure distribution phải dựa trên **mean score** của từng nhóm, không phải tổng số câu lỗi (để tránh sai lệch do kích thước mẫu 20/20/10 không đều nhau).

- **Giới hạn/cách xử lý**:
  - *Vấn đề 1 — Version Conflict*: Với câu ID 39 (avg = 0.0000), LLM nhận được context chứa cả hai phiên bản policy v1.0 và v2.0 mâu thuẫn trực tiếp, dẫn đến kết quả "Không tìm thấy". Đề xuất khắc phục: bổ sung metadata pre-filter trong `m2_search.py` để ưu tiên chunk có `effective_date` mới nhất, loại bỏ phiên bản cũ trước khi đưa vào context.
  - *Vấn đề 2 — Context Bottleneck*: Top-k = 3 sau reranker không đủ bao phủ cho câu hỏi multi-hop cần 3–4 văn bản độc lập, trực tiếp gây Context Recall thấp (0.6167 adversarial, 0.7250 multi_hop). Giải pháp: tăng top-k lên 5–7 kết hợp query decomposition để mỗi sub-query tìm đúng chunk liên quan.

- **Nguồn/AI hỗ trợ nếu có**:
  - Tham khảo tài liệu RAGAS chính thức và khóa học AITC Track 3A.
  - Sử dụng Kiro IDE Agent hỗ trợ rà soát schema JSON, phân tích cây chẩn đoán `DIAGNOSTIC_TREE` và kiểm tra kết quả artifact. Toàn bộ logic triển khai, công thức RAGAS và số liệu phân tích đều được kiểm chứng độc lập qua test suite và `check_lab.py` của đề bài.
