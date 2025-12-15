# LangGraph Invoice Processing Agent with HITL

## 1. Goal / Problem Statement

The goal of this project is to design and implement a **production-oriented LangGraph Agent** that models a complete **Invoice Processing workflow** with:

* Deterministic and non-deterministic execution stages
* Persistent state propagation across nodes
* **Human-In-The-Loop (HITL)** checkpoints with pause & resume
* Dynamic **Bigtool-based tool selection**
* MCP-style server orchestration (COMMON vs ATLAS)

The system demonstrates how modern AI agents can orchestrate complex enterprise workflows while remaining **auditable, resumable, and human-guided** — a critical requirement in Fintech and Finance systems.

---

## 2. High-Level Architecture

```
Client / API
     │
     ▼
FastAPI Application
     │
     ▼
LangGraph Orchestration Engine
     │
     ├── Deterministic Nodes
     ├── Conditional Routing
     ├── HITL Checkpointing
     └── Resume Execution
     │
     ▼
SQLite (Checkpoint & State Store)
```

Key design principles:

* **Single shared state** carried across all nodes
* **Graph-driven execution**, not procedural scripts
* **Explicit checkpoints** instead of hidden pauses

---

## 3. Workflow Overview

The agent follows a 12-stage workflow:

1. **INTAKE** – Validate and persist raw invoice payload
2. **UNDERSTAND** – OCR + line-item parsing
3. **PREPARE** – Vendor normalization, enrichment, risk flags
4. **RETRIEVE** – Fetch PO, GRN, invoice history from ERP
5. **MATCH_TWO_WAY** – Compute invoice vs PO match score
6. **CHECKPOINT_HITL** – Pause workflow on match failure
7. **HITL_DECISION** – Human accepts or rejects invoice
8. **RECONCILE** – Build accounting entries
9. **APPROVE** – Apply approval policies
10. **POSTING** – Post to ERP & schedule payment
11. **NOTIFY** – Notify vendor & finance team
12. **COMPLETE** – Produce final payload & audit log

---

## 4. State Management Model

All nodes operate on a shared `InvoiceState` object:

```python
class InvoiceState(TypedDict):
    invoice_payload: dict
    parsed_invoice: dict
    vendor_profile: dict
    flags: dict
    match_score: float
    match_result: str
    checkpoint_id: str | None
    status: str
    logs: list
```

State guarantees:

* Every node **reads & writes** to the same state
* Logs are appended at each stage
* Checkpoints persist the **entire state blob**

---

## 5. LangGraph Design

* Each workflow stage is implemented as a **LangGraph node**
* Deterministic stages execute sequentially
* Conditional routing is applied after `MATCH_TWO_WAY`
* If `match_score < threshold` → route to `CHECKPOINT_HITL`

Resume logic:

* Workflow resumes from `RECONCILE` after human approval
* Rejected invoices terminate with `MANUAL_HANDOFF` status

---

## 6. Human-In-The-Loop (HITL) Design

### When is HITL triggered?

* If `match_score < config.match_threshold`

### What happens at checkpoint?

* Full `InvoiceState` is serialized to SQLite
* A `checkpoint_id` is generated
* Workflow execution is paused
* Entry is added to the Human Review Queue

### Human Review API

* `GET /human-review/pending`
* `POST /human-review/decision`

On **ACCEPT**:

* State is reloaded from DB
* Graph resumes from `RECONCILE`

On **REJECT**:

* Workflow terminates with `REQUIRES_MANUAL_HANDLING`

---

## 7. Bigtool Selection Strategy

Bigtool is used whenever a tool must be selected dynamically from a pool.

Example capabilities:

* OCR providers
* ERP connectors
* Vendor enrichment sources
* Databases

Implementation approach:

* Deterministic selection for demo purposes
* Every tool choice is logged

Example log:

> `Bigtool selected OCR provider: tesseract`

---

## 8. MCP Server Abstraction

Abilities are routed via logical MCP servers:

* **COMMON Server**

  * Parsing
  * Normalization
  * Matching
  * Accounting logic

* **ATLAS Server**

  * ERP access
  * Vendor enrichment
  * Notifications

In this demo, MCP calls are **mocked** to focus on orchestration logic.

---

## 9. API Endpoints

| Endpoint                 | Method | Description              |
| ------------------------ | ------ | ------------------------ |
| `/run-workflow`          | POST   | Start invoice processing |
| `/human-review/pending`  | GET    | List paused invoices     |
| `/human-review/decision` | POST   | Accept / Reject invoice  |

---

## 10. Demo Instructions

### Run Locally

```bash
pip install -r requirements.txt
python app/main.py
```

### Demo Flow

1. Submit a valid invoice → full auto-processing
2. Submit mismatched invoice → HITL pause
3. Call `/human-review/decision` with ACCEPT
4. Observe workflow resume & complete

Logs clearly show:

* Stage execution order
* Tool selection
* Checkpoint creation
* Resume event

---

## 11. Tradeoffs & Design Decisions

* Real APIs replaced with mocks for reliability
* SQLite chosen for simplicity and transparency
* No frontend UI — API-driven demo
* Focus on correctness over scale

---

## 12. Future Improvements

* Real ERP / OCR integrations
* Async execution & retries
* Frontend Human Review dashboard
* Multi-invoice batch processing
* Observability (metrics, tracing)

---

## 13. Conclusion

This project demonstrates how **LangGraph + HITL + Bigtool** can be combined to build **robust, auditable, enterprise-grade AI workflows** suitable for finance and operations-heavy domains.

The emphasis is on **statefulness, control, and human oversight** — not just automation.
