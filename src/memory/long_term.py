import asyncio
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, func, select
from src.core.config import settings

Base = declarative_base()

class ConversationRecord(Base):
    __tablename__ = "conversation_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128), nullable=False)
    user_query = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    final_status = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

# Build the SAP HANA Cloud DB connection string
DB_URL = f"postgresql+asyncpg://{settings.hana_db_user}:{settings.hana_db_password}@{settings.hana_db_address}:{settings.hana_db_port}/{settings.hana_db_database}"
engine = create_async_engine(DB_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    """Create tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_conversation_record(
    session_id: str,
    user_query: str,
    agent_response: str,
    final_status: Optional[str] = None
) -> None:
    """Save a conversation record to SAP HANA Cloud."""
    async with AsyncSessionLocal() as session:
        record = ConversationRecord(
            session_id=session_id,
            user_query=user_query,
            agent_response=agent_response,
            final_status=final_status
        )
        session.add(record)
        await session.commit()

async def fetch_conversation_records(session_id: Optional[str] = None) -> List[Dict]:
    """Fetch conversation records by session_id (or all if None)."""
    async with AsyncSessionLocal() as session:
        stmt = select(ConversationRecord)
        if session_id:
            stmt = stmt.where(ConversationRecord.session_id == session_id)
        result = await session.execute(stmt)
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "session_id": r.session_id,
                "user_query": r.user_query,
                "agent_response": r.agent_response,
                "final_status": r.final_status,
                "created_at": r.created_at.isoformat() if r.created_at is not None else None
            }
            for r in records
        ]
