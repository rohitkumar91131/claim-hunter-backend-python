"""
Local heuristic-based text analyzer for developer mode (no API key required).

Provides basic claim detection and risk assessment without external AI calls.
"""

import re
from typing import List
from app.schemas.ai_analysis import AIAnalysisResponse, ClaimResult

# Keywords indicating potentially manipulative language
MANIPULATIVE_KEYWORDS = [
    "everyone knows", "nobody can deny", "it's obvious", "clearly",
    "wake up", "they don't want you to know", "secret", "cover-up",
    "conspiracy", "mainstream media", "fake news", "sheeple",
    "agenda", "exposed", "the real story",
]

EMOTIONAL_KEYWORDS = [
    "shocking", "outrageous", "unbelievable", "alarming", "devastating",
    "terrifying", "horrifying", "disgusting", "shameful", "scandalous",
    "incredible", "amazing", "miraculous",
]

FEAR_KEYWORDS = [
    "danger", "dangerous", "threat", "crisis", "emergency",
    "catastrophic", "disaster", "deadly", "lethal", "fatal",
    "urgent", "critical", "severe",
]

CONSPIRATORIAL_KEYWORDS = [
    "deep state", "new world order", "illuminati", "false flag",
    "controlled", "puppets", "elites", "globalist", "planned",
    "orchestrated",
]

# Patterns that indicate a sentence contains a factual claim
_CLAIM_PATTERNS = [
    re.compile(r"\b(is|are|was|were|has|have|had|will|would|can|could|should|must)\b"),
    re.compile(r"\b(studies show|research shows|scientists say|experts say|according to)\b"),
    re.compile(r"\b(proven|confirmed|revealed|demonstrated|established|found)\b"),
    re.compile(r"\b(\d+%|\d+ percent|statistics|data|evidence)\b"),
]


def _split_into_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if len(s.strip()) > 10]


def _count_keyword_hits(text_lower: str, keywords: List[str]) -> int:
    return sum(1 for kw in keywords if kw in text_lower)


def _compute_manipulation_score(text: str) -> int:
    text_lower = text.lower()
    score = (
        _count_keyword_hits(text_lower, MANIPULATIVE_KEYWORDS) * 15
        + _count_keyword_hits(text_lower, EMOTIONAL_KEYWORDS) * 8
        + _count_keyword_hits(text_lower, FEAR_KEYWORDS) * 8
        + _count_keyword_hits(text_lower, CONSPIRATORIAL_KEYWORDS) * 20
    )
    return min(100, score)


def _detect_emotional_tone(text: str, manipulation_score: int) -> str:
    text_lower = text.lower()
    if _count_keyword_hits(text_lower, CONSPIRATORIAL_KEYWORDS) >= 1:
        return "Conspiratorial"
    if manipulation_score >= 60:
        return "Manipulative"
    if _count_keyword_hits(text_lower, FEAR_KEYWORDS) >= 2:
        return "Fear-Based"
    if _count_keyword_hits(text_lower, EMOTIONAL_KEYWORDS) >= 1:
        return "Emotional"
    return "Neutral"


def _analyze_sentence(sentence: str) -> ClaimResult:
    """Score a single sentence as a potential factual claim."""
    sentence_lower = sentence.lower()

    claim_indicator_count = sum(
        1 for p in _CLAIM_PATTERNS if p.search(sentence_lower)
    )
    fact_check_probability = min(90, 20 + claim_indicator_count * 20)

    word_count = len(sentence.split())
    confidence = max(30, min(80, 30 + word_count * 2))

    has_numbers = bool(re.search(r"\d+", sentence))
    has_source = bool(
        re.search(r"(according to|study|research|expert|scientist)", sentence_lower)
    )
    has_absolute = bool(
        re.search(r"\b(always|never|all|none|every|no one|everyone)\b", sentence_lower)
    )
    has_hedge = bool(
        re.search(r"\b(might|may|could|possibly|perhaps|allegedly)\b", sentence_lower)
    )

    if has_source and has_numbers:
        verdict = "Likely True"
        reasoning = "Claim references specific data or sources which increases verifiability."
    elif has_absolute:
        verdict = "Likely False"
        reasoning = "Claim uses absolute language (always/never/all/none) which is often inaccurate."
    elif has_hedge:
        verdict = "Uncertain"
        reasoning = "Claim uses hedging language suggesting uncertainty or speculation."
    else:
        verdict = "Uncertain"
        reasoning = "Claim could not be definitively assessed without external verification."

    return ClaimResult(
        claim=sentence[:200],
        verdict=verdict,
        fact_check_probability=fact_check_probability,
        confidence=confidence,
        reasoning=reasoning,
    )


def analyze_text_local(text: str) -> AIAnalysisResponse:
    """
    Perform local heuristic-based text analysis without an external AI API.

    Uses keyword detection and sentence-level heuristics to produce an
    AIAnalysisResponse that is schema-compatible with the Gemini-backed endpoint.
    Intended for developer testing when no Google API key is configured.
    """
    sentences = _split_into_sentences(text)
    # Limit claim analysis to the first 5 sentences for performance.
    # Fall back to the raw (possibly very short) text if no sentences were detected.
    claim_sentences = sentences[:5] if sentences else [text[:200] or "No content"]

    claims = [_analyze_sentence(s) for s in claim_sentences]

    # Guard against an empty claims list (should not happen with the fallback above)
    if not claims:
        claims = [_analyze_sentence(text[:200] or "No content")]

    manipulation_score = _compute_manipulation_score(text)
    emotional_tone = _detect_emotional_tone(text, manipulation_score)

    # Use the same formula as the Gemini prompt for consistency
    avg_fact_probability = sum(c.fact_check_probability for c in claims) / len(claims)
    summary_score = round((manipulation_score * 0.6) + ((100 - avg_fact_probability) * 0.4))
    summary_score = max(0, min(100, summary_score))

    if summary_score <= 30:
        overall_risk_level = "Low"
    elif summary_score <= 70:
        overall_risk_level = "Medium"
    else:
        overall_risk_level = "High"

    confidence_overall = round(sum(c.confidence for c in claims) / len(claims))

    return AIAnalysisResponse(
        summary_score=summary_score,
        overall_risk_level=overall_risk_level,
        claims=claims,
        emotional_tone=emotional_tone,
        manipulation_score=manipulation_score,
        confidence_overall=confidence_overall,
    )
