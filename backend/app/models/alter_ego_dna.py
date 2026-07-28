"""
Alter Ego — 扁平 DNA Pydantic（AE-0 SoT: docs/ALTER_EGO_SPEC.md 頻道區塊 2）
"""
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DnaStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SKIPPED = "skipped"
    LEGACY_ONLY = "legacy_only"


SentenceRhythm = Literal["short_punchy", "mixed", "long_flowing"]
EmojiStyle = Literal["none", "sparse", "moderate"]
PrimaryLanguage = Literal["zh-TW", "en", "ja"]


class AlterEgoDnaJson(BaseModel):
    """從範文 extract 的結構化文字 DNA（扁平、strict）。"""

    model_config = ConfigDict(extra="forbid")

    lexicon: List[str] = Field(..., min_length=1, max_length=20)
    tone_descriptors: List[str] = Field(..., min_length=1, max_length=8)
    voice_persona: str = Field(..., min_length=1, max_length=120)
    language_primary: PrimaryLanguage
    exemplar_snippets: List[str] = Field(..., min_length=1, max_length=3)

    sentence_rhythm: SentenceRhythm = "mixed"
    emoji_style: EmojiStyle = "sparse"
    opening_patterns: List[str] = Field(default_factory=list, max_length=5)
    closing_patterns: List[str] = Field(default_factory=list, max_length=5)
    hashtag_style: str = Field(default="", max_length=80)
    avoid_list: List[str] = Field(default_factory=list, max_length=10)
    cta_style: str = Field(default="", max_length=80)

    @field_validator("lexicon")
    @classmethod
    def _clip_lexicon(cls, v: List[str]) -> List[str]:
        return [s.strip()[:40] for s in v if s and s.strip()]

    @field_validator("tone_descriptors", "opening_patterns", "closing_patterns", "avoid_list")
    @classmethod
    def _strip_strings(cls, v: List[str]) -> List[str]:
        return [s.strip() for s in v if s and s.strip()]

    @field_validator("exemplar_snippets")
    @classmethod
    def _clip_snippets(cls, v: List[str]) -> List[str]:
        return [s.strip()[:280] for s in v if s and s.strip()]
