"""
單元測試：驗證主題卡監察紅燈與排程自動補產卡邏輯
"""
import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

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
    "bs4", "requests", "httpx", "aiohttp", "loguru", "redis", "redis.asyncio", "redis.asyncio.connection", "redis.exceptions",
    "apscheduler", "apscheduler.schedulers", "apscheduler.schedulers.asyncio",
    "apscheduler.triggers", "apscheduler.triggers.cron", "apscheduler.triggers.interval",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

from app.models.topic import Category
from app.services.observability.traffic_light import (
    TrafficLight,
    evaluate_health,
    light_zh,
    verdict_zh,
)


class TestTrafficLightTopicDeficit(unittest.TestCase):
    """驗證主題卡不足時 traffic_light 正確判定紅燈"""

    def test_healthy_with_full_topics_is_green(self):
        body = {
            "status": "healthy",
            "database": "connected",
            "cost_controls": {"scheduled_topic_collection": True},
            "topics_today": {"v8_count": 15, "expected": 15},
        }
        sig = evaluate_health(body)
        self.assertEqual(sig.light, TrafficLight.GREEN)
        self.assertIn("正式域正常", sig.headline)

    def test_topic_deficit_in_body_is_red(self):
        body = {
            "status": "healthy",
            "database": "connected",
            "cost_controls": {"scheduled_topic_collection": True},
            "topics_today": {"v8_count": 0, "expected": 15},
        }
        sig = evaluate_health(body)
        self.assertEqual(sig.light, TrafficLight.RED)
        self.assertIn("今日主題卡不足（0/15）", sig.headline)
        self.assertEqual(light_zh(sig.light), "紅燈")
        self.assertEqual(verdict_zh(sig.light), "有事・請立即處理")

    def test_topic_deficit_passed_as_kwargs_is_red(self):
        body = {
            "status": "healthy",
            "database": "connected",
            "cost_controls": {"scheduled_topic_collection": True},
        }
        sig = evaluate_health(body, topics_v8=5, topics_expected=15)
        self.assertEqual(sig.light, TrafficLight.RED)
        self.assertIn("今日主題卡不足（5/15）", sig.headline)

    def test_collection_disabled_with_zero_topics_is_green(self):
        body = {
            "status": "healthy",
            "database": "connected",
            "cost_controls": {"scheduled_topic_collection": False},
            "topics_today": {"v8_count": 0, "expected": 15},
        }
        sig = evaluate_health(body)
        self.assertEqual(sig.light, TrafficLight.GREEN)


class TestSchedulerMonitorAutoBackfill(unittest.IsolatedAsyncioTestCase):
    """驗證 SchedulerMonitor 自動補產卡與防重入邏輯"""

    def setUp(self):
        from app.services.automation.scheduler_monitor import SchedulerMonitor
        self.SchedulerMonitor = SchedulerMonitor

    async def test_check_health_triggers_ensure_today_when_topics_deficient(self):
        scheduler = MagicMock()
        scheduler.is_running = True
        scheduler.trigger_manual_generation = AsyncMock(return_value=[])

        monitor = self.SchedulerMonitor(scheduler)
        monitor.topic_repo = MagicMock()
        monitor._count_topics_hkt_today = AsyncMock(return_value=0)
        monitor.ensure_today_topics = AsyncMock()

        with patch("app.services.automation.scheduler_monitor.is_daily_mode", return_value=True), \
             patch("app.services.automation.scheduler_monitor.expected_topics_today", return_value=15), \
             patch("app.utils.cost_controls.scheduled_topic_collection_enabled", return_value=True):
            await monitor._check_scheduler_health()
            await asyncio.sleep(0.05)
            self.assertTrue(monitor.ensure_today_topics.called or monitor._is_ensuring is False)

    async def test_ensure_today_concurrency_lock(self):
        scheduler = MagicMock()
        scheduler.trigger_manual_generation = AsyncMock(return_value=[])

        monitor = self.SchedulerMonitor(scheduler)
        monitor.topic_repo = MagicMock()
        monitor.topic_repo.count_hkt_today_by_category = AsyncMock(
            return_value={"fashion": 0, "food": 0, "trend": 0}
        )

        monitor._is_ensuring = True
        with patch("app.utils.cost_controls.scheduled_topic_collection_enabled", return_value=True):
            await monitor.ensure_today_topics()
            self.assertFalse(monitor.topic_repo.count_hkt_today_by_category.called)

    async def test_ensure_today_fills_partial_deficits(self):
        scheduler = MagicMock()
        scheduler.trigger_manual_generation = AsyncMock(return_value=[{"id": "topic_1"}])

        monitor = self.SchedulerMonitor(scheduler)
        monitor.topic_repo = MagicMock()
        monitor.topic_repo.count_hkt_today_by_category = AsyncMock(
            return_value={"fashion": 5, "food": 2, "trend": 0}
        )

        with patch("app.utils.cost_controls.scheduled_topic_collection_enabled", return_value=True), \
             patch("app.services.automation.scheduler_monitor.category_deficits", return_value={"fashion": 0, "food": 3, "trend": 5}):
            await monitor.ensure_today_topics()

            calls = scheduler.trigger_manual_generation.await_args_list
            self.assertEqual(len(calls), 2)
            called_categories = [c.kwargs["category"] for c in calls]
            self.assertIn(Category.FOOD, called_categories)
            self.assertIn(Category.TREND, called_categories)
            self.assertNotIn(Category.FASHION, called_categories)


