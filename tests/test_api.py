import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    """
    Tests the /health endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_endpoint():
    """
    Tests the root / endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Invoice Agent API"}

def test_chat_endpoint_greeting():
    """
    Tests the /chat endpoint with a simple greeting.
    This is a basic integration test. A full test would require mocking the LLM
    and Redis, which can be done with pytest fixtures.
    """
    # This test assumes the LLM will identify "hello" as a greeting
    # and the 'greeting_node' will be triggered.
    # This will fail if the LLM is not running or configured.
    try:
        response = client.post(
            "/chat",
            json={"session_id": "test_session_123", "message": "hello"},
        )
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["session_id"] == "test_session_123"
        assert "Hello! I am an invoice status chatbot." in json_response["response_message"]
    except Exception as e:
        pytest.fail(f"Chat endpoint test failed, likely due to LLM/environment not being configured. Error: {e}")
