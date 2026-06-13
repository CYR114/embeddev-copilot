# AI 技术知识点索引

> 面向小鹏汽车【嵌入式软件实习生（AI）】岗位的系统化知识总结

## 文档目录

| 文档 | 内容 | 岗位关联 |
|------|------|---------|
| [LLM.md](LLM.md) | 大语言模型原理、架构、训练、部署 | 模型应用基础 |
| [RAG.md](RAG.md) | 检索增强生成全流程 | 探索 LLM/RAG 在研发流程中的应用 |
| [LangChain.md](LangChain.md) | LangChain 框架核心组件与 LCEL | 框架使用（岗位要求） |
| [LangGraph.md](LangGraph.md) | Agent 工作流编排 | 构建 Agent、流程编排（岗位要求） |
| [Prompt-Engineering.md](Prompt-Engineering.md) | 提示设计与优化 | Prompt 设计与性能优化（岗位要求） |
| [AI-Agent.md](AI-Agent.md) | Agent 架构与 CodeAgent | AI Agent 开发（岗位要求） |
| [Code-LLM.md](Code-LLM.md) | 代码大模型与评估 | 代码数据整理、评估数据集（岗位要求） |

## 知识关系图

```
                    ┌─────────┐
                    │   LLM   │ 基础
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         ┌────────┐ ┌────────┐ ┌──────────┐
         │  RAG   │ │ Prompt │ │ Code LLM │
         │ 检索增强│ │  工程  │ │ 代码模型  │
         └────┬───┘ └───┬────┘ └────┬─────┘
              │         │           │
              └────┬────┴─────┬─────┘
                   ▼          ▼
              ┌─────────┐ ┌──────────┐
              │LangChain│ │AI Agent  │
              │ 组件框架 │ │ 智能体    │
              └────┬────┘ └────┬─────┘
                   │           │
                   └─────┬─────┘
                         ▼
                   ┌──────────┐
                   │LangGraph │ 编排
                   │ 工作流    │
                   └──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  EmbedDev Copilot   │ 项目实践
              │  车载嵌入式 AI 助手   │
              └─────────────────────┘
```

## 学习路线建议

### 第一阶段：基础（1-2 周）
1. 阅读 [LLM.md](LLM.md) — 理解基本原理
2. 阅读 [Prompt-Engineering.md](Prompt-Engineering.md) — 能写出有效 Prompt
3. 动手：用 OpenAI API 做简单的代码生成实验

### 第二阶段：核心技能（2-3 周）
4. 阅读 [RAG.md](RAG.md) — 理解检索增强
5. 阅读 [LangChain.md](LangChain.md) — 掌握 LCEL 管道
6. 动手：运行 `embeddev-copilot` 构建知识库和 RAG 问答

### 第三阶段：进阶（2-3 周）
7. 阅读 [LangGraph.md](LangGraph.md) — 掌握工作流编排
8. 阅读 [AI-Agent.md](AI-Agent.md) — 理解 Agent 架构
9. 动手：运行 Agent 演示，理解四节点工作流

### 第四阶段：专项（1-2 周）
10. 阅读 [Code-LLM.md](Code-LLM.md) — 代码模型与评估
11. 动手：运行评估 Benchmark，尝试优化 Prompt 提升通过率

## 面试高频问题速查

| 问题 | 参考文档 |
|------|---------|
| 什么是 RAG？为什么需要？ | [RAG.md](RAG.md) §1 |
| LangChain 和 LangGraph 区别？ | [LangGraph.md](LangGraph.md) §1 |
| 如何减少 LLM 幻觉？ | [LLM.md](LLM.md) §6, [RAG.md](RAG.md) |
| 什么是 CodeAgent？ | [AI-Agent.md](AI-Agent.md) §4 |
| 如何评估代码生成质量？ | [Code-LLM.md](Code-LLM.md) §5 |
| Prompt 怎么优化？ | [Prompt-Engineering.md](Prompt-Engineering.md) §3 |
| Agent 有哪些架构模式？ | [AI-Agent.md](AI-Agent.md) §2 |
