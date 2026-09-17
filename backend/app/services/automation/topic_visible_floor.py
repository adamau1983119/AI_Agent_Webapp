"""Ensure each category keeps a visible floor after post-scan hide."""
from __future__ import annotations

from typing import Any, Dict, List

from app.services.automation.topic_post_scan import visible_floor


def apply_visible_floor(topics: List[Dict[str, Any]]) -> None:
    """If a category hid too many, unhide lowest-penalty cards until floor."""
    floor = visible_floor()
    by_cat: Dict[str, List[Dict[str, Any]]] = {}
    for t in topics:
        if not isinstance(t, dict):
            continue
        cat = str(t.get("category") or "unknown")
        by_cat.setdefault(cat, []).append(t)
    for cat, items in by_cat.items():
        visible = [t for t in items if not t.get("hidden")]
        if len(visible) >= floor:
            continue
        need = floor - len(visible)
        hidden = sorted(
            [t for t in items if t.get("hidden")],
            key=lambda x: int(x.get("sort_penalty") or 0),
        )
        for t in hidden[:need]:
            t["hidden"] = False
            t.pop("hidden_reason", None)
            # Keep penalty so noisy cards still sink in sort
            if int(t.get("sort_penalty") or 0) < 40:
                t["sort_penalty"] = 40
