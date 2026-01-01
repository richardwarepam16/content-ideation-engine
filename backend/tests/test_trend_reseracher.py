import asyncio
from app.agents.trend_researcher import TrendResearcherAgent
from app.services.azure_openai_service import AzureOpenAIService


async def main():
    agent = TrendResearcherAgent(AzureOpenAIService())

    state = {
        "industry": "healthcare",
        "messages": [],
    }

    result = await agent.execute(state)

    print("\n=== FINAL STATE ===")
    print(result)

    print("\n=== TRENDS ===")
    for t in result.get("trends", []):
        print(f"- {t['topic']} ({t['relevance_score']})")


if __name__ == "__main__":
    asyncio.run(main())
