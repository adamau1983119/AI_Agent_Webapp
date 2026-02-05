"""
RSS Feed 診斷腳本
檢查所有 RSS Feed 的可用性和返回數據
"""
import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Any

try:
    import feedparser
except ImportError:
    print("請安裝 feedparser: pip install feedparser")
    exit(1)

# RSS Feed 配置（與 topic_collector.py 相同）
RSS_FEEDS = {
    "FASHION": [
        ("Vogue", "https://www.vogue.com/feed/rss"),
        ("Elle", "https://www.elle.com/rss/all.xml"),
        ("Business of Fashion", "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml"),
        ("WWD", "https://wwd.com/feed/"),
        ("Hypebeast", "https://hypebeast.com/feed"),
        ("Highsnobiety", "https://www.highsnobiety.com/feeds/rss"),
        ("Who What Wear", "https://www.whowhatwear.com/feeds.xml"),
        ("Popbee", "https://popbee.com/feed"),
        ("Fashionista", "https://fashionista.com/.rss/excerpt/"),
        ("Cosmopolitan", "https://www.cosmopolitan.com/rss/all.xml"),
        ("GQ", "https://www.gq.com/feed/rss"),
        ("Dazed Digital", "https://www.dazeddigital.com/rss"),
        ("Marie Claire", "https://www.marieclaire.com/rss/all.xml"),
    ],
    "FOOD": [
        ("Eater", "https://www.eater.com/rss/index.xml"),
        ("Bon Appétit", "https://www.bonappetit.com/feed/rss"),
        ("Epicurious", "https://www.epicurious.com/feed/rss"),
        ("The Kitchn", "https://www.thekitchn.com/main.rss"),
        ("Simply Recipes", "https://feeds.feedburner.com/simplyrecipes"),
        ("Eat This, Not That!", "https://www.eatthis.com/feed/"),
        ("The Takeout", "https://www.thetakeout.com/feed/"),
        ("Mashed", "https://www.mashed.com/feed/"),
        ("BBC Good Food", "https://www.bbcgoodfood.com/feed"),
    ],
    "TREND": [
        ("WIRED", "https://www.wired.com/feed/rss"),
        ("MIT Technology Review", "https://www.technologyreview.com/feed/"),
        ("Singularity Hub", "https://singularityhub.com/feed/"),
        ("IEEE Spectrum", "https://spectrum.ieee.org/feeds/feed.rss"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("Fast Company", "https://www.fastcompany.com/latest/rss"),
        ("The Next Web", "https://thenextweb.com/feed"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("CNET", "https://www.cnet.com/rss/all/"),
        ("Digital Trends", "https://www.digitaltrends.com/feed/"),
        ("Engadget", "https://www.engadget.com/rss.xml"),
        ("Vox", "https://www.vox.com/rss/index.xml"),
        ("Rest of World", "https://restofworld.org/feed/latest/"),
        ("Ars Technica", "https://arstechnica.com/feed/"),
        ("Mashable", "https://mashable.com/feeds/rss/all"),
        ("ZDNET", "https://www.zdnet.com/news/rss.xml"),
    ],
}


async def test_single_feed(client: httpx.AsyncClient, name: str, url: str) -> Dict[str, Any]:
    """測試單個 RSS Feed"""
    result = {
        "name": name,
        "url": url,
        "status": "unknown",
        "http_status": None,
        "entries_count": 0,
        "error": None,
        "sample_titles": [],
        "has_images": False,
    }
    
    try:
        response = await client.get(url)
        result["http_status"] = response.status_code
        
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            entries = feed.entries
            result["entries_count"] = len(entries)
            
            if len(entries) > 0:
                result["status"] = "✅ OK"
                # 取樣前3個標題
                result["sample_titles"] = [e.get("title", "N/A")[:50] for e in entries[:3]]
                
                # 檢查是否有圖片
                for entry in entries[:5]:
                    content = str(entry)
                    if "image" in content.lower() or "media" in content.lower() or "thumbnail" in content.lower():
                        result["has_images"] = True
                        break
            else:
                result["status"] = "⚠️ Empty"
        else:
            result["status"] = f"❌ HTTP {response.status_code}"
            
    except httpx.TimeoutException:
        result["status"] = "❌ Timeout"
        result["error"] = "Request timeout (10s)"
    except Exception as e:
        result["status"] = "❌ Error"
        result["error"] = str(e)[:100]
    
    return result


async def test_category(category: str, feeds: List[tuple]) -> List[Dict[str, Any]]:
    """測試一個分類的所有 feeds"""
    results = []
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [test_single_feed(client, name, url) for name, url in feeds]
        results = await asyncio.gather(*tasks)
    
    return results


async def main():
    """主函數"""
    print("=" * 80)
    print("🔍 RSS Feed 診斷報告")
    print(f"📅 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_results = {}
    
    for category, feeds in RSS_FEEDS.items():
        print(f"\n\n📂 {category} ({len(feeds)} feeds)")
        print("-" * 60)
        
        results = await test_category(category, feeds)
        all_results[category] = results
        
        # 統計
        ok_count = sum(1 for r in results if r["status"].startswith("✅"))
        empty_count = sum(1 for r in results if r["status"].startswith("⚠️"))
        error_count = sum(1 for r in results if r["status"].startswith("❌"))
        
        print(f"\n📊 統計: ✅ 可用 {ok_count} | ⚠️ 空 {empty_count} | ❌ 錯誤 {error_count}")
        print("-" * 60)
        
        for r in results:
            img_icon = "🖼️" if r["has_images"] else "  "
            print(f"{r['status']:<15} {img_icon} {r['name']:<25} | 條目: {r['entries_count']:>3}")
            if r["error"]:
                print(f"                      └─ 錯誤: {r['error']}")
            if r["sample_titles"]:
                print(f"                      └─ 樣本: {r['sample_titles'][0][:40]}...")
    
    # 總結
    print("\n\n" + "=" * 80)
    print("📋 診斷總結")
    print("=" * 80)
    
    for category, results in all_results.items():
        ok_feeds = [r for r in results if r["status"].startswith("✅")]
        ok_with_images = [r for r in ok_feeds if r["has_images"]]
        
        print(f"\n{category}:")
        print(f"  - 可用 feeds: {len(ok_feeds)}/{len(results)}")
        print(f"  - 有圖片的 feeds: {len(ok_with_images)}/{len(ok_feeds)}")
        if ok_feeds:
            print(f"  - 可用來源: {', '.join([r['name'] for r in ok_feeds[:5]])}")
            if len(ok_feeds) > 5:
                print(f"             + {len(ok_feeds) - 5} more...")
    
    # 問題分析
    print("\n\n" + "=" * 80)
    print("🔧 問題分析")
    print("=" * 80)
    
    print("""
根據 topic_collector.py 的邏輯分析：

1. 【邏輯問題】_collect_from_rss 方法：
   - 對每個 feed 循序處理（for feed_url in feeds）
   - 一旦收集到足夠的主題（if len(topics) >= count: break）
   - 就停止處理當前 feed，但會繼續嘗試下一個 feed
   
2. 【實際效果】
   - 第一個可用的 feed（Vogue）如果返回足夠文章
   - 後續 feeds 會被請求，但不會添加文章
   - 因此看起來「只有 Vogue 生效」

3. 【建議修改】
   - 改為「每個 feed 各取 N 篇」，而非「取到足夠就停止」
   - 或使用並行請求所有 feeds，合併後隨機選取
""")


if __name__ == "__main__":
    asyncio.run(main())

