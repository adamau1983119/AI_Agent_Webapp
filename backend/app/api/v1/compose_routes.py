"""POST /alter-ego/compose — public post pack. One-tap generate/charge/latest."""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.middleware.jwt_auth import get_current_user
from app.schemas.alter_ego import (
    ComposeRequest,
    ComposeResponse,
    OneTapChargeRequest,
    OneTapChargeResponse,
    OneTapGenerateRequest,
    OneTapGenerateResponse,
    OneTapLatestResponse,
)
from app.services.compose_service import compose_pack
from app.services.credit_ledger_service import InsufficientCreditsError
from app.services.one_tap_service import (
    charge_one_tap_pack,
    generate_one_tap_pack,
    get_latest_one_tap_pack,
)

router = APIRouter()


def _map_compose_value_error(exc: ValueError) -> HTTPException:
    code = str(exc)
    lowered = code.lower()
    if (
        "model_busy" in lowered
        or "too busy" in lowered
        or "service_unavailable" in lowered
        or "503" in code
    ):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="model_busy",
        )
    if "compose_fail" in code or "compose_json" in code:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="alter_ego_compose_parse_fail",
        )
    if any(
        token in code
        for token in ("Flash-only", "API Key", "pro_forbidden", "401", "403")
    ):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="alter_ego_llm_unavailable",
        )
    if code in ("invalid_pack_token", "pack_not_found"):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=code)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=code)


@router.post("/compose", response_model=ComposeResponse)
async def compose_copy(
    body: ComposeRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        return await compose_pack(current_user["id"], body)
    except InsufficientCreditsError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="insufficient_credits",
        ) from exc
    except ValueError as exc:
        raise _map_compose_value_error(exc) from exc


@router.post("/one-tap-pack/generate", response_model=OneTapGenerateResponse)
async def one_tap_generate(
    body: OneTapGenerateRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        return await generate_one_tap_pack(
            current_user["id"],
            language=body.language,
            topic_id=body.topic_id,
            topic_title=body.topic_title,
            context_summary=body.context_summary,
            domain=body.domain,
            surface=body.surface,
        )
    except InsufficientCreditsError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="insufficient_credits",
        ) from exc
    except ValueError as exc:
        raise _map_compose_value_error(exc) from exc


@router.post("/one-tap-pack/charge", response_model=OneTapChargeResponse)
async def one_tap_charge(
    body: OneTapChargeRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        return await charge_one_tap_pack(
            current_user["id"],
            pack_token=body.pack_token,
        )
    except InsufficientCreditsError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="insufficient_credits",
        ) from exc
    except ValueError as exc:
        raise _map_compose_value_error(exc) from exc


@router.get("/one-tap-pack/latest", response_model=OneTapLatestResponse)
async def one_tap_latest(
    topic_id: str = Query(..., min_length=1, max_length=64),
    current_user: dict = Depends(get_current_user),
):
    pack = await get_latest_one_tap_pack(current_user["id"], topic_id=topic_id)
    if not pack or not pack.pack_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pack_not_found")
    return pack
