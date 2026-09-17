"""Pydantic schemas for Ops Style Trainer."""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Domain = Literal["fashion", "food", "trend"]
LengthBucket = Literal["short", "long"]
WriteProfile = Literal["news_recap", "hook_gossip"]
RefType = Literal["positive", "negative"]
Lang = Literal["zh-TW", "en", "ja"]


class StructureSlots(BaseModel):
    prefix: str = ""
    fact: str = ""
    quote: str = ""
    context: str = ""
    ending: str = ""


class AnalyzeRequest(BaseModel):
    text: str = Field(default="", max_length=12000)
    image_data_url: Optional[str] = Field(default=None, max_length=8_000_000)
    source_url: Optional[str] = Field(default=None, max_length=2000)
    language_hint: Optional[Lang] = None


class AnalyzeResponse(BaseModel):
    language: Lang = "zh-TW"
    domain: Domain = "trend"
    length_bucket: LengthBucket = "short"
    write_profile: WriteProfile = "news_recap"
    ref_type: RefType = "positive"
    structure: StructureSlots = Field(default_factory=StructureSlots)
    body_text: str = ""
    notes: str = ""


class ConfirmRequest(BaseModel):
    language: Lang
    domain: Domain
    length_bucket: LengthBucket
    write_profile: WriteProfile
    ref_type: RefType = "positive"
    structure: StructureSlots
    body_text: str = Field(default="", max_length=12000)
    image_data_url: Optional[str] = Field(default=None, max_length=8_000_000)
    source_url: Optional[str] = Field(default=None, max_length=2000)
    publish: bool = True


class ConfirmResponse(BaseModel):
    id: str
    status: Literal["published"] = "published"


class CoverageLang(BaseModel):
    language: Lang
    filled: int
    target: int = 18
    mode: Literal["A", "B"]


class CoverageResponse(BaseModel):
    languages: List[CoverageLang]
    note: str = "mode_a_until_full"
