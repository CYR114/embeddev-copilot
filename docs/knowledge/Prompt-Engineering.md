# Prompt Engineering（提示工程）知识总结

## 1. 什么是 Prompt Engineering

**Prompt Engineering** 是通过设计和优化输入提示（Prompt），引导 LLM 产生更准确、更一致、更符合预期的输出。它是 LLM 应用开发中**成本最低、见效最快**的优化手段。

---

## 2. Prompt 的基本结构

```
┌─────────────────────────────────┐
│  System Prompt（系统指令）        │  ← 角色、规则、输出格式
├─────────────────────────────────┤
│  Context（上下文）               │  ← RAG 检索结果、代码、文档
├─────────────────────────────────┤
│  Few-shot Examples（示例）       │  ← 输入输出范例
├─────────────────────────────────┤
│  User Query（用户输入）          │  ← 具体问题/需求
└─────────────────────────────────┘
```

### 示例：嵌入式代码生成 Prompt

```
[System]
你是资深嵌入式软件工程师，精通 MISRA-C、AUTOSAR 和车载 CAN 通信。
生成代码必须：
1. 使用 Status_t 返回值
2. 所有指针参数做空指针检查
3. 禁止使用 malloc/free 和 printf
4. 添加完整的函数注释

[Context]
参考文档:
{rag_context}

[User]
请根据以下需求生成 C 代码:
{requirement}

需求分析:
{analysis}
```

---

## 3. 核心技巧

### 3.1 Zero-shot（零样本）

直接描述任务，不给示例：

```
分析以下嵌入式软件需求，输出模块划分和接口设计:
{requirement}
```

适用：模型能力足够、任务简单明确。

### 3.2 Few-shot（少样本）

提供 1-5 个输入输出示例：

```
示例 1:
需求: 实现 GPIO 初始化
输出:
Status_t Gpio_Init(void) {
    if (s_initialized) return STATUS_ALREADY_INIT;
    Gpio_Hw_Init();
    s_initialized = true;
    return STATUS_OK;
}

现在请处理:
需求: {requirement}
```

适用：需要特定输出格式或风格。

### 3.3 Chain-of-Thought（思维链）

引导模型逐步推理：

```
请按以下步骤分析:
1. 识别需求中的硬件模块
2. 列出需要的接口函数
3. 分析可能的错误场景
4. 给出接口设计建议

需求: {requirement}
```

适用：复杂需求分析、Bug 诊断。

### 3.4 Self-Consistency

同一问题多次生成，投票选最优：

```python
answers = [chain.invoke(question) for _ in range(5)]
best = majority_vote(answers)
```

适用：高准确性要求的场景。

### 3.5 Role Prompting（角色设定）

```
你是一位有 10 年经验的车载 ECU 固件工程师，
熟悉小鹏汽车的编码规范和 AUTOSAR 架构...
```

效果：让输出更专业、更符合领域习惯。

---

## 4. 结构化输出

### 4.1 用 Pydantic 约束输出格式

```python
from pydantic import BaseModel, Field

class RequirementAnalysis(BaseModel):
    modules: list[str] = Field(description="涉及的软件模块")
    interfaces: list[str] = Field(description="需要实现的接口")
    risks: list[str] = Field(description="潜在技术风险")
    dependencies: list[str] = Field(description="硬件依赖")

parser = JsonOutputParser(pydantic_object=RequirementAnalysis)
chain = prompt | llm | parser
```

### 4.2 XML / Markdown 标签分隔

```
<analysis>
模块划分内容...
</analysis>

<code>
生成的 C 代码...
</code>

<tests>
单元测试代码...
</tests>
```

便于后处理提取各部分内容。

---

## 5. 参数调优

| 参数 | 代码生成推荐 | 创意写作推荐 | 说明 |
|------|------------|------------|------|
| temperature | 0.0 - 0.2 | 0.7 - 1.0 | 越低越确定性 |
| top_p | 0.9 | 0.95 | 核采样范围 |
| max_tokens | 2048-4096 | 不限 | 控制输出长度 |
| presence_penalty | 0 | 0.5 | 减少重复 |
| frequency_penalty | 0.1 | 0 | 减少用词重复 |

**代码生成原则**：低 temperature + 明确格式约束 + Few-shot 示例。

---

## 6. 常见模式

### 6.1 分步拆解（Decomposition）

复杂任务拆为多个简单 Prompt 依次执行：

```
Step 1: 需求分析 → analysis
Step 2: 基于 analysis 生成代码 → code
Step 3: 基于 code 生成测试 → tests
Step 4: 审查 code → review
```

这正是 LangGraph 多节点工作流的 Prompt 策略。

### 6.2 自我审查（Self-Refine）

```
生成代码 → "审查以下代码的问题" → 修正 → 再审查 → ...直到通过
```

### 6.3 对比选择（Best-of-N）

```
生成 3 个方案 → "比较以下方案，选择最优" → 输出最终方案
```

---

## 7. 反模式（避免）

| 反模式 | 问题 | 改进 |
|--------|------|------|
| Prompt 过长 | 浪费 Token，关键指令被稀释 | 精简 + RAG 按需检索 |
| 指令含糊 | "写好一点" → 输出不稳定 | 具体约束 + 示例 |
| 无输出格式要求 | 自由文本难以解析 | Pydantic / XML 标签 |
| 无边界声明 | 模型编造不存在的内容 | "仅基于提供的文档回答" |
| 单次 Prompt 做所有事 | 质量下降 | 分步 / 多节点 |

---

## 8. Prompt 版本管理

建议实践：

```
prompts/
├── analyze_requirement_v1.txt
├── generate_code_v2.txt      # 增加了 MISRA 约束
├── generate_tests_v1.txt
└── review_code_v1.txt
```

- 每次修改记录变更原因
- A/B 测试不同版本的效果
- 用评估 Benchmark 量化 Prompt 改动的影响

---

## 9. 与本项目的关联

| Agent 节点 | Prompt 策略 |
|-----------|------------|
| 需求分析 | Role + CoT + RAG Context |
| 代码生成 | Role + 强约束（MISRA） + Few-shot 风格 |
| 测试生成 | 指定框架（Unity） + 代码输入 |
| 代码审查 | 检查清单 + 严重级别分类 |

关键参数：`temperature=0.2`（确定性输出）

相关文件：`src/rag/pipeline.py`（RAG Prompt）、`src/agents/workflow.py`（各节点 Prompt）
