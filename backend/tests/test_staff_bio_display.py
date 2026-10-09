"""Staff-bio paragraphs are hidden. The card is not dropped."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.utils.article_boilerplate import clean_extracted_text
from app.utils.staff_bio import drop_leading_staff_bios


_BIO = "Kristen Nichols is the editor at Who What Wear and covers shopping."
_STORY = "The coat sold out in a day after the show in Paris. Buyers queued before the doors opened."


class TestStaffBioHide(unittest.TestCase):
    def test_bio_plus_article_hides_bio(self):
        out = drop_leading_staff_bios(_BIO + "\n\n" + _STORY)
        self.assertNotIn("Kristen Nichols", out)
        self.assertIn("Paris", out)

    def test_bio_only_is_empty(self):
        self.assertEqual(drop_leading_staff_bios(_BIO), "")

    def test_director_got_her_start(self):
        text = "Erin is a director at Who What Wear. She got her start in magazines."
        self.assertEqual(drop_leading_staff_bios(text), "")

    def test_graduated_writer(self):
        text = "She graduated from NYU and is a writer for Vogue."
        self.assertEqual(drop_leading_staff_bios(text), "")

    def test_chinese_deputy_director(self):
        text = "她是 Who What Wear 的副總監，負責購物。"
        self.assertEqual(drop_leading_staff_bios(text), "")

    def test_article_about_an_editor_stays(self):
        text = "The editor quit after the magazine was sold to a new owner in March."
        self.assertIn("sold", drop_leading_staff_bios(text))
        out = clean_extracted_text(_STORY)
        self.assertIn("coat", out)
        self.assertIn("Paris", out)


if __name__ == "__main__":
    unittest.main()
