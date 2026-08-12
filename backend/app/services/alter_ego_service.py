"""
Alter Ego 服務 — extract / preview（Soul Flash + Shell Flash）
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.models.alter_ego_dna import AlterEgoDnaJson
from app.schemas.alter_ego import (
    AdoptCopyRequest,
    AdoptCopyResponse,
    ExtractRequest,
    ExtractResponse,
    PreviewRequest,
    PreviewResponse,
)
from app.services.ai.llm_factory import get_llm_client
from app.services.alter_ego_reextract import (
    charge_reextract,
    mark_free_reextract_used,
    plan_reextract,
)
from app.services.repositories.alter_ego_repository import AlterEgoDnaRepository
from app.services.repositories.audit_log_repository import AuditLogRepository
from app.services.repositories.user_feedback_repository import UserFeedbackRepository
from app.models.audit_log import Action, EntityType
from app.services.shells import get_shell_manager
from app.utils.topic_languages import normalize_topic_language, title_matches_display_language
from app.services.shells.shell_formatter import build_shell_output

logger = logging.getLogger(__name__)

_MAX_EXTRACT_RETRIES = 2
_MAX_PREVIEW_RETRIES = 2
_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_FENCE_RE = re.compile(r"^```[\w]*\n?|```$", re.MULTILINE)

_LANG_LABEL = {
    "zh-TW": "Traditional Chinese (繁體中文)",
    "en": "English",
    "ja": "Japanese (日本語)",
}


def _output_lang_label(lang: str) -> str:
    code = normalize_topic_language(lang)
    return _LANG_LABEL.get(code, code)


def _parse_llm_json(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    m = _JSON_BLOCK_RE.search(text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


def _strip_markdown_fence(text: str) -> str:
    return _FENCE_RE.sub("", (text or "").strip()).strip()


_ALLOWED_DNA_KEYS = {
    "lexicon",
    "tone_descriptors",
    "voice_persona",
    "language_primary",
    "exemplar_snippets",
    "sentence_rhythm",
    "emoji_style",
    "opening_patterns",
    "closing_patterns",
    "hashtag_style",
    "avoid_list",
    "cta_style",
}
_RHYTHM_OK = {"short_punchy", "mixed", "long_flowing"}
_EMOJI_OK = {"none", "sparse", "moderate"}
_LANG_MAP = {
    "zh-tw": "zh-TW",
    "zh_tw": "zh-TW",
    "zh": "zh-TW",
    "zh-hk": "zh-TW",
    "zh-cn": "zh-TW",
    "traditional chinese": "zh-TW",
    "chinese": "zh-TW",
    "en": "en",
    "en-us": "en",
    "english": "en",
    "ja": "ja",
    "jp": "ja",
    "japanese": "ja",
}


def _as_str_list(value: Any, limit: int) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = [p.strip() for p in re.split(r"[,，、\n]+", value) if p.strip()]
        return parts[:limit]
    if isinstance(value, list):
        out: List[str] = []
        for item in value:
            if item is None:
                continue
            s = str(item).strip()
            if s:
                out.append(s)
            if len(out) >= limit:
                break
        return out
    return [str(value).strip()][:limit] if str(value).strip() else []


def _coerce_dna_payload(
    data: Dict[str, Any],
    *,
    language: str,
    exemplars: List[str],
) -> Dict[str, Any]:
    """寬鬆整理 LLM JSON，降低 extract_schema_fail（extra／enum／空陣列）。"""
    raw = {k: v for k, v in (data or {}).items() if k in _ALLOWED_DNA_KEYS}
    lang_raw = str(raw.get("language_primary") or language or "zh-TW").strip()
    lang = _LANG_MAP.get(lang_raw.lower(), lang_raw if lang_raw in ("zh-TW", "en", "ja") else language)

    rhythm = str(raw.get("sentence_rhythm") or "mixed").strip()
    if rhythm not in _RHYTHM_OK:
        rhythm = "mixed"
    emoji = str(raw.get("emoji_style") or "sparse").strip()
    if emoji not in _EMOJI_OK:
        emoji = "sparse"

    lexicon = _as_str_list(raw.get("lexicon"), 20)
    tones = _as_str_list(raw.get("tone_descriptors"), 8)
    snippets = _as_str_list(raw.get("exemplar_snippets"), 3)
    persona = str(raw.get("voice_persona") or "").strip()[:120]

    if not lexicon:
        lexicon = ["分享", "觀察", "日常"] if lang == "zh-TW" else ["share", "note", "daily"]
    if not tones:
        tones = ["真實", "清晰"] if lang == "zh-TW" else ["authentic", "clear"]
    if not snippets:
        snippets = [e.strip()[:280] for e in exemplars if e.strip()][:3] or ["…"]
    if not persona:
        persona = "真誠分享觀點的創作者" if lang == "zh-TW" else "A creator who shares candid observations"

    return {
        "lexicon": lexicon,
        "tone_descriptors": tones,
        "voice_persona": persona,
        "language_primary": lang,
        "exemplar_snippets": snippets,
        "sentence_rhythm": rhythm,
        "emoji_style": emoji,
        "opening_patterns": _as_str_list(raw.get("opening_patterns"), 5),
        "closing_patterns": _as_str_list(raw.get("closing_patterns"), 5),
        "hashtag_style": str(raw.get("hashtag_style") or "")[:80],
        "avoid_list": _as_str_list(raw.get("avoid_list"), 10),
        "cta_style": str(raw.get("cta_style") or "")[:80],
    }


def _dna_block(dna: AlterEgoDnaJson) -> str:
    return (
        f"voice_persona: {dna.voice_persona}\n"
        f"lexicon: {', '.join(dna.lexicon)}\n"
        f"tone: {', '.join(dna.tone_descriptors)}\n"
        f"rhythm: {dna.sentence_rhythm}\n"
        f"emoji: {dna.emoji_style}\n"
        f"avoid: {', '.join(dna.avoid_list) or 'none'}\n"
        f"language: {dna.language_primary}"
    )


def _build_extract_prompt(exemplars: List[str], language: str) -> str:
    joined = "\n---\n".join(f"EXEMPLAR_{i+1}:\n{t[:8000]}" for i, t in enumerate(exemplars))
    schema_hint = """
