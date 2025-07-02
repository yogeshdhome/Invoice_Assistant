import redis
from typing import List
from langchain_core.messages import BaseMessage
from src.core.config import settings
import json

class RedisConversationHistory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True, # Decode responses to strings
        )

    async def get_history(self) -> List[BaseMessage]:
        """Retrieves conversation history from Redis."""
        history_json = await self.client.get(self.session_id)
        if history_json:
            history_dicts = json.loads(history_json)
            return [BaseMessage(**msg) for msg in history_dicts]
        return []

    def save_history(self, history: List[BaseMessage]):
        """Saves conversation history to Redis."""
        # Convert BaseMessage objects to dicts for serialization
        history_dicts = [msg.__dict__ for msg in history]
        self.client.set(self.session_id, json.dumps(history_dicts))

async def get_history_for_session(session_id: str) -> List[BaseMessage]:
    return await RedisConversationHistory(session_id).get_history()

def save_history_for_session(session_id: str, history: List[BaseMessage]):
    RedisConversationHistory(session_id).save_history(history)
