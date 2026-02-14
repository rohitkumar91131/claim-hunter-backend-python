import asyncio
from app.services.analysis_service import AnalysisService
from app.services.gemini_client import GeminiClient
from app.schemas.ai_analysis import AIAnalysisResponse, ClaimResult
from app.config import settings

# Mock Gemini Response
async def mock_gemini_analyze(text):
    print(f"Mocking Gemini for text: {text}")
    return AIAnalysisResponse(
        summary_score=92,
        overall_risk_level="High",
        claims=[
            ClaimResult(
                claim="Test claim",
                verdict="Likely False",
                fact_check_probability=95,
                confidence=90,
                reasoning="Mock reasoning"
            )
        ],
        emotional_tone="Manipulative",
        manipulation_score=85,
        confidence_overall=90
    )

# Override for test
GeminiClient.analyze_text = mock_gemini_analyze

async def test_ai_analysis():
    text = "The product is 100% guaranteed to work forever."
    print(f"Analyzing text: '{text}'")
    
    result = await AnalysisService.perform_ai_analysis(text)
    
    print("\n--- Analysis Result ---")
    print(result.model_dump_json(indent=2))
    
    assert result.summary_score is not None
    assert result.overall_risk_level in ["Low", "Medium", "High"]
    assert len(result.claims) > 0
    print("\n✅ AI Analysis Test Passed")

async def main():
    await test_ai_analysis()

if __name__ == "__main__":
    asyncio.run(main())
