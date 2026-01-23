"""
Pytest 配置和共用 fixtures
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_article() -> Dict[str, Any]:
    """測試用文章數據"""
    return {
        "title": "2025 Fashion Trends: The Rise of Sustainable Style",
        "source": "Vogue",
        "source_name": "Vogue",
        "summary": "Discover the latest fashion trends focusing on sustainability and eco-friendly materials.",
        "original_content": "Fashion is evolving with a strong focus on sustainability...",
        "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        "keywords": ["fashion", "sustainability", "trends"],
        "published": datetime.utcnow() - timedelta(hours=2),
        "fetched_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_topics() -> List[Dict[str, Any]]:
    """測試用主題列表（多樣來源）"""
    return [
        {"title": "Topic 1", "source": "Vogue", "source_name": "Vogue"},
        {"title": "Topic 2", "source": "Elle", "source_name": "Elle"},
        {"title": "Topic 3", "source": "Hypebeast", "source_name": "Hypebeast"},
        {"title": "Topic 4", "source": "WWD", "source_name": "WWD"},
        {"title": "Topic 5", "source": "BoF", "source_name": "BoF"},
        {"title": "Topic 6", "source": "Vogue", "source_name": "Vogue"},
        {"title": "Topic 7", "source": "Fashionista", "source_name": "Fashionista"},
        {"title": "Topic 8", "source": "Popbee", "source_name": "Popbee"},
        {"title": "Topic 9", "source": "SCMP Style", "source_name": "SCMP Style"},
        {"title": "Topic 10", "source": "Refinery29", "source_name": "Refinery29"},
    ]


@pytest.fixture
def single_source_topics() -> List[Dict[str, Any]]:
    """測試用主題列表（單一來源）"""
    return [
        {"title": f"Topic {i}", "source": "Vogue", "source_name": "Vogue"}
        for i in range(1, 11)
    ]


@pytest.fixture
def sample_images() -> List[Dict[str, Any]]:
    """測試用圖片列表"""
    return [
        {
            "url": "https://vogue.com/image1.jpg",
            "alt": "Fashion runway show featuring sustainable designs",
            "caption": "Valentino Spring 2025 Collection",
            "source": "Vogue",
            "width": 1920,
            "height": 1080,
        },
        {
            "url": "https://hypebeast.com/image2.jpg",
            "alt": "Streetwear collection preview",
            "caption": "Supreme x Nike Collaboration",
            "source": "Hypebeast",
            "width": 1200,
            "height": 800,
        },
        {
            "url": "https://unsplash.com/image3.jpg",
            "alt": "Fashion photography",
            "caption": "",
            "source": "Unsplash",
            "width": 800,
            "height": 600,
        },
        {
            "url": "https://elle.com/image4.jpg",
            "alt": "Designer collection",
            "caption": "Paris Fashion Week highlights",
            "source": "Elle",
            "width": 2000,
            "height": 1200,
        },
        {
            "url": "https://vogue.com/image5.jpg",
            "alt": "Luxury fashion editorial",
            "caption": "Gucci Resort 2025",
            "source": "Vogue",
            "width": 1600,
            "height": 900,
        },
    ]


@pytest.fixture
def sample_topic() -> Dict[str, Any]:
    """測試用主題數據"""
    return {
        "title": "可持續時尚的崛起：2025年環保設計趨勢",
        "original_title": "The Rise of Sustainable Fashion: 2025 Eco-Design Trends",
        "category": "fashion",
        "content": "Fashion industry is embracing sustainability with innovative eco-friendly materials and ethical production practices.",
        "description": "探索2025年時尚界如何擁抱可持續發展理念",
        "sources": [
            {
                "name": "Vogue",
                "url": "https://vogue.com/article/sustainable-fashion",
                "keywords": ["sustainable", "fashion", "eco-friendly"],
            }
        ],
    }

