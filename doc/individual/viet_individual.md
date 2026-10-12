# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL REPORT)

### PhungQuocViet-K4-PQV-02

- **Phần được giao và phần thực tế đã làm**:
  - **Phase B (LLM-as-a-Judge)**: Trực tiếp phụ trách và hoàn thành 100% Phase B trong `src/phase_b_judge.py` bao gồm:
    + Task 5 (`pairwise_judge`): Xây dựng prompt có cấu trúc JSON gọi LLM đánh giá so sánh cặp candidate A/B theo 3 tiêu chí: accuracy, completeness, conciseness có đối chiếu ground-truth reference.
    + Task 6 (`swap_and_average`): Triển khai thuật toán 2 lượt hoán đổi vị trí A/B và B/A, chuyển đổi không gian nhãn về gốc, đồng thuận mới chọn winner, bất đồng trả `tie` để triệt tiêu Position Bias.
    + Task 7 (`cohen_kappa`): Lập trình công thức tính hệ số Cohen's $\kappa$ giữa đánh giá nhị phân 0/1 của LLM và nhãn chuyên gia người thật (`human_labels_10q.json`).
    + Task 8 (`bias_report`): Tính toán các chỉ số `position_bias_rate` và `verbosity_bias` kèm chi tiết các trường hợp câu dài hơn giành chiến thắng.
  - Soạn thảo và hoàn thiện toàn bộ báo cáo phân tích thiên lệch vị trí và độ dài tại `doc/reports/bias_report.md`.

- **Bằng chứng**:
  - Nhánh Git `feature/phase-b-judge`: hoàn thiện các hàm Task 5 - 8 trong `src/phase_b_judge.py`.
  - Artifact sinh ra: `artifacts/judge_results.json` với hệ số Cohen's $\kappa = 1.000$ (đạt trọn vẹn **+3 điểm bonus Phase B**), Position Bias phát hiện được là 40.0% (2/5 cặp).
  - Báo cáo kỹ thuật: `doc/reports/bias_report.md` đạt chuẩn thẩm định không còn placeholder.

- **Cách kiểm tra**:
  - Chạy unit tests offline mock:
    ```powershell
    python -m pytest tests/test_phase_b.py -q
    # 8/8 tests passed
    ```
  - Chạy live experiment với OpenAI API:
    ```powershell
    python scripts/run_experiments.py --phase b --live
    # Sinh ra artifacts/judge_results.json
    ```
  - Chạy checker toàn diện:
    ```powershell
    python scripts/check_lab.py --with-tests
    # 0 failed checks
    ```

- **Điều đã học**:
  - Hiểu sâu sắc bản chất của Position Bias: Mô hình LLM (như GPT-4o-mini) có xu hướng ưu tiên câu trả lời ở vị trí thuận lợi khi cả hai câu trả lời đều chưa hoàn hảo hoặc có độ dài/chi tiết khác nhau. Kỹ thuật `swap_and_average` là công cụ thiết yếu để lọc bỏ thiên lệch này.
  - Nắm vững nguyên lý đo lường độ tin cậy giữa hai người đánh giá (Inter-rater reliability) bằng hệ số Cohen's $\kappa$, phân biệt rõ giữa tỷ lệ đồng thuận quan sát ($P_o$) và tỷ lệ đồng thuận ngẫu nhiên ($P_e$).
  - Phân biệt giữa Verbosity Bias thực sự (thiên lệch độ dài mù quáng) và sự tương quan hợp lý (câu dài hơn chứa đựng đầy đủ các điều kiện chính sách bắt buộc như phiên bản, điều kiện thâm niên).

- **Giới hạn/cách xử lý**:
  - *Vấn đề*: Trong thực nghiệm, câu ID 5 và ID 21 có sự bất đồng giữa Pass 1 và Pass 2 do sự giằng co giữa tính đầy đủ và tính súc tích.
  - *Cách xử lý*: Thuật toán đã gán nhãn `tie` theo đúng thiết kế để đảm bảo tính thận trọng; đồng thời kiến nghị trong báo cáo rằng các case `tie` trong production cần được chuyển giao cho con người (Human-in-the-loop) thẩm định.

- **Nguồn/AI hỗ trợ nếu có**:
  - Sử dụng Antigravity IDE Agent hỗ trợ kiểm tra tính tương thích môi trường Python 3.11 trên PowerShell, thực thi live benchmark và đối soát các ràng buộc schema JSON. Toàn bộ logic giải thuật được tuân thủ nghiêm ngặt theo hợp đồng `src/report_contracts.py`.
