"""Pillow title-image overlay (styles a/b/c). MD-M2 ≤150."""
from __future__ import annotations

import io
from typing import Literal

from PIL import Image, ImageDraw, ImageFont

StyleId = Literal["a", "b", "c"]
MAX_EDGE = 1080
_FONT_CANDIDATES = (
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/PingFang.ttc",
)


def _font(size: int) -> ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for ch in text.replace("\n", " "):
        trial = line + ch
        if draw.textlength(trial, font=font) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = ch
        if len(lines) >= 4:
            break
    if line and len(lines) < 4:
        lines.append(line)
    return lines or [text[:40]]


def _draw_heading(draw: ImageDraw.ImageDraw, heading: str, style: StyleId, w: int, h: int) -> None:
    pad = int(w * 0.06)
    font = _font(max(28, int(w * 0.055)))
    lines = _wrap(draw, heading.strip(), font, w - pad * 2)
    line_h = int(font.size * 1.25)
    block_h = len(lines) * line_h
    if style == "a":
        y0 = (h - block_h) // 2
        draw.rectangle((0, y0 - pad // 2, w, y0 + block_h + pad // 2), fill=(0, 0, 0, 90))
        for i, ln in enumerate(lines):
            tw = draw.textlength(ln, font=font)
            draw.text(((w - tw) / 2, y0 + i * line_h), ln, font=font, fill=(255, 255, 255))
        return
    if style == "b":
        y0 = h - block_h - int(pad * 1.5)
        draw.rectangle((0, y0 - pad // 3, w, h), fill=(0, 0, 0, 140))
        for i, ln in enumerate(lines):
            draw.text((pad, y0 + i * line_h), ln, font=font, fill=(255, 255, 255))
        return
    draw.rectangle((0, 0, w, block_h + int(pad * 1.4)), fill=(17, 17, 17))
    for i, ln in enumerate(lines):
        draw.text((pad, int(pad * 0.6) + i * line_h), ln, font=font, fill=(245, 245, 240))


def render_title_jpeg(photo_bytes: bytes, heading: str, style: StyleId) -> bytes:
    base = Image.open(io.BytesIO(photo_bytes)).convert("RGBA")
    scale = max(MAX_EDGE / max(base.width, 1), MAX_EDGE / max(base.height, 1))
    nw, nh = max(1, int(base.width * scale)), max(1, int(base.height * scale))
    base = base.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (MAX_EDGE, MAX_EDGE), (15, 23, 42, 255))
    canvas.paste(base, ((MAX_EDGE - nw) // 2, (MAX_EDGE - nh) // 2))
    overlay = Image.new("RGBA", (MAX_EDGE, MAX_EDGE), (0, 0, 0, 0))
    _draw_heading(ImageDraw.Draw(overlay), heading, style, MAX_EDGE, MAX_EDGE)
    out = Image.alpha_composite(canvas, overlay).convert("RGB")
    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=88, optimize=True)
    return buf.getvalue()
