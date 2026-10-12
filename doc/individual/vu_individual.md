# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL REPORT)

### PhanHoangVu-2A202602450

- **Phần được giao và phần thực tế đã làm**:
  - **Phase B (LLM-as-a-Judge)**: Triển khai hoàn chỉnh mã nguồn `src/phase_b_judge.py` gồm Task 5 (`pairwise_judge`), Task 6 (`swap_and_average` khử position bias), Task 7 (`cohen_kappa`), và Task 8 (`bias_report`). Viết toàn bộ báo cáo phân tích thiên lệch tại `doc/reports/bias_report.md`.
  - **Phase C (Production Guardrails)**: Triển khai `src/phase_c_guard.py` gồm Task 9a (Presidio PII với custom Vietnamese recognizers cho CCCD, SĐT VN, Email và bộ lọc entity tránh false positive), Task 9b (NeMo Input Rails), Task 10 (Adversarial Suite đạt 20/20 attacks blocked và 8/8 clean allowed), Task 11 (NeMo Output Rails 4/4 cases), và Task 12 (đo P95 Latency tuần tự 20 mẫu sau 2 warm-up).
  - **Task 13 (Blueprint CI/CD)**: Soạn thảo toàn diện báo cáo kiến trúc phòng thủ `doc/reports/blueprint.md`, phân tích điểm nghẽn độ trễ do gọi cloud LLM API, và thiết lập các Quality Gates tự động.

- **Bằng chứng**:
  - Nhánh Git `feature/phase-b-judge`: commit `547a452` mang tên Hoang Vu (đã merge vào `main`).
  - Nhánh Git `feature/phase-c-guard`: các thay đổi trong `src/phase_c_guard.py`, `guardrails/config.yml`.
  - File artifact sinh ra: `artifacts/judge_results.json` (Cohen's $\kappa = 1.000$ săn **+3 bonus Phase B**), `artifacts/guard_results.json` (20/20 attacks blocked và 8/8 clean allowed săn **+3 bonus Phase C**).
  - Báo cáo kỹ thuật: `doc/reports/bias_report.md` và `doc/reports/blueprint.md` (cả hai đều đạt chuẩn thẩm định `PASS` qua `check_lab.py`).

- **Cách kiểm tra**:
  - Unit tests offline:
    ```powershell
    python -m pytest tests/test_phase_b.py -q   # 8/8 passed
    python -m pytest tests/test_phase_c.py -q   # 12/12 passed
    ```
  - Chạy live experiments:
    ```powershell
    python scripts/run_experiments.py --phase b --live
    python scripts/run_experiments.py --phase c --live --latency-samples 20
    ```
  - Kiểm định toàn diện qua checker:
    ```powershell
    python scripts/check_lab.py
    ```
    Xác nhận PASS Phase B artifact, Phase C artifact, bias_report.md và blueprint.md.

- **Điều đã học**:
  - Hiểu sâu sắc cơ chế Position Bias trong LLM-as-a-Judge và sự cần thiết của kỹ thuật `swap_and_average` để loại bỏ thiên lệch vị trí xuất hiện của câu trả lời.
  - Nắm vững công thức Cohen's $\kappa$ và cách hiệu chuẩn (calibration) đánh giá tự động với nhãn người thật theo thang đo Landis & Koch.
  - Kỹ thuật xây dựng Guardrails 2 tầng: Presidio PII siêu nhanh trên CPU kết hợp NeMo Guardrails kiểm soát ngữ nghĩa (Jailbreak/Prompt Injection) trên GPU/Cloud.
  - Nhận thức thực tế về bài toán Trade-off giữa An toàn bảo mật và Độ trễ (P95 Latency budget 500ms): việc gọi LLM cloud cho input rails là điểm nghẽn lớn, từ đó định hình giải pháp chuyển sang mô hình SLM on-premise trong production.

- **Giới hạn/cách xử lý**:
  - *Vấn đề 1*: Presidio sử dụng mô hình Spacy tiếng Anh `en_core_web_lg` nhận diện nhầm các từ tiếng Việt thông thường thành `PERSON`, khiến clean inputs bị chặn nhầm (False Positive). Đã xử lý bằng cách cấu hình bộ lọc chỉ giữ lại đúng 3 thực thể PII mục tiêu (`VN_CCCD`, `VN_PHONE`, `EMAIL_ADDRESS`), đưa false positive rate về 0.00% (8/8 clean inputs allowed).
  - *Vấn đề 2*: Câu hỏi chính sách về mật khẩu (ID 107) bị NeMo Guardrails chặn nhầm do prompt self-check quá nhạy cảm. Đã xử lý bằng cách tinh chỉnh prompt trong `guardrails/config.yml` cho phép hỏi quy định chính sách độ dài/đổi mật khẩu.

- **Nguồn/AI hỗ trợ nếu có**:
  - Sử dụng Antigravity IDE Agent hỗ trợ tự động hóa các bước gõ lệnh terminal, rà soát schema JSON và chạy kiểm thử lặp. Toàn bộ logic giải thuật, công thức tính toán và số liệu đo lường đều được kiểm chứng độc lập qua các tệp kiểm thử tự động của repo đề bài.
