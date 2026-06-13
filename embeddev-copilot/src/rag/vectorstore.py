"""向量存储：Demo 模式用内存检索，生产模式用 ChromaDB"""

from __future__ import annotations

import math
from pathlib import Path

from langchain_community.embeddings import FakeEmbeddings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from src.config import settings


def _get_embeddings() -> Embeddings:
    if settings.demo_mode or not settings.openai_api_key:
        return FakeEmbeddings(size=384)
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class InMemoryVectorStore:
    """轻量内存向量库，避免 ChromaDB 在部分 Windows 环境的兼容问题"""

    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self.documents: list[Document] = []
        self.vectors: list[list[float]] = []

    def add_documents(self, docs: list[Document]) -> None:
        texts = [d.page_content for d in docs]
        vecs = self.embeddings.embed_documents(texts)
        self.documents.extend(docs)
        self.vectors.extend(vecs)

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        if not self.documents:
            return []
        q_vec = self.embeddings.embed_query(query)
        scored = [
            (_cosine_similarity(q_vec, vec), doc)
            for vec, doc in zip(self.vectors, self.documents)
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:k]]

    def similarity_search_with_score(self, query: str, k: int = 4) -> list[tuple[Document, float]]:
        if not self.documents:
            return []
        q_vec = self.embeddings.embed_query(query)
        scored = [
            (_cosine_similarity(q_vec, vec), doc)
            for vec, doc in zip(self.vectors, self.documents)
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(doc, score) for score, doc in scored[:k]]


# 全局单例，避免重复构建
_memory_store: InMemoryVectorStore | None = None


class VectorStoreManager:
    def __init__(self, persist_dir: str | None = None):
        self.persist_dir = persist_dir or settings.chroma_dir
        self.embeddings = _get_embeddings()
        self._memory_store: InMemoryVectorStore | None = None
        self._chroma_store = None

    def build(self, chunks: list[Document]):
        global _memory_store

        if settings.demo_mode or not settings.openai_api_key:
            store = InMemoryVectorStore(self.embeddings)
            store.add_documents(chunks)
            self._memory_store = store
            _memory_store = store
            return store

        try:
            from langchain_chroma import Chroma

            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
            self._chroma_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_dir,
            )
            return self._chroma_store
        except Exception:
            store = InMemoryVectorStore(self.embeddings)
            store.add_documents(chunks)
            self._memory_store = store
            _memory_store = store
            return store

    def load(self):
        global _memory_store

        if self._memory_store is not None:
            return self._memory_store
        if _memory_store is not None:
            self._memory_store = _memory_store
            return _memory_store

        if not settings.demo_mode and settings.openai_api_key:
            try:
                from langchain_chroma import Chroma

                self._chroma_store = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings,
                )
                return self._chroma_store
            except Exception:
                pass

        self._memory_store = InMemoryVectorStore(self.embeddings)
        return self._memory_store

    def ensure_index(self, docs_dir: str | Path | None = None) -> None:
        """索引为空时自动从文档目录构建"""
        store = self.load()
        if isinstance(store, InMemoryVectorStore) and store.documents:
            return
        if self._chroma_store is not None:
            return

        from src.rag.loader import load_documents, split_documents

        docs_path = Path(docs_dir or Path(settings.data_dir) / "docs")
        if not docs_path.exists():
            return
        documents = load_documents(docs_path)
        if documents:
            self.build(split_documents(documents))

    def search(self, query: str, k: int | None = None) -> list[Document]:
        store = self.load()
        return store.similarity_search(query, k=k or settings.top_k)

    def search_with_score(self, query: str, k: int | None = None) -> list[tuple[Document, float]]:
        store = self.load()
        return store.similarity_search_with_score(query, k=k or settings.top_k)
