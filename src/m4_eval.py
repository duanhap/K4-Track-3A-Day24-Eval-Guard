from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Run RAGAS evaluation."""
    _zeros = {
        "faithfulness": 0.0, "answer_relevancy": 0.0,
        "context_precision": 0.0, "context_recall": 0.0,
        "per_question": [],
    }
    try:
        # Đảm bảo OPENAI_API_KEY được load trước khi RAGAS khởi tạo LLM
        from dotenv import load_dotenv
        load_dotenv()

        import os
        if not os.getenv("OPENAI_API_KEY"):
            print("  ⚠️  RAGAS skipped: OPENAI_API_KEY not set")
            return _zeros

        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        from datasets import Dataset

        dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        })
        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )
        df = result.to_pandas()

        # Tên cột trong RAGAS 0.3.x có thể là "user_input" thay vì "question"
        q_col      = "question"      if "question"      in df.columns else "user_input"
        a_col      = "answer"        if "answer"        in df.columns else "response"
        ctx_col    = "contexts"      if "contexts"      in df.columns else "retrieved_contexts"
        gt_col     = "ground_truth"  if "ground_truth"  in df.columns else "reference"

        per_question = [
            EvalResult(
                question=row.get(q_col, ""),
                answer=row.get(a_col, ""),
                contexts=row.get(ctx_col, []),
                ground_truth=row.get(gt_col, ""),
                faithfulness=float(row.get("faithfulness") or 0.0),
                answer_relevancy=float(row.get("answer_relevancy") or 0.0),
                context_precision=float(row.get("context_precision") or 0.0),
                context_recall=float(row.get("context_recall") or 0.0),
            )
            for _, row in df.iterrows()
        ]

        def _mean(col):
            return float(df[col].mean()) if col in df.columns else 0.0

        evaluator_models = ["gpt-4o-mini", "text-embedding-ada-002"]
        return {
            "faithfulness":      _mean("faithfulness"),
            "answer_relevancy":  _mean("answer_relevancy"),
            "context_precision": _mean("context_precision"),
            "context_recall":    _mean("context_recall"),
            "per_question":      per_question,
            "metadata": {
                "evaluator_models": evaluator_models,
            },
        }

    except Exception as e:
        print(f"  ⚠️  RAGAS evaluation failed: {e}")
        return {**_zeros, "metadata": {"evaluator_models": ["gpt-4o-mini", "text-embedding-ada-002"]}}


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    diagnostic_tree = {
        "faithfulness":        ("LLM hallucinating — tự bịa câu trả lời ngoài tài liệu",
                                "Tighten system prompt, set temperature=0"),
        "context_recall":      ("Missing relevant chunks — hệ thống bỏ sót đoạn văn đúng",
                                "Improve chunking strategy or add more BM25 keywords"),
        "context_precision":   ("Too many irrelevant chunks — đoạn không liên quan xếp lên đầu",
                                "Add Cross-Encoder reranking or metadata filter"),
        "answer_relevancy":    ("Answer off-topic — câu trả lời lạc đề so với câu hỏi",
                                "Rewrite prompt template to force direct answers"),
    }

    analyzed = []
    for er in eval_results:
        scores = {
            "faithfulness":      er.faithfulness,
            "context_recall":    er.context_recall,
            "context_precision": er.context_precision,
            "answer_relevancy":  er.answer_relevancy,
        }
        avg = sum(scores.values()) / len(scores)
        worst_metric = min(scores, key=lambda k: scores[k])
        diagnosis, suggested_fix = diagnostic_tree[worst_metric]
        analyzed.append({
            "question":      er.question,
            "avg_score":     round(avg, 4),
            "worst_metric":  worst_metric,
            "score":         round(scores[worst_metric], 4),
            "diagnosis":     diagnosis,
            "suggested_fix": suggested_fix,
        })

    # Sắp xếp tăng dần theo avg_score → bottom_n câu tệ nhất
    analyzed.sort(key=lambda x: x["avg_score"])
    return analyzed[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
