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
from app.services.channel_service import channel_service
import logging

logger = logging.getLogger(__name__)


def _step3_lang_key(language: Optional[str]) -> str:
    if not language:
        return "en"
    if str(language).startswith("zh"):
        return "zh-TW"
    if str(language) == "ja":
        return "ja"
    return "en"


# Step 3 後端範本（與前端 i18n key 語意對齊；供無 AI 時精靈與 AI 欄位參考）
_STEP3_CAT: Dict[str, Dict[str, str]] = {
    "zh-TW": {
        "fashion": "時尚",
        "food": "美食",
        "trend": "趨勢",
        "finance": "財經",
        "sports": "運動",
        "tech": "科技",
        "entertainment": "娛樂",
        "other": "其他",
    },
    "en": {
        "fashion": "Fashion",
        "food": "Food",
        "trend": "Trends",
        "finance": "Finance",
        "sports": "Sports",
        "tech": "Tech",
        "entertainment": "Entertainment",
        "other": "Other",
    },
    "ja": {
        "fashion": "ファッション",
        "food": "グルメ",
        "trend": "トレンド",
        "finance": "金融",
        "sports": "スポーツ",
        "tech": "テック",
        "entertainment": "エンタメ",
        "other": "その他",
    },
}
_STEP3_REG: Dict[str, Dict[str, str]] = {
    "zh-TW": {
        "hong_kong": "香港",
        "taiwan": "台灣",
        "japan": "日本",
        "korea": "韓國",
        "china": "中國",
        "usa": "美國",
        "uk": "英國",
        "global": "全球",
    },
    "en": {
        "hong_kong": "Hong Kong",
        "taiwan": "Taiwan",
        "japan": "Japan",
        "korea": "Korea",
        "china": "China",
        "usa": "USA",
        "uk": "UK",
        "global": "Global",
    },
    "ja": {
        "hong_kong": "香港",
        "taiwan": "台湾",
        "japan": "日本",
        "korea": "韓国",
        "china": "中国",
        "usa": "米国",
        "uk": "英国",
        "global": "グローバル",
    },
}


def build_step3_suggestions(
    language: Optional[str],
    category: Optional[str],
    region: Optional[str],
    custom_keywords: Optional[List[str]] = None,
) -> tuple:
    """精靈 Step 3／後備：依類別＋地區＋關鍵字產生建議名稱與一句描述。"""
    if not category or not region:
        return None, None
    lang = _step3_lang_key(language)
    cats = _STEP3_CAT.get(lang, _STEP3_CAT["en"])
    regs = _STEP3_REG.get(lang, _STEP3_REG["en"])
    cat_label = cats.get(category, category)
    reg_label = regs.get(region, region)
    kws = [
        (k or "").strip()
        for k in (custom_keywords or [])
        if isinstance(k, str) and (k or "").strip()
    ][:3]

    if lang == "zh-TW":
        if kws:
            name = (" · ".join(kws))[:44]
            name = (name + f"（{reg_label}{cat_label}）")[:50]
        else:
            name = (f"{reg_label}{cat_label}小報")[:50]
        desc = (
            f"彙整「{cat_label}」在「{reg_label}」的公開 RSS 動向；收集時會優先使用您在步驟二選取的來源。"
        )[:200]
    elif lang == "ja":
        if kws:
            name = (" · ".join(kws))[:44]
            name = (name + f"（{reg_label}・{cat_label}）")[:50]
        else:
            name = (f"{reg_label}{cat_label}ダイジェスト")[:50]
        desc = (
            f"「{cat_label}」かつ「{reg_label}」向けの公開RSSをまとめます。ステップ2で選んだソースを優先します。"
        )[:200]
    else:
        if kws:
            name = (" · ".join(kws))[:40]
            name = (name + f" ({reg_label} {cat_label})")[:50]
        else:
            name = (f"{reg_label} {cat_label} Digest")[:50]
        desc = (
            f"Tracks {cat_label} in {reg_label} from curated RSS; your Step 2 picks are preferred when collecting."
        )[:200]

    return name, desc


