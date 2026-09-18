"""WWD-like share bar + leading recirc chrome stripping."""
from __future__ import annotations

import unittest

from app.utils.article_boilerplate import clean_extracted_text


_WWD_SAMPLE = """
Elyse Walker談顧客留存、人際關係與重建

跳至主要內容

時尚

獨家：Kris Van Assche發表全新改版的同名系列

配件

De Beers London玩轉鑽石蛋面切割

時尚

Dario Vitale獲任命為Emporio Armani創意總監

Elyse Walker

Allie Joseph/@shotsbyalliej

在Facebook上分享此文

在X上分享此文

在Pin It上分享此文

以電子郵件分享此文

列印此文

Elyse Walker或許已從商27年，但她自14歲起便投入零售業，在母親的店裡為女性穿鞋。時至今日，她的心仍繫於賣場，尤其是試衣間，在那裡她得以為顧客提供她心目中的真正奢華體驗。

「我不認為奢華與價格高低有任何關係。我認為真正的奢華，是與你共事的人告訴你：『你知道嗎，我不覺得你需要那個。』」

相關文章

成衣

獨家：The Róse by Sami Miró以Pacsun獨家品牌之姿登場
"""


class TestWwdBoilerplateClean(unittest.TestCase):
    def test_strips_share_and_leading_recirc(self):
        out = clean_extracted_text(_WWD_SAMPLE)
        self.assertIn("從商27年", out)
        self.assertIn("真正的奢華", out)
        self.assertNotIn("跳至主要內容", out)
        self.assertNotIn("在Facebook上分享此文", out)
        self.assertNotIn("Kris Van Assche", out)
        self.assertNotIn("De Beers", out)
        self.assertNotIn("Emporio Armani", out)
        self.assertNotIn("Allie Joseph", out)
        self.assertNotIn("相關文章", out)
        self.assertNotIn("Pacsun", out)

    def test_english_share_this_article(self):
        raw = (
            "Skip to main content\n"
            "Share this article on Facebook\n"
            "Share this article on X\n"
            "Elyse Walker may have been in business for 27 years, "
            "but she has worked in retail since she was 14.\n"
            "Related Articles\n"
            "Other story here\n"
        )
        out = clean_extracted_text(raw)
        self.assertIn("27 years", out)
        self.assertNotIn("Skip to main content", out)
        self.assertNotIn("Share this article", out)
        self.assertNotIn("Related Articles", out)


if __name__ == "__main__":
    unittest.main()
