"""
風格學習服務
Phase 4: AI 個人化
核心服務：分析用戶評分，學習個人風格
"""
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from app.services.repositories.style_profile_repository import StyleProfileRepository
from app.services.repositories.rating_repository import RatingRepository
from app.models.style_profile import (
    PresetStyle, LearningStage, OutputFormat,
    PRESET_STYLE_CONFIGS, OUTPUT_FORMAT_CONFIGS,
    get_learning_stage, calculate_confidence_score
)
from app.models.rating import RatingValue, RatingReason, RatingCreate
import logging

logger = logging.getLogger(__name__)


class StyleLearningService:
    """風格學習服務"""
    
    def __init__(self):
        self.profile_repo = StyleProfileRepository()
        self.rating_repo = RatingRepository()
    
    # ============================================
    # 風格檔案管理
    # ============================================
    
    async def get_or_create_profile(self, user_id: str) -> Dict[str, Any]:
        """取得或建立用戶的風格檔案"""
        return await self.profile_repo.get_or_create(user_id)
    
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """取得用戶的風格檔案"""
        return await self.profile_repo.get_by_user_id(user_id)
    
    async def set_preset_style(
        self,
        user_id: str,
        preset_style: PresetStyle,
        language: str = "zh-TW"
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """設定預設風格"""
        from app.utils.i18n import get_error_message
        # 確保風格檔案存在
        await self.profile_repo.get_or_create(user_id)
        
        profile = await self.profile_repo.update_preset_style(user_id, preset_style)
        if not profile:
            return None, get_error_message("style.update_failed", language)
        
        logger.info(f"用戶 {user_id} 設定預設風格: {preset_style.value}")
        return profile, None
    
    async def reset_profile(self, user_id: str, language: str = "zh-TW") -> Tuple[bool, Optional[str]]:
        """重置風格檔案"""
        from app.utils.i18n import get_error_message
        profile = await self.profile_repo.reset_profile(user_id)
        if not profile:
            return False, get_error_message("style.reset_failed", language)
        
        # 刪除評分記錄
        deleted_count = await self.rating_repo.delete_user_ratings(user_id)
        
        logger.info(f"用戶 {user_id} 重置風格檔案，刪除 {deleted_count} 條評分")
        return True, None
    
    # ============================================
    # 評分處理
    # ============================================
    
    async def submit_rating(
        self,
        user_id: str,
        rating_data: RatingCreate
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        提交評分並更新風格檔案
        
        這是風格學習的核心流程：
        1. 記錄評分
        2. 更新評分統計
        3. 分析評分原因
        4. 調整風格偏好
        5. 更新主題偏好
        """
        # 確保風格檔案存在
        await self.profile_repo.get_or_create(user_id)
        
        # 檢查是否已評分
        existing = await self.rating_repo.get_user_rating_for_content(
            user_id,
            rating_data.content_id
        )
        
        if existing:
            # 更新現有評分
            rating = await self.rating_repo.update_rating(
                user_id,
                rating_data.content_id,
                {
                    "value": rating_data.value.value,
                    "reasons": [r.value for r in rating_data.reasons],
                    "comment": rating_data.comment,
                }
            )
        else:
            # 建立新評分
            rating = await self.rating_repo.create_rating(
                user_id,
                {
                    "content_id": rating_data.content_id,
                    "topic_id": rating_data.topic_id,
                    "value": rating_data.value.value,
                    "reasons": [r.value for r in rating_data.reasons],
                    "comment": rating_data.comment,
                    "content_format": rating_data.content_format,
                    "content_length": rating_data.content_length,
                    "topic_category": rating_data.topic_category,
                }
            )
        
        is_positive = rating_data.value == RatingValue.LIKE
        
        # 更新風格檔案
        await self._process_rating_for_learning(
            user_id,
            rating_data,
            is_positive
        )
        
        logger.info(f"用戶 {user_id} 評分 {rating_data.content_id}: {'👍' if is_positive else '👎'}")
        
        return rating, None
    
    async def _process_rating_for_learning(
        self,
        user_id: str,
        rating_data: RatingCreate,
        is_positive: bool
    ):
        """處理評分以進行風格學習"""
        # 1. 更新評分統計
        await self.profile_repo.increment_ratings(user_id, is_positive)
        
        # 2. 根據評分原因更新語氣偏好
        if rating_data.reasons:
            reason_values = [r.value for r in rating_data.reasons]
            await self.profile_repo.update_tone_from_rating(
                user_id,
                reason_values,
                is_positive
            )
        
        # 3. 更新主題偏好
        keywords = []  # TODO: 從內容中提取關鍵字
        if rating_data.topic_category:
            await self.profile_repo.update_topic_preferences(
                user_id,
                rating_data.topic_category,
                keywords,
                is_positive
            )
    
    async def get_rating_stats(self, user_id: str) -> Dict[str, Any]:
        """取得用戶的評分統計"""
        return await self.rating_repo.get_user_rating_stats(user_id)
    
    async def get_rating_history(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """取得用戶的評分歷史"""
        skip = (page - 1) * limit
        ratings = await self.rating_repo.get_user_ratings(user_id, skip, limit)
        total = await self.rating_repo.count_user_ratings(user_id)
        
        return {
            "ratings": ratings,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    # ============================================
    # 風格分析
    # ============================================
    
    async def analyze_user_style(self, user_id: str) -> Dict[str, Any]:
        """
        分析用戶風格
        
        返回：
        - 學習階段
        - 信心分數
        - 主要風格特徵
        - 建議
        """
        profile = await self.get_or_create_profile(user_id)
        
        stats = await self.rating_repo.get_user_rating_stats(user_id)
        
        learning_stage = LearningStage(profile.get("learning_stage", "cold_start"))
        
        # 分析主要風格特徵
        tone = profile.get("tone", {})
        style_traits = []
        
        if tone.get("formal_score", 0.5) > 0.7:
            style_traits.append("專業正式")
        elif tone.get("formal_score", 0.5) < 0.3:
            style_traits.append("輕鬆隨性")
        
        if tone.get("humor_score", 0.3) > 0.6:
            style_traits.append("幽默風趣")
        
        if tone.get("emotion_score", 0.5) > 0.7:
            style_traits.append("富有情感")
        
        # 生成建議
        recommendations = self._generate_recommendations(profile, stats)
        
        return {
            "user_id": user_id,
            "learning_stage": learning_stage.value,
            "learning_stage_label": self._get_stage_label(learning_stage),
            "confidence_score": profile.get("confidence_score", 0),
            "total_ratings": profile.get("total_ratings", 0),
            "positive_ratio": stats.get("positive_ratio", 0),
            "style_traits": style_traits,
            "preset_style": profile.get("preset_style"),
            "tone": tone,
            "content_preferences": profile.get("content", {}),
            "topic_preferences": profile.get("topics", {}),
            "recommendations": recommendations,
            "top_like_reasons": stats.get("top_like_reasons", []),
            "top_dislike_reasons": stats.get("top_dislike_reasons", []),
        }
    
    def _get_stage_label(self, stage: LearningStage) -> str:
        """取得學習階段標籤"""
        labels = {
            LearningStage.COLD_START: "冷啟動",
            LearningStage.LEARNING: "學習中",
            LearningStage.MATURE: "已成熟",
        }
        return labels.get(stage, "未知")
    
    def _generate_recommendations(
        self,
        profile: Dict[str, Any],
        stats: Dict[str, Any]
    ) -> List[str]:
        """生成風格建議"""
        recommendations = []
        
        total_ratings = profile.get("total_ratings", 0)
        learning_stage = LearningStage(profile.get("learning_stage", "cold_start"))
        
        if learning_stage == LearningStage.COLD_START:
            recommendations.append(f"繼續評分以提升個人化效果！目前已評分 {total_ratings} 次，還需 {20 - total_ratings} 次進入學習階段。")
        elif learning_stage == LearningStage.LEARNING:
            recommendations.append(f"系統正在學習您的風格偏好！再評分 {100 - total_ratings} 次即可達到成熟階段。")
        else:
            recommendations.append("您的風格檔案已經成熟，系統已經充分了解您的偏好！")
        
        # 根據評分統計生成建議
        top_dislike = stats.get("top_dislike_reasons", [])
        if top_dislike:
            reason = top_dislike[0].get("reason", "")
            if reason == "too_long":
                recommendations.append("您似乎偏好較短的內容，系統已調整生成長度。")
            elif reason == "too_short":
                recommendations.append("您似乎偏好較長的內容，系統已調整生成長度。")
            elif reason == "tone_bad":
                recommendations.append("您對語氣有特定偏好，可以嘗試更換預設風格。")
        
        return recommendations
    
    # ============================================
    # 生成 Prompt 構建
    # ============================================
    
    async def build_generation_prompt(
        self,
        user_id: str,
        topic: Dict[str, Any],
        output_format: OutputFormat = OutputFormat.SOCIAL_POST,
        target_language: str = "zh-TW"
    ) -> str:
        """
        建構個人化生成 Prompt
        
        根據用戶的風格檔案，生成包含個人化指引的 Prompt
        """
        profile = await self.profile_repo.get_or_create(user_id)
        
        # 取得輸出格式配置
        format_config = OUTPUT_FORMAT_CONFIGS.get(output_format, OUTPUT_FORMAT_CONFIGS[OutputFormat.SOCIAL_POST])
        
        # 取得預設風格配置
        preset_style = PresetStyle(profile.get("preset_style", PresetStyle.CASUAL.value))
        style_config = PRESET_STYLE_CONFIGS.get(preset_style, PRESET_STYLE_CONFIGS[PresetStyle.CASUAL])
        
        # 取得用戶風格偏好
        tone = profile.get("tone", {})
        content_pref = profile.get("content", {})
        topic_pref = profile.get("topics", {})
        
        # 語言標籤
        lang_labels = {
            "zh-TW": "繁體中文",
            "en": "English",
            "ja": "日本語",
        }
        
        # 建構 Prompt
        prompt = f"""作為專業內容創作者，請根據以下主題生成{format_config['name']}。

## 主題資訊
標題：{topic.get('title', '')}
摘要：{topic.get('summary', topic.get('description', ''))[:300]}
類別：{topic.get('category', '')}

## 輸出要求
- 格式：{format_config['name']}
- 字數：{format_config['min_length']}-{format_config['max_length']} 字
- 結構：{', '.join(format_config['structure'])}
- 語言：{lang_labels.get(target_language, '繁體中文')}
- Hashtag 數量：{format_config['hashtag_count']} 個

## 風格指引（{style_config['name']}）
{chr(10).join('- ' + hint for hint in style_config['prompt_hints'])}

## 語氣偏好
- 正式程度：{'正式' if tone.get('formal_score', 0.5) > 0.6 else '輕鬆' if tone.get('formal_score', 0.5) < 0.4 else '中等'}
- 幽默程度：{'高' if tone.get('humor_score', 0.3) > 0.5 else '低'}
- 情感表達：{'豐富' if tone.get('emotion_score', 0.5) > 0.6 else '適中'}
"""

        # 添加內容偏好
        if content_pref.get("use_emoji", True):
            prompt += "\n- 適當使用表情符號"
        else:
            prompt += "\n- 不使用表情符號"
        
        # 添加主題偏好（避免不喜歡的主題）
        disliked_keywords = topic_pref.get("disliked_keywords", [])
        if disliked_keywords:
            prompt += f"\n\n## 避免使用的關鍵字\n{', '.join(disliked_keywords[:10])}"
        
        # 添加喜歡的關鍵字提示
        liked_keywords = topic_pref.get("liked_keywords", [])
        if liked_keywords:
            prompt += f"\n\n## 可考慮融入的元素\n{', '.join(liked_keywords[:10])}"
        
        prompt += "\n\n請直接輸出內容，不要添加任何解釋或前綴。"
        
        return prompt
    
    def get_available_styles(self) -> List[Dict[str, Any]]:
        """取得可用的預設風格列表"""
        return [
            {
                "value": style.value,
                "name": config["name"],
                "description": config["description"]
            }
            for style, config in PRESET_STYLE_CONFIGS.items()
        ]
    
    def get_available_formats(self) -> List[Dict[str, Any]]:
        """取得可用的輸出格式列表"""
        return [
            {
                "value": fmt.value,
                "name": config["name"],
                "description": config["description"],
                "min_length": config["min_length"],
                "max_length": config["max_length"],
            }
            for fmt, config in OUTPUT_FORMAT_CONFIGS.items()
        ]


# 建立全域實例
style_learning_service = StyleLearningService()

