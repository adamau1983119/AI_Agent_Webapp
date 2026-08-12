"""
排程 API 端點
"""
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Body, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from app.models.topic import Category
from app.services.automation.scheduler import SchedulerService
from app.services.repositories.topic_repository import TopicRepository
from app.database import check_connection_from_request, get_database_from_request
from app.config import settings
from app.utils.cost_controls import scheduled_topic_collection_enabled
from pymongo.errors import ConnectionFailure
# 同時從統一的 exceptions 模組導入（備用方案，避免循環導入問題）
try:
    from app.exceptions import ConnectionFailure as ConnectionFailureFromExceptions
except ImportError:
    # 如果 exceptions 模組不存在，使用直接導入
    ConnectionFailureFromExceptions = ConnectionFailure
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schedules", tags=["schedules"])

# 排程服務實例（單例模式）
_scheduler_service: Optional[SchedulerService] = None


def get_scheduler_service() -> SchedulerService:
    """獲取排程服務實例（單例）"""
    # 在函數內部導入 ConnectionFailure，確保作用域正確
    from pymongo.errors import ConnectionFailure
    import traceback
    
    global _scheduler_service
    if _scheduler_service is None:
        try:
            logger.info("正在初始化 SchedulerService...")
            _scheduler_service = SchedulerService()
            logger.info("SchedulerService 初始化成功")
        except ConnectionFailure as e:
            logger.error(f"SchedulerService 初始化失敗（資料庫連接問題）: {e}")
            logger.error(f"完整錯誤堆疊:\n{traceback.format_exc()}")
            raise
        except Exception as e:
            logger.error(f"SchedulerService 初始化失敗: {e}")
            logger.error(f"錯誤類型: {type(e).__name__}")
            logger.error(f"完整錯誤堆疊:\n{traceback.format_exc()}")
            raise
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
    language: str = "zh-TW"  # 標題/內容的目標語言（zh-TW/en/ja）


@router.get("", response_model=List[ScheduleResponse])
async def get_schedules(
    request: Request,
    date: Optional[str] = Query(None, description="日期篩選（YYYY-MM-DD）")
):
    """
    取得排程列表
    
    如果指定日期，返回該日期的排程；否則返回今天的排程
    優化：快速響應，避免超時
    """
    import asyncio
    
    try:
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        
        # 快速檢查資料庫連接狀態（設置超時）
        try:
            is_connected, reason = await asyncio.wait_for(
                check_connection_from_request(request),
                timeout=2.0  # 2秒超時
            )
        except asyncio.TimeoutError:
            logger.warning("資料庫連接檢查超時，返回預設排程數據")
            is_connected = False
            reason = "連接檢查超時"
        
        if not is_connected:
            # 在開發環境中，資料庫未連接時返回預設排程數據
            if settings.ENVIRONMENT == "development":
                logger.warning(f"資料庫未連接 ({reason})，返回預設排程數據（開發環境）")
                return [
                    ScheduleResponse(
                        date=target_date,
                        timeSlot="07:00",
                        status="pending",
                        topicsCount=0,
                        completedAt=None
                    ),
                    ScheduleResponse(
                        date=target_date,
                        timeSlot="12:00",
                        status="pending",
                        topicsCount=0,
                        completedAt=None
                    ),
                    ScheduleResponse(
                        date=target_date,
                        timeSlot="18:00",
                        status="pending",
                        topicsCount=0,
                        completedAt=None
                    ),
                ]
            else:
                # 生產環境必須有資料庫連接
                from app.utils.i18n import get_error_message, get_user_language
                language = get_user_language(user=current_user, request=request)
                raise HTTPException(
                    status_code=503,
                    detail=get_error_message("schedule.database_unavailable", language)
                )
        
        # 取得該日期的主題（設置超時，避免長時間等待）
        topic_repo = TopicRepository()
        try:
            topics, _ = await asyncio.wait_for(
                topic_repo.list_topics(
                    date=target_date,
                    limit=100
                ),
                timeout=5.0  # 5秒超時
            )
        except asyncio.TimeoutError:
            logger.warning(f"取得日期 {target_date} 的主題超時，返回空列表")
            topics = []
        except ConnectionFailure as e:
            logger.warning(f"資料庫連接失敗: {e}")
            # 在開發環境中，連接失敗時返回預設排程數據
            if settings.ENVIRONMENT == "development":
                topics = []
            else:
                language = get_user_language(request=request)
                raise HTTPException(
                    status_code=503,
                    detail=get_error_message("schedule.database_unavailable", language)
                )
        except Exception as e:
            logger.warning(f"取得日期 {target_date} 的主題失敗: {e}")
            topics = []  # 如果查詢失敗，使用空列表
        
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
        logger.error(f"取得排程失敗: {e}", exc_info=True)
        # 即使出現異常，也返回空排程列表而不是 500 錯誤
        # 這樣前端可以正常顯示，只是沒有排程數據
        return [
            ScheduleResponse(
                date=target_date if 'target_date' in locals() else datetime.now().strftime("%Y-%m-%d"),
                timeSlot="07:00",
                status="pending",
                topicsCount=0,
                completedAt=None
            ),
            ScheduleResponse(
                date=target_date if 'target_date' in locals() else datetime.now().strftime("%Y-%m-%d"),
                timeSlot="12:00",
                status="pending",
                topicsCount=0,
                completedAt=None
            ),
            ScheduleResponse(
                date=target_date if 'target_date' in locals() else datetime.now().strftime("%Y-%m-%d"),
                timeSlot="18:00",
                status="pending",
                topicsCount=0,
                completedAt=None
            ),
        ]


