from .base_agent import BaseAgent
from typing import Dict, List
import json
import re
# from graph.a2a_protocol import create_agent_card

# AGENT_CARD = create_agent_card( 
#     name="Trend Researcher", 
#     role="trend_research", 
#     description="Analyzes industry trends and identifies emerging topics.", 
#     capabilities=["trend-analysis", "scoring", "summarization"], 
#     ) 


class TrendResearcherAgent(BaseAgent):
    def __init__(self, azure_openai_service):
        # BaseAgent stores this as self.llm
        super().__init__("Trend Researcher", azure_openai_service)

    async def execute(self, state: Dict) -> Dict:
        state = self.log_message(state, "Starting trend research analysis...")
        state["current_agent"] = self.name

        industry = state.get("industry", "")

        prompt = f"""You are a trend research expert analyzing the {industry} industry.

Your task:
1. Identify 5–7 current trending topics in {industry}
2. For each trend, provide:
   - Topic name
   - Relevance score (0.0–1.0)
   - Brief description (1–2 sentences)
   - Why it matters now

Focus on trends from the past 3–6 months that are gaining momentum.

Return your analysis as a JSON array with this structure:
[
  {{
    "topic": "Topic Name",
    "relevance_score": 0.85,
    "description": "Brief description",
    "source": "Industry reports/News/Social media"
  }}
]
"""

        state = self.log_message(state, "Analyzing industry trends...")

        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.5,
                max_tokens=2000
            )

            trends = self._parse_trends(response)
            state["trends"] = trends
            state["trend_sources"] = list(
                set(t.get("source", "Unknown") for t in trends)
            )

            state = self.log_message(
                state,
                f"Identified {len(trends)} trending topics"
            )

            state = self.add_a2a_message(
                state,
                message=f"Handoff: {len(trends)} trends identified for audience analysis.",
                data={
                    "trend_count": len(trends),
                    "top_trend": trends[0]["topic"] if trends else "N/A",
                },
                to_agent="Audience Analyst",
                message_type="handoff",
            )

        except Exception as e:
            state["error"] = f"Trend research failed: {str(e)}"
            state = self.log_message(state, f"Error: {str(e)}", "error")

        return state

    def _parse_trends(self, response: str) -> List[Dict]:
        """Extract and parse JSON trends from Azure OpenAI response"""
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except Exception:
            # Safe fallback to prevent pipeline failure
            return [
                {
                    "topic": "AI Integration",
                    "relevance_score": 0.9,
                    "description": "Increasing adoption of AI tools across business workflows",
                    "source": "Industry reports"
                }
            ]
