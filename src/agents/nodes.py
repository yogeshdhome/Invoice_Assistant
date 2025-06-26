import json
from .graph import AgentState
from .prompts import (
    intent_identification_prompt,
    po_details_extraction_prompt,
    non_po_details_extraction_prompt,
)
from src.core.llm import llm
from langchain_core.messages import HumanMessage
from src.agents.tools.sap_api import get_invoice_status_from_sap
from src.agents.tools.servicenow_api import create_servicenow_ticket

def greeting_node(state: AgentState) -> AgentState:
    """
    Greets the user and explains the chatbot's capabilities.
    """
    response = (
        "Hello! I am an invoice status chatbot. "
        "I can help you with the status of your PO and NON PO (ACR) invoices. "
        "I can provide the status for a maximum of 50 invoices in one interaction. "
        "How can I help you today?"
    )
    state["final_response"] = response
    return state

def identify_intent_node(state: AgentState) -> AgentState:
    """
    Identifies the user's intent (PO, NON_PO, GREETING, UNKNOWN).
    """
    prompt = intent_identification_prompt.format(
        user_query=state.get("user_query", ""),
        conversation_history=state.get("conversation_history", [])
    )
    
    response = llm.invoke(prompt)
    intent = str(response.content).strip().upper()

    if "PO" in intent:
        state["invoice_type"] = "PO"
    elif "NON_PO" in intent:
        state["invoice_type"] = "NON_PO"
    elif "GREETING" in intent:
        state["invoice_type"] = "GREETING"
    else:
        state["invoice_type"] = "UNKNOWN"
        state["final_response"] = "I'm sorry, I'm not sure what you're asking. Are you enquiring about PO or NON PO(ACR) based invoices?"

    return state

def ask_po_invoice_details_node(state: AgentState) -> AgentState:
    """
    Asks the user for PO invoice details.
    """
    response = "Please provide the PO Number and the Invoice Number. Also, let me know if you want to check the status of all invoices for the given PO."
    state["final_response"] = response
    return state

def ask_non_po_invoice_details_node(state: AgentState) -> AgentState:
    """
    Asks the user for Non-PO invoice details.
    """
    response = "Please provide either the ACR or Invoice Number, and the Invoice Document Date (in YYYY-MM-DD format) for up to 50 invoices. Please provide the details in a comma-separated format."
    state["final_response"] = response
    return state

def collect_and_validate_po_details_node(state: AgentState) -> AgentState:
    """
    Collects and validates PO invoice details from the user query.
    """
    print("---COLLECTING AND VALIDATING PO DETAILS---")
    
    prompt = po_details_extraction_prompt.format(user_query=state.get("user_query", ""))
    response = llm.invoke(prompt)
    details_json = str(response.content).strip()

    try:
        details = json.loads(details_json)
        state["po_number"] = details.get("po_number")
        state["invoice_number"] = details.get("invoice_number")
        state["check_all_for_po"] = details.get("check_all_for_po")
        # Add validation logic here
        if not state["po_number"] or not state["invoice_number"]:
             state["final_response"] = "I seem to be missing some details. Please provide both the PO Number and Invoice Number."
             # This should ideally route back to ask_po_invoice_details
             return state
    except json.JSONDecodeError:
        state["final_response"] = "I'm sorry, I had trouble understanding the details. Could you please provide them again clearly?"
        # This should ideally route back to ask_po_invoice_details
        return state

    state["final_response"] = "Details for PO collected."
    return state

def collect_and_validate_non_po_details_node(state: AgentState) -> AgentState:
    """
    Collects and validates Non-PO invoice details from the user query.
    """
    print("---COLLECTING AND VALIDATING NON-PO DETAILS---")
    
    prompt = non_po_details_extraction_prompt.format(user_query=state.get("user_query", ""))
    response = llm.invoke(prompt)
    details_json = str(response.content).strip()

    try:
        details = json.loads(details_json)
        # We will store the list of invoices directly in the state for now
        # In a real scenario, you'd iterate and validate each one
        state["json_payload"] = details 
        if not details.get("invoices"):
            raise ValueError("No invoices found")

    except (json.JSONDecodeError, ValueError):
        state["final_response"] = "I'm sorry, I had trouble understanding the details. Could you please provide them again clearly in the requested format?"
        # This should ideally route back to ask_non_po_invoice_details
        return state
    
    state["final_response"] = "Details for Non-PO collected."
    return state

