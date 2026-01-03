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
            data = await websocket.receive_json()
            
            # Use the IdeationRequest model for validation and structure
            try:
                request = IdeationRequest(**data)
            except Exception as e:
                await manager.send_message({"type": "error", "payload": f"Invalid request format: {e}"}, websocket)
                continue

            await manager.send_message({"type": "status", "payload": "Starting ideation pipeline..."}, websocket)
            
            initial_state = {
                "industry": request.industry,
                "target_audience": request.target_audience,
                "content_types": request.content_types,
                "additional_context": request.additional_context or "",
                "messages": [], "execution_logs": [], "trends": [],
                "audience_insights": [], "content_ideas": [], "current_agent": "", "error": ""
            }

            try:
                # Use astream_events to get detailed events
                async for event in workflow.graph.astream(initial_state, stream_mode="values"):
                    # The event contains the full state of the graph after each step
                    current_agent = event.get("current_agent")
                    if current_agent:
                        await manager.send_message({
                            "type": "agent_update",
                            "payload": {"agent_name": current_agent, "message": f"Agent {current_agent} is running."}
                        }, websocket)

                # After the stream is finished, the final state is in 'event'
                final_state = event
                await manager.send_message({
                    "type": "final_result",
                    "payload": {
                        "ideas": final_state.get("content_ideas", [])
                    }
                }, websocket)

            except Exception as e:
                logger.error(f"Workflow execution failed: {e}")
                await manager.send_message({"type": "error", "payload": str(e)}, websocket)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"An unexpected error occurred in WebSocket: {e}")
        manager.disconnect(websocket)

@router.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "content-ideation-engine"}