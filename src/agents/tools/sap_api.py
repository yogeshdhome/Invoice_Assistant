import requests
from typing import Optional
from src.core.config import settings

def get_invoice_status_from_sap(payload: dict) -> Optional[dict]:
    """
    Makes an API call to the SAP S4 system with the JSON data.
    This is a mock implementation that returns detailed data for table generation.
    """
    print(f"---CALLING SAP API with payload: {payload}---")
    
    # In a real implementation, you would use settings.sap_api_url
    # and handle authentication with settings.sap_api_key
    
    # Mock response logic:
    # If the request is for a known invoice, return a success status.
    # Otherwise, return None to simulate "not found".
    
    invoice_type = payload.get("type")
    
    if invoice_type == "PO":
        po_number = payload.get("invoices", [{}])[0].get("po_number", "PO123")
        invoice_number = payload.get("invoices", [{}])[0].get("invoice_number", "INV456")
        return {
            "invoice_details": [
                {
                    "po_number": po_number,
                    "invoice_number": invoice_number,
                    "status_code": "PAID",
                    "status_description": "The invoice has been paid in full."
                }
            ]
        }
    elif invoice_type == "NON_PO":
        invoice_number = payload.get("invoices", [{}])[0].get("invoice_number", "ACR789")
        doc_date = payload.get("invoices", [{}])[0].get("invoice_document_date", "2023-10-27")
        return {
            "invoice_details": [
                {
                    "invoice_number": invoice_number,
                    "invoice_document_date": doc_date,
                    "status_code": "PENDING_APPROVAL",
                    "status_description": "The invoice is pending approval."
                }
            ]
        }
        
    # Return None if the invoice is "not found" in the mock logic
    return None
