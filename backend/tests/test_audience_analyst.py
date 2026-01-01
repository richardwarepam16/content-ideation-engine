import asyncio
from app.agents.audience_analyst import AudienceAnalystAgent
from app.services.azure_openai_service import AzureOpenAIService


async def main():
    agent = AudienceAnalystAgent(AzureOpenAIService())

    state = {
        "industry": "fintech",
        "target_audience": "startup founders",
        "trends": [
            {
                "topic": "AI Automation",
                "description": "Growing use of AI to automate internal workflows"
            },
            {
                "topic": "Embedded Finance",
                "description": "Financial services integrated directly into platforms"
            }
        ],
        "messages": []
    }

    result = await agent.execute(state)

    print("\n========== FULL STATE ==========")
    for k, v in result.items():
        print(f"{k}: {v}")

    insights = result.get("audience_insights", [])
    print("\n========== INSIGHTS COUNT ==========")
    print(len(insights))

    if not insights:
        print("\n⚠️  No audience insights returned")

    print("\n========== AUDIENCE INSIGHTS ==========")
    for i, insight in enumerate(insights, 1):
        print(f"\nInsight #{i}")
        print("Topic:", insight.get("topic"))
        print("Angle:", insight.get("angle"))
        print("Hook:", insight.get("hook"))
        print("Pain Points:", insight.get("pain_points"))
        print("Personas:", insight.get("target_personas"))


if __name__ == "__main__":
    asyncio.run(main())
