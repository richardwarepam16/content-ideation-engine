# backend/app/graph/a2a_protocol.py
import os
from typing import TypedDict, List, Optional, Literal, Dict
from datetime import datetime, UTC
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# 🌐 Shared CORS origins assigned to all agents
# ---------------------------------------------------------------------------
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")


# ---------------------------------------------------------------------------
# 🪪 Agent Card — metadata for each agent (Google-style)
# ---------------------------------------------------------------------------
class AgentCard(TypedDict):
    name: str
    role: str
    description: str
    cors_origins: List[str]
    capabilities: List[str]
    version: str


# ---------------------------------------------------------------------------
# ✉️ A2A Message Envelope — structured agent-to-agent communication
# ---------------------------------------------------------------------------
class A2AMessage(TypedDict, total=False):
    envelope_id: str
    from_agent: str
    to_agent: Optional[str]
    message_type: Literal["info", "handoff", "debug", "error"]
    summary: str
    payload: Dict
    timestamp: str


# ---------------------------------------------------------------------------
# 🏗️ Factory: Create an Agent Card
# ---------------------------------------------------------------------------
def create_agent_card(
    name: str,
    role: str,
    description: str,
    capabilities: List[str],
    version: str = "1.0.0"
) -> AgentCard:
    return AgentCard(
        name=name,
        role=role,
        description=description,
        cors_origins=CORS_ORIGINS,
        capabilities=capabilities,
        version=version
    )


# ---------------------------------------------------------------------------
# 📨 Factory: Create an A2A message envelope
# ---------------------------------------------------------------------------
def create_a2a_message(
    from_agent: str,
    summary: str,
    *,
    to_agent: Optional[str] = None,
    payload: Optional[dict] = None,
    message_type: Literal["info", "handoff", "debug", "error"] = "info",
) -> A2AMessage:
    return A2AMessage(
        envelope_id=f"env-{int(datetime.utcnow().timestamp() * 1000)}",
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=message_type,
        summary=summary,
        payload=payload or {},
        timestamp=datetime.now(UTC).isoformat()
    )
