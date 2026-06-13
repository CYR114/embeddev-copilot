"""文档加载与分块"""

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config import settings


def load_documents(docs_dir: str | Path) -> list[Document]:
    """从目录加载 .md / .txt 文档"""
    docs_dir = Path(docs_dir)
    documents: list[Document] = []

    for pattern in ("*.md", "*.txt"):
        for fp in docs_dir.glob(pattern):
            text = fp.read_text(encoding="utf-8")
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": str(fp.name), "category": fp.stem},
                )
            )
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n", " ", ""],
    )
    return splitter.split_documents(documents)
