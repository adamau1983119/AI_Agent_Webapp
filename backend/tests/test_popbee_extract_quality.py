"""POPBEE-like chrome / mega-menu / CTA / quality / RSS-first."""
from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock

from app.utils.article_boilerplate import clean_extracted_text
from app.utils.article_extract_quality import accept_extracted_body, text_quality
from app.utils.article_body_resolve import resolve_article_body


_POPBEE_SHELL = """
Fashion Beauty Wellness Lifestyle Celebrities Lookbook Streetsnaps Video

加入 POPBEE 會員可以即時閱覽我們的獨家資訊內容，更可享有一系列精彩的尊享禮遇及折扣優惠！立即登記

POPBEE Circle City Guide Popcast
"""

_POPBEE_GOOD = """
這是一篇關於春夏外套剪裁與材質層次的報導。設計師表示今年強調結構，
並在外套內層加入可拆式裡襯，方便香港潮濕天氣穿搭。店內同步推出限定配色，
預計下週於尖沙咀專門店上架，售價尚未公布。
""" * 2

_BRAND_SHORT = "Nike x Off-White 新色波鞋開賣，香港區同步上架。"


class TestPopbeeBoilerplate(unittest.TestCase):
    def test_mega_menu_line_dropped(self):
        out = clean_extracted_text(_POPBEE_SHELL + "\n" + _POPBEE_GOOD)
        self.assertIn("春夏外套", out)
        self.assertNotIn("Lookbook", out)
        self.assertNotIn("加入 POPBEE", out)

    def test_cta_prefix_cuts(self):
        raw = _POPBEE_GOOD + "\n加入 POPBEE 會員尊享禮遇\n後面不該出現的購物文"
        out = clean_extracted_text(raw)
        self.assertIn("春夏外套", out)
        self.assertNotIn("後面不該出現", out)


class TestExtractQuality(unittest.TestCase):
    def test_shell_rejected(self):
        q = text_quality(_POPBEE_SHELL)
        self.assertTrue(q["is_shell"])
        self.assertFalse(accept_extracted_body(_POPBEE_SHELL))

    def test_brand_short_kept(self):
        q = text_quality(_BRAND_SHORT)
        self.assertFalse(q["is_shell"])
        self.assertTrue(accept_extracted_body(_BRAND_SHORT))

    def test_good_zh_kept(self):
        self.assertTrue(accept_extracted_body(_POPBEE_GOOD))


class TestRssFirstResolve(unittest.IsolatedAsyncioTestCase):
    async def test_rss_body_preferred_over_http(self):
        extractor = MagicMock()
        extractor.extract_from_html_content.return_value = {
            "images": ["https://cdn.example/rss.jpg"],
            "original_content": _POPBEE_GOOD,
            "language": "zh-TW",
            "style": {},
            "success": True,
        }
        extractor.extract_article_info = AsyncMock(
            return_value={
                "images": ["https://cdn.example/http.jpg"],
                "original_content": _POPBEE_SHELL,
                "language": "en",
                "style": {},
                "success": False,
            }
        )
        out = await resolve_article_body(
            extractor, "https://example.com/a", rss_html="<p>" + _POPBEE_GOOD + "</p>"
        )
        self.assertIn("春夏外套", out["original_content"] or "")
        extractor.extract_article_info.assert_not_called()

    async def test_http_shell_does_not_block_card_fields(self):
        extractor = MagicMock()
        extractor.extract_from_html_content.return_value = {
            "images": [],
            "original_content": _POPBEE_SHELL,
            "success": False,
        }
        extractor.extract_article_info = AsyncMock(
            return_value={
                "images": [],
                "original_content": _POPBEE_SHELL,
                "success": False,
                "error": "shell",
            }
        )
        out = await resolve_article_body(
            extractor, "https://example.com/b", rss_html=_POPBEE_SHELL
        )
        # Wide-gate: resolve may return empty body; collector still builds card from title.
        self.assertFalse(out.get("success"))


if __name__ == "__main__":
    unittest.main()
