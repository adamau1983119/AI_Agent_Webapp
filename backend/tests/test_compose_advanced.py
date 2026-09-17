"""Unit tests for compose caps / parse / tone (no live LLM)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.compose_caps import (
    HASHTAG_HINTS,
    LENGTH_CHOICES,
    clamp_max_chars,
    compose_credit_cost,
    length_enabled,
)
from app.services.compose_parse import enforce_hashtag_bounds, normalize_pack
from app.services.compose_prompt import build_compose_prompt
from app.services.compose_tone import tone_card
from app.services.ops_trainer_inject import map_max_chars_to_length


class TestComposeAdvanced(unittest.TestCase):
    def test_length_choices_ig_fb(self):
        self.assertEqual(LENGTH_CHOICES, (500, 1500))
        self.assertTrue(length_enabled("facebook", 500))
        self.assertTrue(length_enabled("instagram", 1500))
        self.assertFalse(length_enabled("threads", 1500))
        self.assertEqual(clamp_max_chars("instagram", 1500), 1500)
        self.assertEqual(clamp_max_chars("facebook", 999), 500)
        self.assertEqual(compose_credit_cost(500), 1)
        self.assertEqual(compose_credit_cost(1500), 2)
        self.assertEqual(map_max_chars_to_length(500), "short")
        self.assertEqual(map_max_chars_to_length(1500), "long")

    def test_hashtag_bounds(self):
        self.assertEqual(HASHTAG_HINTS["instagram"], (3, 5))
        self.assertEqual(HASHTAG_HINTS["facebook"], (3, 5))
        sets = enforce_hashtag_bounds(
            [["#a"]], "instagram", fact="luxury tote craft", title="Tote"
        )
        self.assertEqual(len(sets), 3)
        self.assertGreaterEqual(len(sets[0]), 3)
        self.assertLessEqual(len(sets[0]), 5)

    def test_normalize_pads_tags(self):
        pack = normalize_pack(
            {"titles": ["T1"], "body": "x" * 20, "hashtag_sets": [["#one"]]},
            500,
            platform="facebook",
            fact="canvas leather commute",
            topic_title="Tote bag",
        )
        self.assertEqual(len(pack["titles"]), 3)
        self.assertGreaterEqual(len(pack["hashtag_sets"][0]), 3)

    def test_prompt_includes_tone_and_keep(self):
        p = build_compose_prompt(
            platform="instagram",
            style="humorous",
            max_chars=500,
            part="body",
            language="zh-TW",
            topic_title="Tote",
            context_summary="Canvas commute bag.",
            dna_overlay="",
            preserve_snippets=["我只信摸得到的工藝"],
            revision_intent="把你的句子放開頭",
            base_body="舊正文保留測",
        )
        self.assertIn("Tone card", p)
        self.assertIn("USER_KEEP_SNIPPETS", p)
        self.assertIn("我只信摸得到的工藝", p)
        self.assertIn("REVISION_INTENT:", p)
        self.assertIn("BASE_BODY:", p)
        self.assertIn(tone_card("humorous")[:20], p)


if __name__ == "__main__":
    unittest.main()
