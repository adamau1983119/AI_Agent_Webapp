"""Unit tests for ops style trainer helpers (no live LLM / no FastAPI)."""
from __future__ import annotations

import unittest

from app.services.ops_trainer_inject import (
    fewshot_block,
    map_max_chars_to_length,
    map_style_to_profile,
    structure_block,
)
from app.services.compose_prompt import build_compose_prompt


class OpsTrainerInjectTests(unittest.TestCase):
    def test_style_map(self):
        self.assertEqual(map_style_to_profile("humorous"), "hook_gossip")
        self.assertEqual(map_style_to_profile("professional"), "news_recap")

    def test_length_map(self):
        self.assertEqual(map_max_chars_to_length(150), "short")
        self.assertEqual(map_max_chars_to_length(500), "long")

    def test_structure_and_fewshot_in_prompt(self):
        s = structure_block(
            {"prefix": "P", "fact": "F", "quote": "Q", "context": "C", "ending": "E"},
            "A",
        )
        f = fewshot_block(
            [{"body_text": "good post", "structure": {"prefix": "P"}}],
            [{"body_text": "bad ai tone"}],
        )
        prompt = build_compose_prompt(
            platform="instagram",
            style="professional",
            max_chars=150,
            part="body",
            language="zh-TW",
            topic_title="t",
            context_summary="fact",
            dna_overlay="",
            structure_overlay=s,
            fewshot_overlay=f,
        )
        self.assertIn("WRITE_PROFILE_STRUCTURE", prompt)
        self.assertIn("FEW_SHOT_EXEMPLARS", prompt)
        self.assertIn("Never double-translate", prompt)


if __name__ == "__main__":
    unittest.main()
