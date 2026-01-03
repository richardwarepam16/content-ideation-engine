from .base_agent import BaseAgent
from typing import Dict, List
import json

class CreativeWriterAgent(BaseAgent):
    def __init__(self, claude_service):
        super().__init__("Creative Writer", claude_service)
    
    async def execute(self, state: Dict) -> Dict:
        state = self.log_message(state, "Crafting content ideas...")
        state["current_agent"] = self.name
        
        insights = state.get("audience_insights", [])
        content_types = state.get("content_types", ["blog", "video", "social"])
        target_audience = state.get("target_audience", "")
        
        insights_summary = "\\n".join([
            f"Topic: {i['topic']}\\nAngle: {i['angle']}\\nHook: {i['hook']}"
            for i in insights[:5]
        ])
        
        prompt = f"""You are a creative content strategist.

Audience-adapted concepts:
{insights_summary}

Target audience: {target_audience}
Content formats needed: {', '.join(content_types)}

Create detailed content ideas for each format. For each idea provide:
- Title (compelling and click-worthy)
- Description (2-3 sentences)
- Content structure (format-specific details)
- Keywords (5-7 SEO keywords)
- Estimated engagement level (High/Medium/Low)

Return as JSON:
[
  {{
    "format": "blog|video|social",
    "title": "Compelling title",
    "description": "Detailed description",
    "structure": "Format-specific structure details",
    "keywords": ["keyword1", "keyword2"],
    "confidence": 85,
    "trending": true,
    "estimated_engagement": "High"
  }}
]

Generate 2-3 ideas per format type.
"""
        
        state = self.log_message(state, "Generating polished content ideas...")
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=3000
            )
            
            ideas = self._parse_ideas(response, content_types)
            state["content_ideas"] = ideas
            
            state = self.log_message(
                state,
                f"✓ Created {len(ideas)} ready-to-use content ideas"
            )
            
            state = self.add_a2a_message(
                state,
                message=f"Ideation complete. Generated {len(ideas)} content ideas.",
                data={"total_ideas": len(ideas), "formats": content_types},
                to_agent=None,  # Broadcast to the system/end-user
                message_type="info",
            )
            
        except Exception as e:
            state["error"] = f"Content generation failed: {str(e)}"
            state = self.log_message(state, f"Error: {str(e)}", "error")
        
        return state
    
    def _parse_ideas(self, response: str, content_types: List[str]) -> List[Dict]:
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            json_str = response[start:end]
            ideas = json.loads(json_str)
            
            # Add icons and ensure format
            icon_map = {"blog": "📝", "video": "🎥", "social": "📱"}
            for idea in ideas:
                idea["icon"] = icon_map.get(idea.get("format", "blog"), "📝")
                idea["id"] = f"{idea['format']}-{hash(idea['title']) % 10000}"
            
            return ideas
        except:
            return []