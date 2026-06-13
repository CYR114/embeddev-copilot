# Code LLM（代码大模型）知识总结

## 1. 什么是 Code LLM

**Code LLM** 是在大量代码数据上训练或微调的大语言模型，专门针对**代码理解、生成、补全、调试**等编程任务优化。

与普通 LLM 的区别：

| 维度 | 通用 LLM | Code LLM |
|------|---------|----------|
| 训练数据 | 通用文本 | 代码 + 技术文档为主 |
| 代码能力 | 一般 | 强（语法正确率高） |
| 支持语言 | 通用 | 多语言（Python/C/Java/Go...） |
| 上下文理解 | 自然语言 | 代码结构（AST/缩进） |
| 应用场景 | 对话/写作 | IDE 补全/Agent/自动修复 |

---

## 2. 主流 Code LLM

### 2.1 闭源模型

| 模型 | 公司 | 特点 |
|------|------|------|
| GPT-4o | OpenAI | 综合最强，多语言 |
| Claude 3.5 Sonnet | Anthropic | 长上下文，代码审查强 |
| GitHub Copilot | Microsoft | IDE 深度集成 |
| Cursor | Anysphere | 多文件 Agent 编辑 |

### 2.2 开源模型

| 模型 | 参数量 | 特点 |
|------|--------|------|
| DeepSeek-Coder V2 | 16B/236B | 中文友好，代码能力强 |
| Qwen2.5-Coder | 7B/32B | 阿里开源，多语言 |
| CodeLlama | 7B/13B/34B | Meta 开源基线 |
| StarCoder2 | 3B/7B/15B | BigCode 社区 |
| Codestral | 22B | Mistral 代码专用 |

### 2.3 嵌入式设计相关的 Code LLM 考量

车载嵌入式开发主要使用 **C/C++**，选择模型时关注：

1. C 语言训练数据占比
2. 是否理解 MISRA-C / AUTOSAR 等规范
3. 能否生成硬件寄存器操作代码
4. 是否支持长上下文（阅读大型代码库）

---

## 3. Code LLM 训练

### 3.1 数据构成

```
预训练数据:
├── 开源代码仓库 (GitHub)          ~60%
├── 技术文档 / Stack Overflow      ~15%
├── 通用文本                      ~15%
└── 合成代码数据                   ~10%
```

### 3.2 数据清洗

岗位提到的"代码数据整理、清洗和标注"对应：

| 步骤 | 说明 | 工具/方法 |
|------|------|----------|
| 去重 | 删除重复/近似代码 | MinHash / SimHash |
| 过滤 | 移除低质量/有毒代码 | 启发式规则 + 分类器 |
| 格式化 | 统一缩进、编码 | AST 解析 |
| 标注 | 标记语言、功能、质量 | 人工 + 自动标注 |
| 脱敏 | 移除密钥、内部路径 | 正则 + NER |

### 3.3 微调方法

| 方法 | 说明 | 成本 |
|------|------|------|
| Full Fine-tuning | 全参数微调 | 高（需大量 GPU） |
| LoRA | 低秩适配，只训练小矩阵 | 低（单卡可跑） |
| QLoRA | 量化 + LoRA | 更低 |
| Prompt Tuning | 只训练 Prompt 嵌入 | 最低 |

嵌入式场景微调示例：

```
训练数据格式 (Instruction Tuning):
{
  "instruction": "根据需求生成 MISRA-C 兼容的 CAN 驱动",
  "input": "实现 Can_Init 和 Can_Transmit，波特率 500K",
  "output": "Status_t Can_Init(...) { ... }"
}
```

---

## 4. Code LLM 应用场景

### 4.1 代码补全（Completion）

IDE 中根据上下文续写代码：

```c
// 用户输入:
Status_t Can_Init(const Can_Config_t *cfg) {
    if (cfg == NULL) return STATUS_INVALID_

// 模型补全:
PARAM;
    Can_Hw_Init(cfg->baudrate);
    s_state = CAN_STATE_READY;
    return STATUS_OK;
}
```

