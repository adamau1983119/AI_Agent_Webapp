"""
Elasticsearch 搜尋服務
提供中文全文搜尋功能，支援 IK Analyzer 中文斷詞
"""
from typing import Optional, List, Dict, Any
import logging
from elasticsearch import AsyncElasticsearch
from app.config_module import settings

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Elasticsearch 搜尋服務"""
    
    def __init__(self):
        self.es_client: Optional[AsyncElasticsearch] = None
        self.enabled = settings.ELASTICSEARCH_ENABLED
        self.index_name = settings.ELASTICSEARCH_INDEX
    
    async def connect(self):
        """連接到 Elasticsearch"""
        if not self.enabled:
            logger.info("Elasticsearch 已禁用，將使用 MongoDB 搜尋")
            return
        
        try:
            # 解析多個主機（逗號分隔）
            hosts = [
                host.strip() 
                for host in settings.ELASTICSEARCH_HOSTS.split(",")
                if host.strip()
            ]
            
            # 自動檢測是否使用 HTTPS（從 URL 協議判斷）
            use_ssl = settings.ELASTICSEARCH_USE_SSL
            if not use_ssl:
                # 檢查 URL 是否以 https:// 開頭
                for host in hosts:
                    if host.startswith("https://"):
                        use_ssl = True
                        logger.info("檢測到 HTTPS URL，自動啟用 SSL")
                        break
            
            # 建立連接參數
            es_params = {
                "hosts": hosts,
                "timeout": settings.ELASTICSEARCH_TIMEOUT,
                "max_retries": settings.ELASTICSEARCH_MAX_RETRIES,
                "retry_on_timeout": True
            }
            
            # 如果配置了用戶名和密碼，添加認證
            if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
                from elasticsearch import BasicAuth
                es_params["basic_auth"] = (
                    settings.ELASTICSEARCH_USERNAME,
                    settings.ELASTICSEARCH_PASSWORD
                )
                logger.info("Elasticsearch 認證已啟用")
            
            # 如果使用 SSL/HTTPS
            if use_ssl:
                es_params["use_ssl"] = True
                es_params["verify_certs"] = False  # 開發環境可以設為 False（使用自簽名證書）
                es_params["ssl_show_warn"] = False  # 不顯示 SSL 警告
                logger.info("Elasticsearch SSL/HTTPS 已啟用")
            
            # 建立 Elasticsearch 客戶端
            self.es_client = AsyncElasticsearch(**es_params)
            
            # 測試連接
            info = await self.es_client.info()
            logger.info(f"✅ Elasticsearch 連接成功: {info['cluster_name']}")
            
            # 檢查 IK Analyzer 插件
            await self._check_ik_analyzer()
            
            # 確保索引存在
            await self._ensure_index_exists()
        except Exception as e:
            logger.warning(f"Elasticsearch 連接失敗: {e}，將回退到 MongoDB 搜尋")
            self.enabled = False
            self.es_client = None
    
    async def disconnect(self):
        """斷開 Elasticsearch 連接"""
        if self.es_client:
            await self.es_client.close()
    
    async def _check_ik_analyzer(self):
        """檢查 IK Analyzer 插件是否安裝"""
        if not self.es_client:
            return
        
        try:
            # 檢查插件列表
            plugins = await self.es_client.cat.plugins(format="json")
            ik_plugin = [p for p in plugins if "analysis-ik" in p.get("component", "")]
            
            if ik_plugin:
                logger.info(f"✅ IK Analyzer 插件已安裝: {ik_plugin[0].get('version', 'unknown')}")
                
                # 測試 IK Analyzer 是否正常工作
                try:
                    test_result = await self.es_client.indices.analyze(
                        body={
                            "analyzer": "ik_max_word",
                            "text": "測試中文分詞"
                        }
                    )
                    if test_result.get("tokens"):
                        logger.info("✅ IK Analyzer 正常工作")
                    else:
                        logger.warning("⚠️ IK Analyzer 可能未正確配置")
                except Exception as e:
                    logger.warning(f"⚠️ IK Analyzer 測試失敗: {e}")
            else:
                logger.warning("⚠️ IK Analyzer 插件未安裝")
                logger.warning("   請參考 backend/scripts/install_ik_analyzer.md 安裝指南")
                logger.warning("   或訪問: https://github.com/medcl/elasticsearch-analysis-ik")
        except Exception as e:
            logger.warning(f"檢查 IK Analyzer 插件失敗: {e}")
    
    async def _ensure_index_exists(self):
        """確保索引存在，如果不存在則創建"""
        if not self.es_client:
            return
        
        try:
            exists = await self.es_client.indices.exists(index=self.index_name)
            
            if not exists:
                # 創建索引並設定 mapping
                await self.es_client.indices.create(
                    index=self.index_name,
                    body={
                        "settings": {
                            "analysis": {
                                "analyzer": {
                                    "chinese_analyzer": {
                                        "type": "custom",
                                        "tokenizer": "ik_max_word",
                                        "filter": ["lowercase", "stop"]
                                    }
                                }
                            }
                        },
                        "mappings": {
                            "properties": {
                                "id": {"type": "keyword"},
                                "title": {
                                    "type": "text",
                                    "analyzer": "chinese_analyzer",
                                    "fields": {
                                        "keyword": {"type": "keyword"}
                                    }
                                },
                                "summary": {
                                    "type": "text",
                                    "analyzer": "chinese_analyzer"
                                },
                                "description": {
                                    "type": "text",
                                    "analyzer": "chinese_analyzer"
                                },
                                "content": {
                                    "type": "text",
                                    "analyzer": "chinese_analyzer"
                                },
                                "category": {"type": "keyword"},
                                "status": {"type": "keyword"},
                                "generated_at": {"type": "date"},
                                "metadata": {
                                    "properties": {
                                        "categories": {"type": "keyword"},
                                        "tags": {"type": "keyword"},
                                        "created_at": {"type": "date"}
                                    }
                                }
                            }
                        }
                    }
                )
                logger.info(f"✅ 創建 Elasticsearch 索引: {self.index_name}")
        except Exception as e:
            logger.warning(f"確保索引存在失敗: {e}（如果索引已存在則可忽略）")
    
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        使用 Elasticsearch 搜尋主題
        
        Args:
            query: 搜尋關鍵字
            category: 分類篩選
            page: 頁碼
            limit: 每頁數量
            
        Returns:
            搜尋結果，格式：{"total": 0, "results": []}
        """
        if not self.enabled or not self.es_client:
            raise Exception("Elasticsearch 未啟用或未連接")
        
        try:
            # 建立查詢條件
            must_clauses = [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "summary^2", "description^2", "content"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                }
            ]
            
            # 分類篩選
            if category:
                must_clauses.append({"term": {"category": category}})
            
            # 排除已刪除的主題
            must_clauses.append({
                "bool": {
                    "must_not": {
                        "term": {"status": "deleted"}
                    }
                }
            })
            
            # 執行搜尋
            from_index = (page - 1) * limit
            
            response = await self.es_client.search(
                index=self.index_name,
                body={
                    "query": {
                        "bool": {
                            "must": must_clauses
                        }
                    },
                    "sort": [
                        {"_score": {"order": "desc"}},
                        {"generated_at": {"order": "desc"}}
                    ],
                    "from": from_index,
                    "size": limit
                }
            )
            
            # 解析結果
            total = response["hits"]["total"]["value"]
            results = []
            
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                source["_score"] = hit["_score"]  # 保留相關度分數
                results.append(source)
            
            return {
                "total": total,
                "results": results
            }
        except Exception as e:
            logger.error(f"Elasticsearch 搜尋失敗: {e}")
            raise Exception(f"Elasticsearch 搜尋失敗: {str(e)}")
    
    async def index_topic(self, topic: Dict[str, Any]):
        """
        索引主題到 Elasticsearch
        
        Args:
            topic: 主題資料
        """
        if not self.enabled or not self.es_client:
            return
        
        try:
            topic_id = topic.get("id")
            if not topic_id:
                logger.warning("主題缺少 ID，無法索引")
                return
            
            await self.es_client.index(
                index=self.index_name,
                id=topic_id,
                body=topic
            )
            logger.debug(f"索引主題成功: {topic_id}")
        except Exception as e:
            logger.warning(f"索引主題失敗: {e}")
    
    async def update_topic(self, topic_id: str, topic: Dict[str, Any]):
        """
        更新 Elasticsearch 中的主題
        
        Args:
            topic_id: 主題 ID
            topic: 主題資料
        """
        if not self.enabled or not self.es_client:
            return
        
        try:
            await self.es_client.update(
                index=self.index_name,
                id=topic_id,
                body={"doc": topic}
            )
            logger.debug(f"更新主題索引成功: {topic_id}")
        except Exception as e:
            logger.warning(f"更新主題索引失敗: {e}")
    
    async def delete_topic(self, topic_id: str):
        """
        從 Elasticsearch 中刪除主題
        
        Args:
            topic_id: 主題 ID
        """
        if not self.enabled or not self.es_client:
            return
        
        try:
            await self.es_client.delete(
                index=self.index_name,
                id=topic_id,
                ignore=[404]  # 如果不存在則忽略
            )
            logger.debug(f"刪除主題索引成功: {topic_id}")
        except Exception as e:
            logger.warning(f"刪除主題索引失敗: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        檢查 Elasticsearch 健康狀態
        
        Returns:
            健康狀態資訊
        """
        if not self.enabled:
            return {"status": "disabled"}
        
        if not self.es_client:
            return {"status": "not_connected"}
        
        try:
            health = await self.es_client.cluster.health()
            return {
                "status": health["status"],
                "cluster_name": health["cluster_name"],
                "number_of_nodes": health["number_of_nodes"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# 全域 Elasticsearch 服務實例
es_service = ElasticsearchService()

