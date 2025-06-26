import redis
from typing import List
from langchain_core.messages import BaseMessage, from_json, to_json
from src.core.config import settings

class RedisConversationHistory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True, # Decode responses to strings
        )

    def get_history(self) -> List[BaseMessage]:
        """Retrieves conversation history from Redis."""
        history_json = self.client.get(self.session_id)
        if history_json:
            return from_json(history_json)
        return []

    def save_history(self, history: List[BaseMessage]):
        """Saves conversation history to Redis."""
        self.client.set(self.session_id, to_json(history))

def get_history_for_session(session_id: str) -> List[BaseMessage]:
    return RedisConversationHistory(session_id).get_history()

def save_history_for_session(session_id: str, history: List[BaseMessage]):
    RedisConversationHistory(session_id).save_history(history)
