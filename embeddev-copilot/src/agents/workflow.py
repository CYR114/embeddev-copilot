"""LangGraph 多 Agent 工作流：需求分析 → 代码生成 → 测试生成 → 审查"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph

from src.llm.demo_engine import DemoEngine
from src.llm.factory import create_chat_model
from src.rag.pipeline import RAGPipeline


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    requirement: str
    analysis: str
    code: str
    tests: str
    review: str
    rag_context: str
    current_step: str


class EmbedDevAgentGraph:
    """嵌入式软件开发全流程 Agent 编排"""

    STEPS = ["analyze", "generate_code", "generate_tests", "review"]

    def __init__(self, rag: RAGPipeline | None = None):
        self.rag = rag or RAGPipeline()
        self.llm = create_chat_model()
        self.demo = DemoEngine()
        self.graph = self._build_graph()

    def _retrieve_context(self, requirement: str) -> str:
        docs = self.rag.retrieve(requirement)
        return "\n".join(d.page_content[:300] for d in docs)

    def _node_analyze(self, state: AgentState) -> dict:
        req = state["requirement"]
        ctx = state.get("rag_context") or self._retrieve_context(req)

        if self.llm is None:
            analysis = self.demo.analyze_requirement(req, ctx)
        else:
            prompt = (
                f"分析以下嵌入式软件需求，输出模块划分、接口设计与注意事项。\n"
                f"需求: {req}\n参考: {ctx}"
            )
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            analysis = resp.content

        return {
            "analysis": analysis,
            "current_step": "analyze",
            "messages": [AIMessage(content=f"[需求分析完成]\n{analysis[:200]}...")],
        }

    def _node_generate_code(self, state: AgentState) -> dict:
        req, analysis, ctx = state["requirement"], state["analysis"], state.get("rag_context", "")

        if self.llm is None:
            code = self.demo.generate_code(req, analysis, ctx)
        else:
            prompt = (
                f"根据需求和分析生成 MISRA-C 风格的 C 代码。\n"
                f"需求: {req}\n分析: {analysis}\n参考: {ctx}"
            )
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            code = resp.content

        return {
            "code": code,
            "current_step": "generate_code",
            "messages": [AIMessage(content="[代码生成完成]")],
        }

    def _node_generate_tests(self, state: AgentState) -> dict:
        code = state["code"]

        if self.llm is None:
            tests = self.demo.generate_tests(code)
        else:
            prompt = f"为以下 C 代码生成 Unity 框架单元测试:\n```c\n{code}\n```"
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            tests = resp.content

        return {
            "tests": tests,
            "current_step": "generate_tests",
            "messages": [AIMessage(content="[测试用例生成完成]")],
        }

    def _node_review(self, state: AgentState) -> dict:
        code = state["code"]

        if self.llm is None:
            review = self.demo.review_code(code)
        else:
            prompt = f"审查以下嵌入式 C 代码，指出 MISRA 违规、内存安全和实时性问题:\n```c\n{code}\n```"
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            review = resp.content

        return {
            "review": review,
            "current_step": "review",
            "messages": [AIMessage(content=f"[审查完成]\n{review}")],
        }

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("analyze", self._node_analyze)
        workflow.add_node("generate_code", self._node_generate_code)
        workflow.add_node("generate_tests", self._node_generate_tests)
        workflow.add_node("review", self._node_review)

        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "generate_code")
        workflow.add_edge("generate_code", "generate_tests")
        workflow.add_edge("generate_tests", "review")
        workflow.add_edge("review", END)

        return workflow.compile()

    def run(self, requirement: str) -> dict:
        ctx = self._retrieve_context(requirement)
        initial: AgentState = {
            "messages": [HumanMessage(content=requirement)],
            "requirement": requirement,
            "analysis": "",
            "code": "",
            "tests": "",
            "review": "",
            "rag_context": ctx,
            "current_step": "start",
        }
        result = self.graph.invoke(initial)
        return {
            "requirement": requirement,
            "analysis": result["analysis"],
            "code": result["code"],
            "tests": result["tests"],
            "review": result["review"],
            "rag_context": ctx,
            "steps": self.STEPS,
        }
