from .base_agent import BaseAgent
from typing import Dict, List
import json


class AudienceAnalystAgent(BaseAgent):
    def __init__(self, azure_openai_service):
        # BaseAgent stores this as self.llm
        super().__init__("Audience Analyst", azure_openai_service)

    async def execute(self, state: Dict) -> Dict:
        state = self.log_message(state, "Analyzing audience preferences...")
        state["current_agent"] = self.name

        trends = state.get("trends", [])
        target_audience = state.get("target_audience", "")
        industry = state.get("industry", "")

        trends_summary = "\n".join(
            f"- {t['topic']}: {t['description']}"
            for t in trends[:5]
        )

        prompt = f"""You are an audience analysis expert.

Context from Trend Researcher:
{trends_summary}

Your task:
Adapt these trends for the target audience: {target_audience} in {industry}

For each trend, provide:
1. How to angle it for this specific audience
2. A compelling hook
3. Pain points it addresses
4. Relevant personas (2-3 specific profiles)

Return as JSON array:
[
  {{
    "topic": "Trend topic",
    "angle": "How to present to audience",
    "hook": "Compelling opening line",
    "pain_points": ["pain1", "pain2"],
    "target_personas": ["Persona 1", "Persona 2"]
  }}
]
"""

        state = self.log_message(state, "Mapping trends to audience needs...")

        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.6,
                max_tokens=2500
            )

            insights = self._parse_insights(response)
            state["audience_insights"] = insights

            all_personas = []
            for insight in insights:
                all_personas.extend(insight.get("target_personas", []))
            state["personas"] = list(set(all_personas))

            state = self.log_message(
                state,
                f"Generated {len(insights)} audience-adapted concepts"
            )

            state = self.add_a2a_message(
                state,
                f"Adapted trends for {len(state['personas'])} audience personas",
                data={"insights_count": len(insights)}
            )

        except Exception as e:
            state["error"] = f"Audience analysis failed: {str(e)}"
            state = self.log_message(state, f"Error: {str(e)}", "error")

        return state

    def _parse_insights(self, response: str) -> List[Dict]:
        """Extract and parse JSON insights from Azure OpenAI response"""
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            return json.loads(response[start:end])
        except Exception:
            return [
                {
                    "topic": "Industry Transformation",
                    "angle": "What this means for your role",
                    "hook": "The landscape is changing faster than you think",
                    "pain_points": ["Staying current", "Rising competition"],
                    "target_personas": ["Decision Maker", "Practitioner"]
                }
            ]
