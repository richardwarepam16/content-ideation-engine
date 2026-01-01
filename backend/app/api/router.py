from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.models.schemas import IdeationRequest, IdeationResponse, ContentIdea, AgentMessage
from app.graph.workflow import IdeationWorkflow
from typing import List
import uuid
import time
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global workflow instance
workflow = IdeationWorkflow()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.post("/api/ideate", response_model=IdeationResponse)
async def generate_ideas(request: IdeationRequest):
    """Generate content ideas using multi-agent system"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Run workflow
        result = await workflow.run({
            "industry": request.industry,
            "target_audience": request.target_audience,
            "content_types": request.content_types,
            "additional_context": request.additional_context or ""
        })
        
        # Check for errors
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Format response
        ideas = [
            ContentIdea(**idea) for idea in result.get("content_ideas", [])
        ]
        
        agent_logs = [
            AgentMessage(
                agent_name=log["agent"],
                message_type=log["type"],
                content=log["message"],
                timestamp=log["timestamp"]
            )
            for log in result.get("execution_logs", [])
        ]
        
        execution_time = time.time() - start_time
        
        return IdeationResponse(
            request_id=request_id,
            ideas=ideas,
            execution_time=execution_time,
            agent_logs=agent_logs,
            metadata={
                "trends_count": len(result.get("trends", [])),
                "personas": result.get("personas", []),
                "a2a_messages": len(result.get("messages", []))
            }
        )
        
    except Exception as e:
        logger.error(f"Ideation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/ideate")
async def websocket_ideate(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive request
            data = await websocket.receive_json()
            
            # Send status updates during processing
            await manager.send_message({
                "type": "status",
                "message": "Starting ideation pipeline..."
            }, websocket)
            
            # Run workflow with streaming updates
            # (Implementation would stream agent logs in real-time)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "content-ideation-engine"}