# EmbedDev Copilot — 车载嵌入式 AI 编程助手

> **面向岗位**：小鹏汽车【27届暑期】嵌入式软件实习生（AI）  
> **技术栈**：LLM · RAG · LangChain · LangGraph · CodeAgent · 评估 Benchmark

---

## 项目亮点（简历可直接使用）

**EmbedDev Copilot** 是一个面向车载 ECU 固件开发的 AI 编程助手，将 LLM 与 RAG 技术落地到嵌入式软件全生命周期：

| 能力 | 实现 | 对应岗位要求 |
|------|------|-------------|
| 需求分析 | RAG 检索编码规范 + LLM 结构化拆解 | LLM/RAG 探索研发流程应用 |
| 代码生成 | LangGraph 多 Agent 编排生成 MISRA-C 代码 | AI 编程工具 / CodeAgent |
| 测试生成 | 自动生成 Unity 单元测试用例 | 自动化测试用例生成 |
| 代码审查 | 静态规则检查 + LLM 审查报告 | 错误检测与代码优化 |
| 知识问答 | 基于 ChromaDB 的文档 RAG 问答 | 工程文档整理与检索 |
| 质量评估 | 5 类 Benchmark + 通过率报告 | 评估数据集构建 |

### 简历项目描述（精简版）

```
EmbedDev Copilot | 车载嵌入式 AI 编程助手 | Python, LangChain, LangGraph
- 基于 RAG 构建车载 ECU 编码规范/CAN/ADC 技术知识库，支持语义检索增强问答
- 使用 LangGraph 编排「需求分析→代码生成→测试生成→代码审查」四阶段 Agent 工作流
- 实现代码补全、MISRA-C 静态检查工具，覆盖内存安全与编码规范检测
- 构建 5 类代码生成评估数据集，关键词覆盖率 + 安全规则双维度 Benchmark
- 提供 FastAPI 服务与 CLI Demo，支持无 API Key 的离线演示模式
```

### 简历项目描述（详细版）

```
EmbedDev Copilot — 面向小鹏车载 ECU 的 AI 辅助开发平台
• 探索 LLM/RAG 在嵌入式软件研发流程中的应用：需求分析、代码生成、测试用例自动生成
• 使用 LangChain + ChromaDB 实现工程文档 RAG 检索，覆盖编码规范、CAN 驱动、MISRA-C 规则
• 基于 LangGraph 构建 CodeAgent 多 Agent 工作流，串联 4 个专业化 Agent 节点
• 开发嵌入式代码静态分析工具（动态内存检测、printf 禁用、看门狗检查）
• 设计代码生成评估 Benchmark（5 用例 × 关键词覆盖 + 安全规则），量化模型输出质量
• 技术调研：AI Agent 架构、Code LLM 应用、Prompt Engineering 最佳实践
```

---

## 快速开始

### 1. 环境准备

```bash
cd embeddev-copilot
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env   # 可选：填入 OPENAI_API_KEY
```

### 2. 构建知识库

```bash
python scripts/build_index.py
```

### 3. 运行 Agent 演示

```bash
python scripts/run_agent_demo.py "实现 CAN 驱动模块，支持初始化和报文发送"
```

### 4. 运行评估 Benchmark

```bash
python scripts/run_eval.py
```

### 5. 启动 API 服务

```bash
uvicorn src.api.server:app --reload --port 8000
```

访问 `http://127.0.0.1:8000/docs` 查看 Swagger 文档。

---

## 架构设计

```
用户需求
   │
   ▼
┌──────────────────────────────────────────────┐
│           LangGraph Agent 工作流              │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────┐ │
│  │需求分析│→│代码生成│→│测试生成│→│审查│ │
│  └────┬───┘  └────┬───┘  └────────┘  └────┘ │
│       │           │                          │
│       ▼           ▼                          │
│  ┌─────────────────────┐                     │
│  │   RAG 知识库检索     │                     │
│  │ ChromaDB + Embedding│                     │
│  └─────────────────────┘                     │
└──────────────────────────────────────────────┘
   │
   ▼
输出: 分析文档 + C 代码 + 单元测试 + 审查报告
```

---

## 目录结构

```
embeddev-copilot/
├── src/
│   ├── agents/        # LangGraph 多 Agent 工作流
│   ├── rag/           # RAG 检索增强生成
│   ├── llm/           # LLM 工厂 + Demo 引擎
│   ├── tools/         # 代码分析 / 补全工具
│   ├── eval/          # 评估 Benchmark
│   └── api/           # FastAPI 服务
├── data/
│   ├── docs/          # 嵌入式技术文档（知识库源）
│   └── eval/          # 评估数据集
├── scripts/           # 构建索引 / 演示 / 评估脚本
└── requirements.txt
```

---

## Demo 模式

默认 `DEMO_MODE=true`，无需 API Key 即可完整演示所有功能。  
接入真实 LLM 时，在 `.env` 中设置：

```
DEMO_MODE=false
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
```

---

## 面试话术要点

1. **为什么做嵌入式方向？** 岗位是"嵌入式软件实习生（AI）"，项目将 AI 能力与车载 ECU 固件开发结合，不是泛泛的 ChatBot
2. **RAG 的价值？** 通用 LLM 不懂公司内部编码规范和 CAN 参数，RAG 让回答有据可依
3. **为什么用 LangGraph？** 代码生成不是单步任务，需要需求→代码→测试→审查的流程编排
4. **评估怎么做？** 不只看"能不能跑"，用关键词覆盖率和 MISRA 安全规则量化质量

---

## License

MIT — 仅供学习及求职作品集使用
