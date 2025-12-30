"""
重試包裝器
為 AI 服務和圖片服務提供重試機制（exponential backoff）
"""
import asyncio
import logging
from typing import Callable, TypeVar, Optional, List
from functools import wraps
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """重試配置"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        retryable_exceptions: Optional[List[type]] = None
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions or [Exception]


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    service_name: Optional[str] = None
):
    """
    重試裝飾器（exponential backoff）
    
    Args:
        config: 重試配置
        service_name: 服務名稱（用於日誌）
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            service = service_name or func.__name__
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # 檢查是否為可重試的異常
                    if not any(isinstance(e, exc_type) for exc_type in config.retryable_exceptions):
                        logger.warning(
                            f"{service} 發生不可重試的錯誤: {e}",
                            extra={"service": service, "attempt": attempt, "error": str(e)}
                        )
                        raise
                    
                    # 如果是最後一次嘗試，直接拋出異常
                    if attempt >= config.max_attempts:
                        logger.error(
                            f"{service} 重試 {attempt} 次後仍然失敗: {e}",
                            extra={"service": service, "attempt": attempt, "error": str(e)}
                        )
                        raise
                    
                    # 計算延遲時間（exponential backoff）
                    delay = min(
                        config.initial_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )
                    
                    logger.warning(
                        f"{service} 第 {attempt} 次嘗試失敗，{delay:.2f} 秒後重試: {e}",
                        extra={
                            "service": service,
                            "attempt": attempt,
                            "max_attempts": config.max_attempts,
                            "delay": delay,
                            "error": str(e)
                        }
                    )
                    
                    await asyncio.sleep(delay)
            
            # 理論上不會到達這裡
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


class RetryableService:
    """可重試的服務基類"""
    
    def __init__(
        self,
        service_name: str,
        retry_config: Optional[RetryConfig] = None
    ):
        self.service_name = service_name
        self.retry_config = retry_config or RetryConfig()
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> T:
        """
        執行函數並自動重試
        
        Args:
            func: 要執行的函數
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            函數返回值
        """
        last_exception = None
        
        for attempt in range(1, self.retry_config.max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # 檢查是否為可重試的異常
                if not any(isinstance(e, exc_type) for exc_type in self.retry_config.retryable_exceptions):
                    logger.warning(
                        f"{self.service_name} 發生不可重試的錯誤: {e}",
                        extra={"service": self.service_name, "attempt": attempt}
                    )
                    raise
                
                # 如果是最後一次嘗試，直接拋出異常
                if attempt >= self.retry_config.max_attempts:
                    logger.error(
                        f"{self.service_name} 重試 {attempt} 次後仍然失敗: {e}",
                        extra={"service": self.service_name, "attempt": attempt}
                    )
                    raise
                
                # 計算延遲時間
                delay = min(
                    self.retry_config.initial_delay * (self.retry_config.exponential_base ** (attempt - 1)),
                    self.retry_config.max_delay
                )
                
                logger.warning(
                    f"{self.service_name} 第 {attempt} 次嘗試失敗，{delay:.2f} 秒後重試",
                    extra={
                        "service": self.service_name,
                        "attempt": attempt,
                        "delay": delay
                    }
                )
                
                await asyncio.sleep(delay)
        
        if last_exception:
            raise last_exception

