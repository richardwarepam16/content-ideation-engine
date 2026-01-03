import json
from typing import Dict, Any, Literal
from datetime import datetime, UTC

def create_a2a_message(
    from_agent: str,
    summary: str,
    *,
    to_agent: str | None = None,
    payload: Dict[str, Any] | None = None,
    message_type: Literal["info", "handoff", "debug", "error"] = "info",
) -> Dict[str, Any]:
    """
    Creates a structured agent-to-agent (A2A) message envelope
    that is compatible with LangChain message standards.

    This adheres to a Google-style communication protocol while ensuring
    it can be processed by LangGraph. The original message is serialized
    as a JSON string and placed in the 'content' field.

    Args:
        from_agent: The name of the agent sending the message.
        summary: A brief, human-readable summary of the message content.
        to_agent: The intended recipient agent's name. If None, the
                  message is considered a broadcast.
        payload: A dictionary containing the message's data.
        message_type: The type of message, which can be one of "info",
                      "handoff", "debug", or "error".

    Returns:
        A dictionary representing the LangChain-compatible A2A message.
    """
    message_content = {
        "from_agent": from_agent,
        "to_agent": to_agent,
        "type": message_type,
        "summary": summary,
        "payload": payload or {},
        "timestamp": datetime.now(UTC).isoformat(),
    }

    return {
        "role": "function",
        "name": from_agent,
        "content": json.dumps(message_content)
    }
