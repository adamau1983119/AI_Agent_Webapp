"""Parse compose LLM JSON without language-specific header regex."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List


def extract_json_object(text: str) -> Dict[str, Any]:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
        raw = re.sub(r"\s*```$", "", raw)
    start = raw.find("{")
    if start < 0:
        raise ValueError("compose_json_missing")
    depth = 0
    for i, ch in enumerate(raw[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    data = json.loads(raw[start : i + 1])
                except json.JSONDecodeError as exc:
                    raise ValueError("compose_json_invalid") from exc
                if not isinstance(data, dict):
                    raise ValueError("compose_json_not_object")
                return data
    raise ValueError("compose_json_unbalanced")


def _as_tags(item: Any) -> List[str]:
    parts: List[str]
    if isinstance(item, list):
        parts = [str(x).strip() for x in item]
    elif isinstance(item, str):
        parts = re.split(r"[\s,]+", item)
    else:
        return []
    tags: List[str] = []
    for part in parts:
        token = part.strip().lstrip("#")
        if token and token not in tags:
            tags.append("#" + token)
        if len(tags) >= 8:
            break
    return tags


def _pad3(items: List[Any], filler: Any) -> List[Any]:
    out = list(items[:3])
    while len(out) < 3:
        out.append(filler if not out else out[-1])
    return out


def normalize_pack(raw: Dict[str, Any], max_chars: int) -> Dict[str, Any]:
    titles = [str(x).strip() for x in (raw.get("titles") or []) if str(x).strip()]
    titles = _pad3(titles, "")[:3]
    body = str(raw.get("body") or "").strip()
    sets_raw = raw.get("hashtag_sets") or raw.get("hashtags") or []
    if isinstance(sets_raw, list) and sets_raw and not isinstance(sets_raw[0], list):
        sets_raw = [sets_raw]
    hashtag_sets = _pad3([_as_tags(s) for s in sets_raw], [])[:3]
    return {
        "titles": titles,
        "body": body[: max(max_chars, 1)],
        "hashtag_sets": hashtag_sets,
    }
