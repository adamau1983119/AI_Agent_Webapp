"""Few-shot / structure blocks for compose_prompt (Mode A vs B)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def map_style_to_profile(style: str) -> str:
    if style in ("humorous", "storytelling", "casual"):
        return "hook_gossip"
    return "news_recap"


def map_max_chars_to_length(max_chars: int) -> str:
    return "short" if int(max_chars) <= 200 else "long"


def structure_block(slots: Optional[Dict[str, Any]], mode: str) -> str:
    if not slots:
        return ""
    lines = [
        f"prefix: {slots.get('prefix') or ''}",
        f"fact: {slots.get('fact') or ''}",
        f"quote: {slots.get('quote') or ''}",
        f"context: {slots.get('context') or ''}",
        f"ending: {slots.get('ending') or ''}",
    ]
    return (
        f"WRITE_PROFILE_STRUCTURE (Mode {mode}; pattern only, do NOT copy news facts):\n"
        + "\n".join(lines)
        + "\n"
    )


def fewshot_block(positive: List[Dict[str, Any]], negative: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for i, doc in enumerate(positive[:3], 1):
        body = (doc.get("body_text") or "")[:600]
        st = doc.get("structure") or {}
        parts.append(
            f"POSITIVE_EXEMPLAR_{i}:\nbody={body}\n"
            f"slots={st.get('prefix','')}|{st.get('quote','')}|{st.get('ending','')}\n"
        )
    for i, doc in enumerate(negative[:1], 1):
        body = (doc.get("body_text") or "")[:400]
        parts.append(f"NEGATIVE_EXEMPLAR_{i} (do NOT write like this):\n{body}\n")
    if not parts:
        return ""
    return "FEW_SHOT_EXEMPLARS (same language only; never translate):\n" + "".join(parts)
