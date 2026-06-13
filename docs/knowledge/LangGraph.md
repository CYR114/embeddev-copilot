# LangGraph 知识总结

## 1. 什么是 LangGraph

**LangGraph** 是 LangChain 团队推出的 Agent 工作流编排框架，基于**有向图（Graph）** 建模 LLM 应用的执行流程，支持循环、分支、并行和状态管理。

与 LangChain Agent 的区别：

| 维度 | LangChain Agent | LangGraph |
|------|----------------|-----------|
| 控制流 | LLM 自主决策（黑盒） | 开发者显式定义图结构 |
| 循环 | 有限支持 | 原生支持 |
| 状态 | 简单 Memory | 强类型 State + Reducer |
| 可观测 | 一般 | 每个节点可追踪 |
| 适用 | 简单工具调用 | 复杂多步工作流 |

---

## 2. 核心概念

### 2.1 State（状态）

图的共享数据结构，每个节点读取和更新 State：

```python
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]  # Reducer: 追加
    requirement: str
    code: str
    current_step: str
```

**Reducer**：定义同一字段多次更新时的合并策略
- `operator.add`：列表追加（常用于 messages）
- 默认：覆盖

### 2.2 Node（节点）

一个 Python 函数，接收 State，返回 State 更新：

```python
def analyze_node(state: AgentState) -> dict:
    requirement = state["requirement"]
    analysis = llm.invoke(f"分析需求: {requirement}")
    return {
        "analysis": analysis.content,
        "current_step": "analyze",
        "messages": [AIMessage(content="分析完成")],
    }
```

### 2.3 Edge（边）

定义节点间的转移关系：

```python
# 固定边：A 完成后一定到 B
workflow.add_edge("analyze", "generate_code")

# 条件边：根据 State 动态路由
def should_continue(state):
    if state["review_passed"]:
        return "end"
    return "regenerate"

workflow.add_conditional_edges("review", should_continue, {
    "end": END,
    "regenerate": "generate_code",
})
```

### 2.4 Graph 编译与执行

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)
workflow.add_node("analyze", analyze_node)
workflow.add_node("generate_code", code_node)
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "generate_code")
workflow.add_edge("generate_code", END)

app = workflow.compile()
result = app.invoke({"requirement": "实现 CAN 驱动"})
```

---

## 3. 架构模式

### 3.1 线性 Pipeline（本项目使用）

```
需求分析 → 代码生成 → 测试生成 → 代码审查 → END
```

适合：步骤固定、无需回环的 SDLC 流程。

### 3.2 ReAct 循环

```
        ┌──────────┐
        │  Reason  │ ← LLM 思考下一步
        └────┬─────┘
             ▼
        ┌──────────┐
        │   Act    │ ← 调用工具
        └────┬─────┘
             ▼
        ┌──────────┐
   ┌─── │ Observe  │ ← 获取工具结果
   │    └──────────┘
   │         │
   └─ 未完成 ─┘
             │ 完成
             ▼
            END
```

适合：开放式问题求解、自主工具调用。

### 3.3 多 Agent 协作

```
         ┌──────────┐
         │ Supervisor│ ← 路由到专业 Agent
         └────┬─────┘
    ┌────────┼────────┐
    ▼        ▼        ▼
 Analyst  Coder    Reviewer
```

适合：不同领域需要不同专家 Agent。

### 3.4 Human-in-the-Loop

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["review"])

# 执行到 review 前暂停，等待人工确认
config = {"configurable": {"thread_id": "session-1"}}
result = app.invoke(input, config)
# 人工审核后恢复
app.invoke(None, config)  # 从断点继续
```

适合：代码审查需人工确认、高风险操作。

---

## 4. 高级特性

### 4.1 持久化与检查点

```python
from langgraph.checkpoint.memory import MemorySaver
# 或 SqliteSaver / PostgresSaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

支持：断点续跑、多轮对话、状态回溯。

### 4.2 子图（Subgraph）

将复杂流程封装为子图，主图调用：

```python
code_gen_subgraph = build_code_gen_graph().compile()
workflow.add_node("code_gen", code_gen_subgraph)
```

### 4.3 并行执行

```python
from langgraph.graph import Send

def fan_out(state):
    return [Send("process_chunk", {"chunk": c}) for c in state["chunks"]]

workflow.add_conditional_edges("split", fan_out)
```

### 4.4 流式输出

```python
for event in app.stream(initial_state):
    for node_name, update in event.items():
        print(f"[{node_name}] {update}")
```

---

## 5. 与 LangChain 的关系

```
LangChain = 组件库（Model, Prompt, Tool, Retriever...）
LangGraph = 编排引擎（用 LangChain 组件作为节点内的实现）
```

LangGraph 的每个节点内部可以使用 LangChain 的 Chain：

```python
def code_node(state):
    # 节点内使用 LCEL Chain
    chain = code_prompt | llm | StrOutputParser()
    code = chain.invoke({"requirement": state["requirement"]})
    return {"code": code}
```

---

## 6. 设计原则

1. **State 最小化**：只存必要字段，避免 State 膨胀
2. **节点单一职责**：每个节点做一件事
3. **条件边显式化**：分支逻辑写在条件函数中，不散落在节点内
4. **错误节点**：添加专门的 error_handler 节点
5. **可观测**：用 `stream()` + 日志记录每步输入输出

---

## 7. 与本项目的关联

**EmbedDev Copilot** 使用 LangGraph 编排四阶段 Agent 工作流：

```python
# src/agents/workflow.py

workflow = StateGraph(AgentState)
workflow.add_node("analyze", self._node_analyze)          # 需求分析
workflow.add_node("generate_code", self._node_generate_code)  # 代码生成
workflow.add_node("generate_tests", self._node_generate_tests)  # 测试生成
workflow.add_node("review", self._node_review)            # 代码审查

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "generate_code")
workflow.add_edge("generate_code", "generate_tests")
workflow.add_edge("generate_tests", "review")
workflow.add_edge("review", END)
```

每个节点：
1. 从 RAG 知识库检索相关文档
2. 调用 LLM（或 Demo 引擎）执行任务
3. 更新 State 并传递下游

这正是岗位要求的 **"使用 LangChain/LangGraph 构建 Agent，支持任务自动化与流程编排"**。
