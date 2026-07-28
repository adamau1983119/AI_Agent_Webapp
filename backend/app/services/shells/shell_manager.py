"""Alter Ego Shell YAML 載入與規則介面（AE-0 · docs/ALTER_EGO_SPEC.md 頻道區塊 5）。"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

_SHELLS_DIR = Path(__file__).resolve().parents[2] / "config" / "shells"


class ShellConstraints(BaseModel):
    max_lead_chars: Optional[int] = None
    hashtag_min: int = 0
    hashtag_max: int = 6
    max_body_chars: Optional[int] = None
    max_post_chars: Optional[int] = None
    allow_thread: bool = False
    max_thread_posts: Optional[int] = None


class ShellFormat(BaseModel):
    sections: List[str] = Field(default_factory=list)
    hashtag_prefix: str = "#"


class ShellRule(BaseModel):
    platform: str
    display_name: str
    version: int = 1
    constraints: ShellConstraints = Field(default_factory=ShellConstraints)
    format: ShellFormat = Field(default_factory=ShellFormat)
    prompt_hints: Dict[str, str] = Field(default_factory=dict)
    visual_prompt: bool = False


class ShellManager:
    """從 `backend/app/config/shells/*.yaml` 載入平台 Shell 規則。"""

    def __init__(self, shells_dir: Optional[Path] = None) -> None:
        self._dir = shells_dir or _SHELLS_DIR

    def list_platforms(self) -> List[str]:
        if not self._dir.is_dir():
            return []
        return sorted(p.stem for p in self._dir.glob("*.yaml"))

    def load(self, platform: str) -> ShellRule:
        path = self._dir / f"{platform}.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"shell_not_found:{platform}")
        raw: Dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return ShellRule.model_validate(raw)

    def build_prompt_constraints(self, platform: str) -> str:
        rule = self.load(platform)
        c = rule.constraints
        lines = [
            f"Platform: {rule.display_name} ({rule.platform})",
        ]
        if c.max_lead_chars is not None:
            lines.append(f"- Lead paragraph max {c.max_lead_chars} characters.")
        if c.max_post_chars is not None:
            lines.append(f"- Single post max {c.max_post_chars} characters.")
        if c.max_body_chars is not None:
            lines.append(f"- Body max {c.max_body_chars} characters.")
        lines.append(f"- Hashtags: {c.hashtag_min} to {c.hashtag_max}.")
        if c.allow_thread:
            max_t = c.max_thread_posts or "N"
            lines.append(f"- Thread allowed (max {max_t} posts).")
        for section, hint in rule.prompt_hints.items():
            lines.append(f"- [{section}] {hint}")
        return "\n".join(lines)


@lru_cache(maxsize=1)
def get_shell_manager() -> ShellManager:
    return ShellManager()
