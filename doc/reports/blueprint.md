# Blueprint CI/CD cho RAG và guardrails

Nhóm: Nhóm 1 - AITC K4

Người phụ trách: Phan Hoàng Vũ (MSSV: 2A202602450)

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: `artifacts/ragas_50q.json`, `judge_results.json`, `guard_results.json`.
Run timestamp: 2026-10-12T09:58:30.038450+00:00; guard models: gpt-4o-mini.
Models generation/evaluator/judge từ A/B:
- Generation: gpt-4o-mini-2024-07-18 (nguồn `artifacts/answers_50q.json`)
- Evaluator RAGAS (m4): gpt-4o-mini, text-embedding-ada-002 (nguồn `artifacts/ragas_50q.json`)
- LLM Judge: gpt-4o-mini (nguồn `artifacts/judge_results.json`)
- Guard: gpt-4o-mini (nguồn `artifacts/guard_results.json`)

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

### 1. Luồng dữ liệu (Data Flow) và Cơ chế Dừng sớm (Short-circuit)
- **Tầng 1 - Presidio PII Engine**: Thực thi kiểm tra đồng bộ (synchronous regex & pattern matching). Quét nhanh các thực thể PII nhạy cảm tại Việt Nam bao gồm CCCD 12 số, CMND 9 số, Số điện thoại di động và Email. Nếu phát hiện PII, request bị lập tức chặn đứng (short-circuit), không tiêu tốn tài nguyên GPU/API cho các tầng tiếp theo.
- **Tầng 2 - NeMo Input Rails**: Thực thi bất đồng bộ (async). Kiểm tra rủi ro jailbreak, prompt injection (như đóng vai DAN, giả mạo quyền hạn) và câu hỏi lạc đề (off-topic). Đọc quyết định chặn từ cờ `stop` của `activated_rails`, không suy đoán từ khóa từ chối.
- **Tầng 3 - Core RAG Pipeline**: Chỉ những câu hỏi vượt qua 2 tầng input guard mới được đẩy vào pipeline tìm kiếm (Qdrant Dense Vector + BM25 + BGE Reranker) và sinh câu trả lời qua LLM.
- **Tầng 4 - NeMo Output Rails**: Kiểm tra câu trả lời sinh ra trong ngữ cảnh đầy đủ của câu hỏi. Ngăn chặn hiện tượng rò rỉ dữ liệu cá nhân, thông tin bảo mật nội bộ và ngôn từ độc hại trước khi người dùng nhìn thấy.

### 2. Failure Action, Log Redact và Secrets Management
- **Hành động khi chặn (Failure Action)**: Trả về thông báo từ chối lịch sự được định nghĩa trong `rails.co` (ví dụ: "Yêu cầu vi phạm chính sách bảo mật thông tin của công ty").
- **Nhật ký bảo mật (Audit Logging & Redaction)**: Mọi sự kiện vi phạm được ghi vào logging an ninh trung tâm. Dữ liệu PII bị bôi đen (redacted thành `<VN_CCCD>`, `<VN_PHONE>`) trước khi ghi vào log nhằm tuân thủ triệt để Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân.
- **Quản lý khóa bí mật (Secrets Management)**: Tuyệt đối không hardcode API key hay database credentials vào mã nguồn. Tất cả secrets được nạp từ biến môi trường (`.env` local hoặc GitHub Secrets / HashiCorp Vault trong production).
- **Cơ chế Fallback**: Khi NeMo Guardrails hoặc OpenAI API gặp sự cố timeout (> 2000ms) hoặc rate limit (HTTP 429), hệ thống chuyển sang chế độ an toàn (Fail-Closed cho security guard và Extractive Fallback cho RAG), từ chối thực hiện tác vụ thay vì để lọt truy vấn độc hại.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu. Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2; phương pháp: linear.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 6.131 | 7.425 | 7.523 | Đạt ngân sách tối ưu (<10ms) |
| NeMo input | 708.879 | 950.847 | 1577.872 | Bottleneck chính do gọi cloud LLM API |
| Input guard sequential | 715.183 | 957.097 | 1584.229 | Tổng hợp 2 tầng tuần tự |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: P95 = 957.097 ms / budget_ok = False.

### Phân tích Bottleneck và Đề xuất Tối ưu
- **Điểm nghẽn độ trễ (Bottleneck)**: Tầng Presidio chạy cục bộ trên CPU cực nhanh (P95 chỉ 7.43ms). Tuy nhiên, tầng NeMo input rail phụ thuộc vào lệnh gọi mạng tới `gpt-4o-mini` qua Internet, độ trễ P95 lên tới 950.85ms, khiến tổng độ trễ tuần tự chạm ngưỡng 957.10ms (vượt budget 500ms).
- **Giải pháp Production**: 
  1. Thay thế cloud LLM trong NeMo input bằng một SLM (Small Language Model) tự host on-premise (như Qwen2.5-1.5B hoặc Llama-3.2-1B deploy qua vLLM có tensor parallel) để đưa latency P95 về < 80ms.
  2. Áp dụng semantic cache (như GPTCache) cho các câu hỏi phổ biến để bỏ qua bước self-check LLM.