关键技术：FIM（Fill-in-the-Middle）训练，支持中间补全。

### 4.2 代码生成（Generation）

从自然语言描述生成完整代码模块（本项目核心能力）。

### 4.3 代码翻译

```c
// C → Rust 安全迁移
// Python 原型 → C 生产代码
```

### 4.4 Bug 修复

```
输入: 有 Bug 的代码 + 错误信息
输出: 修复后的代码 + 修复说明
```

SWE-bench 是此场景的标准 Benchmark。

### 4.5 测试生成

```
输入: 被测函数代码
输出: 覆盖边界条件的单元测试
```

### 4.6 代码审查

```
输入: 代码
输出: 问题列表（安全、性能、规范）
```

---

## 5. 评估 Benchmark

### 5.1 通用代码 Benchmark

| Benchmark | 内容 | 指标 |
|-----------|------|------|
| HumanEval | 164 道 Python 函数题 | Pass@k |
| MBPP | 基础 Python 编程题 | Pass@k |
| SWE-bench | 真实 GitHub Issue | 修复率 |
| CodeContests | 竞赛级编程题 | Pass@k |

### 5.2 评估指标

- **Pass@k**：生成 k 个候选中至少 1 个通过测试的概率
- **BLEU/CodeBLEU**：生成代码与参考代码的相似度
- **编译通过率**：生成的代码能否编译
- **功能正确率**：测试用例通过率

### 5.3 本项目的评估方案

针对嵌入式 C 代码的定制 Benchmark：

```json
{
  "id": "can_init",
  "requirement": "实现 CAN 驱动...",
  "expected_keywords": ["Can_Init", "Status_t", "STATUS_OK"],
  "forbidden_patterns": ["malloc", "printf"]
}
```

评估维度：
1. **关键词覆盖率**（60% 权重）：是否包含预期函数名和返回值
2. **安全规则分**（30% 权重）：是否触犯 MISRA 禁止项
3. **结构完整性**（10% 权重）：是否有函数定义

---

## 6. 优化策略

### 6.1 提升代码生成质量

| 策略 | 做法 |
|------|------|
| RAG 增强 | 注入编码规范和 API 文档 |
| Few-shot | 提供高质量代码示例 |
| 低 Temperature | 0.0-0.2 减少随机性 |
| 分步生成 | 先接口设计，再实现 |
| 自我审查 | 生成后让模型检查自身输出 |

### 6.2 领域适配

通用 Code LLM → 嵌入式 C 代码的 Gap：

| Gap | 解决方案 |
|-----|---------|
| 不懂 MISRA-C | RAG 注入规则 + Prompt 约束 |
| 喜欢用 malloc | Prompt 禁止 + 后处理检查 |
| 寄存器操作错误 | RAG 注入硬件手册 |
| 不懂 AUTOSAR 风格 | Few-shot AUTOSAR 风格示例 |

---

## 7. 技术趋势

1. **多模态 Code LLM**：理解代码 + 架构图 + 时序图
2. **Repository-level 理解**：理解整个代码仓库而非单文件
3. **Agentic Coding**：Code LLM + Agent 框架 = 自主开发
4. **Small Code Model**：3B-7B 模型在 IDE 本地运行
5. **合成数据训练**：用强模型生成训练数据教小模型

---

## 8. 与本项目的关联

| 功能 | Code LLM 应用 |
|------|--------------|
| 代码生成 | Agent `generate_code` 节点 |
| 测试生成 | Agent `generate_tests` 节点 |
| 代码补全 | `tools/complete` API |
| 代码审查 | Agent `review` 节点 + 静态分析 |
| 评估 | `eval/benchmark.py` 5 类用例 |

数据工程对应：
- `data/docs/` — 工程文档（RAG 知识源）
- `data/eval/codegen_cases.json` — 评估数据集

相关文件：`src/agents/workflow.py`、`src/eval/benchmark.py`、`src/tools/code_analyzer.py`
