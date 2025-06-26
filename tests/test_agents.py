import pytest
from src.agents.nodes import (
    greeting_node,
    ask_po_invoice_details_node,
    ask_non_po_invoice_details_node,
    handle_invoice_not_found_node,
    end_conversation_node,
    explain_invoice_status_node,
)
from src.agents.graph import AgentState

def get_default_state() -> AgentState:
    """Returns a default, complete AgentState for testing."""
    return {
        "conversation_history": [],
        "user_query": "",
        "invoice_type": None,
        "po_number": None,
        "invoice_number": None,
        "check_all_for_po": None,
        "acr_number": None,
        "invoice_document_date": None,
        "json_payload": None,
        "api_response": None,
        "is_satisfied": None,
        "email_id": None,
        "vendor_number": None,
        "service_now_ticket": None,
        "final_response": None,
    }

def test_greeting_node():
    """
    Tests the greeting_node to ensure it returns the correct welcome message.
    """
    initial_state = get_default_state()
    initial_state["user_query"] = "hi"
    updated_state = greeting_node(initial_state)
    assert "Hello! I am an invoice status chatbot." in (updated_state.get("final_response") or "")

def test_ask_po_invoice_details_node():
    """
    Tests the ask_po_invoice_details_node for the correct prompt.
    """
    initial_state = get_default_state()
    initial_state["invoice_type"] = "PO"
    updated_state = ask_po_invoice_details_node(initial_state)
    assert "Please provide the PO Number and the Invoice Number." in (updated_state.get("final_response") or "")

def test_ask_non_po_invoice_details_node():
    """
    Tests the ask_non_po_invoice_details_node for the correct prompt.
    """
    initial_state = get_default_state()
    initial_state["invoice_type"] = "NON_PO"
    updated_state = ask_non_po_invoice_details_node(initial_state)
    assert "Please provide either the ACR or Invoice Number" in (updated_state.get("final_response") or "")

def test_handle_invoice_not_found_node():
    """
    Tests the handle_invoice_not_found_node for the correct message.
    """
    initial_state = get_default_state()
    updated_state = handle_invoice_not_found_node(initial_state)
    assert "The requested invoice was not found." in (updated_state.get("final_response") or "")

def test_explain_invoice_status_node_po():
    """
    Tests that the explain_invoice_status_node correctly formats a PO invoice table.
    """
    initial_state = get_default_state()
    initial_state["invoice_type"] = "PO"
    initial_state["api_response"] = {
        "invoice_details": [{
            "po_number": "PO123",
            "invoice_number": "INV456",
            "status_code": "PAID",
            "status_description": "Paid in full."
        }]
    }
    
    updated_state = explain_invoice_status_node(initial_state)
    response = updated_state.get("final_response") or ""
    
    assert "| Sr# | PO Number | Invoice Number | Status |" in response
    assert "| 1 | PO123 | INV456 | PAID: Paid in full. |" in response

def test_explain_invoice_status_node_non_po():
    """
    Tests that the explain_invoice_status_node correctly formats a Non-PO invoice table.
    """
    initial_state = get_default_state()
    initial_state["invoice_type"] = "NON_PO"
    initial_state["api_response"] = {
        "invoice_details": [{
            "invoice_number": "ACR789",
            "invoice_document_date": "2023-10-27",
            "status_code": "PENDING",
            "status_description": "Pending approval."
        }]
    }
    
    updated_state = explain_invoice_status_node(initial_state)
    response = updated_state.get("final_response") or ""
    
    assert "| Sr# | ACR/Invoice Number | Invoice Document Date | Status |" in response
    assert "| 1 | ACR789 | 2023-10-27 | PENDING: Pending approval. |" in response

def test_end_conversation_node():
    """
    Tests the end_conversation_node for the correct goodbye message.
    """
    initial_state = get_default_state()
    initial_state["user_query"] = "yes"
    updated_state = end_conversation_node(initial_state)
    assert "Thank you for using the invoice agent. Goodbye!" in (updated_state.get("final_response") or "")
