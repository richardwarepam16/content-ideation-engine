from typing import TypedDict, List, Dict, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    # Input
    industry: str
    target_audience: str
    content_types: List[str]
    additional_context: str
    
    # Agent Communication (a2a protocol)
    messages: Annotated[List[Dict], add_messages]
    # agent_cards: List[AgentCard]

    
    # Agent 1: Trend Researcher Output
    trends: List[Dict]
    trend_sources: List[str]
    
    # Agent 2: Audience Analyst Output
    audience_insights: List[Dict]
    personas: List[Dict]
    
    # Agent 3: Creative Writer Output
    content_ideas: List[Dict]
    
    # Metadata
    current_agent: str
    execution_logs: List[Dict]
    error: str