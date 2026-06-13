"""运行评估 Benchmark"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rich.console import Console  # noqa: E402

from src.agents.workflow import EmbedDevAgentGraph  # noqa: E402
from src.eval.benchmark import CodeGenEvaluator  # noqa: E402

console = Console()


def main():
    dataset = ROOT / "data" / "eval" / "codegen_cases.json"
    evaluator = CodeGenEvaluator(dataset)
    agent = EmbedDevAgentGraph()

    outputs = {}
    for case in evaluator.cases:
        console.print(f"运行用例: {case.id} ...")
        result = agent.run(case.requirement)
        outputs[case.id] = result["code"]

    report = evaluator.evaluate_batch(outputs)
    md = evaluator.report_markdown(report)
    console.print(md)

    out = ROOT / "data" / "output" / "eval_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    console.print(f"\n[green]报告已保存[/green]: {out}")


if __name__ == "__main__":
    main()
