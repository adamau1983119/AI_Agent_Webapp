"""
排程 API 端點
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Body
from datetime import datetime
from app.models.topic import Category
from app.services.automation.scheduler import SchedulerService
from app.services.repositories.topic_repository import TopicRepository
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schedules", tags=["schedules"])

# 排程服務實例（單例模式）
_scheduler_service: Optional[SchedulerService] = None


def get_scheduler_service() -> SchedulerService:
    """獲取排程服務實例（單例）"""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service


class ScheduleResponse(BaseModel):
    """排程響應"""
    date: str
    timeSlot: str
    status: str
    topicsCount: int
    completedAt: Optional[str] = None


class ManualGenerationRequest(BaseModel):
    """手動生成請求"""
    category: Category
    count: int = 3


class GenerateTodayRequest(BaseModel):
    """生成今日所有主題請求"""
    force: bool = False  # 是否強制重新生成


@router.get("", response_model=List[ScheduleResponse])
async def get_schedules(date: Optional[str] = Query(None, description="日期篩選（YYYY-MM-DD）")):
    """
    取得排程列表
    
    如果指定日期，返回該日期的排程；否則返回今天的排程
    """
    try:
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        
        # 取得該日期的主題
        topic_repo = TopicRepository()
        topics, _ = await topic_repo.list_topics(
            date=target_date,
            limit=100
        )
        
        # 按時間段分組
        time_slots = {
            "07:00": {"category": Category.FASHION, "topics": []},
            "12:00": {"category": Category.FOOD, "topics": []},
            "18:00": {"category": Category.TREND, "topics": []},
        }
        
        for topic in topics:
            generated_at = topic.get("generated_at")
            if isinstance(generated_at, str):
                try:
                    generated_at = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                except:
                    continue
            
            if isinstance(generated_at, datetime):
                hour = generated_at.hour
                if 6 <= hour < 10:  # 07:00 時間段
                    time_slots["07:00"]["topics"].append(topic)
                elif 11 <= hour < 14:  # 12:00 時間段
                    time_slots["12:00"]["topics"].append(topic)
                elif 17 <= hour < 20:  # 18:00 時間段
                    time_slots["18:00"]["topics"].append(topic)
        
        # 構建響應
        schedules = []
        for time_slot, data in time_slots.items():
            topics_count = len(data["topics"])
            status = "completed" if topics_count >= 3 else ("processing" if topics_count > 0 else "pending")
            
            completed_at = None
            if topics_count > 0:
                # 使用最後一個主題的生成時間
                last_topic = data["topics"][-1]
                completed_at = last_topic.get("generated_at")
                if isinstance(completed_at, datetime):
                    completed_at = completed_at.isoformat()
            
            schedules.append(ScheduleResponse(
                date=target_date,
                timeSlot=time_slot,
                status=status,
                topicsCount=topics_count,
                completedAt=completed_at
            ))
        
        return schedules
        
    except Exception as e:
        logger.error(f"取得排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=dict)
async def manual_generate_topics(
    request: ManualGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    手動觸發主題生成
    
    用於測試或立即執行主題生成任務
    """
    try:
        scheduler_service = get_scheduler_service()
        
        # 在背景任務中執行
        async def generate_task():
            try:
                topics = await scheduler_service.trigger_manual_generation(
                    category=request.category,
                    count=request.count
                )
                logger.info(f"手動生成完成，共建立 {len(topics)} 個主題")
            except Exception as e:
                logger.error(f"手動生成失敗: {e}")
        
        background_tasks.add_task(generate_task)
        
        return {
            "message": "主題生成任務已啟動",
            "category": request.category.value,
            "count": request.count
        }
        
    except Exception as e:
        logger.error(f"啟動主題生成任務失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-today", response_model=dict)
async def generate_today_all_topics(
    request: GenerateTodayRequest = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    立即生成今日所有主題（3個分類 × 3個主題 = 9個主題）
    
    用於補齊今日缺失的主題
    """
    try:
        scheduler_service = get_scheduler_service()
        
        # 檢查今日是否已有主題
        topic_repo = TopicRepository()
        today = datetime.now().strftime("%Y-%m-%d")
        existing_topics, _ = await topic_repo.list_topics(date=today, limit=100)
        
        if not request.force and len(existing_topics) >= 9:
            return {
                "message": "今日主題已完整，無需重新生成",
                "categories": ["fashion", "food", "trend"],
                "expected_count": 9,
                "existing_count": len(existing_topics)
            }
        
        # 在背景任務中執行
        async def generate_all_task():
            try:
                results = {}
                for category in [Category.FASHION, Category.FOOD, Category.TREND]:
                    try:
                        logger.info(f"開始生成 {category.value} 主題...")
                        topics = await scheduler_service.trigger_manual_generation(
                            category=category,
                            count=3
                        )
                        results[category.value] = {
                            "count": len(topics),
                            "topics": [t.get("id") for t in topics]
                        }
                        logger.info(f"✅ 生成 {category.value} 主題完成，共 {len(topics)} 個")
                    except Exception as e:
                        logger.error(f"❌ 生成 {category.value} 主題失敗: {e}", exc_info=True)
                        results[category.value] = {"error": str(e)}
                
                logger.info(f"📊 今日主題生成完成: {results}")
            except Exception as e:
                logger.error(f"❌ 生成今日主題失敗: {e}", exc_info=True)
        
        # 使用 BackgroundTasks 執行
        background_tasks.add_task(generate_all_task)
        
        return {
            "message": "今日主題生成任務已啟動，正在後台處理中...",
            "categories": ["fashion", "food", "trend"],
            "expected_count": 9,
            "existing_count": len(existing_topics)
        }
        
    except Exception as e:
        logger.error(f"❌ 啟動今日主題生成任務失敗: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"啟動生成任務失敗: {str(e)}")


@router.post("/start")
async def start_scheduler():
    """啟動排程服務"""
    try:
        scheduler_service = get_scheduler_service()
        scheduler_service.start()
        return {"message": "排程服務已啟動", "status": "running"}
    except Exception as e:
        logger.error(f"啟動排程服務失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_scheduler():
    """停止排程服務"""
    try:
        scheduler_service = get_scheduler_service()
        scheduler_service.stop()
        return {"message": "排程服務已停止", "status": "stopped"}
    except Exception as e:
        logger.error(f"停止排程服務失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_scheduler_status():
    """取得排程服務狀態"""
    try:
        scheduler_service = get_scheduler_service()
        jobs = []
        if scheduler_service.is_running:
            for job in scheduler_service.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
                })
        
        return {
            "status": "running" if scheduler_service.is_running else "stopped",
            "jobs": jobs
        }
    except Exception as e:
        logger.error(f"取得排程服務狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
