"""
User API 端點
"""
from fastapi import APIRouter, HTTPException
from app.schemas.user_preferences import (
    UserPreferencesResponse,
    UserPreferencesUpdate,
)
from app.services.repositories.user_preferences_repository import UserPreferencesRepository
from app.services.repositories.preference_service import PreferenceService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])

# Repository 和 Service 實例
preferences_repo = UserPreferencesRepository()
preference_service = PreferenceService()


def _convert_to_response(prefs_doc: dict) -> UserPreferencesResponse:
    """將 MongoDB 文檔轉換為 UserPreferencesResponse"""
    prefs_doc.pop("_id", None)
    return UserPreferencesResponse(**prefs_doc)


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_preferences():
    """
    取得使用者偏好
    """
    try:
        prefs = await preferences_repo.get_preferences()
        if not prefs:
            # 如果不存在，建立預設偏好
            prefs = await preferences_repo.create_default_preferences()
        
        return _convert_to_response(prefs)
    except Exception as e:
        logger.error(f"取得使用者偏好失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_preferences(update_data: UserPreferencesUpdate):
    """
    更新使用者偏好
    """
    try:
        # 取得當前偏好
        current = await preferences_repo.get_preferences()
        if not current:
            current = await preferences_repo.create_default_preferences()
        
        # 合併更新資料（保留未更新的欄位）
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 如果更新了權重，需要確保總和為 1.0
        if any(key in update_dict for key in ["fashion_weight", "food_weight", "trend_weight"]):
            # 取得當前權重
            fashion = update_dict.get("fashion_weight", current.get("fashion_weight", 0.5))
            food = update_dict.get("food_weight", current.get("food_weight", 0.3))
            trend = update_dict.get("trend_weight", current.get("trend_weight", 0.2))
            
            # 如果所有權重都已提供，驗證總和
            total = fashion + food + trend
            if abs(total - 1.0) > 0.01:
                raise HTTPException(
                    status_code=422,
                    detail=f"權重總和必須為 1.0，當前總和為 {total:.2f}"
                )
        
        # 更新偏好
        updated = await preferences_repo.update_preferences("user_default", update_dict)
        if not updated:
            raise HTTPException(
                status_code=500,
                detail="更新偏好失敗"
            )
        
        return _convert_to_response(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新使用者偏好失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences/update-from-interactions", response_model=UserPreferencesResponse)
async def update_preferences_from_interactions():
    """
    根據互動數據自動更新偏好模型
    """
    try:
        updated = await preference_service.update_preferences_from_interactions("user_default")
        return _convert_to_response(updated)
    except Exception as e:
        logger.error(f"根據互動更新偏好失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
