"""模型评估：代码生成质量 Benchmark"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EvalCase:
    id: str
    requirement: str
    expected_keywords: list[str] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)
    category: str = "general"


@dataclass
class EvalResult:
    case_id: str
    passed: bool
    keyword_score: float
    safety_score: float
    details: str


class CodeGenEvaluator:
    """评估代码生成：关键词覆盖 + 安全规则 + 结构完整性"""

    def __init__(self, dataset_path: str | Path | None = None):
        self.cases: list[EvalCase] = []
        if dataset_path:
            self.load(dataset_path)

    def load(self, path: str | Path) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.cases = [EvalCase(**item) for item in data]

    def evaluate_single(self, case: EvalCase, generated_code: str) -> EvalResult:
        keyword_hits = sum(1 for kw in case.expected_keywords if kw.lower() in generated_code.lower())
        keyword_score = keyword_hits / max(len(case.expected_keywords), 1)

        forbidden_hits = sum(
            1 for pat in case.forbidden_patterns if re.search(pat, generated_code, re.I)
        )
        safety_score = 1.0 if forbidden_hits == 0 else max(0, 1 - forbidden_hits * 0.3)

        has_function = bool(re.search(r"(void|int|Status_t)\s+\w+\s*\(", generated_code))
        structure_bonus = 0.2 if has_function else 0

        total = min(1.0, keyword_score * 0.6 + safety_score * 0.3 + structure_bonus)
        passed = total >= 0.6 and safety_score >= 0.7

        details = (
            f"关键词命中 {keyword_hits}/{len(case.expected_keywords)}, "
            f"安全分 {safety_score:.2f}, 综合 {total:.2f}"
        )
        return EvalResult(case.id, passed, keyword_score, safety_score, details)

    def evaluate_batch(self, outputs: dict[str, str]) -> dict:
        results = []
        for case in self.cases:
            code = outputs.get(case.id, "")
            results.append(self.evaluate_single(case, code))

        passed = sum(1 for r in results if r.passed)
        return {
            "total": len(results),
            "passed": passed,
            "pass_rate": passed / max(len(results), 1),
            "results": [
                {
                    "case_id": r.case_id,
                    "passed": r.passed,
                    "keyword_score": r.keyword_score,
                    "safety_score": r.safety_score,
                    "details": r.details,
                }
                for r in results
            ],
        }

    def report_markdown(self, eval_result: dict) -> str:
        lines = [
            "# 代码生成评估报告",
            "",
            f"- 总用例: {eval_result['total']}",
            f"- 通过: {eval_result['passed']}",
            f"- 通过率: {eval_result['pass_rate']:.1%}",
            "",
            "## 明细",
        ]
        for r in eval_result["results"]:
            status = "✅" if r["passed"] else "❌"
            lines.append(f"- {status} `{r['case_id']}`: {r['details']}")
        return "\n".join(lines)
