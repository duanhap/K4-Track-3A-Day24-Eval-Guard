# Nhóm thực hiện K4 Track 3A

Tên nhóm: Nhóm 1 - AITC K4

Repo chung: https://github.com/duanhap/K4-Track-3A-Day24-Eval-Guard

Trưởng nhóm/người nộp: Nguyễn Công Duẩn (MSSV: K4-NCD-01)

Ngày lab/deadline áp dụng: 2026-10-12 23:59:00 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: 3a71ea4

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Công Duẩn | K4-NCD-01 | Trưởng nhóm, Khởi tạo Repo, Setup CP0, Phase A RAGAS 4 metrics, Báo cáo lỗi | Commit 1a5265b, 90ebd59, 8197290, artifacts/ragas_50q.json, failure_clusters.md |
| 2 | Phùng Quốc Việt | K4-PQV-02 | Phụ trách Phase B (LLM-as-a-Judge, Swap-and-Average, Cohen's kappa, bias report) | Nhánh feature/phase-b-judge, artifacts/judge_results.json, bias_report.md, doc/individual/viet_individual.md |
| 3 | Phan Hoàng Vũ | 2A202602450 | Phụ trách Phase C (Presidio PII, NeMo Rails, Latency P95), Task 13 Blueprint | Nhánh feature/phase-c-guard, artifacts/guard_results.json, blueprint.md, doc/individual/vu_individual.md |

Người tích hợp/chạy batch/nộp link: Nguyễn Công Duẩn (Trưởng nhóm).

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 64-bit, Python 3.11.9, MSVC v14.50.35719 / Annoy 1.17.3 pre-compiled wheel.
Virtualenv/dependencies/imports: Môi trường ảo `.venv`, cài đặt đầy đủ theo `requirements/requirements.txt` và `constraints-core.txt`, pyarrow 17.0.0, sitecustomize.py fix c10.dll, import ragas, nemoguardrails, presidio, spacy đều OK.
Models/Qdrant/50 answers đã chuẩn bị: Docker Qdrant v1.9.7 (port 6333), embedding BAAI/bge-m3, reranker bge-reranker-v2-m3, spacy en_core_web_lg, sinh thành công 50 answers mode LLM gpt-4o-mini-2024-07-18 lưu tại `artifacts/answers_50q.json`.

## INDIVIDUAL

### NguyenCongDuan-K4-NCD-01

- Phần được giao và phần thực tế đã làm: Trưởng nhóm điều phối, khởi tạo repo chung, thiết lập Docker Qdrant và sinh 50 câu trả lời RAG. Thực hiện Phase A trong `src/phase_a_ragas.py` (Tasks 1-4) và viết báo cáo phân tích lỗi `doc/reports/failure_clusters.md`.
- Bằng chứng: Commit 1a5265b, 90ebd59, 8197290, artifact `artifacts/ragas_50q.json` và báo cáo `failure_clusters.md`.
- Cách kiểm tra: Unit tests mock `python -m pytest tests/test_phase_a.py -q` (6/6 passed), live runner `python scripts/run_experiments.py --phase a --live`.
- Điều đã học: Hiểu sâu về 4 metric RAGAS, nhận diện được bẫy version conflict giữa các phiên bản chính sách cũ và mới khiến RAG suy giảm tính trung thực (faithfulness).
- Giới hạn/cách xử lý: Mô hình embedding dense vector dễ bị thu hút bởi từ khóa trong chính sách cũ; đã đề xuất giải pháp lọc metadata active/effective_date ở tầng retrieval.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu RAGAS và sử dụng AI hỗ trợ phân tích ma trận lỗi theo cây chẩn đoán DIAGNOSTIC_TREE.

### PhungQuocViet-K4-PQV-02

- Phần được giao và phần thực tế đã làm: Phụ trách toàn bộ Phase B (LLM-as-a-Judge): Thiết kế prompt so sánh pairwise A/B, triển khai kỹ thuật Swap-and-Average để triệt tiêu Position Bias, tính toán hệ số Cohen's kappa đối chiếu với nhãn người và viết báo cáo đo lường bias trong `doc/reports/bias_report.md`.
- Bằng chứng: Nhánh `feature/phase-b-judge`, artifact `artifacts/judge_results.json` (Cohen's $\kappa = 1.000$ đạt +3 bonus Phase B, position bias 40%), báo cáo `doc/reports/bias_report.md` và `doc/individual/viet_individual.md`.
- Cách kiểm tra: Unit tests `pytest tests/test_phase_b.py -q` và live runner `python scripts/run_experiments.py --phase b --live`.
- Điều đã học: Bản chất Position Bias và Verbosity Bias trong LLM Judge và nguyên lý Swap-and-Average.
- Giới hạn/cách xử lý: Cần đối chiếu sát sao với tập 10 nhãn `human_labels_10q.json` để kiểm chuẩn độ tin cậy.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu về LLM Judge và thang đo Cohen's kappa.

### PhanHoangVu-2A202602450

- Phần được giao và phần thực tế đã làm: Trực tiếp triển khai mã nguồn Phase C trong `src/phase_c_guard.py` (Tasks 9a-12), xây dựng Guardrails 2 tầng (Presidio PII + NeMo Guardrails), đo lường độ trễ P95 với 20 mẫu thực nghiệm, viết báo cáo kiến trúc hệ thống `doc/reports/blueprint.md` và hoàn thành báo cáo cá nhân `doc/individual/vu_individual.md`.
- Bằng chứng: Nhánh `feature/phase-c-guard`, artifact `artifacts/guard_results.json` (20/20 attacks blocked, 8/8 clean allowed, 4/4 output safe), báo cáo `doc/reports/blueprint.md`, báo cáo cá nhân `doc/individual/vu_individual.md`.
- Cách kiểm tra: `python -m pytest tests/test_phase_c.py -q` (12/12 passed in 0.08s), live runner `python scripts/run_experiments.py --phase c --live --latency-samples 20`.
- Điều đã học: Kỹ thuật phối hợp giữa Presidio (lọc PII siêu tốc tầng 1) và NeMo Guardrails (kiểm soát ngữ nghĩa/jailbreak tầng 2), hiểu rõ bài toán đánh đổi giữa an toàn và độ trễ P95 (950ms cloud API call).
- Giới hạn/cách xử lý: Presidio nhận diện nhầm tiếng Việt ("Nhân viên chính thức") thành `PERSON` -> đã cấu hình whitelist/filter chỉ quét `VN_CCCD`, `VN_PHONE`, `EMAIL_ADDRESS`. Tinh chỉnh prompt NeMo để không chặn nhầm câu hỏi hợp lệ về quy định mật khẩu.
- Nguồn/AI hỗ trợ nếu có: Tự kiểm chứng toàn bộ code qua unit tests và live benchmark.
