"""Regression: list sort must not bury scanned today cards under history."""
import unittest

from app.utils.topic_pipeline import build_topic_list_sort


class TestTopicListSortOrder(unittest.TestCase):
    def test_recency_before_penalty(self):
        sort_list = build_topic_list_sort(sort="generated_at", order="desc")
        self.assertEqual(sort_list[0], ("generated_at", -1))
        self.assertEqual(sort_list[1], ("sort_penalty", 1))

    def test_penalty_not_primary(self):
        self.assertNotEqual(build_topic_list_sort()[0][0], "sort_penalty")


if __name__ == "__main__":
    unittest.main()
