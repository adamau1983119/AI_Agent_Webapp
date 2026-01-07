"""
圖片搜尋錯誤定義
"""
from typing import Optional


class ImageSearchError(Exception):
    """圖片搜尋錯誤"""
    
    def __init__(
        self,
        code: str,
        source: str,
        message: str,
        details: Optional[dict] = None
    ):
        """
        初始化錯誤
        
        Args:
            code: 錯誤代碼
            source: 圖片來源服務名稱
            message: 錯誤訊息
            details: 額外的錯誤詳情
        """
        self.code = code
        self.source = source
        self.message = message
        self.details = details or {}
        super().__init__(f"[{source}] {code}: {message}")
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "code": self.code,
            "source": self.source,
            "message": self.message,
            "details": self.details
        }


# 錯誤代碼定義
class ErrorCode:
    """錯誤代碼常量"""
    # 服務不可用（API Key 未設定）
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    
    # API 配額用盡
    RATE_LIMIT = "RATE_LIMIT"
    
    # 配置錯誤（API Key 或 Search Engine ID 無效）
    INVALID_CONFIG = "INVALID_CONFIG"
    INVALID_CONFIG_OR_PERMISSION = "INVALID_CONFIG_OR_PERMISSION"
    
    # 查詢無結果（正常情況）
    NO_RESULTS = "NO_RESULTS"
    
    # 上游服務錯誤（5xx）
    UPSTREAM_ERROR = "UPSTREAM_ERROR"
    
    # HTTP 錯誤（非 2xx）
    HTTP_ERROR = "HTTP_ERROR"
    
    # 請求超時
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    
    # 未知錯誤
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