- **Kế hoạch đo lường mở rộng**: Với các phần "chưa đo" (RAG, Output Rail, Full Request), nhóm lên kế hoạch triển khai OpenTelemetry tracing với timestamp chi tiết tại từng span (`t_retrieve`, `t_rerank`, `t_generate`, `t_output_rail`) qua 100 mẫu benchmark trên staging server.

## CI gates đề xuất

- RAGAS faithfulness ≥ 0.75, avg_score ≥ 0.65 trên 50 câu benchmark.
- Attacks ≥ 18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng 4/4.
- Full guard P95 < 500ms chỉ áp dụng sau khi thực sự đo full guard trên production infrastructure.

Mốc bắt buộc lab vẫn attacks ≥ 15/20; bonus ≥ 18/20 kèm clean controls đạt (nhóm đã đạt 20/20 attacks và 8/8 clean controls).

### Cấu hình Workflow CI đề xuất (GitHub Actions)
```yaml
name: Production RAG & Guardrails Quality Gate
on: [pull_request, push]
jobs:
  eval-guard-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run Offline Unit Tests
        run: pytest tests/ -q
      - name: Verify Quality Gates
        env:
          OPENAI_API_KEY: "$OPENAI_API_KEY"
        run: |
          python scripts/check_lab.py --with-tests
```
Script kiểm tra sẽ trả mã thoát nonzero (`exit 1`) nếu bất kỳ ngưỡng nào bị vi phạm, tự động chặn merge PR vào nhánh `main`.

## Monitoring và cải tiến

### 1. Hệ thống giám sát Production (Observability & Monitoring)
- **Data Drift**: Giám sát phân phối embedding của câu hỏi người dùng theo thời gian thực (Evidently AI / Langfuse). Cảnh báo khi cosine similarity trung bình so với corpus giảm dưới 0.65 (dấu hiệu người dùng hỏi ngoài phạm vi tài liệu).
- **Privacy & PII Leak Alerts**: Kích hoạt cảnh báo Slack/PagerDuty P1 ngay khi phát hiện output rail gắn cờ chứa PII chưa được che giấu.
- **False Positive Monitoring**: Thiết lập cơ chế cho phép nhân viên phản hồi "Tôi bị chặn nhầm" qua giao diện chat. Chuyên viên bảo mật định kỳ duyệt hàng tuần để cập nhật danh sách cho phép (allowlist).

### 2. Số liệu thực nghiệm tổng hợp của nhóm
- RAGAS mean/worst distribution: Factual = 0.8667, Multi-hop = 0.6828, Adversarial = 0.6369; Worst distribution: `adversarial` (mean = 0.6369, faithfulness thấp nhất = 0.5667).
- Cohen’s κ: 1.000 (Đạt thỏa thuận tuyệt đối trên 10 nhãn người thật, position bias rate = 40.0%, verbosity bias = 100.0%).
- Attacks passed: 20/20 (100% attacks bị chặn); clean false_positive_rate: 0.00% (8/8 clean inputs được cho phép); output safety: 4/4 trường hợp kiểm tra chính xác.

### 3. Đề xuất cải tiến hệ thống có thể kiểm chứng
1. **Lọc siêu dữ liệu thời gian cho RAG**: Cập nhật module `m2_search.py` bổ sung pre-filtering theo `status: active` và `effective_date` mới nhất để giải quyết triệt để bẫy version conflict ở các câu ID 41, 42, 44.
2. **Khử Position Bias bằng Swap-and-Average mặc định**: Tích hợp cơ chế 2-pass swap vào toàn bộ quy trình LLM-as-a-judge tự động trong CI/CD pipeline để đảm bảo kết quả đánh giá không bị sai lệch bởi thứ tự trình bày.
3. **Chuyển đổi NeMo Guardrails sang Local SLM**: Triển khai NeMo Guardrails kết hợp mô hình nhỏ Llama-3.2-1B-Instruct on-premise nhằm giảm P95 latency từ 950ms xuống dưới 100ms, đáp ứng hoàn hảo ngân sách SLA 500ms của ứng dụng enterprise.
4. **Fine-grained Intent Classification**: Bổ sung tầng phân loại ý định (Intent Classifier) trước NeMo input rail để phân biệt rõ câu hỏi chính sách về mật khẩu/bảo mật với hành vi cố tình trích xuất thông tin bí mật.
