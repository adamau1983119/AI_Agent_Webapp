"""Stored JPEG helpers: id split and in-memory compress."""
import io
import unittest

from PIL import Image

from app.services.images.jpeg_compress import DEFAULT_MAX_BYTES, compress_jpeg_bytes
from app.services.images.jpeg_store import (
    http_image_url,
    split_source_image_id,
    url_from_topic_sources,
)


class JpegStoreTests(unittest.TestCase):
    def test_http_image_url(self):
        self.assertEqual(http_image_url("https://cdn.example/a.jpg"), "https://cdn.example/a.jpg")
        self.assertEqual(http_image_url({"url": "http://cdn.example/b.jpg"}), "http://cdn.example/b.jpg")
        self.assertEqual(http_image_url("not-a-url"), "")

    def test_split_source_image_id(self):
        parsed = split_source_image_id("topic_fashion_20261004160325_4_source_0")
        self.assertEqual(parsed, ("topic_fashion_20261004160325_4", 0))
        self.assertIsNone(split_source_image_id("pexels_123"))

    def test_url_from_topic_sources(self):
        topic = {"sources": [{"images": ["https://cdn.example/a.jpg", {"url": "https://cdn.example/b.jpg"}]}]}
        self.assertEqual(url_from_topic_sources(topic, 1), "https://cdn.example/b.jpg")
        self.assertEqual(url_from_topic_sources(topic, 3), "")

    def test_compress_small_png_to_jpeg(self):
        buf = io.BytesIO()
        Image.new("RGB", (32, 32), (20, 40, 60)).save(buf, format="PNG")
        out, _, _ = compress_jpeg_bytes(buf.getvalue())
        self.assertTrue(out.startswith(b"\xff\xd8\xff"))
        self.assertLessEqual(len(out), DEFAULT_MAX_BYTES)


if __name__ == "__main__":
    unittest.main()
