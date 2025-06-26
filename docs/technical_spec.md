# Technical Specification: Invoice Status Chatbot

## 1. Introduction

This document provides the technical details for the Invoice Status Chatbot. It covers the system architecture, technology stack, component design, and data flows.

## 2. System Architecture

The application is designed as a modular, service-oriented system. It is composed of a FastAPI backend that serves a conversational agent built with LangGraph.

-   **Presentation Layer**: A user-facing chat interface (not in scope for this backend project) will interact with the FastAPI endpoints.
-   **Application Layer**: A FastAPI server that exposes a `/chat` endpoint. This layer is responsible for session management and orchestrating the agent's workflow.
-   **Agent Layer**: A LangGraph-based agent that encapsulates the entire conversational logic. It uses a state machine to move through different stages of the conversation, from intent detection to data collection and API calls.
-   **Integration Layer**: This layer consists of clients for external services, namely SAP S/4HANA for invoice data and ServiceNow for ticket creation.
-   **Data Layer**:
    -   **Short-Term Memory**: Redis is used to store conversation history for active user sessions.
    -   **Long-Term Memory**: A SAP HANA Cloud database is designated for storing queries and responses for analytics (implementation is out of scope for the initial build).

![Architecture Diagram](https://i.imgur.com/your-diagram-url.png) *Placeholder for architecture diagram*

## 3. Technology Stack

-   **Backend Framework**: FastAPI
-   **Programming Language**: Python 3.11
-   **Conversational AI Framework**: LangChain & LangGraph
-   **Data Validation**: Pydantic
-   **Short-Term Memory**: Redis
-   **Long-Term Memory**: SAP HANA Cloud (via psycopg2)
-   **Testing**: PyTest
-   **LLM Evaluation**: DeepEval
-   **Deployment**: Docker
-   **CI/CD**: GitHub Actions (not implemented)
-   **Logging/Tracing**: OpenTelemetry (not fully implemented)

## 4. Component Breakdown

### 4.1. FastAPI Application (`src/main.py`)

-   Exposes a `/chat` endpoint that accepts a `ChatRequest` (session_id, message).
-   Manages conversation history per `session_id` using the Redis client.
-   Invokes the LangGraph agent with the current user query and history.
-   Returns a `ChatResponse` with the agent's message and any generated ticket number.

### 4.2. LangGraph Agent (`src/agents/`)

-   **State (`graph.py`)**: An `AgentState` `TypedDict` defines the graph's memory, holding all information for the conversation's lifecycle.
-   **Nodes (`nodes.py`)**: Each function represents a state in the graph. Nodes are responsible for a single task, such as greeting the user, identifying intent, collecting details, or calling a tool.
-   **Prompts (`prompts.py`)**: Centralizes all prompts used by the LLM for tasks like intent identification and data extraction. This allows for easy tuning.
-   **Graph Definition (`graph.py`)**: Wires all the nodes and conditional routing logic together into a compiled, executable `StateGraph`.

### 4.3. Memory Management (`src/memory/`)

-   **Short-Term (`short_term.py`)**: Implements a `RedisConversationHistory` class to get and save `langchain_core.messages` objects for each session. This ensures the conversation is stateful.
-   **Long-Term (`long_term.py`)**: (Future) Will contain logic to connect to SAP HANA Cloud DB to log final outcomes of conversations for analytics.

### 4.4. External Tools (`src/agents/tools/`)

-   **SAP API (`sap_api.py`)**: Contains the function `get_invoice_status_from_sap`. In the initial build, this is a mock that returns predefined data based on the input payload.
-   **ServiceNow API (`servicenow_api.py`)**: Contains `create_servicenow_ticket`. This is a mock that returns a hardcoded ticket number.

## 5. Data Flow

1.  User sends a message to the `/chat` endpoint.
2.  FastAPI retrieves the session's history from Redis.
3.  The `invoice_agent_app` (LangGraph) is invoked with the user query and history.
4.  The graph starts at the `identify_intent` node.
5.  Based on the LLM's output, the graph transitions through various states (e.g., `ask_po_invoice_details`, `collect_and_validate_po_details`).
6.  The `call_sap_api` node is triggered, which calls the mock SAP tool.
7.  The graph continues its flow based on the API result and user feedback.
8.  If escalation is needed, the `create_servicenow_ticket` node is called.
9.  The final response is determined and the graph reaches an `END` state.
10. FastAPI saves the updated conversation history back to Redis and returns the final response to the user.

## 6. Testing and Evaluation

-   **Unit Tests (`/tests`)**: PyTest will be used to test individual nodes, tools, and API endpoints.
-   **LLM Evaluations**: DeepEval will be used to create an evaluation suite to measure the quality of LLM responses for intent detection and data extraction against a golden dataset.
