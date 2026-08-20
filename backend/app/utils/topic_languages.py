"""Topic UI 語言表 + 標題腳本檢測（SoT：backend/config/topic_languages.json）。"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import FrozenSet, Optional, Tuple

logger = logging.getLogger(__name__)

_EMBEDDED_CONFIG = {
    "default": "zh-TW",
    "supported": ["zh-TW", "en", "ja"],
    "deepl_target": {"zh-TW": "ZH-HANT", "en": "EN-US", "ja": "JA"},
    "fallback_prefix": {
        "zh-TW": "[Fallback-ZH]",
        "en": "[Fallback-EN]",
        "ja": "[Fallback-JA]",
    },
    "script_profile": {"zh-TW": "han", "en": "latin", "ja": "japanese"},
}


def _config_candidates() -> Tuple[Path, ...]:
    here = Path(__file__).resolve()
    return (
        here.parents[2] / "config" / "topic_languages.json",
        here.parents[3] / "shared" / "topic_languages.json",
    )


@lru_cache(maxsize=1)
def _load_config() -> dict:
    for path in _config_candidates():
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    logger.warning(
        "topic_languages.json not found (checked %s); using embedded defaults",
        ", ".join(str(p) for p in _config_candidates()),
    )
    return dict(_EMBEDDED_CONFIG)


def supported_languages() -> Tuple[str, ...]:
    return tuple(_load_config().get("supported") or ("zh-TW", "en", "ja"))


def supported_language_set() -> FrozenSet[str]:
    return frozenset(supported_languages())


def default_language() -> str:
    return str(_load_config().get("default") or "zh-TW")


def normalize_topic_language(lang: Optional[str]) -> str:
    if not lang:
        return default_language()
    raw = str(lang).strip()
    low = raw.lower()
    if low in ("zh", "zh-tw", "zh-hk", "zh-hant"):
        return "zh-TW"
    if low.startswith("en"):
        return "en"
    if low in ("ja", "jp", "ja-jp"):
        return "ja"
    return raw if raw in supported_language_set() else default_language()


def preload_languages_for(display_lang: Optional[str]) -> Tuple[str, ...]:
    lang = normalize_topic_language(display_lang)
    return tuple(code for code in supported_languages() if code != lang)


def deepl_target_lang(lang: str) -> Optional[str]:
    targets = _load_config().get("deepl_target") or {}
    return targets.get(normalize_topic_language(lang))


def fallback_prefix(lang: str) -> str:
    prefixes = _load_config().get("fallback_prefix") or {}
    return prefixes.get(normalize_topic_language(lang), "[Fallback]")


def _script_profile(lang: str) -> str:
    profiles = _load_config().get("script_profile") or {}
    return profiles.get(normalize_topic_language(lang), "latin")


def _has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def _has_kana(text: str) -> bool:
    return any("\u3040" <= ch <= "\u309f" or "\u30a0" <= ch <= "\u30ff" for ch in text)


def _has_latin(text: str) -> bool:
    return any(ch.isascii() and ch.isalpha() for ch in text)


def _mostly_ascii_latin(text: str) -> bool:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return False
    latin = sum(1 for ch in letters if ch.isascii())
    return latin / len(letters) >= 0.8


def title_matches_display_language(title: str, display_lang: Optional[str]) -> bool:
    text = (title or "").strip()
    if not text:
        return True
    profile = _script_profile(normalize_topic_language(display_lang))
    if profile == "han":
        return _has_cjk(text)
    if profile == "latin":
        if _has_kana(text):
            return False
        if _has_cjk(text):
            return _mostly_ascii_latin(text)
        return _has_latin(text)
    if profile == "japanese":
        if _has_kana(text):
            return True
        # 無假名且含中文漢字，絕非有效日語標題
        if _has_cjk(text):
            return False
        # 僅短英文/數字品牌詞（如 NASA）允許無假名，長英文句子必須翻譯為日文
        return len(text) <= 15 and not (" " in text and len(text.split()) > 2)
    return True


def title_script_mismatch(title: str, display_lang: Optional[str]) -> bool:
    return not title_matches_display_language(title, display_lang)


def is_fallback_title(text: Optional[str]) -> bool:
    """DeepL 失敗字串前綴；不可當真譯文快取。"""
    t = (text or "").strip()
    return t.startswith("[Fallback-") or t.startswith("[Fallback]")


def usable_cached_title(
    text: Optional[str], target_lang: Optional[str] = None
) -> Optional[str]:
    t = (text or "").strip()
    if not t or is_fallback_title(t):
        return None
    if target_lang and not title_matches_display_language(t, target_lang):
        return None
    return t