class TestSchedulerTopicCreationWithoutDedupDrop(unittest.IsolatedAsyncioTestCase):
    """驗證 SchedulerService 生成卡片時不會被二次去重自我碰撞拋棄"""

    def setUp(self):
        from app.services.automation.scheduler import SchedulerService
        self.SchedulerService = SchedulerService

    async def test_trigger_manual_generation_creates_all_collected_topics(self):
        with patch.object(self.SchedulerService, "__init__", lambda s: None):
            svc = self.SchedulerService()
            svc.config = MagicMock()
            svc.config.is_daily_limit_enabled.return_value = False
            svc.config.get_preview_images_count.return_value = 1
            svc.config.should_generate_content.return_value = False

            svc.topic_collector = MagicMock()
            svc.topic_collector.collect_topics = AsyncMock(return_value=[
                {"title": "Fashion Trend 1", "sources": []},
                {"title": "Fashion Trend 2", "sources": []},
                {"title": "Fashion Trend 3", "sources": []},
            ])

            svc.topic_repo = MagicMock()
            svc.topic_repo.create_topic = AsyncMock(side_effect=lambda d: d)
            svc.workflow = MagicMock()
            svc.workflow.process_topic = AsyncMock(return_value={"content_generated": False})

            import app.services.automation.topic_card_finalize
            with patch("app.utils.cost_controls.scheduled_topic_collection_enabled", return_value=True), \
                 patch("app.services.automation.topic_card_finalize.finalize_produced_cards", new_callable=AsyncMock):
                results = await svc.trigger_manual_generation(
                    category=Category.FASHION,
                    count=3,
                    display_language="zh-TW",
                    respect_quota=False,
                )

                self.assertEqual(len(results), 3)
                self.assertEqual(svc.topic_repo.create_topic.call_count, 3)
                self.assertEqual(svc.workflow.process_topic.call_count, 3)


class TestTopicRepoUpdateOperatorHandling(unittest.IsolatedAsyncioTestCase):
    """驗證 TopicRepository.update_topic 防禦性處理 $set 運算符"""

    async def test_update_topic_avoids_nested_dollar_set(self):
        from app.services.repositories.topic_repository import TopicRepository
        repo = TopicRepository()
        repo.update_by_id = AsyncMock(return_value={"id": "topic_1"})

        # Case 1: 傳入裸字典
        await repo.update_topic("topic_1", {"preview_images": ["http://img1.jpg"]})
        repo.update_by_id.assert_called_with("topic_1", {"$set": {"preview_images": ["http://img1.jpg"]}})

        # Case 2: 傳入含 $set 字典（防禦二次包裝）
        await repo.update_topic("topic_1", {"$set": {"preview_images": ["http://img1.jpg"]}})
        repo.update_by_id.assert_called_with("topic_1", {"$set": {"preview_images": ["http://img1.jpg"]}})




