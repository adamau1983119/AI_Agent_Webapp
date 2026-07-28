"""
Alter Ego 週 batch：依 feedback 用 Flash patch DNA（PD-AE2-01）
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.models.alter_ego_dna import AlterEgoDnaJson
from app.services.ai.llm_factory import get_llm_client
from app.services.repositories.alter_ego_repository import AlterEgoDnaRepository
from app.services.repositories.user_feedback_repository import UserFeedbackRepository

logger = logging.getLogger(__name__)
_JSON_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _parse_json(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    m = _JSON_RE.search(text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


def _feedback_summary(rows: List[Dict[str, Any]]) -> str:
    lines = []
    for r in rows[:20]:
        lines.append(f"- {r.get('action')}: topic={r.get('topic_id') or '-'} {r.get('comment') or ''}")
    return "\n".join(lines) or "(no feedback)"


def _build_patch_prompt(dna: AlterEgoDnaJson, feedback_text: str) -> str:
    return (
        "You adjust writing-style DNA from user thumbs feedback. "
        "Return ONLY a full JSON object with the SAME keys as input DNA "
        "(lexicon, tone_descriptors, voice_persona, language_primary, exemplar_snippets, "
        "sentence_rhythm, emoji_style, opening_patterns, closing_patterns, hashtag_style, "
        "avoid_list, cta_style). Small conservative edits only.\n"
        f"Current DNA JSON:\n{json.dumps(dna.model_dump(), ensure_ascii=False)}\n"
        f"Recent feedback:\n{feedback_text}\n"
    )


class AlterEgoWeeklyBatchService:
    def __init__(self) -> None:
        self._dna = AlterEgoDnaRepository()
        self._feedback = UserFeedbackRepository()

    async def run_for_user(self, user_id: str) -> Optional[str]:
        doc = await self._dna.get_by_user(user_id)
        if not doc or doc.get("dna_status") != "active" or not doc.get("dna_json"):
            return None
        rows = await self._feedback.list_recent_for_user(user_id, days=7)
        if not rows:
            return None
        dna = AlterEgoDnaJson.model_validate(doc["dna_json"])
        client = get_llm_client("alter_ego")
        try:
            raw = await client.generate(_build_patch_prompt(dna, _feedback_summary(rows)))
            patched = AlterEgoDnaJson.model_validate(_parse_json(raw))
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            logger.warning(
                "[ALTER_EGO_WEEKLY_BATCH_FAIL] user_id=%s err=%s",
                user_id,
                type(exc).__name__,
            )
            return None
        version_id = await self._dna.upsert_active(
            user_id=user_id,
            dna_json=patched.model_dump(),
            reason="weekly_batch",
        )
        logger.info(
            "[ALTER_EGO_WEEKLY_BATCH_OK] user_id=%s version=%s feedback_n=%s",
            user_id,
            version_id[:12],
            len(rows),
        )
        return version_id

    async def run_all(self) -> Dict[str, Any]:
        user_ids = await self._feedback.distinct_user_ids_since(7)
        ok, fail = 0, 0
        for uid in user_ids:
            try:
                if await self.run_for_user(uid):
                    ok += 1
                else:
                    fail += 1
            except Exception as exc:
                fail += 1
                logger.error("[ALTER_EGO_WEEKLY_BATCH_ERR] user_id=%s err=%s", uid, exc)
        return {"users": len(user_ids), "patched": ok, "skipped_or_fail": fail}


alter_ego_weekly_batch = AlterEgoWeeklyBatchService()
