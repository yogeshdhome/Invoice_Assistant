from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.graph import app as invoice_agent_app
from src.schemas.api import ChatRequest, ChatResponse
from src.memory.short_term import get_history_for_session, save_history_for_session
from src.memory.long_term import save_conversation_record, fetch_conversation_records
from src.utils.guardrails import validate_input, validate_output, get_guardrails_errors, redact_pii, check_po_number_format, check_invoice_number_format

app = FastAPI(
    title="Invoice Agent API",
    description="API for the Invoice Agent chatbot.",
    version="0.1.0",
)

class HealthCheck(BaseModel):
    status: str

class AnalyticsRecord(BaseModel):
    session_id: str
    user_query: str
    agent_response: str
    final_status: Optional[str] = None

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Invoice Agent API"}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint for the invoice agent.
    """
    session_id = request.session_id
    user_message = request.message
    
    # Input guardrails
    if not validate_input(user_message):
        errors = get_guardrails_errors(user_message, section="input")
        raise HTTPException(status_code=400, detail={"error": "Input failed guardrails validation.", "details": errors})
    
    # Advanced: Custom regex for po number (if present in input)
    import re
    po_number_matches = re.findall(r"\b\d{1,20}\b", user_message)
    for po in po_number_matches:
        if len(po) == 10 and not check_po_number_format(po):
            raise HTTPException(status_code=400, detail={"error": "PO number format invalid. Must be 10 digits.", "po_number": po})
    
    # Retrieve conversation history from Redis
    history = get_history_for_session(session_id)
    
    # Prepare the input for the LangGraph agent
    agent_input = {
        "user_query": user_message,
        "conversation_history": history,
    }
    
    # Invoke the agent
    result = invoice_agent_app.invoke(agent_input)
    llm_response = result.get("final_response", "I am sorry, something went wrong.")
    
    # Output guardrails
    if not validate_output(llm_response):
        errors = get_guardrails_errors(llm_response, section="output")
        raise HTTPException(status_code=400, detail={"error": "Output failed guardrails validation.", "details": errors})
    
    # Advanced: Redact PII in output if present
    llm_response = redact_pii(llm_response)
    
    # Update history
    history.append(HumanMessage(content=user_message))
    history.append(AIMessage(content=llm_response))
    
    # Save updated history to Redis
    save_history_for_session(session_id, history)
    
    return ChatResponse(
        response_message=llm_response,
        session_id=session_id,
        service_now_ticket=result.get("service_now_ticket")
    )

@app.get("/analytics", tags=["Analytics"])
async def get_analytics(session_id: Optional[str] = Query(None, description="Session ID to filter by")):
    """
    Fetch conversation analytics from long-term memory. Optionally filter by session_id.
    """
    try:
        records = await fetch_conversation_records(session_id=session_id)
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics", tags=["Analytics"])
async def save_analytics(record: AnalyticsRecord):
    """
    Save a conversation record to long-term memory.
    """
    try:
        await save_conversation_record(
            session_id=record.session_id,
            user_query=record.user_query,
            agent_response=record.agent_response,
            final_status=record.final_status
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
