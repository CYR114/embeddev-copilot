"""RAG 检索增强生成 Pipeline"""

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from src.config import settings
from src.llm.demo_engine import DemoEngine
from src.llm.factory import create_chat_model
from src.rag.vectorstore import VectorStoreManager


RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "你是嵌入式软件开发专家，熟悉 AUTOSAR、MISRA-C、CAN/LIN 总线和 MCU 外设驱动。"
        "请基于以下参考文档回答问题，若文档不足请明确说明。\n\n参考文档:\n{context}",
    ),
    ("human", "{question}"),
])


def _format_docs(docs: list[Document]) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        src = doc.metadata.get("source", "unknown")
        parts.append(f"[{i}] ({src})\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


class RAGPipeline:
    def __init__(self, store: VectorStoreManager | None = None):
        self.store = store or VectorStoreManager()
        self.store.ensure_index()
        self.llm = create_chat_model()
        self.demo = DemoEngine()

    def retrieve(self, query: str) -> list[Document]:
        return self.store.search(query)

    def query(self, question: str) -> dict:
        docs = self.retrieve(question)
        context = _format_docs(docs)

        if self.llm is None:
            answer = (
                f"【Demo 模式回答】\n"
                f"问题: {question}\n\n"
                f"基于检索到的 {len(docs)} 条文档片段，"
                f"建议在实现时遵循文档中的编码规范与外设配置流程。"
            )
            return {"answer": answer, "sources": docs, "context": context}

        chain = (
            {"context": lambda _: context, "question": RunnablePassthrough()}
            | RAG_PROMPT
            | self.llm
            | StrOutputParser()
        )
        answer = chain.invoke(question)
        return {"answer": answer, "sources": docs, "context": context}
