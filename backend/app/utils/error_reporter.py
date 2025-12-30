"""
結構化錯誤回報器
提供統一的錯誤格式，方便前端顯示和日誌記錄
"""
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """錯誤類型枚舉"""
    CONFIGURATION_ERROR = "configuration_error"  # 配置錯誤（API Key 未設定等）
    GENERATION_ERROR = "generation_error"  # 生成錯誤（AI 服務失敗等）
    NETWORK_ERROR = "network_error"  # 網路錯誤（連接失敗等）
    VALIDATION_ERROR = "validation_error"  # 驗證錯誤（資料格式錯誤等）
    DATABASE_ERROR = "database_error"  # 資料庫錯誤
    SERVICE_UNAVAILABLE = "service_unavailable"  # 服務不可用
    UNKNOWN_ERROR = "unknown_error"  # 未知錯誤


class ErrorReporter:
    """錯誤回報器"""
    
    @staticmethod
    def create_error(
        error_type: ErrorType,
        message: str,
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False
    ) -> Dict[str, Any]:
        """
        創建結構化錯誤訊息
        
        Args:
            error_type: 錯誤類型
            message: 錯誤訊息
            service: 服務名稱（如 "qwen", "unsplash"）
            details: 詳細資訊
            recoverable: 是否可恢復
            
        Returns:
            結構化錯誤字典
        """
        error = {
            "type": error_type.value,
            "message": message,
            "recoverable": recoverable,
        }
        
        if service:
            error["service"] = service
        
        if details:
            error["details"] = details
        
        return error
    
    @staticmethod
    def create_configuration_error(
        message: str,
        service: Optional[str] = None,
        missing_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """創建配置錯誤"""
        details = {}
        if missing_key:
            details["missing_key"] = missing_key
        
        return ErrorReporter.create_error(
            error_type=ErrorType.CONFIGURATION_ERROR,
            message=message,
            service=service,
            details=details,
            recoverable=False
        )
    
    @staticmethod
    def create_generation_error(
        message: str,
        service: Optional[str] = None,
        retry_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """創建生成錯誤"""
        details = {}
        if retry_count is not None:
            details["retry_count"] = retry_count
        
        return ErrorReporter.create_error(
            error_type=ErrorType.GENERATION_ERROR,
            message=message,
            service=service,
            details=details,
            recoverable=True
        )
    
    @staticmethod
    def create_network_error(
        message: str,
        service: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> Dict[str, Any]:
        """創建網路錯誤"""
        details = {}
        if status_code:
            details["status_code"] = status_code
        
        return ErrorReporter.create_error(
            error_type=ErrorType.NETWORK_ERROR,
            message=message,
            service=service,
            details=details,
            recoverable=True
        )
    
    @staticmethod
    def log_error(error: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        """記錄錯誤到日誌"""
        error_msg = f"[{error['type']}] {error['message']}"
        if error.get('service'):
            error_msg += f" (服務: {error['service']})"
        
        if context:
            error_msg += f" | 上下文: {context}"
        
        logger.error(error_msg, extra={
            "error_type": error['type'],
            "error_message": error['message'],
            "service": error.get('service'),
            "context": context
        })
    
    @staticmethod
    def format_for_frontend(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        格式化錯誤訊息供前端顯示
        
        Args:
            errors: 錯誤列表
            
        Returns:
            格式化後的錯誤字典
        """
        if not errors:
            return {
                "has_errors": False,
                "errors": []
            }
        
        # 按錯誤類型分組
        by_type = {}
        for error in errors:
            error_type = error.get('type', 'unknown_error')
            if error_type not in by_type:
                by_type[error_type] = []
            by_type[error_type].append(error)
        
        # 構建用戶友好的訊息
        user_messages = []
        for error in errors:
            error_type = error.get('type', 'unknown_error')
            message = error.get('message', '未知錯誤')
            service = error.get('service')
            
            # 根據錯誤類型生成用戶友好的訊息
            if error_type == ErrorType.CONFIGURATION_ERROR.value:
                if service:
                    user_msg = f"{service.upper()} 服務配置錯誤：{message}"
                else:
                    user_msg = f"配置錯誤：{message}"
            elif error_type == ErrorType.GENERATION_ERROR.value:
                if service:
                    user_msg = f"{service.upper()} 服務生成失敗：{message}"
                else:
                    user_msg = f"生成失敗：{message}"
            elif error_type == ErrorType.NETWORK_ERROR.value:
                user_msg = f"網路連接失敗：{message}"
            else:
                user_msg = message
            
            user_messages.append({
                "type": error_type,
                "message": user_msg,
                "original_message": message,
                "service": service,
                "recoverable": error.get('recoverable', False),
                "details": error.get('details', {})
            })
        
        return {
            "has_errors": True,
            "errors": user_messages,
            "summary": {
                "total": len(errors),
                "by_type": {k: len(v) for k, v in by_type.items()},
                "recoverable_count": sum(1 for e in errors if e.get('recoverable', False))
            }
        }

