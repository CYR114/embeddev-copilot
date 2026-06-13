# AI Agent 知识总结

## 1. 什么是 AI Agent

**AI Agent（智能体）** 是以 LLM 为"大脑"，能够**自主感知环境、制定计划、调用工具、执行行动**的软件实体。

与普通 LLM 对话的区别：

| 维度 | LLM 对话 | AI Agent |
|------|---------|----------|
| 交互方式 | 问答 | 自主执行任务 |
| 工具使用 | 无 | 可调用外部工具/API |
| 规划能力 | 单步回答 | 多步规划与执行 |
| 状态管理 | 对话历史 | 复杂工作流状态 |
| 反馈循环 | 无 | 观察结果并调整 |

```
感知 (Perceive) → 思考 (Think) → 行动 (Act) → 观察 (Observe) → 循环
```

---

## 2. Agent 架构模式

### 2.1 ReAct（Reasoning + Acting）

最经典的 Agent 模式，交替进行推理和行动：

```
Thought: 用户要生成 CAN 驱动，我需要先检索编码规范
Action: search_docs("CAN 驱动规范")
Observation: 找到 can_driver_guide.md，波特率 500K...
Thought: 现在我有足够信息，可以生成代码了
Action: generate_code(requirement, context)
Observation: 代码已生成，包含 Can_Init 和 Can_Transmit
Thought: 任务完成
Action: Finish
```

### 2.2 Plan-and-Execute

先制定完整计划，再逐步执行：

```
Plan:
  1. 分析需求 → 确定模块和接口
  2. 检索 CAN 相关文档
  3. 生成驱动代码
  4. 生成单元测试
  5. 静态代码审查

Execute: 按 Plan 逐步执行，每步结果影响后续步骤
```

**EmbedDev Copilot 采用的正是此模式**（LangGraph 线性工作流）。

### 2.3 Multi-Agent（多智能体）

多个专业化 Agent 协作：

```
┌─────────────┐
│  Supervisor  │  分配任务
└──────┬──────┘
   ┌───┼───┬───────┐
   ▼   ▼   ▼       ▼
 需求  代码  测试   审查
 Agent Agent Agent Agent
```

框架支持：LangGraph、AutoGen、CrewAI、MetaGPT

### 2.4 Tool-Use Agent

LLM 通过 Function Calling 选择并调用工具：

```python
tools = [
    {"name": "search_docs", "description": "搜索技术文档"},
    {"name": "analyze_code", "description": "静态分析 C 代码"},
    {"name": "run_tests", "description": "执行单元测试"},
]
# LLM 根据用户需求自主选择调用哪个工具
```

---

## 3. Agent 核心组件

### 3.1 大脑（Brain）— LLM

- 负责理解任务、推理决策、生成内容
- 选择：通用 LLM（GPT-4）或 Code LLM（DeepSeek-Coder）

### 3.2 记忆（Memory）

| 类型 | 说明 | 实现 |
|------|------|------|
| 短期记忆 | 当前对话上下文 | ConversationBuffer |
| 长期记忆 | 跨会话知识 | VectorStore |
| 工作记忆 | 当前任务中间状态 | LangGraph State |

### 3.3 工具（Tools）

Agent 与外部世界交互的接口：

```python
@tool
def search_coding_standard(query: str) -> str:
    """搜索车载嵌入式编码规范"""
    return rag_pipeline.query(query)["answer"]

@tool
def lint_c_code(code: str) -> str:
    """对 C 代码进行 MISRA 静态检查"""
    return analyzer.format_report(analyzer.analyze(code))
```

### 3.4 规划器（Planner）

- 将复杂任务分解为子任务
- 确定执行顺序和依赖关系
- LangGraph 的 Graph 结构即为显式规划器

---

## 4. CodeAgent 专题

岗位明确提到 **CodeAgent**，这是专为软件开发设计的 Agent：

### CodeAgent 能力矩阵

| 能力 | 说明 | 本项目实现 |
|------|------|-----------|
| 代码补全 | 根据上下文续写代码 | `tools/complete` API |
| 代码生成 | 需求 → 完整模块代码 | Agent `generate_code` 节点 |
| 错误检测 | 静态分析 + LLM 审查 | `tools/analyze` + `review` 节点 |
| 测试生成 | 自动生成单元测试 | Agent `generate_tests` 节点 |
| 代码解释 | 解释复杂代码逻辑 | RAG 问答 |
| 重构建议 | 提出优化方案 | 审查节点 |

### 业界 CodeAgent 产品

| 产品 | 公司 | 特点 |
|------|------|------|
| Cursor | Anysphere | IDE 集成，多文件编辑 |
| GitHub Copilot | Microsoft | 代码补全 |
| Devin | Cognition | 自主 SWE Agent |
| SWE-Agent | Princeton | 开源 Bug 修复 Agent |
| OpenHands | All-Hands-AI | 开源 CodeAgent 框架 |

---

## 5. Agent 评估

### 评估维度

| 维度 | 指标 | 衡量方式 |
|------|------|---------|
| 任务完成率 | 是否达成目标 | 端到端测试 |
| 步骤效率 | 用了多少步 | 统计 Agent 步数 |
| 工具选择准确率 | 是否调对工具 | 对比最优路径 |
| 输出质量 | 代码正确性 | Benchmark 评估 |
| 成本控制 | Token 消耗 | 统计 API 费用 |

### 常见 Benchmark

- **SWE-bench**：真实 GitHub Issue 修复
- **HumanEval**：Python 函数生成
- **MBPP**：基础编程题
- **本项目 Benchmark**：嵌入式 C 代码生成（关键词 + 安全规则）

---

## 6. Agent 安全

| 风险 | 说明 | 防护 |
|------|------|------|
| 无限循环 | Agent 反复调用工具 | 设置 max_iterations |
| 危险操作 | 执行删除/修改命令 | 工具白名单 + 人工确认 |
| 幻觉行动 | 调用不存在的工具 | 严格 Tool Schema |
| 数据泄露 | 将敏感信息发送给 API | 本地部署 / 数据脱敏 |
| 输出不安全代码 | 生成有漏洞的代码 | 静态分析 + 规则审查 |

---

## 7. 技术趋势

1. **Multi-Agent 协作**：专业化 Agent 分工（如本项目四节点）
2. **Computer Use**：Agent 直接操作 IDE/终端/GUI
3. **长期记忆**：跨项目经验积累
4. **边缘 Agent**：车载/嵌入式设备上的轻量 Agent
5. **Agent + RAG 深度融合**：Agent 自主决定何时检索、检索什么

---

## 8. 与本项目的关联

**EmbedDev Copilot** 是一个面向嵌入式软件开发的 CodeAgent：

```
Agent 工作流 (LangGraph):
  需求分析 Agent → 代码生成 Agent → 测试生成 Agent → 审查 Agent

工具集:
  - RAG 文档检索
  - C 代码静态分析
  - 代码补全

记忆:
  - RAG 向量库（长期记忆）
  - LangGraph State（工作记忆）

评估:
  - 5 类 Benchmark 量化代码生成质量
```

相关文件：`src/agents/workflow.py`、`src/tools/code_analyzer.py`
