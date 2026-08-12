"""
Alter Ego API schemas
"""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.models.alter_ego_dna import AlterEgoDnaJson, DnaStatus, PrimaryLanguage


class ExtractRequest(BaseModel):
    exemplars: List[str] = Field(..., min_length=1, max_length=3)
    language: PrimaryLanguage = "zh-TW"


class ExtractResponse(BaseModel):
    dna_json: AlterEgoDnaJson
    dna_version_id: str
    dna_status: Literal["active"] = "active"


class PreviewRequest(BaseModel):
    platform: Literal["facebook", "threads", "x"]
    topic_hint: str = Field(default="", max_length=200)
    language: Optional[PrimaryLanguage] = Field(
        default=None,
        description="UI 語言覆寫（優先於 DNA language_primary）",
    )


class PreviewResponse(BaseModel):
    platform: str
    preview_text: str
    soul_text: str = ""
    shell_constraints: str


class DnaStatusResponse(BaseModel):
    dna_status: DnaStatus
    current_dna_version_id: Optional[str] = None
    has_dna: bool = False


class RollbackRequest(BaseModel):
    snapshot_id: str = Field(..., min_length=8, max_length=64)


class SkipResponse(BaseModel):
    dna_status: Literal["skipped"] = "skipped"


class AdoptCopyRequest(BaseModel):
    platform: Literal["facebook", "threads", "x"]
    topic_id: Optional[str] = Field(default=None, max_length=64)
    preview_text: str = Field(..., min_length=1, max_length=8000)


class AdoptCopyResponse(BaseModel):
    logged: bool = True
    event: Literal["adopted_without_edit"] = "adopted_without_edit"


class FeedbackRequest(BaseModel):
    action: Literal["like", "dislike"]
    topic_id: Optional[str] = Field(default=None, max_length=64)
    comment: Optional[str] = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    logged: bool = True