def generate_json_payload_node(state: AgentState) -> AgentState:
    """
    Generates the JSON payload for the SAP API call.
    """
    print("---GENERATING JSON PAYLOAD---")
    invoice_type = state.get("invoice_type")
    payload = {"type": invoice_type, "invoices": []}

    if invoice_type == "PO":
        invoice_info = {
            "po_number": state.get("po_number"),
            "invoice_number": state.get("invoice_number"),
            "check_all_for_po": state.get("check_all_for_po", False)
        }
        payload["invoices"].append(invoice_info)
    elif invoice_type == "NON_PO":
        # The payload is already structured correctly from the extraction step
        payload = state.get("json_payload", {})

    state["json_payload"] = payload
    return state

def call_sap_api_node(state: AgentState) -> AgentState:
    """
    Calls the SAP API with the generated payload.
    """
    payload = state.get("json_payload")
    if not payload:
        # This case should ideally be handled more gracefully
        state["api_response"] = None
        return state
        
    api_result = get_invoice_status_from_sap(payload)
    state["api_response"] = api_result
    return state

def explain_invoice_status_node(state: AgentState) -> AgentState:
    """
    Formats the invoice status as a table in the response.
    """
    invoice_type = state.get("invoice_type")
    api_response = state.get("api_response", {})
    invoice_details = api_response.get("invoice_details", [])

    if invoice_type == "PO":
        header = "| Sr# | PO Number | Invoice Number | Status |\n|---|---|---|---|"
        rows = [
            f"| {i+1} | {row.get('po_number','')} | {row.get('invoice_number','')} | {row.get('status_code','')}: {row.get('status_description','')} |"
            for i, row in enumerate(invoice_details)
        ]
    else:  # Non-PO
        header = "| Sr# | ACR/Invoice Number | Invoice Document Date | Status |\n|---|---|---|---|"
        rows = [
            f"| {i+1} | {row.get('acr_number') or row.get('invoice_number','')} | {row.get('invoice_document_date','')} | {row.get('status_code','')}: {row.get('status_description','')} |"
            for i, row in enumerate(invoice_details)
        ]

    table = "\n".join([header] + rows)
    explanation = "Here is the status of your invoice(s):\n\n" + table
    state["final_response"] = explanation
    return state

def handle_invoice_not_found_node(state: AgentState) -> AgentState:
    # Placeholder
    print("---HANDLING INVOICE NOT FOUND---")
    state["final_response"] = "The requested invoice was not found. Please check the details and try again, or try again tomorrow."
    return state

def ask_for_satisfaction_node(state: AgentState) -> AgentState:
    # Placeholder
    print("---ASKING FOR SATISFACTION---")
    state["final_response"] = "Are you satisfied with the information provided? (Yes/No)"
    return state

def route_after_satisfaction_query(state: AgentState) -> str:
    # Placeholder for routing based on Yes/No
    if "yes" in state.get("user_query", "").lower():
        return "end_conversation"
    else:
        return "collect_feedback_for_ticket"

def collect_feedback_for_ticket_node(state: AgentState) -> AgentState:
    """
    Collects the user's details for creating a ServiceNow ticket.
    In a real scenario, this would use an LLM to extract entities.
    For now, we'll mock the extraction from the user_query.
    """
    print("---COLLECTING FEEDBACK FOR TICKET---")
    user_query = state.get("user_query", "")
    # Mock extraction
    state["email_id"] = "user@example.com" # Extracted from query
    state["vendor_number"] = "V12345" # Extracted from query
    state["final_response"] = "Thank you. I have collected your details."
    return state

def create_servicenow_ticket_node(state: AgentState) -> AgentState:
    """
    Creates a ServiceNow ticket with the collected user details.
    """
    print("---CREATING SERVICENOW TICKET---")
    
    email = state.get("email_id")
    vendor_number = state.get("vendor_number")
    # For a real implementation, you'd format the history nicely
    conversation_history = str(state.get("conversation_history", []))

    if not email or not vendor_number:
        state["final_response"] = "I am missing some of your details and cannot create a ticket. Please start over."
        return state

    ticket_number = create_servicenow_ticket(
        email=email,
        vendor_number=vendor_number,
        details="User not satisfied with invoice status response.",
        conversation=conversation_history
    )
    
    state["service_now_ticket"] = ticket_number
    state["final_response"] = f"I have created a ServiceNow ticket for you. The ticket number is {ticket_number}. A team member will follow up with you via email."
    return state

def end_conversation_node(state: AgentState) -> AgentState:
    # Placeholder
    print("---ENDING CONVERSATION---")
    state["final_response"] = "Thank you for using the invoice agent. Goodbye!"
    return state
