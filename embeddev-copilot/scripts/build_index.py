"""构建 RAG 知识库索引"""

import sys
from pathlib import Path

# 将项目根目录加入 path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rich.console import Console  # noqa: E402

from src.config import settings  # noqa: E402
from src.rag.loader import load_documents, split_documents  # noqa: E402
from src.rag.vectorstore import VectorStoreManager  # noqa: E402

console = Console()


def main():
    docs_dir = ROOT / settings.data_dir / "docs"
    console.print(f"[bold]加载文档[/bold]: {docs_dir}")

    documents = load_documents(docs_dir)
    if not documents:
        console.print("[red]未找到文档，请检查 data/docs 目录[/red]")
        return

    chunks = split_documents(documents)
    console.print(f"分块完成: {len(documents)} 篇 → {len(chunks)} 块")

    manager = VectorStoreManager()
    manager.build(chunks)
    console.print(f"[green]向量库已构建[/green]: {settings.chroma_dir}")


if __name__ == "__main__":
    main()
