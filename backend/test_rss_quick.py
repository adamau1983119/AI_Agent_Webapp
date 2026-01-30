"""
RSS 快速測試腳本
只測試每個類別的核心來源（減少並行請求）
"""

import asyncio
import httpx
import feedparser
from datetime import datetime
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 核心測試來源（每類別選 1 個）
CORE_FEEDS = [
    # 時尚
    ("Fashion/Global", "Vogue", "https://www.vogue.com/feed/rss"),
    ("Fashion/Global", "Hypebeast", "https://hypebeast.com/feed"),
    
    # 美食
    ("Food/Global", "Eater", "https://www.eater.com/rss/index.xml"),
    ("Food/Global", "BBC Good Food", "https://www.bbcgoodfood.com/feed"),
    
    # 趨勢
    ("Trend/Global", "TechCrunch", "https://techcrunch.com/feed/"),
    ("Trend/Global", "The Verge", "https://www.theverge.com/rss/index.xml"),
    
    # 財經
    ("Finance/Global", "Bloomberg", "https://feeds.bloomberg.com/markets/news.rss"),
    ("Finance/Global", "Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
    
    # 運動
    ("Sports/Global", "ESPN", "https://www.espn.com/espn/rss/news"),
    ("Sports/Global", "BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
    
    # 科技
    ("Tech/Global", "WIRED", "https://www.wired.com/feed/rss"),
    ("Tech/Global", "Ars Technica", "https://arstechnica.com/feed/"),
    
    # 娛樂
    ("Entertainment/Global", "Variety", "https://variety.com/feed/"),
    ("Entertainment/Global", "BBC Entertainment", "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"),
    
    # 本地來源
    ("Local/HK", "SCMP", "https://www.scmp.com/rss/91/feed/"),
    ("Local/Taiwan", "TechNews TW", "https://technews.tw/feed/"),
    ("Local/Japan", "Nikkei Asia", "https://asia.nikkei.com/rss/feed/nar"),
    ("Local/Korea", "Yonhap", "https://en.yna.co.kr/RSS/sports.xml"),
    ("Local/China", "36Kr", "https://36kr.com/feed"),
    ("Local/China", "TechNode", "https://technode.com/feed/"),
]

async def test_feed(client, category, name, url):
    """測試單個 Feed"""
    try:
        response = await client.get(url, timeout=20.0, follow_redirects=True)
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            entries = len(feed.entries)
            if entries > 0:
                return (category, name, "[OK]", entries)
            return (category, name, "[EMPTY]", 0)
        return (category, name, f"[HTTP {response.status_code}]", 0)
    except asyncio.TimeoutError:
        return (category, name, "[TIMEOUT]", 0)
    except Exception as e:
        return (category, name, f"[ERROR]", 0)

async def main():
    print("\n" + "="*70)
    print("RSS QUICK VALIDATION TEST (Core Feeds Only)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    success = 0
    failed = 0
    
    async with httpx.AsyncClient(
        timeout=25.0,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    ) as client:
        # 分批測試，每批 5 個
        for i in range(0, len(CORE_FEEDS), 5):
            batch = CORE_FEEDS[i:i+5]
            tasks = [test_feed(client, cat, name, url) for cat, name, url in batch]
            results = await asyncio.gather(*tasks)
            
            for cat, name, status, entries in results:
                status_icon = "[OK]" if status == "[OK]" else status
                print(f"  {status_icon.ljust(12)} {cat.ljust(20)} {name.ljust(20)} Entries: {entries}")
                if status == "[OK]":
                    success += 1
                else:
                    failed += 1
            
            # 每批之間等待一下
            await asyncio.sleep(0.5)
    
    total = success + failed
    print("\n" + "="*70)
    print(f"SUMMARY: {success}/{total} feeds working ({success/total*100:.1f}%)")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

