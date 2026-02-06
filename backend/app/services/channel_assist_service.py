"""
AI 頻道助手服務
使用 DeepSeek API 解析用戶自然語言輸入，協助建立頻道
"""
import json
import re
from typing import Optional, Dict, Any, List
from app.services.ai.deepseek import DeepSeekService
from app.models.channel import (
    ChannelCategory, ChannelRegion, DEFAULT_RSS_SOURCES
)
import logging

logger = logging.getLogger(__name__)


class ChannelAssistService:
    """AI 頻道助手服務"""
    
    def __init__(self):
        self.ai_service = DeepSeekService()
    
    def _build_assist_prompt(self, user_input: str, language: str = "zh-TW") -> str:
        """
        建立 AI 助手 Prompt
        
        Args:
            user_input: 用戶輸入的自然語言
            language: 用戶語言（zh-TW/en/ja）
            
        Returns:
            Prompt 字串
        """
        # 根據語言選擇提示詞
        if language.startswith("zh"):
            prompt_template = """你是一個頻道建立助手。根據用戶的描述，提取以下資訊：

用戶輸入：{user_input}

請回傳 JSON 格式：
{{
  "category": "fashion|food|trend|finance|sports|tech|entertainment|other",
  "region": "hong_kong|taiwan|japan|korea|china|usa|uk|global",
  "keywords": ["關鍵字1", "關鍵字2"],
  "confidence": 0.0-1.0,
  "clarification_needed": true|false,
  "clarification_question": "如果需要澄清，問什麼問題"
}}

可用類別：
- fashion: 時尚、穿搭、服裝、潮流
- food: 美食、料理、餐廳、飲食
- trend: 趨勢、流行、社會議題
- finance: 財經、投資、經濟
- sports: 運動、體育
- tech: 科技、技術、數位
- entertainment: 娛樂、影視、音樂
- other: 其他（需要自定義關鍵字）

可用地區：
- hong_kong: 香港
- taiwan: 台灣
- japan: 日本
- korea: 韓國
- china: 中國大陸
- usa: 美國
- uk: 英國
- global: 全球

範例：
輸入：「我想看日本的潮流穿搭」
輸出：{{
  "category": "fashion",
  "region": "japan", 
  "keywords": ["潮流", "穿搭"],
  "confidence": 0.95,
  "clarification_needed": false
}}

輸入：「美食」
輸出：{{
  "category": "food",
  "region": null,
  "keywords": [],
  "confidence": 0.6,
  "clarification_needed": true,
  "clarification_question": "你想看哪個地區的美食內容？"
}}

請只回傳 JSON，不要包含其他文字。"""
        elif language == "ja":
            prompt_template = """あなたはチャンネル作成アシスタントです。ユーザーの説明に基づいて、以下の情報を抽出してください：

ユーザー入力：{user_input}

JSON形式で返してください：
{{
  "category": "fashion|food|trend|finance|sports|tech|entertainment|other",
  "region": "hong_kong|taiwan|japan|korea|china|usa|uk|global",
  "keywords": ["キーワード1", "キーワード2"],
  "confidence": 0.0-1.0,
  "clarification_needed": true|false,
  "clarification_question": "明確化が必要な場合、何を尋ねるか"
}}

利用可能なカテゴリ：
- fashion: ファッション、スタイル、服装
- food: グルメ、料理、レストラン
- trend: トレンド、流行、社会問題
- finance: 金融、投資、経済
- sports: スポーツ
- tech: テクノロジー、デジタル
- entertainment: エンターテインメント、映画、音楽
- other: その他（カスタムキーワードが必要）

利用可能な地域：
- hong_kong: 香港
- taiwan: 台湾
- japan: 日本
- korea: 韓国
- china: 中国
- usa: アメリカ
- uk: イギリス
- global: グローバル

JSONのみを返してください。"""
        else:  # English
            prompt_template = """You are a channel creation assistant. Extract the following information from the user's description:

User input: {user_input}

Return JSON format:
{{
  "category": "fashion|food|trend|finance|sports|tech|entertainment|other",
  "region": "hong_kong|taiwan|japan|korea|china|usa|uk|global",
  "keywords": ["keyword1", "keyword2"],
  "confidence": 0.0-1.0,
  "clarification_needed": true|false,
  "clarification_question": "What to ask if clarification is needed"
}}

Available categories:
- fashion: fashion, style, clothing, trends
- food: food, cuisine, restaurants, dining
- trend: trends, popular topics, social issues
- finance: finance, investment, economy
- sports: sports, athletics
- tech: technology, digital
- entertainment: entertainment, movies, music
- other: other (requires custom keywords)

Available regions:
- hong_kong: Hong Kong
- taiwan: Taiwan
- japan: Japan
- korea: Korea
- china: China
- usa: USA
- uk: UK
- global: Global

Return only JSON, no other text."""
        
        return prompt_template.format(user_input=user_input)
    
    async def parse_user_intent(
        self,
        user_input: str,
        language: str = "zh-TW"
    ) -> Dict[str, Any]:
        """
        解析用戶意圖
        
        Args:
            user_input: 用戶輸入的自然語言
            language: 用戶語言
            
        Returns:
            解析結果字典
        """
        try:
            # 建立 Prompt
            prompt = self._build_assist_prompt(user_input, language)
            
            # 調用 AI API
            response = await self.ai_service._call_api(prompt)
            
            # 解析 JSON 回應
            # 移除可能的 markdown 代碼塊標記
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # 解析 JSON
            result = json.loads(response)
            
            # 驗證和標準化結果
            parsed = {
                "category": self._normalize_category(result.get("category")),
                "region": self._normalize_region(result.get("region")),
                "keywords": result.get("keywords", []),
                "confidence": float(result.get("confidence", 0.0)),
                "clarification_needed": bool(result.get("clarification_needed", False)),
                "clarification_question": result.get("clarification_question", "")
            }
            
            logger.info(f"AI 解析結果: {parsed}")
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {e}, 回應: {response[:200]}")
            # 根據語言返回對應的錯誤訊息
            clarification_question = self._get_error_message("parse_failed", language)
            return {
                "category": None,
                "region": None,
                "keywords": [],
                "confidence": 0.0,
                "clarification_needed": True,
                "clarification_question": clarification_question
            }
        except Exception as e:
            logger.error(f"AI 解析錯誤: {e}")
            # 根據語言返回對應的錯誤訊息
            clarification_question = self._get_error_message("processing_error", language)
            return {
                "category": None,
                "region": None,
                "keywords": [],
                "confidence": 0.0,
                "clarification_needed": True,
                "clarification_question": clarification_question
            }
    
    def _get_error_message(self, error_type: str, language: str = "zh-TW") -> str:
        """
        根據語言返回對應的錯誤訊息
        
        Args:
            error_type: 錯誤類型（parse_failed/processing_error）
            language: 用戶語言
            
        Returns:
            對應語言的錯誤訊息
        """
        error_messages = {
            "parse_failed": {
                "zh-TW": "抱歉，我無法理解您的輸入。請試試用更明確的方式描述，例如：「我想看日本的時尚內容」",
                "en": "Sorry, I couldn't understand your input. Please try describing it more clearly, for example: \"I want to see Japanese fashion content\"",
                "ja": "申し訳ございませんが、入力内容を理解できませんでした。より明確に説明してください。例：「日本のファッションコンテンツを見たい」"
            },
            "processing_error": {
                "zh-TW": "抱歉，處理您的請求時發生錯誤。請稍後再試。",
                "en": "Sorry, an error occurred while processing your request. Please try again later.",
                "ja": "申し訳ございませんが、リクエストの処理中にエラーが発生しました。後でもう一度お試しください。"
            }
        }
        
        # 如果語言不在字典中，使用英文作為預設
        lang = language if language in error_messages[error_type] else "en"
        return error_messages[error_type].get(lang, error_messages[error_type]["en"])
    
    def _normalize_category(self, category: Optional[str]) -> Optional[str]:
        """標準化類別"""
        if not category:
            return None
        
        category_lower = category.lower().strip()
        
        # 映射常見變體
        category_map = {
            "fashion": ChannelCategory.FASHION.value,
            "food": ChannelCategory.FOOD.value,
            "trend": ChannelCategory.TREND.value,
            "finance": ChannelCategory.FINANCE.value,
            "sports": ChannelCategory.SPORTS.value,
            "tech": ChannelCategory.TECH.value,
            "technology": ChannelCategory.TECH.value,
            "entertainment": ChannelCategory.ENTERTAINMENT.value,
            "other": ChannelCategory.OTHER.value,
        }
        
        return category_map.get(category_lower, category_lower)
    
    def _normalize_region(self, region: Optional[str]) -> Optional[str]:
        """標準化地區"""
        if not region:
            return None
        
        region_lower = region.lower().strip()
        
        # 映射常見變體
        region_map = {
            "hong_kong": ChannelRegion.HONG_KONG.value,
            "hk": ChannelRegion.HONG_KONG.value,
            "taiwan": ChannelRegion.TAIWAN.value,
            "tw": ChannelRegion.TAIWAN.value,
            "japan": ChannelRegion.JAPAN.value,
            "jp": ChannelRegion.JAPAN.value,
            "korea": ChannelRegion.KOREA.value,
            "kr": ChannelRegion.KOREA.value,
            "china": ChannelRegion.CHINA.value,
            "cn": ChannelRegion.CHINA.value,
            "usa": ChannelRegion.USA.value,
            "us": ChannelRegion.USA.value,
            "uk": ChannelRegion.UK.value,
            "global": ChannelRegion.GLOBAL.value,
        }
        
        return region_map.get(region_lower, region_lower)
    
    def recommend_sources(
        self,
        category: Optional[str],
        region: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        推薦 RSS 來源
        
        Args:
            category: 頻道類別
            region: 頻道地區
            
        Returns:
            推薦的來源列表
        """
        if not category or not region:
            return []
        
        try:
            # 轉換為 Enum
            cat_enum = ChannelCategory(category)
            region_enum = ChannelRegion(region)
            
            # 從 DEFAULT_RSS_SOURCES 取得來源
            category_sources = DEFAULT_RSS_SOURCES.get(cat_enum, {})
            region_sources = category_sources.get(region_enum, [])
            
            # 如果該地區沒有來源，使用 GLOBAL
            if not region_sources:
                region_sources = category_sources.get(ChannelRegion.GLOBAL, [])
            
            # 返回前 5 個來源（最多）
            return region_sources[:5]
            
        except (ValueError, KeyError) as e:
            logger.warning(f"無法取得來源推薦: {e}, category={category}, region={region}")
            return []


# 單例實例
channel_assist_service = ChannelAssistService()

