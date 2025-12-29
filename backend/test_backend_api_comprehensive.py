"""
完整後端 API 測試腳本
測試所有 API 端點、認證、限流和錯誤處理
"""
import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

# 從環境變數或配置讀取 API Key
API_KEY = os.getenv("API_KEY", "")

# 測試結果
test_results: Dict[str, Any] = {
    "passed": [],
    "failed": [],
    "skipped": [],
    "total": 0,
    "start_time": None,
    "end_time": None,
    "api_key_tests": [],
    "rate_limit_tests": [],
}


def log_test(name: str, passed: bool, message: str = "", category: str = "general"):
    """記錄測試結果"""
    test_results["total"] += 1
    result = {"name": name, "message": message, "category": category}
    
    if passed:
        test_results["passed"].append(result)
        logger.info(f"✅ {name}: {message}")
    else:
        test_results["failed"].append(result)
        logger.error(f"❌ {name}: {message}")


def get_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """取得請求標頭"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    return headers


async def test_health_check(client: httpx.AsyncClient):
    """測試健康檢查端點（不需要認證）"""
    try:
        response = await client.get(
            f"{API_BASE_URL}/health",
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            log_test(
                "健康檢查",
                True,
                f"狀態: {data.get('status', 'unknown')}, 環境: {data.get('environment', 'unknown')}",
                "health"
            )
            return True
        else:
            log_test("健康檢查", False, f"狀態碼: {response.status_code}", "health")
            return False
    except Exception as e:
        log_test("健康檢查", False, f"連接失敗: {str(e)}", "health")
        return False


async def test_api_key_authentication(client: httpx.AsyncClient):
    """測試 API Key 認證"""
    logger.info("\n🔐 測試 API Key 認證")
    
    if not API_KEY:
        log_test(
            "API Key 認證 - 檢查配置",
            False,
            "未設定 API_KEY 環境變數，跳過認證測試",
            "authentication"
        )
        return
    
    # 測試 1: 無 API Key（應該失敗）
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics?page=1&limit=1",
            headers=get_headers(),
            timeout=TIMEOUT
        )
        if response.status_code == 401:
            log_test(
                "API Key 認證 - 無 Key",
                True,
                "正確拒絕無 API Key 的請求",
                "authentication"
            )
        else:
            log_test(
                "API Key 認證 - 無 Key",
                False,
                f"預期 401，實際: {response.status_code}",
                "authentication"
            )
    except Exception as e:
        log_test("API Key 認證 - 無 Key", False, f"錯誤: {str(e)}", "authentication")
    
    # 測試 2: 錯誤的 API Key（應該失敗）
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics?page=1&limit=1",
            headers=get_headers("wrong_api_key_12345"),
            timeout=TIMEOUT
        )
        if response.status_code == 401:
            log_test(
                "API Key 認證 - 錯誤 Key",
                True,
                "正確拒絕錯誤的 API Key",
                "authentication"
            )
        else:
            log_test(
                "API Key 認證 - 錯誤 Key",
                False,
                f"預期 401，實際: {response.status_code}",
                "authentication"
            )
    except Exception as e:
        log_test("API Key 認證 - 錯誤 Key", False, f"錯誤: {str(e)}", "authentication")
    
    # 測試 3: 正確的 API Key（應該成功）
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics?page=1&limit=1",
            headers=get_headers(API_KEY),
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            log_test(
                "API Key 認證 - 正確 Key",
                True,
                "正確的 API Key 認證成功",
                "authentication"
            )
        else:
            log_test(
                "API Key 認證 - 正確 Key",
                False,
                f"預期 200，實際: {response.status_code}",
                "authentication"
            )
    except Exception as e:
        log_test("API Key 認證 - 正確 Key", False, f"錯誤: {str(e)}", "authentication")
    
    # 測試 4: Bearer Token 格式
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = await client.get(
            f"{API_BASE_URL}/topics?page=1&limit=1",
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            log_test(
                "API Key 認證 - Bearer Token",
                True,
                "Bearer Token 格式認證成功",
                "authentication"
            )
        else:
            log_test(
                "API Key 認證 - Bearer Token",
                False,
                f"預期 200，實際: {response.status_code}",
                "authentication"
            )
    except Exception as e:
        log_test("API Key 認證 - Bearer Token", False, f"錯誤: {str(e)}", "authentication")


async def test_rate_limiting(client: httpx.AsyncClient):
    """測試 Rate Limiting"""
    logger.info("\n⏱️ 測試 Rate Limiting")
    
    if not API_KEY:
        log_test(
            "Rate Limiting - 檢查配置",
            False,
            "未設定 API_KEY，跳過限流測試",
            "rate_limit"
        )
        return
    
    headers = get_headers(API_KEY)
    
    # 測試 1: 正常請求（應該成功）
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics?page=1&limit=1",
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "N/A")
            rate_limit_limit = response.headers.get("X-RateLimit-Limit", "N/A")
            log_test(
                "Rate Limiting - 正常請求",
                True,
                f"限流標頭正常: Limit={rate_limit_limit}, Remaining={rate_limit_remaining}",
                "rate_limit"
            )
        else:
            log_test(
                "Rate Limiting - 正常請求",
                False,
                f"狀態碼: {response.status_code}",
                "rate_limit"
            )
    except Exception as e:
        log_test("Rate Limiting - 正常請求", False, f"錯誤: {str(e)}", "rate_limit")
    
    # 測試 2: 快速發送多個請求（測試每分鐘限制）
    logger.info("  發送多個請求測試每分鐘限流...")
    success_count = 0
    rate_limit_exceeded = False
    
    try:
        for i in range(70):  # 發送 70 個請求（超過預設的 60/分鐘）
            response = await client.get(
                f"{API_BASE_URL}/topics?page=1&limit=1",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limit_exceeded = True
                log_test(
                    "Rate Limiting - 每分鐘限制",
                    True,
                    f"在第 {i+1} 個請求時觸發限流（429）",
                    "rate_limit"
                )
                break
            else:
                log_test(
                    "Rate Limiting - 每分鐘限制",
                    False,
                    f"預期 200 或 429，實際: {response.status_code}",
                    "rate_limit"
                )
                break
            
            # 稍微延遲，避免過快
            await asyncio.sleep(0.1)
        
        if not rate_limit_exceeded:
            log_test(
                "Rate Limiting - 每分鐘限制",
                False,
                f"發送 {success_count} 個請求未觸發限流（可能需要調整測試）",
                "rate_limit"
            )
    except Exception as e:
        log_test("Rate Limiting - 每分鐘限制", False, f"錯誤: {str(e)}", "rate_limit")


async def test_topics_api(client: httpx.AsyncClient):
    """測試 Topics API"""
    logger.info("\n📋 測試 Topics API")
    
    headers = get_headers(API_KEY) if API_KEY else get_headers()
    
    # 測試 1: 取得主題列表
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics?page=1&limit=10",
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            topics = data.get("data", [])
            pagination = data.get("pagination", {})
            log_test(
                "Topics - 列表",
                True,
                f"取得 {len(topics)} 個主題，總數: {pagination.get('total', 0)}",
                "topics"
            )
            
            # 取得第一個主題 ID 用於後續測試
            topic_id = topics[0].get("id") if topics else None
            
            # 測試分頁
            if pagination.get("totalPages", 0) > 1:
                response2 = await client.get(
                    f"{API_BASE_URL}/topics?page=2&limit=10",
                    headers=headers,
                    timeout=TIMEOUT
                )
                if response2.status_code == 200:
                    log_test("Topics - 分頁", True, "第 2 頁載入成功", "topics")
            
            # 測試搜尋
            response3 = await client.get(
                f"{API_BASE_URL}/topics?search=fashion&page=1&limit=10",
                headers=headers,
                timeout=TIMEOUT
            )
            if response3.status_code == 200:
                log_test("Topics - 搜尋", True, "搜尋功能正常", "topics")
            
            # 測試篩選
            response4 = await client.get(
                f"{API_BASE_URL}/topics?category=fashion&page=1&limit=10",
                headers=headers,
                timeout=TIMEOUT
            )
            if response4.status_code == 200:
                log_test("Topics - 分類篩選", True, "分類篩選正常", "topics")
            
            return topic_id
        else:
            log_test("Topics - 列表", False, f"狀態碼: {response.status_code}", "topics")
            return None
    except Exception as e:
        log_test("Topics - 列表", False, f"錯誤: {str(e)}", "topics")
        return None


async def test_topic_detail(client: httpx.AsyncClient, topic_id: str):
    """測試主題詳情"""
    if not topic_id:
        log_test("Topics - 詳情", False, "無可用主題 ID", "topics")
        return
    
    headers = get_headers(API_KEY) if API_KEY else get_headers()
    
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics/{topic_id}",
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Topics - 詳情",
                True,
                f"主題: {data.get('title', 'N/A')}",
                "topics"
            )
        elif response.status_code == 404:
            log_test("Topics - 詳情", False, f"主題不存在: {topic_id}", "topics")
        else:
            log_test("Topics - 詳情", False, f"狀態碼: {response.status_code}", "topics")
    except Exception as e:
        log_test("Topics - 詳情", False, f"錯誤: {str(e)}", "topics")


async def test_contents_api(client: httpx.AsyncClient, topic_id: str):
    """測試 Contents API"""
    logger.info("\n📄 測試 Contents API")
    
    if not topic_id:
        log_test("Contents - 取得", False, "無可用主題 ID", "contents")
        return
    
    headers = get_headers(API_KEY) if API_KEY else get_headers()
    
    # 測試取得內容
    try:
        response = await client.get(
            f"{API_BASE_URL}/contents/{topic_id}",
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            word_count = data.get("word_count", 0)
            log_test(
                "Contents - 取得",
                True,
                f"字數: {word_count}",
                "contents"
            )
        elif response.status_code == 404:
            log_test("Contents - 取得", False, "內容不存在", "contents")
        else:
            log_test("Contents - 取得", False, f"狀態碼: {response.status_code}", "contents")
    except Exception as e:
        log_test("Contents - 取得", False, f"錯誤: {str(e)}", "contents")


async def test_images_api(client: httpx.AsyncClient, topic_id: str):
    """測試 Images API"""
    logger.info("\n🖼️ 測試 Images API")
    
    headers = get_headers(API_KEY) if API_KEY else get_headers()
    
    # 測試 1: 取得主題圖片列表
    if topic_id:
        try:
            response = await client.get(
                f"{API_BASE_URL}/images/{topic_id}",
                headers=headers,
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                images = data if isinstance(data, list) else data.get("data", [])
                log_test(
                    "Images - 列表",
                    True,
                    f"取得 {len(images)} 張圖片",
                    "images"
                )
            else:
                log_test("Images - 列表", False, f"狀態碼: {response.status_code}", "images")
        except Exception as e:
            log_test("Images - 列表", False, f"錯誤: {str(e)}", "images")
    
    # 測試 2: 搜尋圖片
    try:
        response = await client.get(
            f"{API_BASE_URL}/images/search?keywords=fashion&page=1&limit=10",
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            images = data.get("data", [])
            pagination = data.get("pagination", {})
            log_test(
                "Images - 搜尋",
                True,
                f"找到 {len(images)} 張圖片，總數: {pagination.get('total', 0)}",
                "images"
            )
        else:
            log_test("Images - 搜尋", False, f"狀態碼: {response.status_code}", "images")
    except Exception as e:
        log_test("Images - 搜尋", False, f"錯誤: {str(e)}", "images")


async def test_error_handling(client: httpx.AsyncClient):
    """測試錯誤處理"""
    logger.info("\n⚠️ 測試錯誤處理")
    
    headers = get_headers(API_KEY) if API_KEY else get_headers()
    
    # 測試 1: 404 錯誤
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics/non_existent_id_12345",
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code == 404:
            log_test("錯誤處理 - 404", True, "404 錯誤處理正常", "error_handling")
        else:
            log_test(
                "錯誤處理 - 404",
                False,
                f"預期 404，實際: {response.status_code}",
                "error_handling"
            )
    except Exception as e:
        log_test("錯誤處理 - 404", False, f"錯誤: {str(e)}", "error_handling")
    
    # 測試 2: 400 錯誤（無效參數）
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics?page=-1",
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code in [400, 422]:
            log_test("錯誤處理 - 400", True, "400/422 錯誤處理正常", "error_handling")
        else:
            log_test(
                "錯誤處理 - 400",
                False,
                f"預期 400/422，實際: {response.status_code}",
                "error_handling"
            )
    except Exception as e:
        log_test("錯誤處理 - 400", False, f"錯誤: {str(e)}", "error_handling")
    
    # 測試 3: 無效的 JSON（POST 請求）
    try:
        response = await client.post(
            f"{API_BASE_URL}/topics",
            headers=headers,
            content="invalid json",
            timeout=TIMEOUT
        )
        if response.status_code in [400, 422]:
            log_test("錯誤處理 - 無效 JSON", True, "無效 JSON 處理正常", "error_handling")
        else:
            log_test(
                "錯誤處理 - 無效 JSON",
                False,
                f"預期 400/422，實際: {response.status_code}",
                "error_handling"
            )
    except Exception as e:
        log_test("錯誤處理 - 無效 JSON", False, f"錯誤: {str(e)}", "error_handling")


async def run_all_tests():
    """執行所有測試"""
    test_results["start_time"] = datetime.now().isoformat()
    
    logger.info("=" * 70)
    logger.info("開始執行完整後端 API 測試")
    logger.info("=" * 70)
    logger.info(f"API Base URL: {API_BASE_URL}")
    logger.info(f"API Key: {'已設定' if API_KEY else '未設定'}")
    logger.info("=" * 70)
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # 1. 健康檢查
        logger.info("\n📋 測試 1: 健康檢查")
        health_ok = await test_health_check(client)
        if not health_ok:
            logger.error("❌ API 服務未運行，請先啟動後端服務")
            logger.info("啟動命令: cd backend && python -m uvicorn app.main:app --reload")
            return
        
        # 2. API Key 認證測試
        logger.info("\n📋 測試 2: API Key 認證")
        await test_api_key_authentication(client)
        
        # 3. Rate Limiting 測試
        logger.info("\n📋 測試 3: Rate Limiting")
        await test_rate_limiting(client)
        
        # 4. Topics API 測試
        logger.info("\n📋 測試 4: Topics API")
        topic_id = await test_topics_api(client)
        
        # 5. Topic Detail 測試
        if topic_id:
            logger.info("\n📋 測試 5: Topic Detail")
            await test_topic_detail(client, topic_id)
        
        # 6. Contents API 測試
        if topic_id:
            logger.info("\n📋 測試 6: Contents API")
            await test_contents_api(client, topic_id)
        
        # 7. Images API 測試
        logger.info("\n📋 測試 7: Images API")
        await test_images_api(client, topic_id if topic_id else "")
        
        # 8. 錯誤處理測試
        logger.info("\n📋 測試 8: 錯誤處理")
        await test_error_handling(client)
    
    test_results["end_time"] = datetime.now().isoformat()
    
    # 輸出測試報告
    logger.info("\n" + "=" * 70)
    logger.info("測試報告")
    logger.info("=" * 70)
    logger.info(f"總測試數: {test_results['total']}")
    logger.info(f"✅ 通過: {len(test_results['passed'])}")
    logger.info(f"❌ 失敗: {len(test_results['failed'])}")
    logger.info(f"⏭️ 跳過: {len(test_results['skipped'])}")
    
    # 按類別統計
    categories = {}
    for test in test_results['passed'] + test_results['failed']:
        cat = test.get('category', 'general')
        if cat not in categories:
            categories[cat] = {'passed': 0, 'failed': 0}
        if test in test_results['passed']:
            categories[cat]['passed'] += 1
        else:
            categories[cat]['failed'] += 1
    
    logger.info("\n按類別統計:")
    for cat, stats in categories.items():
        total = stats['passed'] + stats['failed']
        logger.info(f"  {cat}: ✅ {stats['passed']} / ❌ {stats['failed']} (總計: {total})")
    
    if test_results['failed']:
        logger.info("\n失敗的測試:")
        for test in test_results['failed']:
            logger.error(f"  - [{test.get('category', 'general')}] {test['name']}: {test['message']}")
    
    # 儲存測試報告
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n📄 測試報告已儲存: {report_file}")
    
    # 計算成功率
    success_rate = (len(test_results['passed']) / test_results['total'] * 100) if test_results['total'] > 0 else 0
    logger.info(f"📊 成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        logger.info("✅ 測試整體通過！")
    elif success_rate >= 60:
        logger.warning("⚠️ 測試部分通過，建議修復失敗的測試")
    else:
        logger.error("❌ 測試失敗較多，需要檢查系統配置")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

