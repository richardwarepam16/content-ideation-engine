from langgraph.graph import StateGraph, END
from app.models.state import AgentState
from app.agents.trend_researcher import TrendResearcherAgent
from app.agents.audience_analyst import AudienceAnalystAgent
from app.agents.creative_writer import CreativeWriterAgent
from app.services.azure_openai_service import AzureOpenAIService
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class IdeationWorkflow:
    def __init__(self):
        self.llm_service = AzureOpenAIService()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        
        # Initialize agents
        researcher = TrendResearcherAgent(self.llm_service)
        analyst = AudienceAnalystAgent(self.llm_service)
        writer = CreativeWriterAgent(self.llm_service)
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("researcher", researcher.execute)
        workflow.add_node("analyst", analyst.execute)
        workflow.add_node("writer", writer.execute)
        
        # Define edges (sequential flow)
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "writer")
        workflow.add_edge("writer", END)
        
        return workflow.compile()
    
    async def run(self, input_data: Dict) -> Dict:
        """Execute the ideation workflow"""
        logger.info(f"Starting workflow for industry: {input_data.get('industry')}")
        
        # Initialize state
        initial_state = {
            "industry": input_data["industry"],
            "target_audience": input_data["target_audience"],
            "content_types": input_data["content_types"],
            "additional_context": input_data.get("additional_context", ""),
            "messages": [],
            "execution_logs": [],
            "trends": [],
            "audience_insights": [],
            "content_ideas": [],
            "current_agent": "",
            "error": ""
        }
        
        # Run graph
        result = await self.graph.ainvoke(initial_state)
        
        logger.info(f"Workflow completed. Generated {len(result.get('content_ideas', []))} ideas")
        
        return result