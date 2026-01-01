import asyncio
from app.graph.workflow import IdeationWorkflow


async def main():
    workflow = IdeationWorkflow()

    input_data = {
        "industry": "fintech",
        "target_audience": "startup founders",
        "content_types": ["blog", "video", "social"],
        "additional_context": "Focus on early-stage SaaS companies"
    }

    result = await workflow.run(input_data)

    print("\n========== WORKFLOW RESULT ==========")
    for key, value in result.items():
        if key in {"trends", "audience_insights", "content_ideas"}:
            print(f"{key}: {len(value)} items")
        else:
            print(f"{key}: {value}")

    print("\n========== FINAL OUTPUT ==========")
    print(f"Trends: {len(result.get('trends', []))}")
    print(f"Audience Insights: {len(result.get('audience_insights', []))}")
    print(f"Content Ideas: {len(result.get('content_ideas', []))}")

    if result.get("error"):
        print("\n❌ ERROR DETECTED:")
        print(result["error"])
    else:
        print("\n✅ WORKFLOW COMPLETED SUCCESSFULLY")

    print("\n========== SAMPLE CONTENT IDEA ==========")
    ideas = result.get("content_ideas", [])
    if ideas:
        idea = ideas[0]
        for k, v in idea.items():
            print(f"{k}: {v}")
    else:
        print("No content ideas generated")


if __name__ == "__main__":
    asyncio.run(main())
