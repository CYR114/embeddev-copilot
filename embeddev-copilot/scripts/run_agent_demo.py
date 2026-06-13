"""CLI 演示：完整 Agent 工作流"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402

from src.agents.workflow import EmbedDevAgentGraph  # noqa: E402

console = Console(force_terminal=True, legacy_windows=False)


def main():
    requirement = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "实现一个 CAN 总线驱动模块，支持初始化、发送报文，遵循 AUTOSAR 风格接口"
    )

    console.print(Panel(f"[bold]需求[/bold]\n{requirement}", title="EmbedDev Copilot"))
    agent = EmbedDevAgentGraph()
    result = agent.run(requirement)

    for key, title in [
        ("analysis", "需求分析"),
        ("code", "生成代码"),
        ("tests", "单元测试"),
        ("review", "代码审查"),
    ]:
        console.print(Panel(result[key], title=title, border_style="cyan"))

    out = ROOT / "data" / "output" / "last_run.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"\n[green]结果已保存[/green]: {out}")


if __name__ == "__main__":
    main()
