import asyncio
from app.agents.creative_writer import CreativeWriterAgent
from app.services.azure_openai_service import AzureOpenAIService


async def main():
    agent = CreativeWriterAgent(AzureOpenAIService())

    state = {
        "industry": "fintech",
        "target_audience": "startup founders",
        "content_types": ["blog", "video", "social"],
        "audience_insights": [
            {
                "topic": "AI Automation",
                "angle": "Position AI as a force multiplier for lean teams",
                "hook": "How founders scale without hiring",
                "pain_points": ["Limited headcount", "Operational bottlenecks"],
                "target_personas": ["Technical Founder", "Product-focused CEO"]
            },
            {
                "topic": "Embedded Finance",
                "angle": "Frame as a growth lever for platform businesses",
                "hook": "Why payments are becoming invisible",
                "pain_points": ["Monetization", "User retention"],
                "target_personas": ["Growth Lead", "Platform Founder"]
            }
        ],
        "messages": []
    }

    result = await agent.execute(state)

    print("\n========== FULL STATE ==========")
    for k, v in result.items():
        print(f"{k}: {v}")

    ideas = result.get("content_ideas", [])
    print("\n========== IDEAS COUNT ==========")
    print(len(ideas))

    if not ideas:
        print("\n⚠️  No content ideas generated")

    print("\n========== CONTENT IDEAS ==========")
    for i, idea in enumerate(ideas, 1):
        print(f"\nIdea #{i}")
        print("Format:", idea.get("format"), idea.get("icon"))
        print("Title:", idea.get("title"))
        print("Description:", idea.get("description"))
        print("Structure:", idea.get("structure"))
        print("Keywords:", idea.get("keywords"))
        print("Engagement:", idea.get("estimated_engagement"))
        print("Trending:", idea.get("trending"))
        print("ID:", idea.get("id"))


if __name__ == "__main__":
    asyncio.run(main())
