"""Compose prompt: fact-anchor + style; DNA tone overlay only (no lexicon)."""
from __future__ import annotations

from typing import Optional

from app.models.alter_ego_dna import AlterEgoDnaJson
from app.services.compose_caps import HASHTAG_HINTS, clamp_max_chars

_LANG = {
    "zh-TW": "Traditional Chinese (zh-TW)",
    "en": "English",
    "ja": "Japanese",
}

_PART_HINT = {
    "all": "Fill titles (3), body (1), and hashtag_sets (3 arrays).",
    "title": "Fill titles (3). body may be \"\" and hashtag_sets may be [[],[],[]].",
    "body": "Fill body only. titles may be [\"\",\"\",\"\"] and hashtag_sets empty.",
    "hashtags": "Fill hashtag_sets (3 arrays). titles/body may be empty.",
}


def dna_tone_overlay(dna: Optional[AlterEgoDnaJson]) -> str:
    if dna is None:
        return ""
    tones = ", ".join(dna.tone_descriptors[:4])
    return (
        f"Voice overlay (tone/rhythm only, NEVER copy domain lexicon): "
        f"persona={dna.voice_persona}; tone={tones}; "
        f"rhythm={dna.sentence_rhythm}; emoji={dna.emoji_style}."
    )


def build_compose_prompt(
    *,
    platform: str,
    style: str,
    max_chars: int,
    part: str,
    language: str,
    topic_title: str,
    context_summary: str,
    dna_overlay: str,
) -> str:
    cap = clamp_max_chars(platform, max_chars)
    label = _LANG.get(language, "Traditional Chinese (zh-TW)")
    lo, hi = HASHTAG_HINTS.get(platform, (0, 6))
    fact = (context_summary or topic_title or "").strip()[:1500]
    return (
        "You write ONE social post pack as JSON only (no markdown).\n"
        f"Platform: {platform}. Style (must follow): {style}.\n"
        f"LANGUAGE: Write titles and body ONLY in {label}. Do not mix languages.\n"
        f"HARD LIMIT: chosen title + body + hashtags together MUST be <= {cap} characters.\n"
        f"Hashtags per set: {lo} to {hi}.\n"
        f"Topic title: {topic_title.strip()[:300]}\n"
        f"FACTUAL SUMMARY (Truth Anchor):\n{fact}\n"
        f"{dna_overlay}\n"
        "CRITICAL GUARDRAILS:\n"
        "1. FACT ANCHORING: Use only the topic and factual summary. Do not invent events.\n"
        "2. ANTI-POLLUTION: Style and optional voice overlay are tone-only. "
        "DO NOT force unrelated domain terms, food items, or jargon into a non-related topic "
        "(e.g., never insert food metaphors into business/trade news).\n"
        f"3. {_PART_HINT.get(part, _PART_HINT['all'])}\n"
        'JSON shape: {"titles":["","",""],"body":"","hashtag_sets":[[],[],[]]}\n'
    )
