"""Image search provider order — Google first, no DuckDuckGo."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.image import ImageSource
from app.services.images.image_service_manager import ImageServiceManager


@pytest.mark.asyncio
async def test_search_tries_google_before_unsplash():
    mgr = ImageServiceManager()
    google_images = [{"id": "google_1", "url": "https://example.com/a.jpg", "source": "Google Custom Search"}]

    with patch.object(mgr.google_custom_search, "search_images", AsyncMock(return_value=google_images)) as mock_google, patch.object(
        mgr.unsplash, "search_images", AsyncMock(return_value=[])
    ) as mock_unsplash:
        result = await mgr.search_images("fashion", trace_id="t1")

    mock_google.assert_awaited_once()
    mock_unsplash.assert_not_awaited()
    assert len(result["items"]) == 1
    assert result["source"] == ImageSource.GOOGLE_CUSTOM_SEARCH.value


@pytest.mark.asyncio
async def test_search_no_duckduckgo_fallback():
    mgr = ImageServiceManager()

    with patch.object(mgr.google_custom_search, "search_images", AsyncMock(side_effect=Exception("no key"))), patch.object(
        mgr.unsplash, "search_images", AsyncMock(side_effect=ValueError("no key"))
    ), patch.object(mgr.pexels, "search_images", AsyncMock(side_effect=ValueError("no key"))), patch.object(
        mgr.pixabay, "search_images", AsyncMock(side_effect=ValueError("no key"))
    ):
        result = await mgr.search_images("test", trace_id="t2")

    sources = [a["source"] for a in result["attempts"]]
    assert "DuckDuckGo" not in sources
    assert result["items"] == []


@pytest.mark.asyncio
async def test_unsupported_source_rejects_duckduckgo():
    mgr = ImageServiceManager()
    from app.services.images.exceptions import ImageSearchError

    with pytest.raises(ImageSearchError):
        await mgr.search_images("test", source=ImageSource.DUCKDUCKGO)
