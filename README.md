# 求职作品集总览

本仓库为 **小鹏汽车【27届暑期】嵌入式软件实习生（AI）** 岗位定制。

## 核心交付物

| 文件/目录 | 说明 |
|-----------|------|
| [embeddev-copilot/](embeddev-copilot/) | 主项目：车载嵌入式 AI 编程助手 |
| [docs/knowledge/](docs/knowledge/) | LLM/RAG/LangChain 等知识点总结 |

## 岗位匹配度

```
岗位要求                              项目对应
─────────────────────────────────────────────────────
LLM/RAG 探索研发流程应用          → RAG 知识库 + Agent 工作流
AI 编程工具 (CodeAgent)           → 代码生成/补全/审查/测试
LangChain / LangGraph Agent       → 四阶段 Agent 编排
Prompt 设计与模型调优             → 各节点专用 Prompt + Demo/LLM 双模式
代码数据整理与评估数据集           → 5 类 Benchmark 评估集
AI Agent / Code LLM 技术调研      → docs/knowledge/ 知识文档
```

## 快速体验

```bash
cd embeddev-copilot
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python scripts/build_index.py
python scripts/run_agent_demo.py
```

## 简历一句话

> 独立开发 EmbedDev Copilot 车载嵌入式 AI 编程助手，基于 LangGraph 编排多 Agent 工作流，结合 RAG 知识库实现需求分析、MISRA-C 代码生成、单元测试自动生成与质量评估。
