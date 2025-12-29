"""
日誌工具
統一管理應用程式日誌
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from loguru import logger
import json


class InterceptHandler(logging.Handler):
    """攔截標準 logging 並轉發到 loguru"""
    
    def emit(self, record):
        # 取得對應的 loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # 找出調用者
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
):
    """設定日誌系統"""
    # 移除預設的 handler
    logger.remove()
    
    # 添加控制台輸出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
    # 添加檔案輸出（如果指定）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            encoding="utf-8",
        )
    
    # 攔截標準 logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 設定第三方庫的日誌級別
    for logger_name in ["uvicorn", "uvicorn.access", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]


def log_request(request, response_time: float = None):
    """記錄 API 請求"""
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "query_params": str(request.query_params),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("User-Agent", "unknown"),
    }
    
    if response_time:
        log_data["response_time"] = f"{response_time:.3f}s"
    
    logger.info(f"API Request: {json.dumps(log_data, ensure_ascii=False)}")


def log_error(error: Exception, context: dict = None):
    """記錄錯誤"""
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        error_data.update(context)
    
    logger.error(f"Error occurred: {json.dumps(error_data, ensure_ascii=False)}")


def log_security_event(event_type: str, details: dict):
    """記錄安全事件"""
    event_data = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        **details,
    }
    
    logger.warning(f"Security Event: {json.dumps(event_data, ensure_ascii=False)}")

