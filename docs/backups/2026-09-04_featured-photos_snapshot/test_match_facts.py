"""Unit tests for featured-photo fact fallback and cap."""
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.images.match_facts import FEATURED_CAP, featured_slots, match_fact_text


class TestMatchFacts(unittest.TestCase):
    def test_flash_wins(self):
        text = match_fact_text(
            {
                "summary_flash": "flash body",
                "sources": [{"original_content": "long original"}],
                "title": "t",
            }
        )
        self.assertEqual(text, "flash body")

    def test_original_then_title(self):
        self.assertEqual(
            match_fact_text({"sources": [{"original_content": "src"}], "title": "t"}),
            "src",
        )
        self.assertEqual(match_fact_text({"title": "only-title"}), "only-title")
        self.assertEqual(match_fact_text({}), "")

    def test_slots_cap(self):
        self.assertEqual(FEATURED_CAP, 4)
        self.assertEqual(featured_slots(0), 4)
        self.assertEqual(featured_slots(3), 1)
        self.assertEqual(featured_slots(4), 0)
        self.assertEqual(featured_slots(9), 0)


if __name__ == "__main__":
    unittest.main()