class ChannelAssistService:
    """AI 頻道助手服務"""
    
    def __init__(self):
        self.ai_service = DeepSeekService()

    def _build_dialogue_section(
        self,
        user_input: str,
        language: str,
        conversation_history: List[Dict[str, Any]],
    ) -> str:
        """將多輪對話格式化成 prompt 片段（不含本次 user_input 於 history 內）。"""
        lines: List[str] = []
        for turn in conversation_history[-24:]:
            role = turn.get("role")
            content = (turn.get("content") or "").strip()
            if not content or role not in ("user", "assistant"):
                continue
            if language.startswith("zh"):
                prefix = "使用者" if role == "user" else "助手"
            elif language == "ja":
                prefix = "ユーザー" if role == "user" else "アシスタント"
            else:
                prefix = "User" if role == "user" else "Assistant"
            lines.append(f"{prefix}: {content}")

        block = "\n".join(lines)
        if language.startswith("zh"):
            if block:
                return (
                    "以下是使用者與助手迄今的對話（由舊到新）：\n"
                    f"{block}\n\n"
                    "使用者最新一則訊息如下（請與上文一併理解；若上文已談及類別或地區，"
                    "最新訊息只補充其中一項時，請合併推斷完整 category 與 region）：\n"
                    f"{user_input}"
                )
            return f"用戶輸入：{user_input}"
        if language == "ja":
            if block:
                return (
                    "これまでのユーザーとアシスタントの対話（古い順）：\n"
                    f"{block}\n\n"
                    "最新のユーザー発話（上文と合わせて解釈してください）：\n"
                    f"{user_input}"
                )
            return f"ユーザー入力：{user_input}"
        if block:
            return (
                "Conversation so far (oldest first):\n"
                f"{block}\n\n"
                "Latest user message (interpret together with the above; "
                "if category or region was already implied, merge with short follow-ups):\n"
                f"{user_input}"
            )
        return f"User input: {user_input}"
    
    def _build_assist_prompt(
        self,
        user_input: str,
        language: str = "zh-TW",
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        建立 AI 助手 Prompt
        
        Args:
            user_input: 用戶輸入的自然語言
            language: 用戶語言（zh-TW/en/ja）
            conversation_history: 先前對話（不含本次 user_input）
            
        Returns:
            Prompt 字串
        """
        history = conversation_history or []
        dialogue_section = self._build_dialogue_section(user_input, language, history)

        # 根據語言選擇提示詞
        if language.startswith("zh"):
            prompt_template = """你是一個頻道建立助手。根據用戶的描述，提取以下資訊：

{dialogue_section}

請回傳 JSON 格式：
{{
  "category": "fashion|food|trend|finance|sports|tech|entertainment|other",
  "region": "hong_kong|taiwan|japan|korea|china|usa|uk|global",
  "keywords": ["關鍵字1", "關鍵字2"],
  "confidence": 0.0-1.0,
  "clarification_needed": true|false,
  "clarification_question": "如果需要澄清，問什麼問題",
  "suggested_channel_name": "簡短頻道標題（約 2～24 字；信心足且不需澄清時填寫，否則 null）",
  "suggested_channel_description": "一句話頻道說明（約 20～120 字；否則 null）"
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

{dialogue_section}

JSON形式で返してください：
{{
  "category": "fashion|food|trend|finance|sports|tech|entertainment|other",
  "region": "hong_kong|taiwan|japan|korea|china|usa|uk|global",
  "keywords": ["キーワード1", "キーワード2"],
  "confidence": 0.0-1.0,
  "clarification_needed": true|false,
  "clarification_question": "明確化が必要な場合、何を尋ねるか",
  "suggested_channel_name": "短いチャンネル名（明確で補足不要なときのみ、それ以外は null）",
  "suggested_channel_description": "一文の説明（不要なら null）"
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

{dialogue_section}

Return JSON format:
{{
  "category": "fashion|food|trend|finance|sports|tech|entertainment|other",
  "region": "hong_kong|taiwan|japan|korea|china|usa|uk|global",
  "keywords": ["keyword1", "keyword2"],
  "confidence": 0.0-1.0,
  "clarification_needed": true|false,
  "clarification_question": "What to ask if clarification is needed",
  "suggested_channel_name": "Short channel title when intent is clear (else null)",
  "suggested_channel_description": "One-sentence channel description (else null)"
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
        
        return prompt_template.format(dialogue_section=dialogue_section)
    
    async def parse_user_intent(
        self,
        user_input: str,
        language: str = "zh-TW",
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        解析用戶意圖
        
        Args:
            user_input: 用戶輸入的自然語言
            language: 用戶語言
            conversation_history: 先前對話輪次（不含本次 user_input）
            
        Returns:
            解析結果字典
        """
        try:
            # 建立 Prompt
            prompt = self._build_assist_prompt(
                user_input,
                language,
                conversation_history=conversation_history or [],
            )
            
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
            
            def _clip_opt(val: Any, max_len: int) -> Optional[str]:
                if val is None:
                    return None
                if not isinstance(val, str):
                    return None
                s = val.strip()
                return s[:max_len] if s else None

            # 驗證和標準化結果
            parsed = {
                "category": self._normalize_category(result.get("category")),
                "region": self._normalize_region(result.get("region")),
                "keywords": result.get("keywords", []),
                "confidence": float(result.get("confidence", 0.0)),
                "clarification_needed": bool(result.get("clarification_needed", False)),
                "clarification_question": result.get("clarification_question", ""),
                "suggested_channel_name": _clip_opt(result.get("suggested_channel_name"), 50),
                "suggested_channel_description": _clip_opt(result.get("suggested_channel_description"), 200),
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
                "clarification_question": clarification_question,
                "suggested_channel_name": None,
                "suggested_channel_description": None,
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
                "clarification_question": clarification_question,
                "suggested_channel_name": None,
                "suggested_channel_description": None,
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
        region: Optional[str],
        exclude_urls: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        推薦 RSS 來源（白名單）；可排除已選／已展示之 URL，改取後續候選（再推薦 MVP）。
        """
        if not category or not region:
            return []

        excluded = {
            (u or "").strip()
            for u in (exclude_urls or [])
            if (u or "").strip()
        }

        try:
            cat_enum = ChannelCategory(category)
            region_enum = ChannelRegion(region)

            category_sources = DEFAULT_RSS_SOURCES.get(cat_enum, {})
            region_sources = list(category_sources.get(region_enum, []))

            if not region_sources:
                region_sources = list(category_sources.get(ChannelRegion.GLOBAL, []))

            out: List[Dict[str, Any]] = []
            for src in region_sources:
                if len(out) >= limit:
                    break
                u = (src.get("url") or "").strip()
                if not u or u in excluded:
                    continue
                out.append(dict(src))

            return out

        except (ValueError, KeyError) as e:
            logger.warning(f"無法取得來源推薦: {e}, category={category}, region={region}")
            return []

    def get_wizard_options(
        self,
        step: int,
        category: Optional[str] = None,
        region: Optional[str] = None,
        exclude_urls: Optional[List[str]] = None,
        language: Optional[str] = "zh-TW",
        custom_keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        精靈步驟之結構化選項（檢索 MVP：僅白名單 DEFAULT_RSS / list_default_primary_feeds）。

        quick_options.label_key 供前端 i18n，與 CreateChannel categoryI18nKeys / regionI18nKeys 對齊。
        """
        excluded = {
            (u or "").strip()
            for u in (exclude_urls or [])
            if (u or "").strip()
        }

        if step == 1:
            quick = [
                {
                    "kind": "category",
                    "value": c.value,
                    "label_key": f"channels.category.{c.value}",
                }
                for c in ChannelCategory
            ]
            return {
                "step": 1,
                "retrieval_mvp": "whitelist_default_rss",
                "quick_options": quick,
                "feed_options": [],
                "suggested_channel_name": None,
                "suggested_channel_description": None,
            }

        if step == 2:
            quick = [
                {
                    "kind": "region",
                    "value": r.value,
                    "label_key": f"channels.region.{r.value}",
                }
                for r in ChannelRegion
            ]
            feeds_out: List[Dict[str, str]] = []
            if category and region:
                try:
                    cat_e = ChannelCategory(category)
                    reg_e = ChannelRegion(region)
                    raw = channel_service.list_default_primary_feeds(cat_e, reg_e)
                    for s in raw:
                        u = (s.get("url") or "").strip()
                        if not u or u in excluded:
                            continue
                        feeds_out.append(
                            {
                                "kind": "feed",
                                "name": (s.get("name") or "").strip() or "RSS",
                                "url": u,
                                "role": (s.get("role") or "").strip() or "",
                            }
                        )
                except ValueError:
                    pass
            return {
                "step": 2,
                "retrieval_mvp": "whitelist_default_rss",
                "quick_options": quick,
                "feed_options": feeds_out,
                "suggested_channel_name": None,
                "suggested_channel_description": None,
            }

        # step == 3：命名／描述（#32/#33 後備範本；AI 另見 assist 回傳欄位）
        sn, sd = build_step3_suggestions(language, category, region, custom_keywords)
        return {
            "step": 3,
            "retrieval_mvp": "whitelist_default_rss",
            "quick_options": [],
            "feed_options": [],
            "suggested_channel_name": sn,
            "suggested_channel_description": sd,
        }


# 單例實例
channel_assist_service = ChannelAssistService()