Return ONLY a JSON object with these keys (no extra keys):
{
  "lexicon": ["string", ...],
  "tone_descriptors": ["string", ...],
  "voice_persona": "string",
  "language_primary": "zh-TW" | "en" | "ja",
  "exemplar_snippets": ["short excerpt up to 280 chars each", ...],
  "sentence_rhythm": "short_punchy" | "mixed" | "long_flowing",
  "emoji_style": "none" | "sparse" | "moderate",
  "opening_patterns": [],
  "closing_patterns": [],
  "hashtag_style": "",
  "avoid_list": [],
  "cta_style": ""
}
"""
    return (
        "You are a writing-style analyst. Extract structured voice DNA from the exemplar posts.\n"
        f"Target language_primary: {language}\n"
        f"{schema_hint}\n"
        f"Exemplars:\n{joined}\n"
        "exemplar_snippets must be SHORT excerpts (not full text). Return only JSON."
    )


def _build_soul_prompt(dna: AlterEgoDnaJson, topic_hint: str, output_lang: str) -> str:
    topic = topic_hint or "分享一則生活近況"
    label = _output_lang_label(output_lang)
    return (
        "You are the author's digital voice (Soul layer). Write a SHORT platform-neutral post draft.\n"
        "Match the DNA voice exactly. No hashtags. No platform-specific formatting.\n"
        f"Topic: {topic}\n"
        f"DNA:\n{_dna_block(dna)}\n"
        f"IMPORTANT: Write the entire post ONLY in {label}. Do not mix languages.\n"
        "Return only the post body text."
    )


def _build_shell_prompt(
    dna: AlterEgoDnaJson,
    soul_text: str,
    platform: str,
    constraints: str,
    output_lang: str,
) -> str:
    return (
        f"You are the Shell layer for {platform}. Format the Soul draft for this platform.\n"
        f"Platform rules:\n{constraints}\n"
        f"DNA voice (preserve tone): {_dna_block(dna)}\n"
        f"Hashtag style hint: {dna.hashtag_style or 'use relevant tags from lexicon'}\n"
        f"Soul draft:\n{soul_text}\n"
        f"IMPORTANT: Return ONLY the final copy-ready post in {_output_lang_label(output_lang)}. "
        "Do not mix languages. Include hashtags per platform rules."
    )


def _hashtags_from_dna(dna: AlterEgoDnaJson) -> List[str]:
    tags = list(dna.lexicon[:6])
    if dna.hashtag_style:
        for part in re.split(r"[,，\s#]+", dna.hashtag_style):
            part = part.strip().lstrip("#")
            if part and part not in tags:
                tags.append(part)
    return tags[:6]


def _finalize_preview_text(shell_llm_text: str, soul_text: str, platform: str, dna: AlterEgoDnaJson) -> str:
    """Shell LLM 輸出 + YAML 約束後處理（確保平台硬限制）。"""
    cleaned = _strip_markdown_fence(shell_llm_text)
    if not cleaned:
        cleaned = soul_text
    tags = _hashtags_from_dna(dna)
    formatted = build_shell_output(cleaned, platform, tags)
    if platform == "facebook":
        return formatted.get("copy_text") or cleaned
    return formatted.get("post") or formatted.get("copy_text") or cleaned


class AlterEgoService:
    def __init__(self) -> None:
        self._dna_repo = AlterEgoDnaRepository()
        self._audit = AuditLogRepository()
        self._feedback = UserFeedbackRepository()

    async def extract(self, user_id: str, request: ExtractRequest) -> ExtractResponse:
        exemplars = [e.strip() for e in request.exemplars if e and e.strip()]
        if not exemplars:
            raise ValueError("exemplars_required")

        existing = await self._dna_repo.get_by_user(user_id)
        gate_note = plan_reextract(existing)
        if gate_note == "charge_reextract":
            # 先確認餘額；真正扣點在成功後
            from app.services.credit_ledger_service import credit_ledger_service

            bal = await credit_ledger_service.ensure_initial_balance(user_id)
            if bal < 1:
                from app.services.alter_ego_reextract import InsufficientCreditsError

                raise InsufficientCreditsError(f"balance={bal}, need=1")

        client = get_llm_client("alter_ego")
        prompt = _build_extract_prompt(exemplars, request.language)
        last_err: Optional[Exception] = None

        for attempt in range(_MAX_EXTRACT_RETRIES + 1):
            try:
                raw = await client.generate(prompt)
                data = _parse_llm_json(raw)
                data = _coerce_dna_payload(
                    data, language=request.language, exemplars=exemplars
                )
                dna = AlterEgoDnaJson.model_validate(data)
                version_id = await self._dna_repo.upsert_active(
                    user_id=user_id,
                    dna_json=dna.model_dump(),
                    reason="extract",
                )
                if gate_note == "free_reextract":
                    await mark_free_reextract_used(self._dna_repo, user_id)
                elif gate_note == "charge_reextract" and existing:
                    await charge_reextract(user_id, existing)
                logger.info(
                    "[ALTER_EGO_EXTRACT_OK] user_id=%s gate=%s version=%s",
                    user_id,
                    gate_note,
                    version_id[:12],
                )
                return ExtractResponse(
                    dna_json=dna,
                    dna_version_id=version_id,
                )
            except (json.JSONDecodeError, ValidationError) as exc:
                last_err = exc
                detail = str(exc)
                if isinstance(exc, ValidationError):
                    detail = exc.errors()[:3]
                logger.warning(
                    "[ALTER_EGO_DNA_EXTRACT_FAIL] user_id=%s attempt=%s err=%s detail=%s",
                    user_id,
                    attempt + 1,
                    type(exc).__name__,
                    detail,
                )
            except ValueError as exc:
                # API Key／上游失敗：勿偽裝成 schema fail
                msg = str(exc)
                if any(
                    token in msg
                    for token in (
                        "API Key",
                        "DeepSeek API",
                        "Flash-only",
                        "pro_forbidden",
                        "401",
                        "403",
                        "Authentication",
                    )
                ):
                    raise
                last_err = exc
                logger.warning(
                    "[ALTER_EGO_DNA_EXTRACT_FAIL] user_id=%s attempt=%s err=ValueError detail=%s",
                    user_id,
                    attempt + 1,
                    msg,
                )

        raise ValueError(f"extract_schema_fail:{type(last_err).__name__}")

    async def preview(self, user_id: str, request: PreviewRequest) -> PreviewResponse:
        """Soul Flash + Shell Flash → 平台仿文（PD-AE1-02）。"""
        doc = await self._dna_repo.get_by_user(user_id)
        if not doc or not doc.get("dna_json"):
            raise ValueError("dna_not_found")

        dna = AlterEgoDnaJson.model_validate(doc["dna_json"])
        output_lang = normalize_topic_language(request.language or dna.language_primary)
        client = get_llm_client("alter_ego")
        shell = get_shell_manager()
        constraints = shell.build_prompt_constraints(request.platform)
        topic = (request.topic_hint or "分享一則生活近況").strip()

        soul_text = ""
        last_soul_err: Optional[Exception] = None
        for attempt in range(_MAX_PREVIEW_RETRIES + 1):
            try:
                soul_raw = await client.generate(_build_soul_prompt(dna, topic, output_lang))
                soul_text = _strip_markdown_fence(soul_raw)
                if len(soul_text) < 10:
                    raise ValueError("soul_too_short")
                if not title_matches_display_language(soul_text, output_lang):
                    raise ValueError("soul_lang_mismatch")
                break
            except ValueError as exc:
                last_soul_err = exc
                if str(exc) == "alter_ego_namespace_pro_forbidden":
                    raise
                logger.warning(
                    "[ALTER_EGO_SOUL_PREVIEW_FAIL] user_id=%s platform=%s attempt=%s",
                    user_id,
                    request.platform,
                    attempt + 1,
                )
        else:
            raise ValueError(f"preview_soul_fail:{type(last_soul_err).__name__}")

        preview_text = soul_text
        last_shell_err: Optional[Exception] = None
        for attempt in range(_MAX_PREVIEW_RETRIES + 1):
            try:
                shell_raw = await client.generate(
                    _build_shell_prompt(dna, soul_text, request.platform, constraints, output_lang)
                )
                preview_text = _finalize_preview_text(
                    shell_raw, soul_text, request.platform, dna
                )
                if len(preview_text) < 10:
                    raise ValueError("shell_too_short")
                if not title_matches_display_language(preview_text, output_lang):
                    raise ValueError("shell_lang_mismatch")
                break
            except ValueError as exc:
                last_shell_err = exc
                if str(exc) == "alter_ego_namespace_pro_forbidden":
                    raise
                logger.warning(
                    "[ALTER_EGO_SHELL_PREVIEW_FAIL] user_id=%s platform=%s attempt=%s",
                    user_id,
                    request.platform,
                    attempt + 1,
                )
        else:
            preview_text = _finalize_preview_text("", soul_text, request.platform, dna)
            if not title_matches_display_language(preview_text, output_lang):
                raise ValueError(f"preview_lang_mismatch:{output_lang}")
            logger.warning(
                "[ALTER_EGO_SHELL_PREVIEW_FAIL] user_id=%s fallback=formatter",
                user_id,
            )

        return PreviewResponse(
            platform=request.platform,
            preview_text=preview_text,
            soul_text=soul_text,
            shell_constraints=constraints,
        )

    async def rollback(self, user_id: str, snapshot_id: str) -> ExtractResponse:
        version_id = await self._dna_repo.rollback_to_snapshot(user_id, snapshot_id.strip())
        doc = await self._dna_repo.get_by_user(user_id)
        if not doc or not doc.get("dna_json"):
            raise ValueError("rollback_failed")
        dna = AlterEgoDnaJson.model_validate(doc["dna_json"])
        logger.info(
            "[ALTER_EGO_DNA_ROLLBACK] user_id=%s snapshot_id=%s new_version=%s",
            user_id,
            snapshot_id[:12],
            version_id[:12],
        )
        return ExtractResponse(dna_json=dna, dna_version_id=version_id)

    async def skip_onboarding(self, user_id: str) -> None:
        await self._dna_repo.upsert_skipped(user_id)
        logger.info("[ALTER_EGO_ONBOARDING_SKIP] user_id=%s", user_id)

    async def log_adopt_without_edit(self, user_id: str, body: AdoptCopyRequest) -> AdoptCopyResponse:
        await self._audit.create_log(
            action=Action.UPDATE,
            entity_type=EntityType.CONTENT,
            topic_id=body.topic_id,
            user=user_id,
            changes={
                "event": "adopted_without_edit",
                "platform": body.platform,
                "preview_text_len": len(body.preview_text),
            },
        )
        doc = await self._dna_repo.get_by_user(user_id)
        await self._feedback.insert_feedback(
            user_id=user_id,
            action="adopted_without_edit",
            topic_id=body.topic_id,
            dna_version_id=(doc or {}).get("current_dna_version_id"),
            meta={"platform": body.platform},
        )
        logger.info(
            "[ALTER_EGO_ADOPT_WITHOUT_EDIT] user_id=%s platform=%s topic_id=%s",
            user_id,
            body.platform,
            body.topic_id or "-",
        )
        return AdoptCopyResponse()

    async def log_thumb_feedback(
        self,
        user_id: str,
        *,
        action: str,
        topic_id: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        doc = await self._dna_repo.get_by_user(user_id)
        await self._feedback.insert_feedback(
            user_id=user_id,
            action=action,
            topic_id=topic_id,
            dna_version_id=(doc or {}).get("current_dna_version_id"),
            comment=comment,
        )
        logger.info(
            "[ALTER_EGO_FEEDBACK] user_id=%s action=%s topic_id=%s",
            user_id,
            action,
            topic_id or "-",
        )


alter_ego_service = AlterEgoService()