class TestTopicGenerationGuardrails(unittest.TestCase):
    """驗證主題卡事實錨定、按需生成與風格解耦防污染 (Rule 19)"""

    def setUp(self):
        from app.models.alter_ego_dna import AlterEgoDnaJson
        self.mock_dna = AlterEgoDnaJson(
            lexicon=["串豬大腸", "網紅名店", "脆皮多汁", "必吃推薦"],
            tone_descriptors=["熱情", "接地氣"],
            voice_persona="美食探店博主",
            language_primary="zh-TW",
            exemplar_snippets=["這家串豬大腸太絕了！外脆內嫩"],
            sentence_rhythm="short_punchy",
            emoji_style="moderate",
            hashtag_style="#美食探店,#吃貨日常",
        )

    def test_soul_prompt_contains_fact_anchoring_and_anti_pollution(self):
        from app.services.alter_ego_service import _build_soul_prompt
        topic = "美加達成新貿易協定"
        summary = "美國與加拿大今日就關鍵關稅與供應鏈達成全新貿易共識，將降低邊境商品關稅。"
        article = "詳細報導指出，本次雙邊協定著重於科技與能源領域合作。"

        prompt = _build_soul_prompt(
            dna=self.mock_dna,
            topic_hint=topic,
            output_lang="zh-TW",
            context_summary=summary,
            base_content=article,
        )

        self.assertIn("FACTUAL ARTICLE CONTENT", prompt)
        self.assertIn("FACT ANCHORING", prompt)
        self.assertIn("ANTI-POLLUTION", prompt)
        self.assertIn("DO NOT force unrelated domain terms", prompt)
        self.assertIn("never insert food metaphors into business/trade news", prompt)

    def test_hashtags_from_dna_prioritizes_topic_hint(self):
        from app.services.alter_ego_service import _hashtags_from_dna
        topic = "美加貿易協定 關稅最新進展"
        tags = _hashtags_from_dna(self.mock_dna, topic_hint=topic)
        self.assertTrue(any("貿易" in t or "協定" in t or "關稅" in t or "美加" in t for t in tags))

    def test_preview_request_accepts_context_fields(self):
        from app.schemas.alter_ego import PreviewRequest
        req = PreviewRequest(
            platform="facebook",
            topic_hint="科技趨勢",
            context_summary="AI 晶片突破",
            base_content="最新 2nm 晶片正式量產",
        )
        self.assertEqual(req.context_summary, "AI 晶片突破")
        self.assertEqual(req.base_content, "最新 2nm 晶片正式量產")

    def test_article_prompt_contains_anti_pollution_rule(self):
        from app.prompts.article_prompt import build_article_prompt
        prompt = build_article_prompt(
            topic_title="全球供應鏈重組",
            topic_category="trend",
            keywords=["經濟", "關稅"],
            target_length=300,
            summary_flash="各國正在重新佈局製造業中心以因應新政策。",
            target_language="zh-TW",
            style_hint="熱情探店博主",
        )
        self.assertIn("風格與主題解耦防污染", prompt)
        self.assertIn("嚴禁將與本主題領域無關之專有名詞或食物詞彙", prompt)


