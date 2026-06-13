"""FastAPI 服务：提供 RAG 问答、Agent 工作流、代码分析接口"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.agents.workflow import EmbedDevAgentGraph
from src.rag.pipeline import RAGPipeline
from src.tools.code_analyzer import EmbeddedCodeAnalyzer, complete_code

app = FastAPI(
    title="EmbedDev Copilot API",
    description="嵌入式 AI 编程助手 - 面向车载 ECU 固件开发的 CodeAgent",
    version="1.0.0",
)

rag = RAGPipeline()
agent = EmbedDevAgentGraph(rag=rag)
analyzer = EmbeddedCodeAnalyzer()


class RAGRequest(BaseModel):
    question: str = Field(..., description="技术问题，如 CAN 滤波器配置")


class AgentRequest(BaseModel):
    requirement: str = Field(..., description="软件开发需求描述")


class CodeAnalyzeRequest(BaseModel):
    code: str


class CodeCompleteRequest(BaseModel):
    prefix: str
    context: str = ""


@app.get("/health")
def health():
    return {"status": "ok", "service": "embeddev-copilot"}


@app.post("/rag/query")
def rag_query(req: RAGRequest):
    return rag.query(req.question)


@app.post("/agent/run")
def agent_run(req: AgentRequest):
    return agent.run(req.requirement)


@app.post("/tools/analyze")
def analyze_code(req: CodeAnalyzeRequest):
    issues = analyzer.analyze(req.code)
    return {
        "issues": [
            {"severity": i.severity, "line": i.line, "message": i.message, "rule": i.rule}
            for i in issues
        ],
        "report": analyzer.format_report(issues),
    }


@app.post("/tools/complete")
def code_complete(req: CodeCompleteRequest):
    return {"completion": complete_code(req.prefix, req.context)}
