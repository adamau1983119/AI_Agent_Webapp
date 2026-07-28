"""
Alter Ego Shell 格式化（純函數 · YAML 約束 · AE-1b）
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.services.shells.shell_manager import ShellRule, get_shell_manager

_HASHTAG_RE = re.compile(r"#(\w+)")


def _normalize_tags(tags: Optional[List[str]]) -> List[str]:
    out: List[str] = []
    for t in tags or []:
        t = (t or "").strip().lstrip("#")
        if t and t not in out:
            out.append(t)
    return out


def build_shell_output(
    soul_text: str,
    platform: str,
    hashtags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    將 Soul 正文套用平台 YAML 約束（無 LLM；供 Shell 層與驗收腳本）。
    """
    rule = get_shell_manager().load(platform)
    c = rule.constraints
    body = (soul_text or "").strip()
    tags = _normalize_tags(hashtags)

    if platform == "facebook":
        lead = body.split("\n\n")[0].strip()
        if c.max_lead_chars:
            lead = lead[: c.max_lead_chars]
        use_tags = tags[: c.hashtag_max]
        if len(use_tags) < c.hashtag_min:
            use_tags = (tags + [f"tag{i}" for i in range(1, 8)])[: c.hashtag_max]
            use_tags = use_tags[: max(c.hashtag_min, len(use_tags))]
        tag_line = " ".join(f"#{t}" for t in use_tags)
        return {
            "platform": platform,
            "lead": lead,
            "body": body,
            "hashtags": use_tags,
            "hashtag_line": tag_line,
            "lead_len": len(lead),
            "copy_text": "\n\n".join(p for p in [lead, body, tag_line] if p),
        }

    if platform == "threads":
        use_tags = tags[: c.hashtag_max]
        tag_line = " ".join(f"#{t}" for t in use_tags) if use_tags else ""
        post = body if not tag_line else f"{body}\n\n{tag_line}"
        return {
            "platform": platform,
            "post": post,
            "hashtags": use_tags,
            "hashtag_count": len(use_tags),
            "post_len": len(post),
        }

    if platform == "x":
        use_tags = tags[: c.hashtag_max]
        tag_line = " ".join(f"#{t}" for t in use_tags)
        post = body if not tag_line else f"{body} {tag_line}"
        max_chars = c.max_post_chars or 280
        if len(post) > max_chars:
            post = post[: max_chars - 1] + "…"
        return {
            "platform": platform,
            "post": post,
            "hashtags": use_tags,
            "post_len": len(post),
            "max_post_chars": max_chars,
            "is_thread": c.allow_thread and len(body) > max_chars,
        }

    raise ValueError(f"unsupported_platform:{platform}")


def count_hashtags(text: str) -> int:
    return len(_HASHTAG_RE.findall(text or ""))
