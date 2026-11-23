"""One-tap pack cost + latest response shape (no LLM / DB)."""
import unittest

from app.schemas.alter_ego import OneTapLatestResponse
from app.services.one_tap_service import ONE_TAP_COST, ONE_TAP_MAX_CHARS


class TestOneTapCost(unittest.TestCase):
    def test_cost_and_cap(self) -> None:
        self.assertEqual(ONE_TAP_COST, 20)
        self.assertEqual(ONE_TAP_MAX_CHARS, 500)

    def test_latest_response_fields(self) -> None:
        pack = OneTapLatestResponse(
            pack_token="a" * 16,
            titles=["t"],
            body="body",
            hashtag_sets=[["#a"]],
            charged=True,
        )
        self.assertTrue(pack.charged)
        self.assertEqual(pack.credits_required, 20)


if __name__ == "__main__":
    unittest.main()
