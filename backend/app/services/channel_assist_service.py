"""
AI 頻道助手服務
使用 DeepSeek API 解析用戶自然語言輸入，協助建立頻道
"""
import json
from typing import Optional, Dict, Any, List
from app.services.ai.deepseek import DeepSeekService
from app.models.channel import (
    ChannelCategory, ChannelRegion, DEFAULT_RSS_SOURCES
)
from app.services.channel_assist_policy import ASSIST_CATEGORIES, finalize_intent
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
        catalog = "|".join(sorted(ASSIST_CATEGORIES))
        if language.startswith("zh"):
            role = (
                "你是頻道定位專家。語氣肯定，不追問。"
                "只輸出 JSON，不要解釋。"
            )
        elif language == "ja":
            role = (
                "あなたはチャンネル設計の専門家です。断定し、質問で返さない。"
                "JSON だけを出力する。"
            )
        else:
            role = (
                "You are a channel strategist. Be decisive and do not ask follow-up questions. "
                "Return JSON only."
            )
        return f"""{role}

{dialogue_section}

Pick one primary category, only from: {catalog}.
If the topic is outside these 11 (including lego, cosplay, other, pets, politics), set category to null and out_of_catalog to true.
Regions may only be hong_kong|taiwan|japan|korea|china|usa|uk|global.
If no region is stated, or the region is outside those eight, set region to global and region_defaulted to true. Never say there is no source list.
If the user explicitly asks for global, set region to global and region_defaulted to false.
If several categories or regions appear, keep only the primary pair and set split_channel to true.
clarification_needed must be false. suggested_channel_name and suggested_channel_description must be null.

{{
  "category": "{catalog}|null",
  "region": "hong_kong|taiwan|japan|korea|china|usa|uk|global",
  "keywords": ["keyword"],
  "confidence": 0.9,
  "out_of_catalog": false,
  "region_defaulted": false,
  "split_channel": false,
  "clarification_needed": false,
  "clarification_question": null,
  "suggested_channel_name": null,
  "suggested_channel_description": null
}}"""

    
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
            parsed = finalize_intent(result)
            logger.info(f"AI 解析結果: {parsed}")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {e}, 回應: {response[:200]}")
            return finalize_intent({})
        except Exception as e:
            logger.error(f"AI 解析錯誤: {e}")
            return finalize_intent({})
    
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
            hidden = {
                ChannelCategory.LEGO,
                ChannelCategory.COSPLAY,
                ChannelCategory.OTHER,
            }
            quick = [
                {
                    "kind": "category",
                    "value": c.value,
                    "label_key": f"channels.category.{c.value}",
                }
                for c in ChannelCategory
                if c not in hidden
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

