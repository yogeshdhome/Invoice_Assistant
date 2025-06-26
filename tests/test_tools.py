import pytest
from src.agents.tools.sap_api import get_invoice_status_from_sap
from src.agents.tools.servicenow_api import create_servicenow_ticket

def test_sap_api_po_success():
    """
    Tests the mock SAP API for a successful PO invoice lookup.
    """
    payload = {
        "type": "PO",
        "invoices": [{"po_number": "123", "invoice_number": "INV456"}]
    }
    response = get_invoice_status_from_sap(payload)
    assert response is not None
    assert response["invoice_details"][0]["status_code"] == "PAID"

def test_sap_api_non_po_success():
    """
    Tests the mock SAP API for a successful Non-PO invoice lookup.
    """
    payload = {
        "type": "NON_PO",
        "invoices": [{"acr_number": "ACR789", "invoice_document_date": "2023-01-01"}]
    }
    response = get_invoice_status_from_sap(payload)
    assert response is not None
    assert response["invoice_details"][0]["status_code"] == "PENDING_APPROVAL"

def test_sap_api_not_found():
    """
    Tests the mock SAP API for a case where the invoice is not found.
    """
    payload = {"type": "UNKNOWN_TYPE", "invoices": []}
    response = get_invoice_status_from_sap(payload)
    assert response is None

def test_servicenow_ticket_creation():
    """
    Tests the mock ServiceNow API for ticket creation.
    """
    ticket_number = create_servicenow_ticket(
        email="test@example.com",
        vendor_number="V987",
        details="Test details",
        conversation="User: Hello\nAgent: Hi"
    )
    assert "INC" in ticket_number
    assert len(ticket_number) > 5
