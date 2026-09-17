"""Ops Style Trainer API — allowlist only; no guest credits."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.jwt_auth import get_current_user
from app.schemas.ops_trainer import (
    AnalyzeRequest,
    AnalyzeResponse,
    ConfirmRequest,
    ConfirmResponse,
    CoverageResponse,
    CoverageLang,
)
from app.services.ops_trainer_access import require_trainer, user_may_access_trainer
from app.services.ops_trainer_analyze import analyze_input
from app.services import ops_trainer_store as store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ops/trainer", tags=["ops-trainer"])


@router.get("/access")
async def trainer_access(current_user: dict = Depends(get_current_user)):
    return {"allowed": user_may_access_trainer(current_user)}


@router.get("/coverage", response_model=CoverageResponse)
async def trainer_coverage(current_user: dict = Depends(get_current_user)):
    require_trainer(current_user)
    rows = await store.coverage_all()
    return CoverageResponse(
        languages=[CoverageLang(**r) for r in rows],
        note="mode_a_until_full",
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def trainer_analyze(
    body: AnalyzeRequest,
    current_user: dict = Depends(get_current_user),
):
    require_trainer(current_user)
    try:
        return await analyze_input(
            text=body.text or "",
            image_data_url=body.image_data_url,
            source_url=body.source_url,
            language_hint=body.language_hint,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("ops_trainer analyze fail")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="analyze_upstream_fail",
        ) from exc


@router.post("/confirm", response_model=ConfirmResponse)
async def trainer_confirm(
    body: ConfirmRequest,
    current_user: dict = Depends(get_current_user),
):
    require_trainer(current_user)
    doc = {
        "language": body.language,
        "domain": body.domain,
        "length_bucket": body.length_bucket,
        "write_profile": body.write_profile,
        "ref_type": body.ref_type,
        "structure": body.structure.model_dump(),
        "body_text": body.body_text,
        "source_url": body.source_url,
        "has_image": bool(body.image_data_url),
        "created_by": current_user.get("id"),
        "created_by_email": current_user.get("email"),
    }
    # Do not store huge base64 in Mongo by default — keep flag only
    eid = await store.insert_published(doc)
    return ConfirmResponse(id=eid, status="published")
