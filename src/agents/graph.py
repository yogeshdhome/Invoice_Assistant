from typing import List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from .nodes import (
    greeting_node,
    identify_intent_node,
    ask_po_invoice_details_node,
    ask_non_po_invoice_details_node,
    collect_and_validate_po_details_node,
    collect_and_validate_non_po_details_node,
    generate_json_payload_node,
    call_sap_api_node,
    explain_invoice_status_node,
    handle_invoice_not_found_node,
    ask_for_satisfaction_node,
    collect_feedback_for_ticket_node,
    create_servicenow_ticket_node,
    end_conversation_node,
    route_after_satisfaction_query,
)

class AgentState(TypedDict):
    """
    Represents the state of the agent.
    """
    conversation_history: List[BaseMessage]
    user_query: str
    invoice_type: Optional[str]  # "PO" or "NON_PO"
    po_number: Optional[str]
    invoice_number: Optional[str]
    check_all_for_po: Optional[bool]
    acr_number: Optional[str]
    invoice_document_date: Optional[str]
    json_payload: Optional[dict]
    api_response: Optional[dict]
    is_satisfied: Optional[bool]
    email_id: Optional[str]
    vendor_number: Optional[str]
    service_now_ticket: Optional[str]
    final_response: Optional[str]


def route_after_intent_identification(state: AgentState) -> str:
    """
    Routes the conversation based on the identified intent.
    """
    invoice_type = state.get("invoice_type")
    if invoice_type == "PO":
        return "ask_po_invoice_details"
    elif invoice_type == "NON_PO":
        return "ask_non_po_invoice_details"
    elif invoice_type == "GREETING":
        return "greeting"
    else:  # UNKNOWN
        return "identify_intent"

def route_after_sap_call(state: AgentState) -> str:
    """
    Routes based on the SAP API response.
    """
    if state.get("api_response"):
        return "explain_invoice_status"
    else:
        return "handle_invoice_not_found"

# Define the workflow
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("greeting", greeting_node)
workflow.add_node("identify_intent", identify_intent_node)
workflow.add_node("ask_po_invoice_details", ask_po_invoice_details_node)
workflow.add_node("ask_non_po_invoice_details", ask_non_po_invoice_details_node)
workflow.add_node("collect_and_validate_po_details", collect_and_validate_po_details_node)
workflow.add_node("collect_and_validate_non_po_details", collect_and_validate_non_po_details_node)
workflow.add_node("generate_json_payload", generate_json_payload_node)
workflow.add_node("call_sap_api", call_sap_api_node)
workflow.add_node("explain_invoice_status", explain_invoice_status_node)
workflow.add_node("handle_invoice_not_found", handle_invoice_not_found_node)
workflow.add_node("ask_for_satisfaction", ask_for_satisfaction_node)
workflow.add_node("collect_feedback_for_ticket", collect_feedback_for_ticket_node)
workflow.add_node("create_servicenow_ticket", create_servicenow_ticket_node)
workflow.add_node("end_conversation", end_conversation_node)


# Set the entry point
workflow.set_entry_point("identify_intent")

# Define the edges
workflow.add_conditional_edges(
    "identify_intent",
    route_after_intent_identification,
    {
        "greeting": "greeting",
        "ask_po_invoice_details": "ask_po_invoice_details",
        "ask_non_po_invoice_details": "ask_non_po_invoice_details",
        "identify_intent": "identify_intent",
    },
)

workflow.add_edge("greeting", END)
workflow.add_edge("ask_po_invoice_details", "collect_and_validate_po_details")
workflow.add_edge("ask_non_po_invoice_details", "collect_and_validate_non_po_details")
workflow.add_edge("collect_and_validate_po_details", "generate_json_payload")
workflow.add_edge("collect_and_validate_non_po_details", "generate_json_payload")
workflow.add_edge("generate_json_payload", "call_sap_api")

workflow.add_conditional_edges(
    "call_sap_api",
    route_after_sap_call,
    {
        "explain_invoice_status": "explain_invoice_status",
        "handle_invoice_not_found": "handle_invoice_not_found"
    }
)

workflow.add_edge("handle_invoice_not_found", END)
workflow.add_edge("explain_invoice_status", "ask_for_satisfaction")

workflow.add_conditional_edges(
    "ask_for_satisfaction",
    route_after_satisfaction_query,
    {
        "end_conversation": "end_conversation",
        "collect_feedback_for_ticket": "collect_feedback_for_ticket"
    }
)

workflow.add_edge("collect_feedback_for_ticket", "create_servicenow_ticket")
workflow.add_edge("create_servicenow_ticket", END)
workflow.add_edge("end_conversation", END)

# Compile the graph
app = workflow.compile()
