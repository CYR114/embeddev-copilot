# RAG（检索增强生成）知识总结

## 1. 什么是 RAG

**RAG（Retrieval-Augmented Generation）** = 检索（Retrieval）+ 增强（Augmented）+ 生成（Generation）

在 LLM 生成回答前，先从外部知识库检索相关文档片段，将其作为上下文注入 Prompt，使回答**有据可依、减少幻觉**。

```
用户问题 → 向量化 → 检索 Top-K 文档 → 拼接 Prompt → LLM 生成回答
```

### 为什么需要 RAG

| 问题 | RAG 如何解决 |
|------|-------------|
| LLM 不知道公司内部规范 | 检索编码规范文档 |
| LLM 编造 CAN 寄存器地址 | 检索真实技术手册 |
| 知识更新需重新训练模型 | 只需更新文档库 |
| 长代码库无法放入 Context | 分块 + 语义检索 |

---

## 2. RAG 架构

### 经典 Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 文档加载  │ →  │ 文本分块  │ →  │ 向量化   │ →  │ 向量存储  │
│ Loader   │    │ Splitter │    │ Embedding│    │ VectorDB │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
用户 Query → 向量化 → 相似度搜索 → Top-K Chunks → Prompt → LLM → 回答
```

### 进阶架构

- **Hybrid Search**：向量检索 + BM25 关键词检索融合
- **Reranker**：用 Cross-Encoder 对初检结果重排序
- **Query Rewrite**：改写用户问题提升检索命中率
- **Self-RAG**：模型自主判断是否需要检索
- **GraphRAG**：基于知识图谱的检索增强

---

## 3. 核心组件详解

### 3.1 文档加载（Document Loading）

```python
from langchain_core.documents import Document

doc = Document(
    page_content="CAN 波特率配置为 500Kbps...",
    metadata={"source": "can_driver_guide.md", "category": "can"}
)
```

支持的文档类型：PDF、Markdown、Word、HTML、代码文件、数据库记录

### 3.2 文本分块（Chunking）

**为什么分块？** 文档太长无法整篇放入 Embedding 和 Context。

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| 固定长度 | 按字符/token 数切分 | 通用 |
| 递归字符 | 按分隔符层级切分（`\n## ` → `\n` → ` `） | Markdown 文档 |
| 语义分块 | 按语义边界切分 | 长篇文章 |
| 代码分块 | 按函数/类切分 | 代码库检索 |

关键参数：
- `chunk_size`：块大小（通常 256-1024）
- `chunk_overlap`：重叠区域（通常 10%-20%），避免语义断裂

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=64,
    separators=["\n## ", "\n### ", "\n", " ", ""]
)
chunks = splitter.split_documents(documents)
```

### 3.3 向量化（Embedding）

将文本映射到高维向量空间，语义相近的文本向量距离更近。

| 模型 | 维度 | 特点 |
|------|------|------|
| OpenAI text-embedding-3-small | 1536 | 效果好，需 API |
| BGE-large-zh | 1024 | 中文优秀，可本地部署 |
| m3e-base | 768 | 轻量中文 Embedding |

```python
# 相似度计算：余弦相似度
similarity = dot(query_vec, doc_vec) / (norm(query_vec) * norm(doc_vec))
```

### 3.4 向量数据库（Vector Store）

| 数据库 | 特点 | 适用 |
|--------|------|------|
| ChromaDB | 轻量、嵌入式、零配置 | 原型/Demo |
| FAISS | Meta 开源、高性能 | 本地大规模 |
| Milvus | 分布式、生产级 | 企业部署 |
| Pinecone | 全托管 SaaS | 快速上线 |
| pgvector | PostgreSQL 扩展 | 已有 PG 基础设施 |

---

## 4. 检索策略

### 相似度搜索

```python
# 基础：返回 Top-K 最相似文档
docs = vectorstore.similarity_search(query, k=4)

# 带分数：可设阈值过滤低质量结果
docs_with_scores = vectorstore.similarity_search_with_score(query, k=4)
```

### 提升检索质量的方法

1. **元数据过滤**：`filter={"category": "can"}` 限定检索范围
2. **Multi-Query**：用 LLM 生成多个查询变体
3. **HyDE**：先生成假设性回答再检索
4. **Parent Document**：小块检索、大块返回

---

## 5. Prompt 组装

```python
RAG_PROMPT = """
你是嵌入式软件专家。请基于以下参考文档回答问题。
若文档中没有相关信息，请明确说明。

参考文档:
{context}

问题: {question}
"""
```

关键原则：
- 明确角色定位
- 要求基于文档回答
- 允许说"不知道"
- 标注引用来源

---

## 6. 评估指标

| 指标 | 含义 | 衡量什么 |
|------|------|---------|
| Context Precision | 检索结果的相关性 | 检索质量 |
| Context Recall | 是否检索到所有相关文档 | 检索完整性 |
| Faithfulness | 回答是否忠于检索内容 | 减少幻觉 |
| Answer Relevance | 回答与问题的相关度 | 生成质量 |

---

## 7. 常见问题与优化

| 问题 | 原因 | 优化方案 |
|------|------|---------|
| 检索不到相关内容 | 分块太大/太小 | 调整 chunk_size |
| 回答编造内容 | Prompt 约束不足 | 加强"仅基于文档"指令 |
| 检索结果冗余 | Top-K 太大 | 减少 K + 加重排序 |
| 跨文档推理失败 | 信息分散在多个块 | 增加 overlap / Parent Document |
| 中文检索效果差 | Embedding 模型不适配 | 换用 BGE/m3e 中文模型 |

---

## 8. 与本项目的关联

**EmbedDev Copilot** 的 RAG 实现：

```
data/docs/               → 编码规范、CAN 指南、ADC 规范、MISRA 规则
    ↓ load_documents()
    ↓ split_documents()  → 512 字符分块，64 重叠
    ↓ ChromaDB + Embedding
    ↓ similarity_search()  → Top-4 检索
    ↓ 注入 Agent 各节点 Prompt
```

相关文件：
- `src/rag/loader.py` — 文档加载与分块
- `src/rag/vectorstore.py` — ChromaDB 向量存储
- `src/rag/pipeline.py` — RAG 问答 Pipeline
- `scripts/build_index.py` — 构建索引脚本
