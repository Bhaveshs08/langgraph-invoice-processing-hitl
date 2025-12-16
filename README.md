# LangGraph Invoice Processing with Human-in-the-Loop (HITL)

## 📌 Overview

This project implements an **invoice processing workflow** using **LangGraph**, designed to demonstrate a **production-grade Human-in-the-Loop (HITL) architecture**.

The system ingests invoice data, performs parsing and validation, applies a matching decision, and **pauses execution for human review** when confidence is low. Workflow state is **persisted to SQLite** and execution is **resumed deterministically** after human approval.

This project was built as part of a **Data Scientist coding assignment**, focusing on orchestration logic, state management, and HITL design — not UI or deployment.

---

## 🧠 Key Design Principles

* **State-driven orchestration** using LangGraph
* **Durable HITL checkpoints** (SQLite persistence)
* **Deterministic resume** without re-running upstream steps
* **Clean separation of concerns** (state, graph, persistence)
* **Local-first MVP**, suitable for extension to APIs or cloud systems

---

## 🏗️ Architecture

```
┌──────────┐
│  INTAKE  │  ← Invoice payload received
└────┬─────┘
     ↓
┌────────────┐
│ UNDERSTAND │  ← OCR / parsing (mocked)
└────┬───────┘
     ↓
┌──────────┐
│ PREPARE  │  ← Vendor normalization & enrichment
└────┬─────┘
     ↓
┌──────────┐
│ RETRIEVE │  ← ERP / reference data (mocked)
└────┬─────┘
     ↓
┌──────────────┐
│ MATCH_TWO_WAY│  ← Confidence scoring
└────┬─────────┘
     ↓ (low confidence)
┌──────────────────┐
│ CHECKPOINT_HITL  │  ← State saved to SQLite
└─────────┬────────┘
          │
          │  Human Review (async)
          │
┌─────────▼────────┐
│   FINALIZE       │  ← Resume graph after approval
└──────────────────┘
```

### 🔑 Important Architectural Insight

LangGraph **always starts execution from its entry node**.
To support correct HITL resume **without re-running upstream steps**, this project uses:

* **Main Graph** → Executes until HITL pause
* **Resume Graph** → Continues execution *after* human approval

This mirrors real-world workflow engines like Temporal or Airflow.

---

## 📂 Project Structure

```
langgraph_invoice_processing_hitl/
│
├── app/
│   ├── __init__.py
│   ├── graph.py          # Main + resume graphs
│   └── state.py          # Shared InvoiceState definition
│
├── db/
│   ├── database.py       # SQLite initialization
│   ├── checkpoint_repo.py# Save/load checkpoint logic
│   └── checkpoints.db    # Auto-created SQLite DB
│
├── README.md
└── requirements.txt
```

---

## 🧩 State Model (`InvoiceState`)

The entire workflow is driven by a typed state object:

* `invoice_payload` – Raw invoice input
* `parsed_invoice` – Extracted fields (mocked)
* `vendor_profile` – Normalized vendor info
* `flags` – Risk / enrichment metadata
* `match_score` – Confidence score
* `match_result` – MATCHED / FAILED
* `hitl_checkpoint_id` – Identifier for human review
* `status` – Workflow status
* `logs` – Execution trace

This state is **fully serializable** and stored during HITL pauses.

---

## 🔄 Workflow Execution

### 1️⃣ Normal Processing

* Invoice is ingested
* Parsed and enriched
* Matched against reference data

### 2️⃣ HITL Trigger

If match confidence is low:

* Workflow pauses
* Full state is **persisted to SQLite**
* Checkpoint ID is generated

### 3️⃣ Human Review (Simulated)

* A human reviews the invoice externally
* Decision is applied to the stored state

### 4️⃣ Deterministic Resume

* State is loaded from SQLite
* Execution resumes via **resume graph**
* Invoice is finalized without reprocessing earlier steps

---

## ▶️ How to Run

From the project root:

```powershell
python -m app.graph
```

### Expected Output

* **PAUSED STATE** → Workflow stopped for HITL
* **RESUMED FINAL STATE** → Invoice approved

---

## 💡 Why This Design

* Avoids re-running expensive or unsafe steps
* Ensures auditability of human decisions
* Makes HITL asynchronous and scalable
* Aligns with real production workflow engines

---

## 🚀 Future Extensions

* Replace mocks with OCR / LLM parsing
* Add FastAPI for human approval UI
* Support rejection & rework paths
* Cloud DB or object storage for checkpoints

---

## 🏁 Summary

This project demonstrates a **correct, production-aligned Human-in-the-Loop workflow** using LangGraph with durable state persistence and deterministic resume semantics.

It focuses on **architecture, correctness, and explainability**, which are critical for real-world AI systems involving human review.

---

**Author:** Commander
