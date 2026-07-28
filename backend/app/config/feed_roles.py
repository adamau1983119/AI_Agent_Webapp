"""
RSS Feed 角色分配配置
按角色分類 RSS Feed，確保內容來源多樣性
"""
from typing import Dict, List, Tuple
from app.models.topic import Category


# ========== Fashion 角色分配 ==========
FASHION_ROLES: Dict[str, List[Tuple[str, str, float]]] = {
    # 角色: [(來源名稱, URL, 權重)]
    "authority": [
        ("Vogue", "https://www.vogue.com/feed/rss", 1.0),
        ("Elle", "https://www.elle.com/rss/all.xml", 0.95),
    ],
    "streetwear": [
        ("Hypebeast", "https://hypebeast.com/feed", 0.9),
        ("Highsnobiety", "https://www.highsnobiety.com/feeds/rss", 0.85),
    ],
    "asian": [
        ("Popbee", "https://popbee.com/feed", 0.8),
        ("SCMP Style", "https://www.scmp.com/rss/91/feed/", 0.75),
    ],
    "industry": [
        ("Business of Fashion", "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml", 0.9),
        ("WWD", "https://wwd.com/feed/", 0.85),
    ],
    "practical": [
        ("Who What Wear", "https://www.whowhatwear.com/feeds.xml", 0.8),
        ("Fashionista", "https://fashionista.com/.rss/excerpt/", 0.75),
        ("Refinery29", "https://www.refinery29.com/rss.xml", 0.7),
    ],
}

# ========== Food 角色分配 ==========
FOOD_ROLES: Dict[str, List[Tuple[str, str, float]]] = {
    "mainstream": [
        ("Eater", "https://www.eater.com/rss/index.xml", 1.0),
        ("Bon Appétit", "https://www.bonappetit.com/feed/rss", 0.95),
    ],
    "professional": [
        ("Epicurious", "https://www.epicurious.com/feed/rss", 0.9),
        ("The Kitchn", "https://www.thekitchn.com/main.rss", 0.85),
    ],
    "cultural": [
        ("BBC Good Food", "https://www.bbcgoodfood.com/feed", 0.85),
        ("Simply Recipes", "https://feeds.feedburner.com/simplyrecipes", 0.8),
    ],
    "healthy": [
        ("Eat This Not That", "https://www.eatthis.com/feed/", 0.8),
    ],
    "casual": [
        ("The Takeout", "https://www.thetakeout.com/feed/", 0.75),
        ("Mashed", "https://www.mashed.com/feed/", 0.7),
    ],
}

# ========== Trend 角色分配 ==========
TREND_ROLES: Dict[str, List[Tuple[str, str, float]]] = {
    "tech": [
        ("TechCrunch", "https://techcrunch.com/feed/", 1.0),
        ("The Verge", "https://www.theverge.com/rss/index.xml", 0.95),
    ],
    "science": [
        ("Ars Technica", "https://arstechnica.com/feed/", 0.9),
        ("IEEE Spectrum", "https://spectrum.ieee.org/feeds/feed.rss", 0.85),
    ],
    "culture": [
        ("Vox", "https://www.vox.com/rss/index.xml", 0.85),
        ("The Atlantic", "https://www.theatlantic.com/feed/all/", 0.8),
    ],
    "innovation": [
        ("WIRED", "https://www.wired.com/feed/rss", 0.95),
        ("MIT Technology Review", "https://www.technologyreview.com/feed/", 0.9),
        ("Singularity Hub", "https://singularityhub.com/feed/", 0.8),
    ],
    "lifestyle": [
        ("Fast Company", "https://www.fastcompany.com/latest/rss", 0.85),
        ("Rest of World", "https://restofworld.org/feed/latest/", 0.8),
        ("The Next Web", "https://thenextweb.com/feed", 0.75),
    ],
}

# 角色到分類的映射
CATEGORY_ROLES: Dict[Category, Dict[str, List[Tuple[str, str, float]]]] = {
    Category.FASHION: FASHION_ROLES,
    Category.FOOD: FOOD_ROLES,
    Category.TREND: TREND_ROLES,
}

# 預設角色分配比例（與 topic_generation.yaml count=5 對齊：5 角色 × 1）
DEFAULT_ROLE_DISTRIBUTION: Dict[Category, Dict[str, int]] = {
    Category.FASHION: {
        "authority": 1,
        "streetwear": 1,
        "asian": 1,
        "industry": 1,
        "practical": 1,
    },
    Category.FOOD: {
        "mainstream": 1,
        "professional": 1,
        "cultural": 1,
        "healthy": 1,
        "casual": 1,
    },
    Category.TREND: {
        "tech": 1,
        "science": 1,
        "culture": 1,
        "innovation": 1,
        "lifestyle": 1,
    },
}

# 來源權重（用於評分）
SOURCE_WEIGHTS: Dict[str, float] = {
    # Tier S (1.0) - 權威來源
    "Vogue": 1.0,
    "Elle": 0.95,
    "Business of Fashion": 0.95,
    "NYT": 1.0,
    "BBC": 0.95,
    
    # Tier A (0.85-0.9) - 專業來源
    "TechCrunch": 0.9,
    "The Verge": 0.9,
    "WIRED": 0.9,
    "Hypebeast": 0.85,
    "WWD": 0.85,
    "Eater": 0.9,
    "Bon Appétit": 0.85,
    
    # Tier B (0.7-0.8) - 可靠來源
    "Highsnobiety": 0.8,
    "Ars Technica": 0.8,
    "Fast Company": 0.8,
    "Epicurious": 0.75,
    "The Kitchn": 0.75,
    
    # Tier C (0.5-0.7) - 一般來源
    "Popbee": 0.7,
    "Fashionista": 0.65,
    "The Takeout": 0.6,
    "Mashed": 0.55,
    
    # Tier D (0.4-0.5) - 外部搜尋
    "Unsplash": 0.5,
    "Pexels": 0.5,
    "Pixabay": 0.45,
}


def get_roles_for_category(category: Category) -> Dict[str, List[Tuple[str, str, float]]]:
    """獲取分類的角色配置"""
    return CATEGORY_ROLES.get(category, {})


def get_role_distribution(category: Category) -> Dict[str, int]:
    """獲取分類的角色分配比例"""
    return DEFAULT_ROLE_DISTRIBUTION.get(category, {})


def get_source_weight(source_name: str) -> float:
    """獲取來源權重，未知來源返回 0.5"""
    # 模糊匹配：檢查來源名稱是否包含已知來源
    for known_source, weight in SOURCE_WEIGHTS.items():
        if known_source.lower() in source_name.lower():
            return weight
    return 0.5  # 未知來源預設權重


def get_all_feeds_for_category(category: Category) -> List[Tuple[str, str, float]]:
    """獲取分類的所有 Feed（扁平化）"""
    roles = get_roles_for_category(category)
    all_feeds = []
    for role_feeds in roles.values():
        all_feeds.extend(role_feeds)
    return all_feeds

