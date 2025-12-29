"""
完整 API 測試腳本
測試所有 API 端點的功能和錯誤處理
"""
import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

# 測試結果
test_results: Dict[str, Any] = {
    "passed": [],
    "failed": [],
    "skipped": [],
    "total": 0,
    "start_time": None,
    "end_time": None,
}


def log_test(name: str, passed: bool, message: str = ""):
    """記錄測試結果"""
    test_results["total"] += 1
    if passed:
        test_results["passed"].append({"name": name, "message": message})
        logger.info(f"✅ {name}: {message}")
    else:
        test_results["failed"].append({"name": name, "message": message})
        logger.error(f"❌ {name}: {message}")


async def test_health_check(client: httpx.AsyncClient):
    """測試健康檢查端點"""
    try:
        response = await client.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            log_test("健康檢查", True, f"狀態: {data.get('status', 'unknown')}")
            return True
        else:
            log_test("健康檢查", False, f"狀態碼: {response.status_code}")
            return False
    except Exception as e:
        log_test("健康檢查", False, f"連接失敗: {str(e)}")
        return False


async def test_topics_list(client: httpx.AsyncClient):
    """測試主題列表端點"""
    try:
        # 測試基本列表
        response = await client.get(
            f"{API_BASE_URL}/topics?page=1&limit=10",
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            topics = data.get("data", [])
            pagination = data.get("pagination", {})
            log_test(
                "主題列表",
                True,
                f"取得 {len(topics)} 個主題，總數: {pagination.get('total', 0)}"
            )
            
            # 測試分頁
            if pagination.get("totalPages", 0) > 1:
                response2 = await client.get(
                    f"{API_BASE_URL}/topics?page=2&limit=10",
                    timeout=TIMEOUT
                )
                if response2.status_code == 200:
                    log_test("主題列表分頁", True, "第 2 頁載入成功")
                else:
                    log_test("主題列表分頁", False, f"狀態碼: {response2.status_code}")
            
            # 測試篩選
            response3 = await client.get(
                f"{API_BASE_URL}/topics?category=fashion&page=1&limit=10",
                timeout=TIMEOUT
            )
            if response3.status_code == 200:
                log_test("主題列表篩選", True, "分類篩選成功")
            else:
                log_test("主題列表篩選", False, f"狀態碼: {response3.status_code}")
            
            return True
        else:
            log_test("主題列表", False, f"狀態碼: {response.status_code}")
            return False
    except Exception as e:
        log_test("主題列表", False, f"錯誤: {str(e)}")
        return False


async def test_topic_detail(client: httpx.AsyncClient, topic_id: str = "dior_2026_spring_summer"):
    """測試主題詳情端點"""
    try:
        response = await client.get(
            f"{API_BASE_URL}/topics/{topic_id}",
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            log_test(
                "主題詳情",
                True,
                f"主題: {data.get('title', 'N/A')}"
            )
            return data
        elif response.status_code == 404:
            log_test("主題詳情", False, f"主題不存在: {topic_id}")
            return None
        else:
            log_test("主題詳情", False, f"狀態碼: {response.status_code}")
            return None
    except Exception as e:
        log_test("主題詳情", False, f"錯誤: {str(e)}")
        return None


async def test_topic_update(client: httpx.AsyncClient, topic_id: str):
    """測試更新主題端點"""
    try:
        update_data = {
            "title": f"測試更新主題 - {datetime.now().strftime('%H:%M:%S')}",
        }
        response = await client.put(
            f"{API_BASE_URL}/topics/{topic_id}",
            json=update_data,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            log_test("更新主題", True, "主題已更新")
            return True
        else:
            log_test("更新主題", False, f"狀態碼: {response.status_code}")
            return False
    except Exception as e:
        log_test("更新主題", False, f"錯誤: {str(e)}")
        return False


async def test_topic_status_update(client: httpx.AsyncClient, topic_id: str):
    """測試更新主題狀態端點"""
    try:
        response = await client.patch(
            f"{API_BASE_URL}/topics/{topic_id}/status",
            json={"status": "confirmed"},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            log_test("更新主題狀態", True, "狀態已更新為 confirmed")
            return True
        else:
            log_test("更新主題狀態", False, f"狀態碼: {response.status_code}")
            return False
    except Exception as e:
        log_test("更新主題狀態", False, f"錯誤: {str(e)}")
        return False


async def test_content_get(client: httpx.AsyncClient, topic_id: str):
    """測試取得內容端點"""
    try:
        response = await client.get(
            f"{API_BASE_URL}/contents/{topic_id}",
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            word_count = data.get("word_count", 0)
            log_test(
                "取得內容",
                True,
                f"字數: {word_count}"
            )
            return True
        elif response.status_code == 404:
            log_test("取得內容", False, "內容不存在")
            return False
        else:
            log_test("取得內容", False, f"狀態碼: {response.status_code}")
            return False
    except Exception as e:
        log_test("取得內容", False, f"錯誤: {str(e)}")
        return False


async def test_content_generate(client: httpx.AsyncClient, topic_id: str):
    """測試生成內容端點"""
    try:
        generate_data = {
            "type": "both",
            "article_length": 500,
            "script_duration": 30,
        }
        response = await client.post(
            f"{API_BASE_URL}/contents/{topic_id}/generate",
            json=generate_data,
            timeout=120.0  # 生成內容可能需要較長時間
        )
        if response.status_code == 200:
            data = response.json()
            log_test(
                "生成內容",
                True,
                f"內容已生成，字數: {data.get('word_count', 0)}"
            )
            return True
        else:
            error_data = response.json() if response.content else {}
            log_test(
                "生成內容",
                False,
                f"狀態碼: {response.status_code}, 錯誤: {error_data.get('detail', 'unknown')}"
            )
            return False
    except Exception as e:
        log_test("生成內容", False, f"錯誤: {str(e)}")
        return False


async def test_images_get(client: httpx.AsyncClient, topic_id: str):
    """測試取得圖片列表端點"""
    try:
        response = await client.get(
            f"{API_BASE_URL}/images/{topic_id}",
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            images = data if isinstance(data, list) else data.get("data", [])
            log_test(
                "取得圖片列表",
                True,
                f"取得 {len(images)} 張圖片"
            )
            return True
        else:
            log_test("取得圖片列表", False, f"狀態碼: {response.status_code}")
            return False
    except Exception as e:
        log_test("取得圖片列表", False, f"錯誤: {str(e)}")
        return False


async def test_images_search(client: httpx.AsyncClient):
    """測試搜尋圖片端點"""
    try:
        response = await client.get(
            f"{API_BASE_URL}/images/search?keywords=fashion&page=1&limit=10",
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            images = data.get("data", [])
            pagination = data.get("pagination", {})
            log_test(
                "搜尋圖片",
                True,
                f"找到 {len(images)} 張圖片，總數: {pagination.get('total', 0)}"
            )
            return True
        else:
            log_test("搜尋圖片", False, f"狀態碼: {response.status_code}")
            return False
    except Exception as e:
        log_test("搜尋圖片", False, f"錯誤: {str(e)}")
        return False


async def test_error_handling(client: httpx.AsyncClient):
    """測試錯誤處理"""
    try:
        # 測試 404 錯誤
        response = await client.get(
            f"{API_BASE_URL}/topics/non_existent_id",
            timeout=TIMEOUT
        )
        if response.status_code == 404:
            log_test("錯誤處理 - 404", True, "404 錯誤處理正常")
        else:
            log_test("錯誤處理 - 404", False, f"預期 404，實際: {response.status_code}")
        
        # 測試 400 錯誤（無效參數）
        response2 = await client.get(
            f"{API_BASE_URL}/topics?page=-1",
            timeout=TIMEOUT
        )
        if response2.status_code in [400, 422]:
            log_test("錯誤處理 - 400", True, "400 錯誤處理正常")
        else:
            log_test("錯誤處理 - 400", False, f"預期 400/422，實際: {response2.status_code}")
        
        return True
    except Exception as e:
        log_test("錯誤處理", False, f"錯誤: {str(e)}")
        return False


async def run_all_tests():
    """執行所有測試"""
    test_results["start_time"] = datetime.now().isoformat()
    
    logger.info("=" * 60)
    logger.info("開始執行完整 API 測試")
    logger.info("=" * 60)
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # 1. 健康檢查
        logger.info("\n📋 測試 1: 健康檢查")
        health_ok = await test_health_check(client)
        if not health_ok:
            logger.error("❌ API 服務未運行，請先啟動後端服務")
            logger.info("啟動命令: cd backend && python -m uvicorn app.main:app --reload")
            return
        
        # 2. 主題列表
        logger.info("\n📋 測試 2: 主題列表")
        await test_topics_list(client)
        
        # 3. 主題詳情
        logger.info("\n📋 測試 3: 主題詳情")
        topic_data = await test_topic_detail(client)
        topic_id = topic_data.get("id") if topic_data else "dior_2026_spring_summer"
        
        # 4. 更新主題
        if topic_data:
            logger.info("\n📋 測試 4: 更新主題")
            await test_topic_update(client, topic_id)
        
        # 5. 更新主題狀態
        if topic_data:
            logger.info("\n📋 測試 5: 更新主題狀態")
            await test_topic_status_update(client, topic_id)
        
        # 6. 取得內容
        logger.info("\n📋 測試 6: 取得內容")
        await test_content_get(client, topic_id)
        
        # 7. 生成內容（可選，需要較長時間）
        logger.info("\n📋 測試 7: 生成內容（跳過，需要 AI 服務）")
        test_results["skipped"].append({
            "name": "生成內容",
            "message": "需要 AI 服務，手動測試"
        })
        
        # 8. 取得圖片列表
        logger.info("\n📋 測試 8: 取得圖片列表")
        await test_images_get(client, topic_id)
        
        # 9. 搜尋圖片
        logger.info("\n📋 測試 9: 搜尋圖片")
        await test_images_search(client)
        
        # 10. 錯誤處理
        logger.info("\n📋 測試 10: 錯誤處理")
        await test_error_handling(client)
    
    test_results["end_time"] = datetime.now().isoformat()
    
    # 輸出測試報告
    logger.info("\n" + "=" * 60)
    logger.info("測試報告")
    logger.info("=" * 60)
    logger.info(f"總測試數: {test_results['total']}")
    logger.info(f"✅ 通過: {len(test_results['passed'])}")
    logger.info(f"❌ 失敗: {len(test_results['failed'])}")
    logger.info(f"⏭️ 跳過: {len(test_results['skipped'])}")
    
    if test_results['failed']:
        logger.info("\n失敗的測試:")
        for test in test_results['failed']:
            logger.error(f"  - {test['name']}: {test['message']}")
    
    # 儲存測試報告
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n📄 測試報告已儲存: {report_file}")
    
    # 計算成功率
    success_rate = (len(test_results['passed']) / test_results['total'] * 100) if test_results['total'] > 0 else 0
    logger.info(f"📊 成功率: {success_rate:.1f}%")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

