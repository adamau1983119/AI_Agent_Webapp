"""
Post Kit — Facebook 發文殼層純函數（v7 P3-07）
"""
from typing import List, Optional, Dict, Any


def build_facebook_shell(
    title: str,
    article: str,
    hashtags: Optional[List[str]] = None,
    image_urls: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    將產文結果組裝為 Post Kit 可複製結構（純函數、無 I/O）。
    """
    title = (title or "").strip()
    body = (article or "").strip()
    tags = hashtags or []
    tag_line = " ".join(f"#{t.lstrip('#')}" for t in tags if t)[:200]
    images = [u for u in (image_urls or []) if u][:5]

    variants = [title[:100]] if title else []
    if title and len(title) > 40:
        variants.append(title[:40] + "…")

    bundle_parts = [p for p in [title, body, tag_line] if p]
    return {
        "title_variants": variants,
        "body": body,
        "hashtags": tag_line,
        "image_links": images,
        "copy_bundle": "\n\n".join(bundle_parts),
    }
