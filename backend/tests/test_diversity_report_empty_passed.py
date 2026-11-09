"""Empty diversity report must include passed=False (stdlib unittest; no pytest)."""
from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock

from app.services.scoring_service import DiversityScorer


class TestDiversityReportEmptyPassed(unittest.TestCase):
    def test_empty_report_has_passed_false(self):
        report = DiversityScorer.get_diversity_report([])
        self.assertEqual(report["status"], "no_data")
        self.assertIn("passed", report)
        self.assertIs(report["passed"], False)

    def test_nonempty_report_still_has_passed(self):
        topics = [{"source_name": f"S{i}"} for i in range(5)]
        report = DiversityScorer.get_diversity_report(topics)
        self.assertIn("passed", report)
        self.assertIsInstance(report["passed"], bool)


class TestCollectTopicsEmptyDedupNoKeyError(unittest.IsolatedAsyncioTestCase):
    async def test_all_duplicates_does_not_raise_passed_keyerror(self):
        from app.models.topic import Category
        from app.services.automation.topic_collector import TopicCollector

        collector = TopicCollector(enable_dedup=True)
        collector.deduplicator = MagicMock()
        collector.deduplicator.initialize = AsyncMock()
        collector.deduplicator.is_duplicate = AsyncMock(
            return_value=(True, "exact_match", None)
        )
        collector.deduplicator.get_stats = MagicMock(
            return_value={"duplicate_rate": "100%"}
        )
        collector._collect_by_roles = AsyncMock(
            return_value=[
                {"title": "Dup A", "source_name": "Eater"},
                {"title": "Dup B", "source_name": "Eater"},
            ]
        )

        out = await collector.collect_topics(
            Category.FOOD, count=1, use_fallback=False
        )
        self.assertEqual(out, [])
        self.assertEqual(collector._collect_by_roles.await_count, 2)


if __name__ == "__main__":
    unittest.main()
