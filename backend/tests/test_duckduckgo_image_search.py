"""DuckDuckGo image search fallback (ddgs)."""
from unittest.mock import MagicMock, patch

import pytest

from app.services.images.duckduckgo import DuckDuckGoService


@pytest.mark.asyncio
async def test_duckduckgo_search_normalizes_results():
    fake = [
        {
            "title": "Sample",
            "image": "https://example.com/a.jpg",
            "thumbnail": "https://example.com/t.jpg",
            "width": "800",
            "height": "600",
        }
    ]

    with patch.object(DuckDuckGoService, "_search_sync", return_value=[DuckDuckGoService()._normalize(fake[0], "test")]):
        svc = DuckDuckGoService()
        out = await svc.search_images("test", page=1, limit=5, trace_id="t1")
        assert len(out) == 1
        assert out[0]["url"] == "https://example.com/a.jpg"
        assert out[0]["source"] == "DuckDuckGo"


@pytest.mark.asyncio
async def test_duckduckgo_search_sync_calls_ddgs():
    svc = DuckDuckGoService()
    mock_ddgs = MagicMock()
    mock_ddgs.images.return_value = [
        {"image": "https://example.com/b.jpg", "thumbnail": "https://example.com/b-t.jpg", "title": "B"}
    ]

    with patch("ddgs.DDGS", return_value=mock_ddgs):
        out = svc._search_sync("fashion", 1, 3)
        mock_ddgs.images.assert_called_once()
        assert len(out) == 1
        assert out[0]["url"] == "https://example.com/b.jpg"
