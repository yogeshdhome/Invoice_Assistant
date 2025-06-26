from langchain_core.prompts import PromptTemplate

intent_identification_prompt = PromptTemplate.from_template(
    """
    Given the user query, identify if the user is asking about a PO invoice or a NON PO (ACR) invoice.
    The user query is: "{user_query}"
    The conversation history is:
    {conversation_history}

    Possible intents are: "PO", "NON_PO", "GREETING", "UNKNOWN".

    If the user is asking about a PO invoice, respond with "PO".
    If the user is asking about a NON PO (ACR) invoice, respond with "NON_PO".
    If the user is just greeting, respond with "GREETING".
    If the intent is not clear, respond with "UNKNOWN".

    Respond with only one word: "PO", "NON_PO", "GREETING", or "UNKNOWN".
    """
)

po_details_extraction_prompt = PromptTemplate.from_template(
    """
    You are an expert at extracting invoice details from a user query.
    Extract the PO Number and the Invoice Number from the following query.
    Also, determine if the user wants to check the status for all invoices for the given PO.

    User query: "{user_query}"

    Respond with a JSON object with the following keys:
    - "po_number" (string)
    - "invoice_number" (string)
    - "check_all_for_po" (boolean)
    
    Example response for a single invoice:
    {{
        "invoices": [
            {{
                "po_number": "1234567890",
                "invoice_number": "1234567890",
                "check_all_for_po": true,
            }}
        ]
    }}
    If a value is not present, use null.
    """
)

non_po_details_extraction_prompt = PromptTemplate.from_template(
    """
    You are an expert at extracting invoice details from a user query.
    Extract the ACR Number, Invoice Number, and Invoice Document Date from the following query.
    The user might provide up to 50 comma-separated values for each.

    User query: "{user_query}"

    Respond with a JSON object containing a list of invoices, where each object has the following keys:
    - "acr_number" (string or null)
    - "invoice_number" (string or null)
    - "invoice_document_date" (string in "YYYY-MM-DD" format)

    Example response for a single invoice:
    {{
        "invoices": [
            {{
                "acr_number": "12345",
                "invoice_number": null,
                "invoice_document_date": "2023-10-26"
            }}
        ]
    }}
    
    If a value is not present, use null.
    """
)