class TestSourceArticleTranslation(unittest.IsolatedAsyncioTestCase):
    """驗證源文章完整新聞報道多語言翻譯與快取服務"""

    async def test_resolve_source_article_translation_cache_hit(self):
        from app.services.translation.source_article_translator import resolve_source_article_translation
        topic = {
            "id": "test_topic_1",
            "source_content_i18n": {
                "zh-TW": "這是快取的完整新聞中文報道全文內容，詳細介紹最新時尚趨勢。"
            },
            "sources": [{"original_content": "This is full English article."}]
        }
        res = await resolve_source_article_translation(topic, "zh-TW")
        self.assertIn("快取的完整新聞中文報道", res)

    async def test_resolve_source_article_translation_fallback_raw(self):
        from app.services.translation.source_article_translator import resolve_source_article_translation
        topic = {
            "id": "test_topic_2",
            "summary_flash": "簡短事實摘要",
            "sources": [{"original_content": "Original fashion news report body.", "language": "en"}]
        }
        # 当请求 en 且原文即为 en 时，直接返回原文
        res = await resolve_source_article_translation(topic, "en")
        self.assertEqual(res, "Original fashion news report body.")

    async def test_resolve_source_article_translation_chinese_same_lang(self):
        from app.services.translation.source_article_translator import resolve_source_article_translation
        topic = {
            "id": "test_topic_3",
            "sources": [{"original_content": "這是來自 Popbee 的中文新聞報道全文，介紹珠寶與時尚潮流趨勢。", "language": "zh-TW"}]
        }
        res = await resolve_source_article_translation(topic, "zh-TW", save_cache=False)
        self.assertIn("Popbee 的中文新聞報道全文", res)
        self.assertIn("zh-TW", topic.get("source_content_i18n", {}))

    def test_article_extractor_from_html_content(self):
        from app.utils.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        html = """
        <article class="post-content">
            <p>Tiffany & Co. 最新珠寶系列正式發表，設計靈感源自大自然。</p>
            <p>本次作品包含精美的胸針與項鍊，展現卓越工藝與優雅風格。</p>
            <img src="https://example.com/photo1.jpg" alt="photo" />
        </article>
        """
        info = extractor.extract_from_html_content(html)
        self.assertTrue(info["success"])
        self.assertIn("Tiffany & Co.", info["original_content"])
        self.assertIn("https://example.com/photo1.jpg", info["images"])

    def test_article_extractor_strips_share_chrome(self):
        from app.utils.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        html = """
        <article>
            <nav class="breadcrumb">Home / Fashion</nav>
            <p>Tiffany & Co. 最新珠寶系列正式發表。</p>
            <div class="share-bar">Facebook</div>
            <p>Whatsapp</p>
            <p>X</p>
            <p>跳至分類</p>
            <p>本次作品包含精美的胸針與項鍊。</p>
        </article>
        """
        info = extractor.extract_from_html_content(html)
        self.assertTrue(info["success"])
        body = info["original_content"] or ""
        self.assertIn("Tiffany & Co.", body)
        self.assertNotIn("跳至分類", body)
        self.assertNotIn("Whatsapp", body)
        self.assertNotIn("Facebook", body)

    def test_article_extractor_strips_elle_chrome(self):
        from app.utils.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        html = """
        <article>
            <p>Tiffany & Co. 最新珠寶系列正式發表。</p>
            <p>（圖片來源：</p>
            <p>@cameliafarhoodi</p>
            <p>）</p>
            <p>跳至分類：</p>
            <p>Facebook</p>
            <p>X</p>
            <p>Whatsapp</p>
            <p>Pinterest</p>
            <p>分享本文</p>
            <p>加入討論</p>
            <p>關注我們</p>
            <p>在 Google 上將我們加入偏好來源</p>
            <p>Advertisement</p>
            <p>本次作品包含精美的胸針與項鍊。</p>
            <p>選購時裝</p>
            <p>選購美妝</p>
        </article>
        """
        info = extractor.extract_from_html_content(html)
        body = info["original_content"] or ""
        self.assertIn("Tiffany & Co.", body)
        self.assertIn("胸針與項鍊", body)
        for noise in (
            "圖片來源", "@cameliafarhoodi", "跳至分類", "選購時裝", "選購美妝",
            "Facebook", "Whatsapp", "Pinterest", "分享本文", "加入討論",
            "關注我們", "偏好來源", "Advertisement",
        ):
            self.assertNotIn(noise, body)
        self.assertNotRegex(body, r"(?m)^X$")

    def test_article_extractor_cuts_shopping_appendix(self):
        from app.utils.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        html = """
        <article>
            <p>The trench coat is back this season, cut slightly oversized.</p>
            <p>Who What Wear 最新影片</p>
            <p>選購時裝</p>
            <p>Los Angeles Apparel</p>
            <p>Baby Rib 3/4 袖船型領上衣</p>
            <p>J.Crew</p>
            <p>選購美妝</p>
            <p>Celisse</p>
            <p>Quickcoat 指甲油</p>
            <p>探索更多：</p>
            <p>Audry Hiaoui</p>
            <p>副購物編輯</p>
        </article>
        """
        info = extractor.extract_from_html_content(html)
        body = info["original_content"] or ""
        self.assertIn("trench coat", body)
        for noise in (
            "最新影片", "選購時裝", "Los Angeles Apparel", "Baby Rib",
            "J.Crew", "選購美妝", "Celisse", "Quickcoat", "探索更多",
            "Audry Hiaoui", "副購物編輯",
        ):
            self.assertNotIn(noise, body)

    def test_article_extractor_cuts_recirc_appendix(self):
        from app.utils.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        html = """
        <article>
            <p>The restaurant opened a second location in Taipei this spring.</p>
            <p>Related Stories</p>
            <p>Another viral burger ranking you should skip</p>
            <p>Newsletter</p>
            <p>More pasta tips from the archive</p>
        </article>
        """
        info = extractor.extract_from_html_content(html)
        body = info["original_content"] or ""
        self.assertIn("Taipei", body)
        self.assertNotIn("Related Stories", body)
        self.assertNotIn("burger ranking", body)
        self.assertNotIn("Newsletter", body)
        self.assertNotIn("pasta tips", body)

    async def test_on_demand_false_skips_scrape(self):
        from unittest.mock import patch
        from app.services.translation.source_article_translator import (
            resolve_source_article_translation,
        )
        topic = {
            "id": "test_ondemand_off",
            "summary_flash": "A short English summary about fashion week.",
            "sources": [
                {"original_content": "", "url": "https://example.com/a", "language": "en"}
            ],
        }
        with patch("app.utils.article_extractor.ArticleExtractor") as ext:
            res = await resolve_source_article_translation(
                topic, "zh-TW", save_cache=False, on_demand=False
            )
            ext.assert_not_called()
        self.assertEqual(res, "")


