from typing import TypedDict, Optional, List, Dict, Any


class InvoiceState(TypedDict):
    invoice_payload: Dict[str, Any]
    parsed_invoice: Dict[str, Any]
    vendor_profile: Dict[str, Any]
    flags: Dict[str, Any]
    match_score: float
    match_result: str
    hitl_checkpoint_id: Optional[str]
    status: str
    logs: List[str]
