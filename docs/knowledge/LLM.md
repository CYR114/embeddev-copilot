# 大语言模型（LLM）知识总结

## 1. 基础概念

### 什么是 LLM

大语言模型（Large Language Model）是基于 Transformer 架构、在海量文本上预训练的语言模型，通过预测下一个 Token 学习语言的统计规律与知识表征。

### 核心能力

| 能力 | 说明 | 嵌入式 AI 场景 |
|------|------|---------------|
| 文本生成 | 续写、翻译、摘要 | 需求文档生成、注释生成 |
| 代码生成 | 根据描述生成代码 | C 驱动、接口实现 |
| 推理 | 链式思考、逻辑推导 | 需求拆解、Bug 分析 |
| 对话 | 多轮上下文理解 | 编程助手交互 |

### 关键术语

- **Token**：模型处理的最小单位（英文约 4 字符/token，中文约 1-2 字/token）
- **Context Window**：模型一次能处理的最大 Token 数（4K ~ 128K+）
- **Temperature**：控制输出随机性（0=确定性，1=创造性）
- **Top-p / Top-k**：采样策略，控制候选词范围

---

## 2. 模型架构

### Transformer 核心

```
输入文本 → Tokenizer → Embedding → [Self-Attention × N] → FFN → 输出概率分布
```

- **Self-Attention**：每个 Token 关注序列中所有 Token，捕获长距离依赖
- **FFN**：前馈网络，增加非线性变换能力
- **位置编码**：注入 Token 在序列中的位置信息

### 主流架构变体

| 架构 | 代表模型 | 特点 |
|------|---------|------|
| 纯 Decoder | GPT 系列、LLaMA、Qwen | 自回归生成，适合对话/代码 |
| Encoder-Decoder | T5、BART | 适合翻译、摘要 |
| MoE | Mixtral、DeepSeek-V2 | 稀疏激活，降低推理成本 |

---

## 3. 训练范式

### 三阶段训练

```
预训练 (Pre-training)     →  海量无标注文本，学习语言知识
    ↓
监督微调 (SFT)            →  指令-回答对，学习遵循指令
    ↓
人类反馈强化学习 (RLHF)    →  人类偏好排序，对齐价值观
```

### 新兴对齐方法

- **DPO**（Direct Preference Optimization）：无需奖励模型，直接优化偏好
- **RLAIF**：用 AI 替代人类标注偏好
- **Constitutional AI**：用规则约束模型行为

---

## 4. 推理与部署

### 推理优化技术

| 技术 | 原理 | 效果 |
|------|------|------|
| 量化 (Quantization) | FP16/INT8/INT4 降低精度 | 减少显存，加速推理 |
| KV Cache | 缓存已计算的 Key/Value | 加速自回归生成 |
| 投机解码 (Speculative) | 小模型草稿 + 大模型验证 | 提升吞吐 |
| 批处理 (Batching) | 合并多个请求 | 提升 GPU 利用率 |

### 部署方式

- **云端 API**：OpenAI、Azure、国内大模型 API（简单、按量付费）
- **本地部署**：Ollama、vLLM、TGI（数据安全、低延迟）
- **边缘部署**：量化小模型跑在车载/嵌入式设备（本项目可延伸方向）

---

## 5. API 使用要点

### OpenAI 兼容接口

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key="sk-xxx",
    base_url="https://api.openai.com/v1",  # 可替换为国内 API
    temperature=0.2,  # 代码生成建议低温度
)
response = llm.invoke("实现一个 GPIO 初始化函数")
```

### 成本控制策略

1. 选用合适型号（gpt-4o-mini vs gpt-4o）
2. 控制 Context 长度（RAG 只检索 Top-K 相关片段）
3. 缓存重复查询结果
4. 设置 `max_tokens` 限制输出长度

---

## 6. 局限性 & 应对

| 局限 | 表现 | 解决方案 |
|------|------|---------|
| 幻觉 | 编造不存在的 API/参数 | RAG 检索真实文档 |
| 知识截止 | 不了解最新技术 | 外挂知识库 / 联网搜索 |
| 上下文有限 | 无法一次读完整代码库 | 分块检索 + 摘要 |
| 不一致性 | 同样问题不同回答 | 低 Temperature + 结构化 Prompt |
| 安全风险 | 生成不安全代码 | 静态分析 + 规则审查 |

---

## 7. 与本项目的关联

在 **EmbedDev Copilot** 中，LLM 承担：

1. **需求分析节点**：理解自然语言需求，输出结构化分析
2. **代码生成节点**：生成 MISRA-C 风格嵌入式代码
3. **测试生成节点**：根据代码生成 Unity 单元测试
4. **代码审查节点**：发现潜在安全与规范问题
5. **RAG 问答**：基于检索上下文回答技术问题

相关文件：`src/llm/factory.py`、`src/llm/demo_engine.py`
