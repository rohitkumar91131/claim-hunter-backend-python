import asyncio
from app.services.gemini_client import GeminiClient
from app.config import settings

async def test_real_connection():
    print(f"Testing Gemini API with key: {settings.GOOGLE_API_KEY[:5]}... via URL: {GeminiClient.GEMINI_API_URL if hasattr(GeminiClient, 'GEMINI_API_URL') else 'Unknown'}")
    text = "The earth is flat."
    try:
        # Note: calling this directly calls the REAL API because we are not mocking it here
        result = await GeminiClient.analyze_text(text)
        print("Success!")
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    from app.services.gemini_client import GEMINI_API_URL
    print(f"URL: {GEMINI_API_URL}")
    asyncio.run(test_real_connection())
