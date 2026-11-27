"""RobotsTagMiddleware：API 子域 noindex／robots.txt。"""
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.testclient import TestClient

from app.middleware.robots_tag import ROBOTS_BODY, ROBOTS_TAG, RobotsTagMiddleware


async def _ok(_request: Request) -> Response:
    return JSONResponse({"ok": True})


def _app() -> Starlette:
    app = Starlette(routes=[Route("/", _ok), Route("/health", _ok)])
    app.add_middleware(RobotsTagMiddleware)
    return app


class TestRobotsTagMiddleware(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(_app())

    def test_robots_txt_allow(self) -> None:
        r = self.client.get("/robots.txt")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/plain", r.headers.get("content-type", ""))
        self.assertEqual(r.text, ROBOTS_BODY)
        self.assertIn("Allow: /", r.text)
        self.assertNotIn("Disallow:", r.text)
        self.assertEqual(r.headers.get("x-robots-tag"), ROBOTS_TAG)

    def test_json_routes_get_header(self) -> None:
        for path in ("/", "/health"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.headers.get("x-robots-tag"), ROBOTS_TAG)


if __name__ == "__main__":
    unittest.main()
