"""
靈感策劃成本監控服務
根據 v5.0 靈感策劃技術設計報告實現

功能：
1. 成本監控（每日/每月 Token 限制）
2. 成本警告機制（80% 閾值警告）
3. 成本計算（根據 AI 服務）
4. 成本記錄（保存到資料庫）
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.repositories.base_repository import BaseRepository
from app.database import get_database
import logging

logger = logging.getLogger(__name__)


# AI 服務成本配置（每 1M Token 的價格，USD）
AI_SERVICE_COSTS = {
    "deepseek": {
        "input": 0.14,  # $0.14 per 1M input tokens
        "output": 0.28,  # $0.28 per 1M output tokens
        "name": "DeepSeek"
    },
    "openai": {
        "input": 2.50,  # $2.50 per 1M input tokens (GPT-4o-mini)
        "output": 10.00,  # $10.00 per 1M output tokens
        "name": "OpenAI"
    },
    "gemini": {
        "input": 0.15,  # $0.15 per 1M input tokens (Gemini 1.5 Flash)
        "output": 0.60,  # $0.60 per 1M output tokens
        "name": "Gemini"
    },
    "qwen": {
        "input": 0.10,  # $0.10 per 1M input tokens (估算)
        "output": 0.20,  # $0.20 per 1M output tokens
        "name": "Qwen"
    },
    "ollama": {
        "input": 0.0,  # 本地運行，無成本
        "output": 0.0,
        "name": "Ollama"
    }
}

# 預設限制
DEFAULT_DAILY_LIMIT = 10000  # 每日 Token 限制
DEFAULT_MONTHLY_LIMIT = 300000  # 每月 Token 限制
WARNING_THRESHOLD = 0.8  # 80% 警告閾值


class CostRecordRepository(BaseRepository):
    """成本記錄 Repository"""
    
    def __init__(self):
        super().__init__("cost_records")
    
    async def create_record(
        self,
        user_id: str,
        service: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        operation: str
    ) -> Dict[str, Any]:
        """建立成本記錄"""
        document = {
            "user_id": user_id,
            "service": service,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost,
            "operation": operation,
            "created_at": datetime.utcnow(),
            "date": datetime.utcnow().date().isoformat(),
            "month": datetime.utcnow().strftime("%Y-%m")
        }
        return await self.create(document)
    
    async def get_daily_usage(
        self,
        user_id: str,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """取得每日使用量"""
        if not date:
            date = datetime.utcnow().date().isoformat()
        
        records = await self.find_many(
            filter={"user_id": user_id, "date": date}
        )
        
        total_tokens = sum(r.get("total_tokens", 0) for r in records)
        total_cost = sum(r.get("cost", 0.0) for r in records)
        
        return {
            "date": date,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "record_count": len(records)
        }
    
    async def get_monthly_usage(
        self,
        user_id: str,
        month: Optional[str] = None
    ) -> Dict[str, Any]:
        """取得每月使用量"""
        if not month:
            month = datetime.utcnow().strftime("%Y-%m")
        
        records = await self.find_many(
            filter={"user_id": user_id, "month": month}
        )
        
        total_tokens = sum(r.get("total_tokens", 0) for r in records)
        total_cost = sum(r.get("cost", 0.0) for r in records)
        
        return {
            "month": month,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "record_count": len(records)
        }
    
    async def get_user_statistics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """取得用戶統計資訊"""
        start_date = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
        
        records = await self.find_many(
            filter={
                "user_id": user_id,
                "created_at": {"$gte": datetime.fromisoformat(start_date)}
            }
        )
        
        total_tokens = sum(r.get("total_tokens", 0) for r in records)
        total_cost = sum(r.get("cost", 0.0) for r in records)
        
        # 按服務統計
        service_stats = {}
        for record in records:
            service = record.get("service", "unknown")
            if service not in service_stats:
                service_stats[service] = {
                    "tokens": 0,
                    "cost": 0.0,
                    "count": 0
                }
            service_stats[service]["tokens"] += record.get("total_tokens", 0)
            service_stats[service]["cost"] += record.get("cost", 0.0)
            service_stats[service]["count"] += 1
        
        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "record_count": len(records),
            "service_stats": service_stats,
            "days": days
        }


class CostMonitor:
    """成本監控服務"""
    
    def __init__(self):
        self.cost_repo = CostRecordRepository()
        self.daily_limit = DEFAULT_DAILY_LIMIT
        self.monthly_limit = DEFAULT_MONTHLY_LIMIT
        self.warning_threshold = WARNING_THRESHOLD
    
    def _calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        service: str
    ) -> float:
        """
        計算成本
        
        Args:
            input_tokens: 輸入 Token 數量
            output_tokens: 輸出 Token 數量
            service: AI 服務名稱
            
        Returns:
            成本（USD）
        """
        service_lower = service.lower()
        if service_lower not in AI_SERVICE_COSTS:
            logger.warning(f"未知的 AI 服務: {service}，使用 DeepSeek 成本計算")
            service_lower = "deepseek"
        
        cost_config = AI_SERVICE_COSTS[service_lower]
        
        # 計算成本（Token 轉換為百萬）
        input_cost = (input_tokens / 1_000_000) * cost_config["input"]
        output_cost = (output_tokens / 1_000_000) * cost_config["output"]
        
        total_cost = input_cost + output_cost
        
        return round(total_cost, 6)  # 保留 6 位小數
    
    async def check_cost(
        self,
        user_id: str,
        estimated_tokens: int,
        daily_limit: Optional[int] = None,
        monthly_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        檢查成本是否允許
        
        Args:
            user_id: 用戶 ID
            estimated_tokens: 預估 Token 數量
            daily_limit: 每日限制（可選，使用預設值）
            monthly_limit: 每月限制（可選，使用預設值）
            
        Returns:
            檢查結果，包含 allowed, reason, message
        """
        daily_limit = daily_limit or self.daily_limit
        monthly_limit = monthly_limit or self.monthly_limit
        
        # 取得當前使用量
        daily_usage = await self.cost_repo.get_daily_usage(user_id)
        monthly_usage = await self.cost_repo.get_monthly_usage(user_id)
        
        current_daily = daily_usage.get("total_tokens", 0)
        current_monthly = monthly_usage.get("total_tokens", 0)
        
        # 檢查每日限制
        if current_daily + estimated_tokens > daily_limit:
            return {
                "allowed": False,
                "reason": "daily_limit_exceeded",
                "message": f"今日 Token 使用量已達上限（{current_daily}/{daily_limit}）",
                "current_daily": current_daily,
                "daily_limit": daily_limit,
                "estimated_tokens": estimated_tokens
            }
        
        # 檢查每月限制
        if current_monthly + estimated_tokens > monthly_limit:
            return {
                "allowed": False,
                "reason": "monthly_limit_exceeded",
                "message": f"本月 Token 使用量已達上限（{current_monthly}/{monthly_limit}）",
                "current_monthly": current_monthly,
                "monthly_limit": monthly_limit,
                "estimated_tokens": estimated_tokens
            }
        
        return {
            "allowed": True,
            "current_daily": current_daily,
            "current_monthly": current_monthly,
            "daily_limit": daily_limit,
            "monthly_limit": monthly_limit
        }
    
    async def record_usage(
        self,
        user_id: str,
        service: str,
        input_tokens: int,
        output_tokens: int,
        operation: str = "unknown"
    ) -> Dict[str, Any]:
        """
        記錄使用量
        
        Args:
            user_id: 用戶 ID
            service: AI 服務名稱
            input_tokens: 輸入 Token 數量
            output_tokens: 輸出 Token 數量
            operation: 操作類型（例如：question_generation, source_verification, content_generation）
            
        Returns:
            記錄結果，包含 cost, warning
        """
        # 計算成本
        cost = self._calculate_cost(input_tokens, output_tokens, service)
        
        # 記錄到資料庫
        record = await self.cost_repo.create_record(
            user_id=user_id,
            service=service,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            operation=operation
        )
        
        # 檢查警告閾值
        warnings = []
        
        # 取得更新後的使用量
        daily_usage = await self.cost_repo.get_daily_usage(user_id)
        monthly_usage = await self.cost_repo.get_monthly_usage(user_id)
        
        current_daily = daily_usage.get("total_tokens", 0)
        current_monthly = monthly_usage.get("total_tokens", 0)
        
        # 檢查每日警告
        if current_daily >= self.daily_limit * self.warning_threshold:
            warnings.append({
                "type": "daily_warning",
                "message": f"今日 Token 使用量已達 {int(self.warning_threshold * 100)}%（{current_daily}/{self.daily_limit}）",
                "threshold": self.warning_threshold,
                "current": current_daily,
                "limit": self.daily_limit
            })
        
        # 檢查每月警告
        if current_monthly >= self.monthly_limit * self.warning_threshold:
            warnings.append({
                "type": "monthly_warning",
                "message": f"本月 Token 使用量已達 {int(self.warning_threshold * 100)}%（{current_monthly}/{self.monthly_limit}）",
                "threshold": self.warning_threshold,
                "current": current_monthly,
                "limit": self.monthly_limit
            })
        
        return {
            "record_id": record.get("id"),
            "cost": cost,
            "total_tokens": input_tokens + output_tokens,
            "warnings": warnings,
            "current_daily": current_daily,
            "current_monthly": current_monthly
        }
    
    async def get_user_statistics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        取得用戶統計資訊
        
        Args:
            user_id: 用戶 ID
            days: 統計天數（預設 30 天）
            
        Returns:
            統計資訊
        """
        return await self.cost_repo.get_user_statistics(user_id, days)
    
    async def get_cost_summary(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        取得成本摘要
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            成本摘要，包含每日/每月使用量、警告狀態
        """
        daily_usage = await self.cost_repo.get_daily_usage(user_id)
        monthly_usage = await self.cost_repo.get_monthly_usage(user_id)
        
        daily_percentage = (daily_usage.get("total_tokens", 0) / self.daily_limit) * 100
        monthly_percentage = (monthly_usage.get("total_tokens", 0) / self.monthly_limit) * 100
        
        warnings = []
        if daily_percentage >= self.warning_threshold * 100:
            warnings.append("daily")
        if monthly_percentage >= self.warning_threshold * 100:
            warnings.append("monthly")
        
        return {
            "daily": {
                "tokens": daily_usage.get("total_tokens", 0),
                "limit": self.daily_limit,
                "percentage": round(daily_percentage, 2),
                "cost": daily_usage.get("total_cost", 0.0),
                "warning": daily_percentage >= self.warning_threshold * 100
            },
            "monthly": {
                "tokens": monthly_usage.get("total_tokens", 0),
                "limit": self.monthly_limit,
                "percentage": round(monthly_percentage, 2),
                "cost": monthly_usage.get("total_cost", 0.0),
                "warning": monthly_percentage >= self.warning_threshold * 100
            },
            "warnings": warnings
        }
    
    def get_service_cost_info(self, service: str) -> Dict[str, Any]:
        """
        取得服務成本資訊
        
        Args:
            service: AI 服務名稱
            
        Returns:
            成本資訊
        """
        service_lower = service.lower()
        if service_lower not in AI_SERVICE_COSTS:
            service_lower = "deepseek"
        
        cost_config = AI_SERVICE_COSTS[service_lower]
        
        return {
            "service": service_lower,
            "name": cost_config["name"],
            "input_cost_per_1m": cost_config["input"],
            "output_cost_per_1m": cost_config["output"],
            "estimated_cost_per_1k": {
                "input": round(cost_config["input"] / 1000, 6),
                "output": round(cost_config["output"] / 1000, 6)
            }
        }
    
    def compare_services_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, Any]:
        """
        比較不同服務的成本
        
        Args:
            input_tokens: 輸入 Token 數量
            output_tokens: 輸出 Token 數量
            
        Returns:
            各服務的成本比較
        """
        comparison = {}
        
        for service, cost_config in AI_SERVICE_COSTS.items():
            cost = self._calculate_cost(input_tokens, output_tokens, service)
            comparison[service] = {
                "name": cost_config["name"],
                "cost": cost,
                "cost_per_1k_tokens": round(cost / ((input_tokens + output_tokens) / 1000), 6) if (input_tokens + output_tokens) > 0 else 0
            }
        
        # 排序（按成本）
        sorted_comparison = sorted(
            comparison.items(),
            key=lambda x: x[1]["cost"]
        )
        
        return {
            "comparison": dict(sorted_comparison),
            "cheapest": sorted_comparison[0][0] if sorted_comparison else None,
            "most_expensive": sorted_comparison[-1][0] if sorted_comparison else None
        }


# 建立全域實例
inspiration_cost_monitor = CostMonitor()

