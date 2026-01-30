"""
RSS 驗證測試腳本
測試所有配置的 RSS Feed 的可用性
"""

import asyncio
import httpx
import feedparser
from datetime import datetime
from typing import Dict, Any, List
import sys
import io

# 設定 UTF-8 輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 從 channel.py 導入 DEFAULT_RSS_SOURCES
sys.path.insert(0, '.')

from app.models.channel import DEFAULT_RSS_SOURCES, ChannelCategory, ChannelRegion

class RSSValidationTest:
    """RSS 驗證測試類"""
    
    def __init__(self):
        self.results = []
        self.stats = {
            "total": 0,
            "success": 0,
            "empty": 0,
            "failed": 0,
            "timeout": 0
        }
    
    async def _test_single_feed(self, client: httpx.AsyncClient, category: str, region: str, source_name: str, url: str) -> Dict[str, Any]:
        """測試單個 RSS Feed"""
        result = {
            "category": category,
            "region": region,
            "name": source_name,
            "url": url,
            "status": "unknown",
            "http_status": None,
            "entries_count": 0,
            "error": None,
            "has_images": False,
            "latest_entry": None
        }
        
        try:
            response = await client.get(url, timeout=15.0, follow_redirects=True)
            result["http_status"] = response.status_code
            
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                entries = feed.entries
                result["entries_count"] = len(entries)
                
                if len(entries) > 0:
                    result["status"] = "[OK]"
                    self.stats["success"] += 1
                    
                    # 獲取最新條目標題
                    result["latest_entry"] = entries[0].get("title", "N/A")[:50]
                    
                    # 檢查是否有圖片
                    for entry in entries[:3]:
                        content = str(entry)
                        if any(keyword in content.lower() for keyword in ["image", "media", "thumbnail", "enclosure"]):
                            result["has_images"] = True
                            break
                else:
                    result["status"] = "[EMPTY]"
                    self.stats["empty"] += 1
            else:
                result["status"] = f"[HTTP {response.status_code}]"
                self.stats["failed"] += 1
                
        except httpx.TimeoutException:
            result["status"] = "[TIMEOUT]"
            result["error"] = "Request timeout (15s)"
            self.stats["timeout"] += 1
        except Exception as e:
            result["status"] = "[ERROR]"
            result["error"] = str(e)[:80]
            self.stats["failed"] += 1
        
        self.stats["total"] += 1
        return result
    
    async def validate_all_feeds(self):
        """驗證所有 RSS Feed"""
        print("\n" + "="*80)
        print("RSS VALIDATION TEST")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        tasks = []
        
        async with httpx.AsyncClient(
            timeout=20.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        ) as client:
            # 遍歷所有類別和地區
            for category_enum in ChannelCategory:
                category_sources = DEFAULT_RSS_SOURCES.get(category_enum, {})
                for region_enum in ChannelRegion:
                    feeds_in_region = category_sources.get(region_enum, [])
                    for feed_info in feeds_in_region:
                        source_name = feed_info["name"]
                        url = feed_info["url"]
                        tasks.append(
                            self._test_single_feed(
                                client, 
                                category_enum.value, 
                                region_enum.value, 
                                source_name, 
                                url
                            )
                        )
            
            # 並行執行所有測試
            print(f"Preparing to test {len(tasks)} RSS Feeds...\n")
            self.results = await asyncio.gather(*tasks)
        
        return self.results
    
    def print_results(self):
        """打印測試結果"""
        # 按類別和地區分組顯示
        current_category = None
        current_region = None
        
        for result in sorted(self.results, key=lambda x: (x["category"], x["region"])):
            # 類別分隔
            if result["category"] != current_category:
                current_category = result["category"]
                print(f"\n{'='*80}")
                print(f"CATEGORY: {current_category.upper()}")
                print("="*80)
            
            # 地區分隔
            if result["region"] != current_region:
                current_region = result["region"]
                print(f"\n  REGION: {current_region}")
                print("  " + "-"*60)
            
            # 顯示結果
            status = result["status"].ljust(12)
            name = result["name"][:25].ljust(25)
            entries = result["entries_count"]
            images = "[IMG]" if result["has_images"] else "     "
            
            print(f"    {status} {name} | Entries: {entries:3d} {images}")
            
            if result["error"]:
                print(f"       Error: {result['error']}")
        
        # 打印統計
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        total = self.stats['total']
        print(f"  Total Tested: {total} RSS Feeds")
        print(f"  [OK]      Success: {self.stats['success']} ({self.stats['success']/total*100:.1f}%)")
        print(f"  [EMPTY]   Empty:   {self.stats['empty']} ({self.stats['empty']/total*100:.1f}%)")
        print(f"  [FAILED]  Failed:  {self.stats['failed']} ({self.stats['failed']/total*100:.1f}%)")
        print(f"  [TIMEOUT] Timeout: {self.stats['timeout']} ({self.stats['timeout']/total*100:.1f}%)")
        print("="*80 + "\n")
        
        # 列出有問題的來源
        failed_feeds = [r for r in self.results if not r["status"].startswith("[OK]")]
        if failed_feeds:
            print("FEEDS REQUIRING ATTENTION:")
            print("-"*60)
            for feed in failed_feeds:
                print(f"  {feed['status'].ljust(12)} [{feed['category']}/{feed['region']}] {feed['name']}")
                if feed["error"]:
                    print(f"       Reason: {feed['error']}")

async def main():
    tester = RSSValidationTest()
    await tester.validate_all_feeds()
    tester.print_results()

if __name__ == "__main__":
    asyncio.run(main())
