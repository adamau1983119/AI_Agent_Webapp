"""Detect title script → zh-TW / en / ja for honest display_language."""
from __future__ import annotations

import re

_CJK = re.compile(r"[\u3000-\u9fff\u3040-\u30ff\uff66-\uff9d]")
_KANA = re.compile(r"[\u3040-\u30ff\uff66-\uff9d]")
_LATIN = re.compile(r"[A-Za-z]")
_OK = frozenset({"zh-TW", "en", "ja"})


def detect_title_language(title: str) -> str:
    text = (title or "").strip()
    if not text:
        return "en"
    cjk = len(_CJK.findall(text))
    kana = len(_KANA.findall(text))
    latin = len(_LATIN.findall(text))
    if kana >= 2 and kana >= cjk * 0.3:
        return "ja"
    if cjk >= 2 and cjk >= latin:
        return "zh-TW"
    if latin >= 3:
        return "en"
    return "zh-TW" if cjk else "en"


def resolve_stored_display_language(
    *,
    source_title: str,
    stored_title: str,
    requested_lang: str,
    translation_applied: bool,
) -> str:
    req = (requested_lang or "zh-TW").strip()
    if translation_applied and req in _OK:
        return req
    return detect_title_language(source_title or stored_title)
