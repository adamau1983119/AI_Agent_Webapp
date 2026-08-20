"""
單元測試：驗證中日英多語言標題腳本檢測、成套快取驗證與 Content Locale Overlay 邏輯
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Mock external dependencies if not installed in local environment
if "pydantic_settings" not in sys.modules:
    mock_ps = MagicMock()
    class DummyBaseSettings:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    mock_ps.BaseSettings = DummyBaseSettings
    mock_ps.SettingsConfigDict = dict
    sys.modules["pydantic_settings"] = mock_ps

for mod in [
    "yaml", "pytz", "bson", "pymongo", "pymongo.errors", "motor", "motor.motor_asyncio",
    "bs4", "requests", "httpx", "aiohttp", "loguru",
    "apscheduler", "apscheduler.schedulers", "apscheduler.schedulers.asyncio",
    "apscheduler.triggers", "apscheduler.triggers.cron", "apscheduler.triggers.interval",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

from app.utils.topic_languages import (
    title_matches_display_language,
    title_script_mismatch,
    usable_cached_title,
    normalize_topic_language,
)
from app.services.translation.flash_pack_provider import _pack_ok
from app.services.content_locale.topic_locale_resolver import apply_locale_overlay


class TestTopicLanguagesScriptDetection(unittest.TestCase):
    """驗證中日英標題腳本檢測正確性"""

    def test_chinese_title_matches_zh_and_fails_ja_and_en(self):
        zh_titles = [
            "這款婚宴賓客禮服趨勢將定義2026年秋季",
            "美國貿易沙皇對加拿大貿易協議「最終結果非常滿意」，但細節仍舊寥寥無幾",
            "Rosé 同款必須加入願望清單！Tiffany & Co. 全新「石上鳥」羽翼珠寶太浪漫",
            "adidas Originals 為寵物穿上皇家馬德里和曼聯球衣",
            "據傳葛妮絲·派特洛將為AI大亨山姆·奧特曼舉辦派對。外界對這種觀感不太買單",
            "馬斯克預計將他的金錢機器指向德州政治",
        ]
        for title in zh_titles:
            self.assertTrue(
                title_matches_display_language(title, "zh-TW"),
                f"Should match zh-TW: {title}",
            )
            self.assertFalse(
                title_matches_display_language(title, "ja"),
                f"Chinese title should NOT match ja: {title}",
            )
            self.assertTrue(
                title_script_mismatch(title, "ja"),
                f"Should be script mismatch for ja: {title}",
            )

    def test_japanese_title_matches_ja_and_fails_en(self):
        ja_titles = [
            "『フラグメント』第5話についての52の考え",
            "ハッシュブラウンでもワッフルでもない：ワッフルハウスで最も売れているメニュー項目に驚くかもしれない",
            "焼きフェタチーズのグリーンソースパスタ",
            "健康的な食事計画の立て方",
            "60歳以降、キッチンカウンターでできる5つのエクササイズがレッグプレスより速く膝の力を再構築する",
            "なぜアンソニー・ボーデインの編集者は「トニー」をもっと暗くしたかったのか",
            "ストライプがOpenRouterを買収したのは「シンギュラリティ」のせいではない",
            "NASA、スウィフトガンマ線観測衛星の救出ミッションを中止",
            "カナダへの新たな関税は当面なし",
        ]
        for title in ja_titles:
            self.assertTrue(
                title_matches_display_language(title, "ja"),
                f"Should match ja: {title}",
            )
            self.assertFalse(
                title_script_mismatch(title, "ja"),
                f"Should NOT be script mismatch for ja: {title}",
            )
            self.assertFalse(
                title_matches_display_language(title, "en"),
                f"Japanese title should NOT match en: {title}",
            )

    def test_english_sentence_matches_en_and_fails_ja_and_zh(self):
        en_titles = [
            "NASA Cancels Mission to Rescue Swift Gamma-Ray Observatory",
            "This Wedding-Guest Dress Trend Will Define Fall 2026",
            "Elon Musk Is Expected to Point His Money Machine at Texas Politics",
            "Why Anthony Bourdain’s Editor Wanted ‘Tony’ to Be Darker",
        ]
        for title in en_titles:
            self.assertTrue(
                title_matches_display_language(title, "en"),
                f"Should match en: {title}",
            )
            self.assertFalse(
                title_matches_display_language(title, "ja"),
                f"English sentence should NOT match ja: {title}",
            )
            self.assertFalse(
                title_matches_display_language(title, "zh-TW"),
                f"English sentence should NOT match zh-TW: {title}",
            )

    def test_short_brand_acronym_allowed_in_ja(self):
        self.assertTrue(title_matches_display_language("NASA", "ja"))
        self.assertTrue(title_matches_display_language("OpenAI", "ja"))

    def test_usable_cached_title_with_target_lang(self):
        # 繁體中文存入 ja 時應判定為 None (不可用)
        self.assertIsNone(
            usable_cached_title("這款婚宴賓客禮服趨勢將定義2026年秋季", "ja")
        )
        # 繁體中文在 zh-TW 應可用
        self.assertEqual(
            usable_cached_title("這款婚宴賓客禮服趨勢將定義2026年秋季", "zh-TW"),
            "這款婚宴賓客禮服趨勢將定義2026年秋季",
        )
        # 正確日語在 ja 應可用
        self.assertEqual(
            usable_cached_title("『フラグメント』第5話についての52の考え", "ja"),
            "『フラグメント』第5話についての52の考え",
        )


class TestLocaleOverlayBehavior(unittest.TestCase):
    """驗證 apply_locale_overlay 拒絕損壞快取並正確標記 locale_resolved"""

    def test_overlay_rejects_chinese_cache_when_ui_is_ja(self):
        topic = {
            "id": "test_1",
            "title": "這款婚宴賓客禮服趨勢將定義2026年秋季",
            "description": "This Wedding-Guest Dress Trend",
            "display_language": "zh-TW",
            "titles_i18n": {
                "zh-TW": "這款婚宴賓客禮服趨勢將定義2026年秋季",
                "en": "This Wedding-Guest Dress Trend Will Define Fall 2026",
                "ja": "這款婚宴賓客禮服趨勢將定義2026年秋季",  # 錯誤的中文快取
            },
            "description_i18n": {
                "zh-TW": "這款婚宴賓客禮服趨勢",
                "en": "This Wedding-Guest Dress Trend",
                "ja": "このウェディングゲストドレスのトレンド",
            },
        }
        res = apply_locale_overlay(topic, "ja")
        # 應標記為未解決，避免前端直接顯示中文
        self.assertFalse(res["locale_resolved"])
        self.assertEqual(res["content_locale"], "zh-TW")

    def test_overlay_accepts_valid_japanese_cache(self):
        topic = {
            "id": "test_2",
            "title": "關於《碎片》第五集的52個想法",
            "description": "52 Thoughts I Had",
            "display_language": "zh-TW",
            "titles_i18n": {
                "zh-TW": "關於《碎片》第五集的52個想法",
                "en": "52 Thoughts I Had About Episode 5 of 'Fragments'",
                "ja": "『フラグメント』第5話についての52の考え",
            },
            "description_i18n": {
                "zh-TW": "關於《碎片》第五集的52個想法",
                "en": "52 Thoughts I Had",
                "ja": "エピソードについての52の考え",
            },
        }
        res = apply_locale_overlay(topic, "ja")
        self.assertTrue(res["locale_resolved"])
        self.assertEqual(res["content_locale"], "ja")
        self.assertEqual(res["title"], "『フラグメント』第5話についての52の考え")
        self.assertEqual(res["description"], "エピソードについての52の考え")


class TestFlashPackValidation(unittest.TestCase):
    """驗證 DeepSeek Flash 翻譯回傳結果檢查"""

    def test_pack_ok_rejects_mismatched_target_language(self):
        # 翻譯至 ja 但標題仍為中文，_pack_ok 必須拒絕
        ok = _pack_ok(
            title="這款婚宴賓客禮服趨勢將定義2026年秋季",
            desc="このウェディングゲストドレスのトレンド",
            need_desc=True,
            target_lang="ja",
        )
        self.assertFalse(ok)

    def test_pack_ok_accepts_matched_target_language(self):
        ok = _pack_ok(
            title="『フラグメント』第5話についての52の考え",
            desc="エピソードについての52の考え",
            need_desc=True,
            target_lang="ja",
        )
        self.assertTrue(ok)


class TestInspirationMultilingualParsing(unittest.TestCase):
    """驗證靈感策劃 AI 回應多語言正則解析與降級機制"""

    def test_parse_chinese_inspiration(self):
        from app.services.inspiration_service import InspirationService
        svc = InspirationService()
        raw_zh = """靈感1: 2026年東京潮流穿搭指南
