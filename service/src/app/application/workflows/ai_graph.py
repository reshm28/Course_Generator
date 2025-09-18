from typing import TypedDict

# Minimal LangGraph workflow with graceful fallback if langgraph is unavailable


class GraphState(TypedDict):
    text: str
    result: str


def echo_node(state: GraphState) -> GraphState:
    # In a real graph, you could call an LLM here
    state["result"] = f"echo: {state['text']}"
    return state


class SimpleGraphRunner:
    def __init__(self) -> None:
        ...

    def run_text(self, text: str) -> str:
        state: GraphState = {"text": text, "result": ""}
        # Single-node graph for demo
        out = echo_node(state)
        return out["result"]


class LangGraphRunner:
    """Uses langgraph to build a trivial graph with one node."""

    def __init__(self) -> None:
        # Import locally to avoid hard dependency at import time
        from langgraph.graph import StateGraph

        graph = StateGraph(GraphState)
        graph.add_node("echo", echo_node)
        graph.set_entry_point("echo")
        self._app = graph.compile()

    def run_text(self, text: str) -> str:
        # The app returns the final state
        out_state = self._app.invoke({"text": text, "result": ""})
        return out_state["result"]


_runner: SimpleGraphRunner | LangGraphRunner | None = None


def get_ai_graph_runner() -> SimpleGraphRunner:
    global _runner
    if _runner is None:
        try:
            # Probe for langgraph
            import importlib

            importlib.import_module("langgraph")
            _runner = LangGraphRunner()
        except Exception:
            # Fallback to simple runner
            _runner = SimpleGraphRunner()
    return _runner
