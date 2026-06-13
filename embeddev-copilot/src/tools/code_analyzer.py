"""代码分析工具：供 Agent 调用的静态检查"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class LintIssue:
    severity: str  # error | warning | info
    line: int
    message: str
    rule: str


class EmbeddedCodeAnalyzer:
    """轻量嵌入式代码静态分析（演示用，可对接 cppcheck / PC-lint）"""

    RULES = [
        ("MISRA-21.3", r"\bmalloc\b|\bfree\b|\brealloc\b", "warning", "避免动态内存分配"),
        ("MISRA-17.7", r"\bprintf\b|\bsprintf\b", "warning", "避免标准 IO，使用日志宏"),
        ("SAFETY-01", r"\bwhile\s*\(\s*1\s*\)", "info", "无限循环需确认有 break/看门狗"),
        ("STYLE-01", r"//\s*TODO", "info", "存在未完成的 TODO"),
        ("PTR-01", r"(\w+)\s*\(\s*\)", "info", "检查空参数函数是否需要 const 修饰"),
    ]

    def analyze(self, code: str) -> list[LintIssue]:
        issues: list[LintIssue] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            for rule_id, pattern, severity, msg in self.RULES:
                if re.search(pattern, line):
                    issues.append(LintIssue(severity, i, msg, rule_id))

        return issues

    def format_report(self, issues: list[LintIssue]) -> str:
        if not issues:
            return "✅ 未发现静态分析问题"
        lines = ["## 静态分析报告", ""]
        for issue in issues:
            icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
            lines.append(f"{icon} L{issue.line} [{issue.rule}] {issue.message}")
        return "\n".join(lines)


def complete_code(prefix: str, context: str = "") -> str:
    """代码补全工具接口"""
    from src.llm.demo_engine import DemoEngine

    return DemoEngine().complete_code(prefix, context)
