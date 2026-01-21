"""
測試 IK Analyzer 是否正確安裝和配置
"""
import asyncio
import httpx
import json
from typing import Dict, Any


async def test_ik_analyzer(es_host: str = "http://localhost:9200") -> Dict[str, Any]:
    """
    測試 IK Analyzer 是否正常工作
    
    Args:
        es_host: Elasticsearch 主機地址
        
    Returns:
        測試結果字典
    """
    results = {
        "elasticsearch_connected": False,
        "ik_plugin_installed": False,
        "ik_max_word_works": False,
        "ik_smart_works": False,
        "errors": []
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # 1. 檢查 Elasticsearch 連接
        try:
            response = await client.get(es_host)
            if response.status_code == 200:
                results["elasticsearch_connected"] = True
                es_info = response.json()
                results["es_version"] = es_info.get("version", {}).get("number", "unknown")
                print(f"✅ Elasticsearch 連接成功，版本: {results['es_version']}")
            else:
                results["errors"].append(f"Elasticsearch 返回狀態碼: {response.status_code}")
        except Exception as e:
            results["errors"].append(f"無法連接到 Elasticsearch: {str(e)}")
            print(f"❌ Elasticsearch 連接失敗: {e}")
            return results
        
        # 2. 檢查 IK 插件是否安裝
        try:
            response = await client.get(f"{es_host}/_cat/plugins?format=json")
            if response.status_code == 200:
                plugins = response.json()
                ik_plugin = [p for p in plugins if "analysis-ik" in p.get("component", "")]
                if ik_plugin:
                    results["ik_plugin_installed"] = True
                    results["ik_plugin_version"] = ik_plugin[0].get("version", "unknown")
                    print(f"✅ IK Analyzer 插件已安裝，版本: {results['ik_plugin_version']}")
                else:
                    results["errors"].append("IK Analyzer 插件未找到")
                    print("❌ IK Analyzer 插件未安裝")
        except Exception as e:
            results["errors"].append(f"檢查插件失敗: {str(e)}")
        
        # 3. 測試 ik_max_word 分析器
        try:
            test_text = "中華人民共和國"
            response = await client.post(
                f"{es_host}/_analyze",
                json={
                    "analyzer": "ik_max_word",
                    "text": test_text
                }
            )
            if response.status_code == 200:
                data = response.json()
                tokens = [token["token"] for token in data.get("tokens", [])]
                if len(tokens) > 1:  # 應該分解為多個詞彙
                    results["ik_max_word_works"] = True
                    results["ik_max_word_tokens"] = tokens
                    print(f"✅ ik_max_word 正常工作，分詞結果: {tokens}")
                else:
                    results["errors"].append(f"ik_max_word 分詞結果異常: {tokens}")
            else:
                results["errors"].append(f"ik_max_word 測試失敗，狀態碼: {response.status_code}")
        except Exception as e:
            results["errors"].append(f"測試 ik_max_word 失敗: {str(e)}")
        
        # 4. 測試 ik_smart 分析器
        try:
            test_text = "我愛北京天安門"
            response = await client.post(
                f"{es_host}/_analyze",
                json={
                    "analyzer": "ik_smart",
                    "text": test_text
                }
            )
            if response.status_code == 200:
                data = response.json()
                tokens = [token["token"] for token in data.get("tokens", [])]
                if tokens:
                    results["ik_smart_works"] = True
                    results["ik_smart_tokens"] = tokens
                    print(f"✅ ik_smart 正常工作，分詞結果: {tokens}")
                else:
                    results["errors"].append(f"ik_smart 分詞結果為空")
            else:
                results["errors"].append(f"ik_smart 測試失敗，狀態碼: {response.status_code}")
        except Exception as e:
            results["errors"].append(f"測試 ik_smart 失敗: {str(e)}")
    
    return results


async def main():
    """主函數"""
    import sys
    
    es_host = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:9200"
    
    print("=== IK Analyzer 測試 ===")
    print(f"Elasticsearch 主機: {es_host}\n")
    
    results = await test_ik_analyzer(es_host)
    
    print("\n=== 測試結果 ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # 總結
    if all([
        results["elasticsearch_connected"],
        results["ik_plugin_installed"],
        results["ik_max_word_works"],
        results["ik_smart_works"]
    ]):
        print("\n✅ 所有測試通過！IK Analyzer 已正確安裝和配置。")
        return 0
    else:
        print("\n❌ 部分測試失敗，請檢查錯誤訊息。")
        if results["errors"]:
            print("\n錯誤列表：")
            for error in results["errors"]:
                print(f"  - {error}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

