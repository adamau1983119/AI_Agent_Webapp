"""Hidden topic cards: list/today filters exclude without deleting."""
from __future__ import annotations

import unittest

from app.utils.topic_pipeline import (
    list_topics_hidden_filter,
    merge_topic_list_filters,
)


class TestTopicHiddenFilter(unittest.TestCase):
    def test_default_excludes_hidden(self):
        f = list_topics_hidden_filter()
        self.assertEqual(f, {"hidden": {"$ne": True}})

    def test_include_hidden_is_empty(self):
        self.assertEqual(list_topics_hidden_filter(include_hidden=True), {})

    def test_merge_with_generation(self):
        merged = merge_topic_list_filters(
            {"pipeline_version": {"$gte": 8}},
            list_topics_hidden_filter(),
        )
        self.assertIn("$and", merged)
        self.assertEqual(len(merged["$and"]), 2)


if __name__ == "__main__":
    unittest.main()
