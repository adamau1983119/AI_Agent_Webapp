"""
共用 Schemas
包含分頁、錯誤回應等共用模型
"""
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """分頁參數"""
    page: int = Field(default=1, ge=1, description="頁碼")
    limit: int = Field(default=10, ge=1, le=100, description="每頁數量")


class PaginationResponse(BaseModel):
    """分頁回應"""
    page: int = Field(..., description="當前頁碼")
    limit: int = Field(..., description="每頁數量")
    total: int = Field(..., ge=0, description="總數量")
    total_pages: int = Field(..., ge=0, description="總頁數")

    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationResponse":
        """建立分頁回應"""
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )


class ErrorDetail(BaseModel):
    """錯誤詳情"""
    code: str = Field(..., description="錯誤碼")
    message: str = Field(..., description="錯誤訊息")
    details: Optional[Dict[str, Any]] = Field(None, description="錯誤詳情")


class ErrorResponse(BaseModel):
    """錯誤回應"""
    error: ErrorDetail = Field(..., description="錯誤資訊")

    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> "ErrorResponse":
        """建立錯誤回應"""
        return cls(
            error=ErrorDetail(
                code=code,
                message=message,
                details=details
            )
        )


class SuccessResponse(BaseModel):
    """成功回應"""
    message: str = Field(..., description="成功訊息")
    data: Optional[Dict[str, Any]] = Field(None, description="回應資料")
