"""標題層硬閘與分類錨點。不碰翻譯／finalize。MD-M2 ≤150。"""
from __future__ import annotations

from typing import FrozenSet, Optional, Set

from app.models.topic import Category

_HARD = (
    "porn", "xxx", "nsfw", "onlyfans", "hentai",
    "coupon code", "promo code", "discount code", "voucher",
    "flash sale", "clearance sale",
)
_HARD_PATH = (
    "/deals/", "/coupons/", "/offers/", "/sales/", "/shopping/", "/promo/",
)
_FASHION = frozenset({
    "fashion", "style", "designer", "runway", "collection", "couture",
    "streetwear", "outfit", "wardrobe", "apparel", "clothing", "sneaker",
    "shoe", "dress", "luxury", "vogue", "nike", "chanel", "dior", "handbag",
    "時裝", "時尚", "潮流", "設計師", "穿搭", "服飾",
})
_FOOD = frozenset({
    "food", "recipe", "restaurant", "chef", "cuisine", "cooking", "dining",
    "gourmet", "ingredient", "dish", "menu", "bakery", "taco",
    "美食", "食譜", "餐廳", "料理", "烹飪", "小吃",
})
_TREND = frozenset({
    "tech", "technology", "ai", "innovation", "startup", "digital",
    "science", "research", "climate", "software", "科技", "創新", "趨勢",
})
_ANCHOR = {
    Category.FASHION: _FASHION,
    Category.FOOD: _FOOD,
    Category.TREND: _TREND,
}


def hard_reject(title: str, link: str) -> bool:
    t = (title or "").lower()
    u = (link or "").lower()
    if any(p in u for p in _HARD_PATH):
        return True
    return any(k in t for k in _HARD)


def has_category_anchor(title: str, category: Category) -> bool:
    text = (title or "").lower()
    words: FrozenSet[str] = _ANCHOR.get(category, frozenset())
    return any(w.lower() in text for w in words)


def should_skip_entry(
    title: str,
    link: str,
    category: Category,
    source_name: str = "",
    used_sources: Optional[Set[str]] = None,
    max_source: int = 1,
) -> Optional[str]:
    if hard_reject(title, link):
        return "policy"
    if not has_category_anchor(title, category):
        return "no_anchor"
    if used_sources is not None and source_name and source_name in used_sources:
        if max_source <= 1:
            return "source_cap"
    return None
