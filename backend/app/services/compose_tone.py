"""Style tone cards for compose (tone-only; no domain lexicon). MD-M2."""
from __future__ import annotations

STYLE_CARDS = {
    "professional": (
        "Short sentences; few/no emoji; conclusion first; calm authority."
    ),
    "casual": (
        "Conversational second-person; one light question; everyday words."
    ),
    "humorous": (
        "Allow one witty contrast line; never invent false facts for jokes."
    ),
    "storytelling": (
        "Scene → turn → close; concrete sensory detail from the facts only."
    ),
    "educational": (
        "Teach one clear takeaway; use 'key point' structure; list-friendly."
    ),
}


def tone_card(style: str) -> str:
    return STYLE_CARDS.get(style, STYLE_CARDS["casual"])