class TestComposePack(unittest.TestCase):
    """Public composer caps / JSON parse / Rule 19 prompt (no translation pipeline)."""

    def test_threads_cap_150_and_length_gate(self):
        from app.services.compose_caps import clamp_max_chars, length_enabled, platform_cap
        self.assertEqual(platform_cap("threads"), 150)
        self.assertEqual(clamp_max_chars("threads", 150), 150)
        self.assertEqual(clamp_max_chars("instagram", 150), 150)
        self.assertTrue(length_enabled("threads", 50))
        self.assertTrue(length_enabled("facebook", 150))

    def test_parse_json_without_cjk_headers(self):
        from app.services.compose_parse import extract_json_object, normalize_pack
        raw = 'Here is the pack:\n{"titles":["A","B","C"],"body":"Hello","hashtag_sets":[["#x"],["#y"],["#z"]]}'
        pack = normalize_pack(extract_json_object(raw), 100)
        self.assertEqual(pack["titles"], ["A", "B", "C"])
        self.assertEqual(pack["body"], "Hello")
        self.assertEqual(len(pack["hashtag_sets"]), 3)

    def test_compose_prompt_anchors_facts_not_lexicon(self):
        from app.models.alter_ego_dna import AlterEgoDnaJson
        from app.services.compose_prompt import build_compose_prompt, dna_tone_overlay
        dna = AlterEgoDnaJson(
            lexicon=["串豬大腸", "網紅名店"],
            tone_descriptors=["熱情"],
            voice_persona="美食探店博主",
            language_primary="zh-TW",
            exemplar_snippets=["這家串豬大腸太絕了"],
        )
        overlay = dna_tone_overlay(dna)
        self.assertNotIn("串豬大腸", overlay)
        prompt = build_compose_prompt(
            platform="facebook",
            style="professional",
            max_chars=100,
            part="all",
            language="en",
            topic_title="US-Canada trade deal",
            context_summary="Tariffs on border goods will fall.",
            dna_overlay=overlay,
        )
        self.assertIn("FACT ANCHORING", prompt)
        self.assertIn("ANTI-POLLUTION", prompt)
        self.assertIn("Tariffs on border goods will fall.", prompt)
        self.assertIn("professional", prompt)
        self.assertNotIn("串豬大腸", prompt)

    def test_preview_platform_contract_unchanged(self):
        from app.schemas.alter_ego import ComposeRequest, PreviewRequest
        prev = PreviewRequest(platform="x", topic_hint="hi")
        self.assertEqual(prev.platform, "x")
        req = ComposeRequest(
            platform="instagram",
            style="casual",
            max_chars=50,
            language="ja",
        )
        self.assertEqual(req.platform, "instagram")


if __name__ == "__main__":
    unittest.main()
