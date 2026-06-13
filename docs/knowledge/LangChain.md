# LangChain 知识总结

## 1. 什么是 LangChain

**LangChain** 是构建 LLM 应用的开源框架，提供标准化的组件抽象，将 LLM、Prompt、检索、工具、记忆等模块串联为可运行的 Chain（链）。

核心理念：**Composable（可组合）** — 像乐高一样拼装 LLM 应用。

---

## 2. 核心概念

### 2.1 LCEL（LangChain Expression Language）

用 `|` 管道符串联组件，统一 Input/Output 接口：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"question": "CAN 波特率怎么配？"})
```

等价于：

```python
result = StrOutputParser().parse(llm.invoke(prompt.invoke({"question": "..."})))
```

### 2.2 Runnable 接口

所有 LCEL 组件实现统一接口：

| 方法 | 说明 |
|------|------|
| `invoke(input)` | 单次同步调用 |
| `batch(inputs)` | 批量调用 |
| `stream(input)` | 流式输出 |
| `ainvoke(input)` | 异步调用 |

### 2.3 核心抽象一览

```
┌─────────────────────────────────────────────────┐
│                  LangChain 生态                   │
├──────────┬──────────┬──────────┬────────────────┤
│ Models   │ Prompts  │ Parsers  │ Retrievers     │
│ Chat/LLM │ Template │ Str/JSON │ VectorStore    │
├──────────┼──────────┼──────────┼────────────────┤
│ Tools    │ Memory   │ Chains   │ Agents         │
│ 函数调用  │ 对话记忆  │ LCEL管道  │ ReAct/ToolCall │
└──────────┴──────────┴──────────┴────────────────┘
```

---

## 3. 核心组件

### 3.1 Models（模型）

```python
# Chat Model（推荐，支持多轮消息）
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# 调用
from langchain_core.messages import HumanMessage, SystemMessage
response = llm.invoke([
    SystemMessage(content="你是嵌入式专家"),
    HumanMessage(content="解释 CAN 总线"),
])
```

### 3.2 Prompts（提示模板）

```python
from langchain_core.prompts import ChatPromptTemplate

# 消息式模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是 {role}"),
    ("human", "{question}"),
])

# 带 Few-shot 示例
from langchain_core.prompts import FewShotChatMessagePromptTemplate
```

### 3.3 Output Parsers（输出解析）

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# 字符串解析
chain = prompt | llm | StrOutputParser()

# JSON 结构化解析
from pydantic import BaseModel

class CodeReview(BaseModel):
    issues: list[str]
    score: int

parser = JsonOutputParser(pydantic_object=CodeReview)
```

### 3.4 Document Loaders & Splitters

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = TextLoader("can_guide.md")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)
```

### 3.5 Vector Stores & Retrievers

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 在 Chain 中使用
chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm
```

### 3.6 Tools（工具）

```python
from langchain_core.tools import tool

@tool
def analyze_c_code(code: str) -> str:
    """分析 C 代码的静态问题"""
    issues = []
    if "malloc" in code:
        issues.append("使用了动态内存分配")
    return "\n".join(issues) if issues else "无问题"
```

### 3.7 Memory（记忆）

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)
# 在 Chain 中注入历史对话
```

---

## 4. 构建 RAG Chain 的标准模式

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("CAN 滤波器怎么配置？")
```

数据流：

```
question ──┬──→ retriever → format_docs ──→ context ──┐
             │                                        ├→ prompt → llm → parser
             └──────────────────────────────── question ┘
```

---

## 5. Agent（LangChain 原生）

LangChain 内置 Agent 模式，让 LLM 自主选择工具：

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor

tools = [analyze_c_code, search_docs]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": "检查这段 CAN 驱动代码"})
```

> **注意**：复杂工作流推荐使用 **LangGraph**（见 LangGraph.md），LangChain Agent 适合简单工具调用场景。

---

## 6. 包结构（v0.3+）

LangChain 已拆分为多个包：

| 包名 | 职责 |
|------|------|
| `langchain-core` | 核心抽象（Runnable、Prompt、Parser） |
| `langchain` | 高级 Chain 和 Agent |
| `langchain-community` | 社区集成（VectorStore、Loader） |
| `langchain-openai` | OpenAI 模型集成 |
| `langchain-text-splitters` | 文本分块工具 |

---

## 7. 最佳实践

1. **用 LCEL 而非旧版 Chain 类**（`| ` 管道语法更简洁）
2. **Prompt 模板化**：所有 Prompt 用 `ChatPromptTemplate`，便于版本管理
3. **结构化输出**：用 Pydantic + JsonOutputParser 替代自由文本
4. **流式输出**：`chain.stream()` 提升用户体验
5. **错误处理**：LLM 调用包 try-except，设置 timeout 和 retry
6. **可观测性**：接入 LangSmith 追踪 Chain 执行链路

---

## 8. 与本项目的关联

| 模块 | LangChain 组件 |
|------|---------------|
| `src/llm/factory.py` | `ChatOpenAI` 模型工厂 |
| `src/rag/loader.py` | `Document` + `RecursiveCharacterTextSplitter` |
| `src/rag/vectorstore.py` | `Chroma` + `OpenAIEmbeddings` |
| `src/rag/pipeline.py` | LCEL Chain：`prompt \| llm \| StrOutputParser` |
| `src/agents/workflow.py` | `HumanMessage` / `AIMessage` 消息体系 |
