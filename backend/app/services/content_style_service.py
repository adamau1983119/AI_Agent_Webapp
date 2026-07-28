"""
ContentStyleService — Alter Ego 風格 context 唯一入口（PD-AE1-05）
"""
from typing import Literal, Optional, TypedDict

from app.models.alter_ego_dna import AlterEgoDnaJson
from app.services.repositories.alter_ego_repository import AlterEgoDnaRepository

RouteName = Literal["ae", "contents_generate", "assist"]


class StyleContext(TypedDict):
    route: str
    dna_status: str
    compressed_dna: str
    dna_version_id: Optional[str]
    legacy_style_hint: str


def _empty_context(route: RouteName, dna_status: str = "pending") -> StyleContext:
    return StyleContext(
        route=route,
        dna_status=dna_status,
        compressed_dna="",
        dna_version_id=None,
        legacy_style_hint="",
    )


class ContentStyleService:
    def __init__(self) -> None:
        self._dna_repo = AlterEgoDnaRepository()

    @staticmethod
    def compress_for_generate(dna: AlterEgoDnaJson) -> str:
        parts = [
            f"persona:{dna.voice_persona}",
            f"tone:{','.join(dna.tone_descriptors[:5])}",
            f"lexicon:{','.join(dna.lexicon[:8])}",
            f"rhythm:{dna.sentence_rhythm}",
            f"emoji:{dna.emoji_style}",
        ]
        if dna.avoid_list:
            parts.append(f"avoid:{','.join(dna.avoid_list[:5])}")
        return "; ".join(parts)[:500]

    async def _legacy_hint(self, user_id: str) -> str:
        try:
            from app.services.style_learning_service import style_learning_service

            profile = await style_learning_service.get_profile(user_id)
            if not profile:
                return ""
            tone = profile.get("tone") or {}
            preset = profile.get("preset_style", "casual")
            formal = tone.get("formal_score", 0.5)
            return f"預設風格 {preset}；正式度 {formal:.1f}"
        except Exception:
            return ""

    def _active_context(self, route: RouteName, doc: dict) -> StyleContext:
        dna = AlterEgoDnaJson.model_validate(doc["dna_json"])
        return StyleContext(
            route=route,
            dna_status=str(doc.get("dna_status", "active")),
            compressed_dna=self.compress_for_generate(dna),
            dna_version_id=doc.get("current_dna_version_id"),
            legacy_style_hint="",
        )

    async def resolve_for_route(self, user_id: str, route: RouteName) -> StyleContext:
        doc = await self._dna_repo.get_by_user(user_id)
        status = str((doc or {}).get("dna_status", "pending"))

        if route == "ae":
            if status != "active" or not doc or not doc.get("dna_json"):
                return _empty_context(route, status)
            return self._active_context(route, doc)

        if route == "contents_generate":
            if status == "active" and doc and doc.get("dna_json"):
                return self._active_context(route, doc)
            if status == "legacy_only":
                hint = await self._legacy_hint(user_id)
                return StyleContext(
                    route=route,
                    dna_status=status,
                    compressed_dna="",
                    dna_version_id=None,
                    legacy_style_hint=hint,
                )
            return _empty_context(route, status)

        return _empty_context(route, status)


content_style_service = ContentStyleService()