@router.post("/generate", response_model=dict)
async def manual_generate_topics(
    request: ManualGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    手動觸發主題生成
    
    用於測試或立即執行主題生成任務
    """
    if not scheduled_topic_collection_enabled():
        raise HTTPException(
            status_code=403,
            detail={
                "code": "scheduled_topic_collection_disabled",
                "message": "排程主題卡收集已暫停。請設 ENABLE_SCHEDULED_TOPIC_COLLECTION=true 或改用頻道收集。",
            },
        )
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
    request: Request,
    request_body: GenerateTodayRequest = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    立即生成今日所有主題（三分類 × 配置檔 count；預設各 5 = 15）
    
    用於補齊今日缺失的主題
    """
    if not scheduled_topic_collection_enabled():
        raise HTTPException(
            status_code=403,
            detail={
                "code": "scheduled_topic_collection_disabled",
                "message": "每日主打主題卡生成已暫停 (ENABLE_SCHEDULED_TOPIC_COLLECTION=false)。",
            },
        )
    try:
        from app.config.topic_config import get_topic_config
        from app.utils.i18n import get_error_message, get_user_language

        topic_cfg = get_topic_config()
        per_category = {
            cat.value: topic_cfg.get_category_count(cat.value)
            for cat in [Category.FASHION, Category.FOOD, Category.TREND]
        }
        expected_total = sum(per_category.values())

        # 記錄 API 請求
        logger.info(
            f"收到生成今日主題請求: force={request_body.force} "
            f"per_category={per_category} expected={expected_total}"
        )
        
        scheduler_service = get_scheduler_service()
        
        # 1. 取得資料庫連接（簡化版檢查，統一使用 request.app.state.db）
        db = request.app.state.db
        if db is None:
            logger.error("❌ 資料庫未連接，無法生成主題")
            language = get_user_language(request=request)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "failed",
                    "message": get_error_message("schedule.database_not_connected", language),
                    "detail": "資料庫客戶端未初始化",
                    "categories": ["fashion", "food", "trend"],
                    "expected_count": expected_total,
                    "existing_count": 0,
                    "suggestion": get_error_message("schedule.suggestion.check_mongodb", language)
                }
            )
        
        logger.info(f"✅ 從 app.state.db 獲取資料庫實例，ID: {id(db)}")
        
        # 2. 查詢現有主題（HKT 營運日 + generated_at）
        existing_topics = []
        
        try:
            from app.services.automation.topic_day_hkt import hkt_day_utc_bounds

            from app.utils.topic_pipeline import list_topics_generation_filter

            start_utc, end_utc = hkt_day_utc_bounds()
            # soft cutover：只計目前世代，舊卡不擋 generate-today
            clauses = [{"generated_at": {"$gte": start_utc, "$lte": end_utc}}]
            gen_f = list_topics_generation_filter(include_legacy=False)
            if gen_f:
                clauses.append(gen_f)
            day_filter = clauses[0] if len(clauses) == 1 else {"$and": clauses}
            existing_topics_cursor = db["topics"].find(day_filter)
            existing_topics = await existing_topics_cursor.to_list(length=100)
            logger.info(f"📊 現有主題數量（含世代過濾）: {len(existing_topics)}")
        except ConnectionFailure as e:
            logger.error(f"❌ 查詢現有主題時資料庫連接失敗: {e}")
            language = get_user_language(request=request)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "failed",
                    "message": get_error_message("schedule.database_unavailable", language),
                    "detail": str(e),
                    "categories": ["fashion", "food", "trend"],
                    "expected_count": expected_total,
                    "existing_count": 0,
                    "suggestion": get_error_message("schedule.suggestion.check_mongodb_config", language)
                }
            )
        except Exception as e:
            logger.warning(f"⚠️ 取得現有主題失敗: {e}")
            existing_topics = []
        
        # 4. 檢查是否已達到上限
        existing_by_category: Dict[str, int] = {cat.value: 0 for cat in [Category.FASHION, Category.FOOD, Category.TREND]}
        for topic in existing_topics:
            cat = topic.get("category")
            if cat in existing_by_category:
                existing_by_category[cat] += 1

        from app.services.automation.topic_day_hkt import category_deficits

        deficits = category_deficits(existing_by_category)

        if not request_body.force and len(existing_topics) >= expected_total:
            logger.info("今日主題已完整，無需重新生成")
            return {
                "status": "skipped",
                "message": "今日主題已完整，無需重新生成",
                "categories": ["fashion", "food", "trend"],
                "expected_count": expected_total,
                "existing_count": len(existing_topics),
                "per_category": per_category,
                "deficits": deficits,
            }
        
        # 5. 在背景任務中執行生成
        target_language = request_body.language
        async def generate_all_task():
            """背景任務：生成所有主題"""
            try:
                logger.info("=" * 60)
                logger.info(f"🚀 背景任務開始：生成今日所有主題 (語言: {target_language})")
                logger.info("=" * 60)
                results = {}
                total_generated = 0
                
                for category in [Category.FASHION, Category.FOOD, Category.TREND]:
                    try:
                        cat_count = (
                            per_category[category.value]
                            if request_body.force
                            else deficits.get(category.value, 0)
                        )
                        if cat_count <= 0:
                            logger.info(f"{category.value} 已達配額，略過生成")
                            results[category.value] = {"count": 0, "topics": []}
                            continue
                        logger.info(
                            f"📝 開始生成 {category.value} 主題"
                            f"（目標：{cat_count} 個, 語言: {target_language}）..."
                        )
                        topics = await scheduler_service.trigger_manual_generation(
                            category=category,
                            count=cat_count,
                            display_language=target_language,
                            respect_quota=not request_body.force,
                        )
                        generated_count = len(topics) if topics else 0
                        total_generated += generated_count
                        results[category.value] = {
                            "count": generated_count,
                            "topics": [t.get("id") for t in topics] if topics else []
                        }
                        logger.info(f"✅ 生成 {category.value} 主題完成，共 {generated_count} 個")
                        if topics:
                            logger.info(f"   主題 ID: {[t.get('id') for t in topics]}")
                    except ConnectionFailure as e:
                        logger.error(f"❌ 生成 {category.value} 主題時資料庫連接失敗: {e}")
                        results[category.value] = {
                            "error": f"資料庫連接失敗: {str(e)}"
                        }
                    except Exception as e:
                        logger.error(f"❌ 生成 {category.value} 主題失敗: {e}", exc_info=True)
                        results[category.value] = {
                            "error": str(e)
                        }
                
                logger.info("=" * 60)
                logger.info(f"📊 今日主題生成完成！")
                logger.info(f"   總計生成：{total_generated}/{expected_total} 個主題")
                logger.info(f"   詳細結果：{results}")
                logger.info("=" * 60)
            except Exception as e:
                logger.error(f"❌ 背景任務執行失敗: {e}", exc_info=True)
        
        # 5. 提交背景任務
        background_tasks.add_task(generate_all_task)
        logger.info("生成任務已提交到背景執行")
        
        # 6. API 即時回應（不等待背景任務完成）
        return {
            "status": "accepted",
            "message": "生成任務已提交，請稍後查看結果",
            "categories": ["fashion", "food", "trend"],
            "expected_count": expected_total,
            "existing_count": len(existing_topics),
            "per_category": per_category,
            "language": target_language
        }
        
    except ConnectionFailure as e:
        import traceback
        logger.error(f"❌ 資料庫連接失敗: {e}")
        logger.error(f"錯誤類型: {type(e).__name__}")
        logger.error(f"完整錯誤堆疊:\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "failed",
                "message": "資料庫連接失敗，無法生成主題",
                "detail": str(e),
                "categories": ["fashion", "food", "trend"],
                "expected_count": 9,
                "existing_count": 0
            }
        )
    except Exception as e:
        # 捕獲所有未預期異常，避免直接 500
        import traceback
        logger.error(f"❌ API 執行失敗: {e}")
        logger.error(f"完整錯誤堆疊:\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "伺服器內部錯誤",
                "detail": str(e) if settings.DEBUG else "請聯繫管理員"
            }
        )


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
