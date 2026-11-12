"""before_date HKT filter for related (historical) topic cards."""
from __future__ import annotations

import sys
import unittest
from datetime import datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.automation.topic_day_hkt import (  # noqa: E402
    generated_at_before_hkt_day,
    hkt_day_utc_bounds,
)


class TestGeneratedAtBeforeHktDay(unittest.TestCase):
    def test_clause_uses_lt_start_of_day(self):
        start, _ = hkt_day_utc_bounds("2026-11-12")
        clause = generated_at_before_hkt_day("2026-11-12")
        self.assertEqual(clause, {"generated_at": {"$lt": start}})
        self.assertIsInstance(clause["generated_at"]["$lt"], datetime)

    def test_before_excludes_that_calendar_day(self):
        start, end = hkt_day_utc_bounds("2026-11-12")
        clause = generated_at_before_hkt_day("2026-11-12")
        bound = clause["generated_at"]["$lt"]
        self.assertEqual(bound, start)
        self.assertLess(bound, end)


if __name__ == "__main__":
    unittest.main()
