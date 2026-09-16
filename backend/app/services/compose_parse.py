"""Parse compose LLM JSON without language-specific header regex."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

from app.services.compose_caps import HASHTAG_HINTS


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


def _as_tags(item: Any, hi: int = 5) -> List[str]:
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
        if len(tags) >= hi:
            break
    return tags


def _pad3(items: List[Any], filler: Any) -> List[Any]:
    out = list(items[:3])
    while len(out) < 3:
        out.append(filler if not out else out[-1])
    return out


def _keyword_tags(fact: str, title: str, need: int) -> List[str]:
    blob = f"{title} {fact}"
    words = re.findall(r"[\w\u3040-\u30ff\u3400-\u9fff]{2,}", blob)
    out: List[str] = []
    for w in words:
        tag = "#" + w[:24]
        if tag not in out:
            out.append(tag)
        if len(out) >= need:
            break
    while len(out) < need:
        out.append(f"#tip{len(out)+1}")
    return out


def enforce_hashtag_bounds(
    sets: List[List[str]],
    platform: str,
    *,
    fact: str = "",
    title: str = "",
) -> List[List[str]]:
    lo, hi = HASHTAG_HINTS.get(platform, (3, 5))
    filler = _keyword_tags(fact, title, hi)
    fixed: List[List[str]] = []
    for s in sets:
        tags = list(s[:hi])
        i = 0
        while len(tags) < lo and i < len(filler):
            if filler[i] not in tags:
                tags.append(filler[i])
            i += 1
        fixed.append(tags[:hi])
    return _pad3(fixed, filler[: max(lo, 1)])[:3]


def body_char_count(body: str) -> int:
    return len(list(body or ""))


def normalize_pack(
    raw: Dict[str, Any],
    max_chars: int,
    *,
    platform: str = "instagram",
    fact: str = "",
    topic_title: str = "",
) -> Dict[str, Any]:
    titles = [str(x).strip() for x in (raw.get("titles") or []) if str(x).strip()]
    titles = _pad3(titles, "")[:3]
    body = str(raw.get("body") or "").strip()
    body = body[: max(max_chars, 1)]
    sets_raw = raw.get("hashtag_sets") or raw.get("hashtags") or []
    if isinstance(sets_raw, list) and sets_raw and not isinstance(sets_raw[0], list):
        sets_raw = [sets_raw]
    _, hi = HASHTAG_HINTS.get(platform, (3, 5))
    hashtag_sets = _pad3([_as_tags(s, hi) for s in sets_raw], [])[:3]
    hashtag_sets = enforce_hashtag_bounds(
        hashtag_sets, platform, fact=fact, title=topic_title or (titles[0] or "")
    )
    short = body_char_count(body) < int(max_chars * 0.7) if body else False
    return {
        "titles": titles,
        "body": body,
        "hashtag_sets": hashtag_sets,
        "short_body": short,
    }
