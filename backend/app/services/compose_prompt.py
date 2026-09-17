"""Compose prompt: fact-anchor + target length + tone; DNA overlay only."""
from __future__ import annotations

from typing import List, Optional

from app.models.alter_ego_dna import AlterEgoDnaJson
from app.services.compose_caps import HASHTAG_HINTS, clamp_max_chars
from app.services.compose_tone import tone_card

_LANG = {
    "zh-TW": "Traditional Chinese (zh-TW)",
    "en": "English",
    "ja": "Japanese",
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


def _keep_block(snippets: List[str]) -> str:
    clean = [s.strip() for s in snippets if s and s.strip()][:8]
    if not clean:
        return ""
    joined = "\n".join(f"- {s[:280]}" for s in clean)
    return (
        "USER_KEEP_SNIPPETS (verbatim; must appear unchanged in body):\n"
        f"{joined}\n"
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
    preserve_snippets: Optional[List[str]] = None,
    revision_intent: str = "",
    base_body: str = "",
    structure_overlay: str = "",
    fewshot_overlay: str = "",
) -> str:
    cap = clamp_max_chars(platform, max_chars)
    lo_band = max(1, int(cap * 0.85))
    label = _LANG.get(language, "Traditional Chinese (zh-TW)")
    lo, hi = HASHTAG_HINTS.get(platform, (3, 5))
    fact = (context_summary or topic_title or "").strip()[:1500]
    keep = _keep_block(preserve_snippets or [])
    intent = (revision_intent or "").strip()[:400]
    body_src = (base_body or "").strip()[:4000]
    tone = tone_card(style)
    rev_block = f"REVISION_INTENT: {intent}\n" if intent else ""
    base_block = f"BASE_BODY:\n{body_src}\n" if body_src else ""

    if part == "body":
        task = (
            "Fill body only. titles may be [\"\",\"\",\"\"] and hashtag_sets [[],[],[]].\n"
            "First outline 2–3 bullet points internally, then write body toward TARGET length."
        )
    elif part == "title":
        task = (
            "Fill titles (3) derived from BASE_BODY. body may be \"\" ; hashtag_sets empty."
        )
    elif part == "hashtags":
        task = (
            f"Fill hashtag_sets (3 arrays, each {lo}-{hi} tags) from BASE_BODY. "
            "titles/body may be empty."
        )
    elif part == "meta":
        task = (
            f"Fill titles (3) AND hashtag_sets (3 arrays, each {lo}-{hi} tags) from BASE_BODY. "
            "body must be \"\"."
        )
    else:
        task = (
            "Fill titles (3), body (1), and hashtag_sets (3 arrays). "
            "Body first toward TARGET; titles/hashtags must match the body."
        )

    return (
        "You write ONE social post pack as JSON only (no markdown).\n"
        f"Platform: {platform}.\n"
        f"Style id: {style}. Tone card (must be visibly different): {tone}\n"
        f"LANGUAGE: Write titles and body ONLY in {label}. Do not mix languages.\n"
        f"TARGET length for body ≈ {cap} Unicode characters "
        f"(stay within {lo_band}–{cap}; prefer approaching {cap}).\n"
        f"HARD CAP: body alone MUST be <= {cap} characters.\n"
        f"Hashtags per set: {lo} to {hi} (never invent unrelated brand lexicon).\n"
        f"Topic title: {topic_title.strip()[:300]}\n"
        f"FACTUAL SUMMARY (Truth Anchor):\n{fact}\n"
        f"{dna_overlay}\n"
        f"{structure_overlay}"
        f"{fewshot_overlay}"
        f"{keep}"
        f"{rev_block}"
        f"{base_block}"
        "CRITICAL GUARDRAILS:\n"
        "0. Never double-translate exemplars; write natively in LANGUAGE.\n"
        "1. FACT ANCHORING: Use only the topic and factual summary. Do not invent events.\n"
        "2. ANTI-POLLUTION: Style and optional voice overlay are tone-only. "
        "DO NOT force unrelated domain terms into a non-related topic.\n"
        "3. Keep snippets must appear verbatim; rewrite only the rest.\n"
        f"4. {task}\n"
        'JSON shape: {"titles":["","",""],"body":"","hashtag_sets":[[],[],[]]}\n'
    )
