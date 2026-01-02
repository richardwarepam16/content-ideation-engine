from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime, UTC
import logging
# from app.graph.a2a_protocol import create_a2a_message

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, llm_service):
        self.name = name
        self.llm = llm_service      # ✅ canonical
        # self.claude = llm_service  # ✅ backward compatibility

    def log_message(self, state: Dict, message: str, message_type: str = "log") -> Dict:
        log_entry = {
            "agent": self.name,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now(UTC).isoformat()
        }

        if "execution_logs" not in state:
            state["execution_logs"] = []
        state["execution_logs"].append(log_entry)

        logger.info(f"[{self.name}] {message}")
        return state

    def add_a2a_message(self, state: Dict, message: str, data: Any = None) -> Dict:
        a2a_message = {
            "from_agent": self.name,
            "message": message,
            "data": data,
            "timestamp": datetime.now(UTC).isoformat()
        }

        if "messages" not in state:
            state["messages"] = []
        state["messages"].append(a2a_message)

        return state

    # def add_a2a_message(
    #     self,
    #     state: Dict,
    #     message: str,
    #     data: dict = None,
    #     *,
    #     to_agent: str | None = None,
    #     message_type: str = "info"
    # ) -> Dict:
    #     """
    #     Push a Google-style A2A envelope into the shared `messages` list
    #     on the state, using the protocol definition.
    #     """
    #     envelope = create_a2a_message(
    #         from_agent=self.name,
    #         summary=message,
    #         to_agent=to_agent,
    #         payload=data or {},
    #         message_type=message_type if message_type in ["info", "handoff", "debug", "error"] else "info",
    #     )
    #     state.setdefault("messages", []).append(envelope)
    #     return state
    

    @abstractmethod
    async def execute(self, state: Dict) -> Dict:
        pass