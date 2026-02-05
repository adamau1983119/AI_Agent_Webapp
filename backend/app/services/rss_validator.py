"""
RSS 來源驗證服務
用於驗證所有配置的 RSS 來源是否有效

功能：
1. 驗證 RSS URL 可達性
2. 驗證 RSS 格式有效性
3. 統計來源健康狀況
4. 生成驗證報告
"""
import asyncio
import logging
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

import httpx

try:
    import feedparser
except ImportError:
    feedparser = None

logger = logging.getLogger(__name__)


class RSSValidator:
    """
    RSS 來源驗證器
    """
    
    def __init__(self, timeout: float = 15.0):
        """
        初始化驗證器
        
        Args:
            timeout: 請求超時時間（秒）
        """
        self.timeout = timeout
        self.results: Dict[str, Any] = {}
    
    async def validate_single_feed(
        self,
        client: httpx.AsyncClient,
        name: str,
        url: str,
        category: str = "",
        region: str = ""
    ) -> Dict[str, Any]:
        """
        驗證單個 RSS Feed
        
        Returns:
            {
                "name": str,
                "url": str,
                "category": str,
                "region": str,
                "status": "ok" | "empty" | "error",
                "http_status": int,
                "entries_count": int,
                "has_images": bool,
                "error": str | None,
                "response_time_ms": int,
                "sample_title": str | None
            }
        """
        result = {
            "name": name,
            "url": url,
            "category": category,
            "region": region,
            "status": "unknown",
            "http_status": None,
            "entries_count": 0,
            "has_images": False,
            "error": None,
            "response_time_ms": 0,
            "sample_title": None,
            "validated_at": datetime.utcnow().isoformat()
        }
        
        start_time = datetime.now()
        
        try:
            response = await client.get(url)
            result["http_status"] = response.status_code
            result["response_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                # 解析 RSS
                if feedparser:
                    feed = feedparser.parse(response.text)
                    entries = feed.entries
                    result["entries_count"] = len(entries)
                    
                    if len(entries) > 0:
                        result["status"] = "ok"
                        result["sample_title"] = entries[0].get("title", "")[:80]
                        
                        # 檢查是否有圖片
                        for entry in entries[:5]:
                            content = str(entry)
                            if any(kw in content.lower() for kw in ["image", "media", "thumbnail", "enclosure"]):
                                result["has_images"] = True
                                break
                    else:
                        result["status"] = "empty"
                        result["error"] = "Feed is empty"
                else:
                    # 沒有 feedparser，只檢查 HTTP 狀態
                    if "<rss" in response.text or "<feed" in response.text or "<channel" in response.text:
                        result["status"] = "ok"
                    else:
                        result["status"] = "error"
                        result["error"] = "Not a valid RSS/Atom feed"
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"
                
        except httpx.TimeoutException:
            result["status"] = "error"
            result["error"] = "Timeout"
            result["response_time_ms"] = int(self.timeout * 1000)
        except httpx.ConnectError:
            result["status"] = "error"
            result["error"] = "Connection failed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)[:100]
        
        return result
    
    async def validate_feeds_list(
        self,
        feeds: List[Dict[str, str]],
        category: str = "",
        region: str = ""
    ) -> List[Dict[str, Any]]:
        """
        驗證一組 RSS Feeds
        
        Args:
            feeds: [{"name": str, "url": str}, ...]
            category: 類別名稱
            region: 地區名稱
            
        Returns:
            驗證結果列表
        """
        results = []
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            tasks = []
            for feed in feeds:
                task = self.validate_single_feed(
                    client=client,
                    name=feed.get("name", "Unknown"),
                    url=feed.get("url", ""),
                    category=category,
                    region=region
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
        
        return results
    
    async def validate_all_channel_sources(self) -> Dict[str, Any]:
        """
        驗證所有 channel.py 中配置的 RSS 來源
        
        Returns:
            完整驗證報告
        """
        from app.models.channel import DEFAULT_RSS_SOURCES, ChannelCategory, ChannelRegion
        
        report = {
            "validated_at": datetime.utcnow().isoformat(),
            "total_sources": 0,
            "valid_count": 0,
            "empty_count": 0,
            "error_count": 0,
            "categories": {},
            "all_results": [],
            "errors": [],
            "summary": {}
        }
        
        logger.info("🔍 開始驗證所有 RSS 來源...")
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            for category, regions in DEFAULT_RSS_SOURCES.items():
                category_name = category.value
                report["categories"][category_name] = {
                    "total": 0,
                    "valid": 0,
                    "empty": 0,
                    "error": 0,
                    "regions": {}
                }
                
                for region, feeds in regions.items():
                    region_name = region.value
                    report["categories"][category_name]["regions"][region_name] = {
                        "total": len(feeds),
                        "valid": 0,
                        "empty": 0,
                        "error": 0,
                        "feeds": []
                    }
                    
                    for feed in feeds:
                        result = await self.validate_single_feed(
                            client=client,
                            name=feed.get("name", "Unknown"),
                            url=feed.get("url", ""),
                            category=category_name,
                            region=region_name
                        )
                        
                        report["all_results"].append(result)
                        report["total_sources"] += 1
                        report["categories"][category_name]["total"] += 1
                        
                        if result["status"] == "ok":
                            report["valid_count"] += 1
                            report["categories"][category_name]["valid"] += 1
                            report["categories"][category_name]["regions"][region_name]["valid"] += 1
                        elif result["status"] == "empty":
                            report["empty_count"] += 1
                            report["categories"][category_name]["empty"] += 1
                            report["categories"][category_name]["regions"][region_name]["empty"] += 1
                        else:
                            report["error_count"] += 1
                            report["categories"][category_name]["error"] += 1
                            report["categories"][category_name]["regions"][region_name]["error"] += 1
                            report["errors"].append(result)
                        
                        report["categories"][category_name]["regions"][region_name]["feeds"].append(result)
                        
                        # 顯示進度
                        status_icon = "✅" if result["status"] == "ok" else ("⚠️" if result["status"] == "empty" else "❌")
                        logger.info(f"{status_icon} [{category_name}/{region_name}] {result['name']}: {result['status']}")
        
        # 生成摘要
        report["summary"] = {
            "valid_rate": f"{report['valid_count'] / report['total_sources'] * 100:.1f}%" if report["total_sources"] > 0 else "0%",
            "empty_rate": f"{report['empty_count'] / report['total_sources'] * 100:.1f}%" if report["total_sources"] > 0 else "0%",
            "error_rate": f"{report['error_count'] / report['total_sources'] * 100:.1f}%" if report["total_sources"] > 0 else "0%",
            "categories_summary": {}
        }
        
        for cat_name, cat_data in report["categories"].items():
            report["summary"]["categories_summary"][cat_name] = {
                "valid_rate": f"{cat_data['valid'] / cat_data['total'] * 100:.1f}%" if cat_data["total"] > 0 else "0%",
                "status": "🟢" if cat_data["error"] == 0 else ("🟡" if cat_data["error"] < cat_data["total"] * 0.3 else "🔴")
            }
        
        logger.info(f"✅ 驗證完成: {report['valid_count']}/{report['total_sources']} 有效 ({report['summary']['valid_rate']})")
        
        return report
    
    async def validate_license_status_sources(self) -> Dict[str, Any]:
        """
        驗證 rss_license_status.yaml 中的所有來源
        """
        config_path = Path(__file__).parent.parent.parent / "config" / "rss_license_status.yaml"
        
        if not config_path.exists():
            return {"error": f"Config file not found: {config_path}"}
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        report = {
            "validated_at": datetime.utcnow().isoformat(),
            "config_file": str(config_path),
            "categories": {},
            "all_results": [],
            "total": 0,
            "valid": 0,
            "error": 0
        }
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            # 處理主要類別
            for category in ["fashion", "food", "trend", "finance", "sports", "tech", "entertainment"]:
                if category not in config:
                    continue
                
                cat_config = config[category]
                report["categories"][category] = {"whitelist": [], "greylist": []}
                
                # 驗證白名單
                for feed in cat_config.get("whitelist", []):
                    result = await self.validate_single_feed(
                        client=client,
                        name=feed.get("name", "Unknown"),
                        url=feed.get("url", ""),
                        category=category,
                        region="whitelist"
                    )
                    report["all_results"].append(result)
                    report["categories"][category]["whitelist"].append(result)
                    report["total"] += 1
                    if result["status"] == "ok":
                        report["valid"] += 1
                    else:
                        report["error"] += 1
                
                # 驗證灰名單
                for feed in cat_config.get("greylist", []):
                    result = await self.validate_single_feed(
                        client=client,
                        name=feed.get("name", "Unknown"),
                        url=feed.get("url", ""),
                        category=category,
                        region="greylist"
                    )
                    report["all_results"].append(result)
                    report["categories"][category]["greylist"].append(result)
                    report["total"] += 1
                    if result["status"] == "ok":
                        report["valid"] += 1
                    else:
                        report["error"] += 1
        
        report["valid_rate"] = f"{report['valid'] / report['total'] * 100:.1f}%" if report["total"] > 0 else "0%"
        
        return report
    
    def generate_report_markdown(self, report: Dict[str, Any]) -> str:
        """
        生成 Markdown 格式的驗證報告
        """
        lines = [
            "# RSS 來源驗證報告",
            "",
            f"> **驗證時間**: {report.get('validated_at', 'N/A')}",
            "",
            "## 📊 摘要",
            "",
            f"| 指標 | 數值 |",
            f"|------|:----:|",
            f"| 總來源數 | {report.get('total_sources', report.get('total', 0))} |",
            f"| 有效 | {report.get('valid_count', report.get('valid', 0))} |",
            f"| 空內容 | {report.get('empty_count', 0)} |",
            f"| 錯誤 | {report.get('error_count', report.get('error', 0))} |",
            f"| 有效率 | {report.get('summary', {}).get('valid_rate', report.get('valid_rate', 'N/A'))} |",
            "",
        ]
        
        # 類別摘要
        if "categories" in report:
            lines.extend([
                "## 📂 各類別狀態",
                "",
                "| 類別 | 有效 | 錯誤 | 狀態 |",
                "|------|:----:|:----:|:----:|",
            ])
            
            for cat_name, cat_data in report["categories"].items():
                if isinstance(cat_data, dict) and "total" in cat_data:
                    status = "🟢" if cat_data.get("error", 0) == 0 else "🔴"
                    lines.append(f"| {cat_name} | {cat_data.get('valid', 0)} | {cat_data.get('error', 0)} | {status} |")
            
            lines.append("")
        
        # 錯誤列表
        errors = report.get("errors", [])
        if errors:
            lines.extend([
                "## ❌ 錯誤來源",
                "",
                "| 來源 | 類別 | 地區 | 錯誤 |",
                "|------|------|------|------|",
            ])
            
            for err in errors[:20]:  # 只顯示前 20 個
                lines.append(f"| {err.get('name', 'N/A')} | {err.get('category', 'N/A')} | {err.get('region', 'N/A')} | {err.get('error', 'N/A')} |")
            
            if len(errors) > 20:
                lines.append(f"| ... | ... | ... | +{len(errors) - 20} 更多 |")
            
            lines.append("")
        
        return "\n".join(lines)


async def run_validation():
    """
    執行 RSS 驗證（命令列入口）
    """
    validator = RSSValidator(timeout=15.0)
    
    print("=" * 60)
    print("🔍 RSS 來源驗證工具")
    print("=" * 60)
    
    # 驗證 channel.py 中的來源
    print("\n📂 驗證 channel.py 配置...")
    channel_report = await validator.validate_all_channel_sources()
    
    # 生成報告
    report_md = validator.generate_report_markdown(channel_report)
    
    # 保存報告
    report_path = Path(__file__).parent.parent.parent / "RSS_驗證報告.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    
    print(f"\n📄 報告已保存: {report_path}")
    print(f"\n✅ 有效: {channel_report['valid_count']}/{channel_report['total_sources']}")
    print(f"⚠️ 空: {channel_report['empty_count']}")
    print(f"❌ 錯誤: {channel_report['error_count']}")
    
    return channel_report


if __name__ == "__main__":
    asyncio.run(run_validation())

