from langgraph.graph import END, START, StateGraph

from src.graph.nodes import chunk, parse_pdf, route_input, summarize, transcribe
from src.graph.state import NotesState


def route_after_input(state: NotesState) -> str:
    file_type = state["file_type"]
    if file_type == "audio":
        return "transcribe"
    if file_type == "pdf":
        return "parse_pdf"
    return "chunk"


def build_graph():
    graph = StateGraph(NotesState)

    graph.add_node("route_input", route_input)
    graph.add_node("transcribe", transcribe)
    graph.add_node("parse_pdf", parse_pdf)
    graph.add_node("chunk", chunk)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "route_input")
    graph.add_conditional_edges(
        "route_input",
        route_after_input,
        {
            "transcribe": "transcribe",
            "parse_pdf": "parse_pdf",
            "chunk": "chunk",
        },
    )
    graph.add_edge("transcribe", "chunk")
    graph.add_edge("parse_pdf", "chunk")
    graph.add_edge("chunk", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()
