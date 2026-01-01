from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime

class IdeationRequest(BaseModel):
    industry: str = Field(..., min_length=1, max_length=100)
    target_audience: str = Field(..., min_length=1, max_length=200)
    content_types: List[Literal["blog", "video", "social"]] = ["blog", "video", "social"]
    additional_context: Optional[str] = None

class Trend(BaseModel):
    topic: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    source: str
    description: str

class AudienceInsight(BaseModel):
    topic: str
    angle: str
    hook: str
    pain_points: List[str]
    target_personas: List[str]

class ContentIdea(BaseModel):
    id: str
    format: Literal["blog", "video", "social"]
    icon: str
    title: str
    description: str
    structure: str
    confidence: float = Field(ge=0.0, le=100.0)
    trending: bool = False
    keywords: List[str] = []
    estimated_engagement: Optional[str] = None

class AgentMessage(BaseModel):
    agent_name: str
    message_type: Literal["status", "data", "error", "log"]
    content: str
    data: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class IdeationResponse(BaseModel):
    request_id: str
    ideas: List[ContentIdea]
    execution_time: float
    agent_logs: List[AgentMessage]
    metadata: Dict