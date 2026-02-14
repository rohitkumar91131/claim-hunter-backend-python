import httpx
import json
from typing import Dict, Any
from app.config import settings
from fastapi import HTTPException, status
from app.schemas.ai_analysis import AIAnalysisResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

class GeminiClient:
    @staticmethod
    async def analyze_text(text: str) -> AIAnalysisResponse:
        if not settings.GOOGLE_API_KEY:
            logger.error("GOOGLE_API_KEY not set.")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI Verification Service Unavailable (Config Error)")

        prompt = f"""
        You are an advanced AI fact-checking and misinformation risk analysis system.

        Analyze the following text and return STRICT JSON only.

        TEXT TO ANALYZE:
        "{text}"

        ---------------------------
        ANALYSIS REQUIREMENTS
        ---------------------------

        1. Extract factual claims from the text.

        2. For each claim, provide:
           - claim (string)
           - verdict ("True", "Likely True", "Uncertain", "Likely False", "False")
           - fact_check_probability (0-100) 
             → How objectively verifiable this claim is.
           - confidence (0-100)
           - reasoning (short explanation)

        3. Determine:
           - emotional_tone ("Neutral", "Emotional", "Manipulative", "Fear-Based", "Conspiratorial")
           - manipulation_score (0-100)

        4. Compute summary_score USING THIS EXACT FORMULA:

           Step A:
           average_fact_probability = average of all fact_check_probability values

           Step B:
           summary_score = round(
               (manipulation_score * 0.6) +
               ((100 - average_fact_probability) * 0.4)
           )

        5. Risk Level Mapping (MANDATORY):

           If summary_score <= 30 → overall_risk_level = "Low"
           If 31 <= summary_score <= 70 → overall_risk_level = "Medium"
           If summary_score > 70 → overall_risk_level = "High"

        6. SELF-VALIDATION STEP (MANDATORY):

           Before producing final JSON:
           - Recalculate summary_score.
           - Verify that overall_risk_level matches the mapping rules.
           - If inconsistent, recompute until valid.
           - DO NOT output inconsistent values.

        7. Provide:
           - summary_score (0-100)
           - overall_risk_level
           - claims (list)
           - emotional_tone
           - manipulation_score
           - confidence_overall (0-100)

        ---------------------------
        OUTPUT FORMAT (STRICT JSON ONLY)
        ---------------------------

        {{
          "summary_score": number,
          "overall_risk_level": "Low | Medium | High",
          "claims": [
            {{
              "claim": "string",
              "verdict": "True | Likely True | Uncertain | Likely False | False",
              "fact_check_probability": number,
              "confidence": number,
              "reasoning": "string"
            }}
          ],
          "emotional_tone": "string",
          "manipulation_score": number,
          "confidence_overall": number
        }}

        IMPORTANT:
        - Return JSON only.
        - No markdown.
        - No explanation outside JSON.
        - No extra keys.
        """

        headers = {
            "Content-Type": "application/json"
        }
        
        url = f"{GEMINI_API_URL}?key={settings.GOOGLE_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        # Retry logic for 429 warnings
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.ANALYSIS_TIMEOUT) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 429:
                        if attempt < max_retries:
                            wait_time = base_delay * (2 ** attempt)
                            logger.warning(f"Rate limit hit. Retrying in {wait_time}s...")
                            import asyncio
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            # If we exhausted retries, raise the error to be caught below
                            response.raise_for_status()
                    
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    try:
                        text_response = data['candidates'][0]['content']['parts'][0]['text']
                        # Clean potential markdown code blocks if AI disobeys
                        text_response = text_response.replace("```json", "").replace("```", "").strip()
                        
                        # Parse JSON
                        results_dict = json.loads(text_response)
                        
                        # Validate with Pydantic Schema
                        validated_response = AIAnalysisResponse(**results_dict)
                        
                        return validated_response
    
                    except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
                        logger.error(f"Failed to parse/validate Gemini response: {e}. Raw response: {data}")
                        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI Malformed Response")
                    except Exception as e:
                         logger.error(f"Validation Error: {e}")
                         raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI Response Validation Failed")
    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                     logger.error(f"Gemini API Rate Limit Exceeded: {e.response.text}")
                     raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI Usage Limit Exceeded. Please try again later.")
                
                logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI Verification Service Unavailable")
                
            except httpx.RequestError as e:
                logger.error(f"Gemini API connection error: {repr(e)}")
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI Verification Service Connectivity Error: {str(e)}")
