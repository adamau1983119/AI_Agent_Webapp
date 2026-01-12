"""
Google Custom Search API 綜合測試腳本
任務 1.1：測試 Google Custom Search API
"""
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.images.google_custom_search import GoogleCustomSearchService
from app.config import settings
import logging

# 設定輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoogleCSETestReport:
    """Google CSE 測試報告"""
    
    def __init__(self):
        self.test_queries = [
            "cat",
            "dog", 
            "sunset",
            "technology"
        ]
        self.results: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        
    def add_result(self, query: str, status_code: int, items_count: int, error: str = None):
        """添加測試結果"""
        self.results.append({
            "query": query,
            "status_code": status_code,
            "items_count": items_count,
            "error": error,
            "success": status_code == 200 and items_count > 0
        })
    
    def generate_report(self) -> str:
        """生成測試報告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
{'='*80}
Google Custom Search API 測試報告
{'='*80}

測試時間: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
測試持續時間: {duration:.2f} 秒
測試查詢數量: {total_tests}

配置檢查:
  - GOOGLE_API_KEY: {'✅ 已設定' if settings.GOOGLE_API_KEY else '❌ 未設定'}
  - GOOGLE_SEARCH_ENGINE_ID: {'✅ 已設定' if settings.GOOGLE_SEARCH_ENGINE_ID else '❌ 未設定'}

測試結果摘要:
  - 總測試數: {total_tests}
  - 成功數: {successful_tests}
  - 失敗數: {total_tests - successful_tests}
  - 成功率: {success_rate:.1f}%

詳細測試結果:
{'-'*80}
"""
        
        for i, result in enumerate(self.results, 1):
            status_icon = "✅" if result["success"] else "❌"
            report += f"""
測試 {i}: {result['query']}
  {status_icon} 狀態碼: {result['status_code']}
  {status_icon} 返回項目數: {result['items_count']}
"""
            if result["error"]:
                report += f"  ⚠️  錯誤訊息: {result['error']}\n"
        
        report += f"""
{'-'*80}

結論:
"""
        
        if success_rate >= 80:
            report += "✅ 測試通過！至少 80% 的查詢返回了結果。\n"
        else:
            report += "❌ 測試失敗！成功率低於 80%。\n"
            report += "建議檢查:\n"
            report += "  1. Google API Key 是否正確\n"
            report += "  2. Search Engine ID 是否正確\n"
            report += "  3. API 配額是否用盡\n"
            report += "  4. Custom Search Engine 是否啟用圖片搜尋功能\n"
        
        report += f"\n{'='*80}\n"
        
        return report


async def test_google_cse_query(service: GoogleCustomSearchService, query: str, trace_id: str = "") -> Dict[str, Any]:
    """測試單個查詢"""
    try:
        logger.info(f"[{trace_id}] 測試查詢: '{query}'")
        
        # 調用搜尋 API
        images = await service.search_images(
            keywords=query,
            page=1,
            limit=10,
            trace_id=trace_id
        )
        
        items_count = len(images) if images else 0
        status_code = 200  # 如果沒有拋出異常，視為成功
        
        logger.info(f"[{trace_id}] ✅ 查詢成功: 返回 {items_count} 張圖片")
        
        return {
            "status_code": status_code,
            "items_count": items_count,
            "error": None
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[{trace_id}] ❌ 查詢失敗: {error_msg}")
        
        # 嘗試從異常中提取狀態碼
        status_code = 500
        if "403" in error_msg or "Forbidden" in error_msg:
            status_code = 403
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            status_code = 429
        elif "400" in error_msg or "Bad Request" in error_msg:
            status_code = 400
        
        return {
            "status_code": status_code,
            "items_count": 0,
            "error": error_msg
        }


async def main():
    """主測試函數"""
    import uuid
    
    trace_id = str(uuid.uuid4())[:8]
    logger.info(f"[{trace_id}] 開始 Google Custom Search API 綜合測試")
    
    # 檢查配置
    has_api_key = bool(settings.GOOGLE_API_KEY)
    has_search_engine_id = bool(settings.GOOGLE_SEARCH_ENGINE_ID)
    
    if not has_api_key or not has_search_engine_id:
        logger.error("❌ Google Custom Search API 未完整設定！")
        logger.info("請在 Railway 環境變數中設定:")
        logger.info("  - GOOGLE_API_KEY")
        logger.info("  - GOOGLE_SEARCH_ENGINE_ID")
        return
    
    # 初始化服務
    service = GoogleCustomSearchService()
    
    # 初始化測試報告
    report = GoogleCSETestReport()
    
    # 執行測試
    logger.info(f"\n開始執行 {len(report.test_queries)} 個測試查詢...\n")
    
    for query in report.test_queries:
        result = await test_google_cse_query(service, query, trace_id)
        report.add_result(query, result["status_code"], result["items_count"], result["error"])
        
        # 避免速率限制，稍作延遲
        await asyncio.sleep(1)
    
    # 生成並顯示報告
    report_text = report.generate_report()
    print(report_text)
    
    # 保存報告到文件
    report_file = f"google_cse_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    logger.info(f"✅ 測試報告已保存到: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())

