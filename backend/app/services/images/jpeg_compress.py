"""Compress remote JPEG to ≤ max_bytes. MD-M2 ≤150."""
from __future__ import annotations

import io
from typing import Tuple

import httpx
from PIL import Image, UnidentifiedImageError

from app.utils.logger import log_cost_event

MAX_EDGE = 1440
DEFAULT_MAX_BYTES = 200 * 1024
FETCH_TIMEOUT = 30.0


def _looks_like_image(raw: bytes, content_type: str) -> bool:
    ct = (content_type or "").lower()
    if ct.startswith("image/") and "svg" not in ct:
        return True
    if len(raw) < 24:
        return False
    # JPEG / PNG / WebP / GIF magic
    if raw[:3] == b"\xff\xd8\xff":
        return True
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return True
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return True
    return False


def compress_jpeg_bytes(raw: bytes, max_bytes: int = DEFAULT_MAX_BYTES) -> Tuple[bytes, int, int]:
    if not raw:
        raise ValueError("empty_image")
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except UnidentifiedImageError as e:
        raise ValueError("unidentified_image") from e
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    w, h = img.size
    scale = min(1.0, MAX_EDGE / max(w, h, 1))
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)

    quality = 85
    out = b""
    while quality >= 40:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        out = buf.getvalue()
        if len(out) <= max_bytes:
            break
        quality -= 8
    if len(out) > max_bytes:
        for shrink in (0.85, 0.7, 0.55):
            nw = max(1, int(img.size[0] * shrink))
            nh = max(1, int(img.size[1] * shrink))
            small = img.resize((nw, nh), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            small.save(buf, format="JPEG", quality=70, optimize=True)
            out = buf.getvalue()
            if len(out) <= max_bytes:
                break
    if not out:
        raise ValueError("encode_failed")
    return out, img.size[0], img.size[1]


async def fetch_and_compress(
    url: str,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    tag: str = "TOPIC_IMAGE_STORE",
) -> bytes:
    if not (url or "").strip():
        raise ValueError("missing_url")
    async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, follow_redirects=True) as client:
        res = await client.get(
            url.strip(),
            headers={"User-Agent": "Mozilla/5.0 (compatible; AlterEgo/1.0)"},
        )
        res.raise_for_status()
        raw = res.content
        ct = res.headers.get("content-type", "")
    if not _looks_like_image(raw, ct):
        raise ValueError("not_an_image")
    compressed, _, _ = compress_jpeg_bytes(raw, max_bytes=max_bytes)
    log_cost_event(
        tag,
        success=True,
        src_bytes=len(raw),
        out_bytes=len(compressed),
        max_bytes=max_bytes,
        url=(url or "")[:120],
    )
    return compressed
