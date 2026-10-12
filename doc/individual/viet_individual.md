# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL REPORT)

### PhungQuocViet-2A202602456

- **Phần được giao và phần thực tế đã làm**:
  - **Phụ trách độc quyền Phase B (LLM-as-a-Judge)**: Tôi được phân công phụ trách toàn bộ Phase B theo đúng bảng phân công nhóm. Tôi đã trực tiếp thiết kế, lập trình và hoàn thiện 100% mã nguồn trong `src/phase_b_judge.py` bao gồm:
    - **Task 5 (`pairwise_judge`)**: Thiết kế prompt có cấu trúc JSON để gọi LLM (`gpt-4o-mini`) đánh giá so sánh cặp câu trả lời A/B theo 3 tiêu chí cốt lõi: độ chính xác (accuracy đối chiếu với tài liệu tham chiếu), độ đầy đủ (completeness), và tính súc tích (conciseness).
    - **Task 6 (`swap_and_average`)**: Xây dựng thuật toán đánh giá 2 lượt hoán đổi vị trí $A/B$ và $B/A$, quy đổi nhãn lượt 2 về không gian nhãn gốc ban đầu. Thuật toán chỉ công nhận chiến thắng khi có sự đồng thuận tuyệt đối giữa 2 lượt; nếu có bất đồng, gán nhãn `tie` để triệt tiêu hoàn toàn Position Bias.
    - **Task 7 (`cohen_kappa`)**: Lập trình thuật toán tính hệ số Cohen's $\kappa$ để hiệu chuẩn đánh giá nhị phân (0/1) của LLM Judge đối chiếu với 10 nhãn chuyên gia người thật (`human_labels_10q.json`).
    - **Task 8 (`bias_report`)**: Xây dựng module đo lường thiên lệch, thống kê tỷ lệ `position_bias_rate` và `verbosity_bias` kèm chi tiết các trường hợp câu trả lời dài hơn giành chiến thắng.
  - **Soạn thảo báo cáo kỹ thuật Phase B**: Tôi đã trực tiếp phân tích số liệu thực nghiệm và hoàn thiện toàn bộ báo cáo phân tích thiên lệch tại `doc/reports/bias_report.md`.

- **Bằng chứng**:
  - Nhánh Git độc quyền: `feature/phase-b-judge` với commit `3a71ea4`
  - Mã nguồn đã hoàn thiện sạch sẽ mọi TODO: `src/phase_b_judge.py`.
  - Artifact thực nghiệm live: `artifacts/judge_results.json` với hệ số Cohen's $\kappa = 1.000$ (đạt tối đa **+3 điểm bonus Phase B**), Position Bias phát hiện là 40.0% (2/5 cặp).
  - Báo cáo phân tích chuyên sâu: `doc/reports/bias_report.md` đã điền đầy đủ mọi bảng biểu, số liệu thực nghiệm và nhận định chuyên môn, đạt chuẩn thẩm định không còn placeholder.

- **Cách kiểm tra**:
  - Kiểm thử unit tests offline (Mock LLM SDK):

    ```powershell
    python -m pytest tests/test_phase_b.py -q
    # Kết quả: 8/8 tests passed
    ```

  - Chạy thực nghiệm live gọi OpenAI API:

    ```powershell
    python scripts/run_experiments.py --phase b --live
    # Kết quả: Sinh artifacts/judge_results.json thành công
    ```

  - Chạy công cụ thẩm định tự động toàn diện của đề bài:

    ```powershell
    python scripts/check_lab.py --with-tests
    # Kết quả: 86 passed, 0 failed checks
    ```

- **Điều đã học**:
  - Hiểu sâu sắc bản chất hiện tượng Position Bias trong LLM Evaluation: Ngay cả các mô hình ngôn ngữ lớn tiên tiến cũng có xu hướng ưu tiên lựa chọn câu trả lời xuất hiện ở vị trí đầu tiên hoặc vị trí thuận lợi khi hai câu trả lời có chất lượng tương đương nhau hoặc cùng mắc lỗi nhỏ. Kỹ thuật `swap_and_average` là bắt buộc phải có để loại bỏ thiên lệch này trong môi trường sản xuất.
  - Nắm vững cơ sở toán học và ý nghĩa thực tiễn của hệ số tương quan Cohen's $\kappa$ trong đo lường độ tin cậy giữa hai người đánh giá (Inter-rater reliability), phân biệt rành mạch giữa tỷ lệ đồng thuận quan sát ($P_o$) và tỷ lệ đồng thuận ngẫu nhiên ($P_e$).
  - Phân biệt rõ ràng giữa Verbosity Bias thực sự (thiên lệch chọn câu dài một cách mù quáng) và sự tương quan hợp lý về mặt nội dung (câu trả lời dài hơn thực chất chứa đựng đầy đủ các điều kiện tiên quyết, phiên bản chính sách có hiệu lực).

- **Giới hạn/cách xử lý**:
  - *Vấn đề phát sinh*: Trong quá trình thực nghiệm 5 cặp A/B, câu hỏi ID 5 và ID 21 bị đảo chiều kết quả khi đổi vị trí do câu trả lời ngắn súc tích nhưng thiếu điều kiện, còn câu dài thì giải thích chi tiết nhưng thừa ý.
  - *Giải pháp*: Tôi đã cho hệ thống gán nhãn `tie` theo đúng cơ chế consensus của đề bài nhằm đảm bảo tính an toàn cao nhất; đồng thời đưa ra đề xuất trong báo cáo rằng đối với các trường hợp `tie` trong production, hệ thống cần kích hoạt cơ chế fallback chuyển giao cho con người thẩm định lần cuối (Human-in-the-loop).

- **Nguồn/AI hỗ trợ nếu có**:
  - Tham khảo tài liệu khóa học AITC Track 3A, tài liệu hướng dẫn LLM Evaluation của OpenAI và bài báo khoa học về thang đo Cohen's kappa (Landis & Koch, 1977).
  - Sử dụng Antigravity IDE làm môi trường soạn thảo mã nguồn và thực thi terminal. Toàn bộ thuật toán, logic xử lý và phân tích số liệu đều được tôi tự kiểm chứng độc lập qua test suite và script checker của bài lab.
