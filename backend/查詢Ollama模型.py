"""
查詢 Ollama 雲端 API 可用的模型列表
"""
import asyncio
import httpx
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def list_available_models():
    """查詢可用的模型列表"""
    if not settings.OLLAMA_API_KEY:
        logger.error("❌ 未配置 OLLAMA_API_KEY")
        return
    
    base_url = settings.OLLAMA_CLOUD_BASE_URL or "https://ollama.com/api"
    api_key = settings.OLLAMA_API_KEY
    
    # 嘗試查詢模型列表
    url = f"{base_url}/tags"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"查詢端點: {url}")
            response = await client.get(url, headers=headers)
            logger.info(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ 查詢成功！")
                logger.info(f"回應內容: {data}")
                
                if "models" in data:
                    logger.info("\n可用的模型：")
                    for model in data["models"]:
                        logger.info(f"  - {model.get('name', 'unknown')}")
            else:
                logger.error(f"❌ 查詢失敗: {response.status_code}")
                logger.error(f"回應: {response.text}")
                
                # 嘗試其他端點
                logger.info("\n嘗試其他端點...")
                alt_urls = [
                    f"{base_url}/api/tags",
                    "https://ollama.com/api/tags",
                    "https://api.ollama.com/api/tags"
                ]
                
                for alt_url in alt_urls:
                    try:
                        logger.info(f"嘗試: {alt_url}")
                        response = await client.get(alt_url, headers=headers)
                        logger.info(f"狀態碼: {response.status_code}")
                        if response.status_code == 200:
                            logger.info(f"✅ 成功！回應: {response.text[:200]}")
                            break
                    except Exception as e:
                        logger.warning(f"  ❌ 失敗: {e}")
                        
    except Exception as e:
        logger.error(f"❌ 查詢時發生錯誤: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(list_available_models())
