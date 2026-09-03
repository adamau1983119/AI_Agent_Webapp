"""
Alter Ego API — extract / preview / rollback（AE-1a）
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.alter_ego_build import AE_PIPELINE_VERSION
from app.middleware.jwt_auth import get_current_user
from app.models.alter_ego_dna import DnaStatus
from app.schemas.alter_ego import (
    DnaStatusResponse,
    ExtractRequest,
    ExtractResponse,
    AdoptCopyRequest,
    AdoptCopyResponse,
    FeedbackRequest,
    FeedbackResponse,
    PreviewRequest,
    PreviewResponse,
    RollbackRequest,
    SkipResponse,
)
from app.api.v1.compose_routes import router as compose_router
from app.services.alter_ego_reextract import InsufficientCreditsError
from app.services.alter_ego_service import alter_ego_service
from app.services.repositories.alter_ego_repository import AlterEgoDnaRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alter-ego", tags=["alter-ego"])
_dna_repo = AlterEgoDnaRepository()


@router.post("/extract", response_model=ExtractResponse)
async def extract_dna(
    body: ExtractRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    從 1～3 篇範文 extract 文字 DNA（Flash-only + strict Pydantic）。
    """
    try:
        return await alter_ego_service.extract(current_user["id"], body)
    except InsufficientCreditsError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="insufficient_credits_for_reextract",
        ) from exc
    except ValueError as exc:
        code = str(exc)
        if code.startswith("extract_schema_fail"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="alter_ego_extract_schema_fail",
            ) from exc
        if any(
            token in code
            for token in (
                "Flash-only",
                "API Key",
                "DeepSeek API",
                "pro_forbidden",
                "401",
                "403",
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="alter_ego_llm_unavailable",
            ) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=code) from exc


@router.post("/preview", response_model=PreviewResponse)
async def preview_copy(
    body: PreviewRequest,
    response: Response,
    current_user: dict = Depends(get_current_user),
):
    """仿文預覽：Soul Flash + Shell Flash（PD-AE1-02）。"""
    try:
        result = await alter_ego_service.preview(current_user["id"], body)
        response.headers["X-Alter-Ego-Preview-Version"] = str(AE_PIPELINE_VERSION)
        if not (result.soul_text or "").strip():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="alter_ego_preview_missing_soul",
            )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/status", response_model=DnaStatusResponse)
async def get_dna_status(current_user: dict = Depends(get_current_user)):
    doc = await _dna_repo.get_by_user(current_user["id"])
    if not doc:
        return DnaStatusResponse(dna_status=DnaStatus.PENDING, has_dna=False)
    return DnaStatusResponse(
        dna_status=doc.get("dna_status", "pending"),
        current_dna_version_id=doc.get("current_dna_version_id"),
        has_dna=bool(doc.get("dna_json")),
    )


@router.post("/skip", response_model=SkipResponse)
async def skip_onboarding(current_user: dict = Depends(get_current_user)):
    """首登 Skip → dna_status=skipped（PD-AE1-F02）。"""
    await alter_ego_service.skip_onboarding(current_user["id"])
    return SkipResponse()


@router.post("/dna/rollback", response_model=ExtractResponse)
async def rollback_dna(
    body: RollbackRequest,
    current_user: dict = Depends(get_current_user),
):
    """還原至指定 snapshot（PD-AE1-07）。"""
    try:
        return await alter_ego_service.rollback(current_user["id"], body.snapshot_id)
    except ValueError as exc:
        if str(exc) == "snapshot_not_found":
            raise HTTPException(status_code=404, detail="snapshot_not_found") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/adopt-copy", response_model=AdoptCopyResponse)
async def adopt_copy_without_edit(
    body: AdoptCopyRequest,
    current_user: dict = Depends(get_current_user),
):
    """Post Kit 一鍵採用（CD-AE-C2 審計事件）。"""
    return await alter_ego_service.log_adopt_without_edit(current_user["id"], body)


@router.post("/feedback", response_model=FeedbackResponse)
async def post_feedback(
    body: FeedbackRequest,
    current_user: dict = Depends(get_current_user),
):
    """👍👎 → user_feedback_logs（PD-AE2-02）。"""
    await alter_ego_service.log_thumb_feedback(
        current_user["id"],
        action=body.action,
        topic_id=body.topic_id,
        comment=body.comment,
    )
    return FeedbackResponse()


router.include_router(compose_router)
