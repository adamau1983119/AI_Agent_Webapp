"""Detect title script → zh-TW / en / ja for honest display_language."""
from __future__ import annotations

import re

_HAN = re.compile(r"[\u4e00-\u9fff]")
_KANA = re.compile(r"[\u3040-\u30ff\uff66-\uff9d]")
_LATIN = re.compile(r"[A-Za-z]")
_OK = frozenset({"zh-TW", "en", "ja"})


def detect_title_language(title: str) -> str:
    """Latin brand names must not override real CJK/kana script."""
    text = (title or "").strip()
    if not text:
        return "en"
    han = len(_HAN.findall(text))
    kana = len(_KANA.findall(text))
    latin = len(_LATIN.findall(text))
    if kana >= 2:
        return "ja"
    if han >= 2:
        return "zh-TW"
    if latin >= 3:
        return "en"
    return "zh-TW" if han else "en"


def text_matches_lang(text: str, lang: str) -> bool:
    """Reject mis-tagged slots (e.g. Chinese stored under en)."""
    t = (text or "").strip()
    if not t:
        return False
    han = bool(_HAN.search(t))
    kana = bool(_KANA.search(t))
    latin = bool(_LATIN.search(t))
    if lang == "en":
        return not han and not kana and latin
    if lang == "ja":
        return kana or han
    if lang == "zh-TW":
        return han and not kana
    return False


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
