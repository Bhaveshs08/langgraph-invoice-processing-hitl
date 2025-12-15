"""
DAY 1 GOAL:
- Define shared InvoiceState
- Build LangGraph skeleton
- Implement INTAKE -> MATCH_TWO_WAY flow
- Conditional routing to CHECKPOINT_HITL
- Avoid LangGraph reserved channels
"""

from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END


# --------------------------------------------------
# 1. SHARED STATE (AVOID RESERVED NAMES)
# --------------------------------------------------
class InvoiceState(TypedDict):
    invoice_payload: dict
    parsed_invoice: dict
    vendor_profile: dict
    flags: dict
    match_score: float
    match_result: str
    hitl_checkpoint_id: Optional[str]
    status: str
    logs: List[str]


# --------------------------------------------------
# 2. NODE IMPLEMENTATIONS
# --------------------------------------------------
def intake_node(state: InvoiceState) -> InvoiceState:
    state["logs"].append("INTAKE: Payload validated and stored")
    state["status"] = "INGESTED"
    return state


def understand_node(state: InvoiceState) -> InvoiceState:
    state["parsed_invoice"] = {
        "amount": state["invoice_payload"]["amount"]
    }
    state["logs"].append("UNDERSTAND: OCR + parsing completed")
    return state


def prepare_node(state: InvoiceState) -> InvoiceState:
    state["vendor_profile"] = {
        "normalized_name": "ACME_CORP"
    }
    state["flags"] = {
        "risk_score": 0.2
    }
    state["logs"].append("PREPARE: Vendor normalized and enriched")
    return state


def retrieve_node(state: InvoiceState) -> InvoiceState:
    state["logs"].append("RETRIEVE: Mock ERP data fetched")
    return state


def match_two_way_node(state: InvoiceState) -> InvoiceState:
    # Hardcoded for demo
    state["match_score"] = 0.82
    state["match_result"] = (
        "FAILED" if state["match_score"] < 0.9 else "MATCHED"
    )
    state["logs"].append(
        f"MATCH_TWO_WAY: score={state['match_score']} result={state['match_result']}"
    )
    return state


def checkpoint_hitl_node(state: InvoiceState) -> InvoiceState:
    state["hitl_checkpoint_id"] = "chk_001"
    state["status"] = "PAUSED_FOR_HITL"
    state["logs"].append(
        "CHECKPOINT_HITL: Workflow paused for human review"
    )
    return state


# --------------------------------------------------
# 3. CONDITIONAL ROUTING
# --------------------------------------------------
def route_after_match(state: InvoiceState):
    if state["match_result"] == "FAILED":
        return "CHECKPOINT_HITL"
    return END


# --------------------------------------------------
# 4. BUILD LANGGRAPH
# --------------------------------------------------
graph = StateGraph(InvoiceState)

graph.add_node("INTAKE", intake_node)
graph.add_node("UNDERSTAND", understand_node)
graph.add_node("PREPARE", prepare_node)
graph.add_node("RETRIEVE", retrieve_node)
graph.add_node("MATCH_TWO_WAY", match_two_way_node)
graph.add_node("CHECKPOINT_HITL", checkpoint_hitl_node)

graph.set_entry_point("INTAKE")

graph.add_edge("INTAKE", "UNDERSTAND")
graph.add_edge("UNDERSTAND", "PREPARE")
graph.add_edge("PREPARE", "RETRIEVE")
graph.add_edge("RETRIEVE", "MATCH_TWO_WAY")

graph.add_conditional_edges(
    "MATCH_TWO_WAY",
    route_after_match
)

graph.add_edge("CHECKPOINT_HITL", END)

app = graph.compile()


# --------------------------------------------------
# 5. LOCAL TEST RUN
# --------------------------------------------------
if __name__ == "__main__":
    initial_state: InvoiceState = {
        "invoice_payload": {
            "invoice_id": "INV-001",
            "amount": 1200
        },
        "parsed_invoice": {},
        "vendor_profile": {},
        "flags": {},
        "match_score": 0.0,
        "match_result": "",
        "hitl_checkpoint_id": None,
        "status": "NEW",
        "logs": [],
    }

    final_state = app.invoke(initial_state)

    print("\nFINAL STATE:")
    for k, v in final_state.items():
        print(f"{k}: {v}")
