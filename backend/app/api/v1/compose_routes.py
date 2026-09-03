"""POST /alter-ego/compose — public post pack (1 credit). Old preview unchanged."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.jwt_auth import get_current_user
from app.schemas.alter_ego import ComposeRequest, ComposeResponse
from app.services.compose_service import compose_pack
from app.services.credit_ledger_service import InsufficientCreditsError

router = APIRouter()


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
        code = str(exc)
        if "compose_fail" in code or "compose_json" in code:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="alter_ego_compose_parse_fail",
            ) from exc
        if any(
            token in code
            for token in ("Flash-only", "API Key", "pro_forbidden", "401", "403")
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="alter_ego_llm_unavailable",
            ) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=code) from exc
