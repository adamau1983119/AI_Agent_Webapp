"""
測試 Elasticsearch HTTPS 連接
"""
import asyncio
import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.elasticsearch_service import es_service
from app.config_module import settings


async def test_elasticsearch_https():
    """測試 Elasticsearch HTTPS 連接"""
    print("=" * 50)
    print("Elasticsearch HTTPS Connection Test")
    print("=" * 50)
    print()
    
    # 顯示配置
    print("Configuration:")
    print(f"  ELASTICSEARCH_ENABLED: {settings.ELASTICSEARCH_ENABLED}")
    print(f"  ELASTICSEARCH_HOSTS: {settings.ELASTICSEARCH_HOSTS}")
    print(f"  ELASTICSEARCH_USE_SSL: {settings.ELASTICSEARCH_USE_SSL}")
    print(f"  ELASTICSEARCH_USERNAME: {settings.ELASTICSEARCH_USERNAME}")
    print(f"  ELASTICSEARCH_PASSWORD: {'*' * len(settings.ELASTICSEARCH_PASSWORD) if settings.ELASTICSEARCH_PASSWORD else '(empty)'}")
    print()
    
    if not settings.ELASTICSEARCH_ENABLED:
        print("❌ Elasticsearch is disabled in configuration")
        print("   Set ELASTICSEARCH_ENABLED=true in .env file")
        return
    
    # 測試連接
    print("Testing connection...")
    try:
        await es_service.connect()
        
        if es_service.es_client:
            print("✅ Connection successful!")
            print()
            
            # 檢查健康狀態
            print("Checking health status...")
            health = await es_service.health_check()
            print(f"  Status: {health.get('status', 'unknown')}")
            print(f"  Cluster: {health.get('cluster_name', 'unknown')}")
            print(f"  Nodes: {health.get('number_of_nodes', 'unknown')}")
            print()
            
            # 測試 IK Analyzer
            print("Testing IK Analyzer...")
            try:
                test_result = await es_service.es_client.indices.analyze(
                    body={
                        "analyzer": "ik_max_word",
                        "text": "測試中文分詞"
                    }
                )
                tokens = test_result.get("tokens", [])
                if tokens:
                    print("✅ IK Analyzer is working!")
                    print(f"  Tokens: {[t['token'] for t in tokens]}")
                else:
                    print("⚠️ IK Analyzer returned no tokens")
            except Exception as e:
                print(f"⚠️ IK Analyzer test failed: {e}")
            
            # 斷開連接
            await es_service.disconnect()
        else:
            print("❌ Connection failed - client is None")
            print("   Check Elasticsearch logs for details")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check if Elasticsearch is running")
        print("  2. Verify HTTPS configuration in .env")
        print("  3. Check username and password")
        print("  4. Review Elasticsearch logs")


if __name__ == "__main__":
    asyncio.run(test_elasticsearch_https())