描述: 探索原宿與澀谷最新街頭風格。

靈感2: 必吃米其林拉麵特輯
描述: 嚴選五大東京頂級拉麵名店。"""
        results = svc._parse_ai_response(raw_zh, 5)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "2026年東京潮流穿搭指南")
        self.assertEqual(results[0]["description"], "探索原宿與澀谷最新街頭風格。")

    def test_parse_english_inspiration(self):
        from app.services.inspiration_service import InspirationService
        svc = InspirationService()
        raw_en = """Inspiration 1: 2026 Tokyo Fashion Trend Guide
Description: Explore the latest street style in Harajuku and Shibuya.

Inspiration 2: Top Michelin Ramen Special
Description: Curated guide to five top ramen shops in Tokyo."""
        results = svc._parse_ai_response(raw_en, 5)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "2026 Tokyo Fashion Trend Guide")
        self.assertEqual(results[0]["description"], "Explore the latest street style in Harajuku and Shibuya.")

    def test_parse_japanese_inspiration(self):
        from app.services.inspiration_service import InspirationService
        svc = InspirationService()
        raw_ja = """アイディア1: 2026年東京トレンドファッションガイド
説明: 原宿と渋谷の最新ストリートスタイルを徹底解説。

アイディア2: ミシュラン掲載ラーメン特集
概要: 東京の厳選ラーメン店5選。"""
        results = svc._parse_ai_response(raw_ja, 5)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "2026年東京トレンドファッションガイド")
        self.assertEqual(results[0]["description"], "原宿と渋谷の最新ストリートスタイルを徹底解説。")

    def test_parse_fallback_unstructured(self):
        from app.services.inspiration_service import InspirationService
        svc = InspirationService()
        raw_unstructured = """1. 2026年東京潮流穿搭
這是詳細的第一段靈感介紹。

2. 必吃拉麵特輯
這是詳細的第二段靈感介紹。"""
        results = svc._parse_ai_response(raw_unstructured, 5)
        self.assertEqual(len(results), 2)
        self.assertIn("2026年東京潮流穿搭", results[0]["title"])


class TestTopicRepositoryMultilingualSearchFilter(unittest.TestCase):
    """驗證 TopicRepository 多語言搜尋 Filter 結構"""

    def test_search_clauses_include_multilingual_fields(self):
        # 建立模擬測試，不依賴資料庫連線
        from app.services.repositories.topic_repository import TopicRepository
        # 檢驗 list_topics 中的 clauses 構造
        search_query = "wedding"
        expected_fields = [
            "title",
            "original_title",
            "source",
            "titles_i18n.ja",
            "titles_i18n.en",
            "titles_i18n.zh-TW",
        ]
        # 驗證 topic_repository 代碼中確實構造了上述子句
        import inspect
        src = inspect.getsource(TopicRepository.list_topics)
        for field in expected_fields:
            self.assertIn(f'"{field}"', src, f"Search clause must include field '{field}'")


if __name__ == "__main__":
    unittest.main()
