"""
靈感策劃來源驗證服務
根據 v5.0 靈感策劃技術設計報告實現

功能：
1. 三層驗證機制（邏輯判斷 + AI 驗證 + 交叉比對）
2. 來源可信度評估
3. 驗證狀態標註
"""
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from app.services.ai.ai_service_factory import AIServiceFactory
import logging

logger = logging.getLogger(__name__)


class InspirationSourceVerificationService:
    """靈感策劃來源驗證服務"""
    
    def __init__(self):
        self.ai_service = None
    
    def _get_ai_service(self):
        """取得 AI 服務實例（延遲載入）"""
        if self.ai_service is None:
            self.ai_service = AIServiceFactory.get_service()
        return self.ai_service
    
    async def verify_sources(
        self,
        information: str,
        sources: List[Dict[str, Any]],
        language: str = "zh-TW"
    ) -> Dict[str, Any]:
        """
        三層驗證機制
        
        Args:
            information: 要驗證的資訊
            sources: 來源列表，每個來源包含：
                - url: 來源 URL
                - type: 來源類型（official, wikipedia, media, platform, other）
                - content: 來源內容（可選）
            language: 語言
            
        Returns:
            驗證結果，包含：
            - status: 'verified' | 'partially_verified' | 'unverified'
            - confidence: 0.0 - 1.0
            - sources: 驗證後的來源列表（包含可信度分數）
            - verification_details: 各層驗證結果
        """
        if not sources:
            return {
                "status": "unverified",
                "confidence": 0.0,
                "sources": [],
                "verification_details": {
                    "layer1": {"status": "unverified", "reason": "no_sources"},
                    "layer2": None,
                    "layer3": {"status": "unverified", "reason": "no_sources"}
                }
            }
        
        # 第一層：邏輯判斷（零成本）
        layer1_result = self._logic_verification(sources)
        
        # 第二層：AI 驗證（500-800 Token）
        layer2_result = await self._ai_verification(information, sources, language)
        
        # 第三層：交叉比對（零成本）
        layer3_result = self._cross_reference(sources)
        
        # 綜合結果
        final_result = self._combine_results(
            layer1_result,
            layer2_result,
            layer3_result,
            sources
        )
        
        return final_result
    
    def _logic_verification(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        第一層：邏輯判斷（零成本）
        
        檢查項目：
        1. 來源數量（至少 2 個）
        2. 來源類型（官方網站 > 媒體 > 維基百科）
        3. 來源 URL 格式
        """
        if not sources:
            return {
                "status": "unverified",
                "confidence": 0.0,
                "reason": "no_sources"
            }
        
        # 檢查來源數量
        source_count = len(sources)
        if source_count < 2:
            return {
                "status": "partially_verified",
                "confidence": 0.5,
                "reason": "insufficient_sources",
                "source_count": source_count
            }
        
        # 檢查來源類型
        source_types = [s.get("type", "other") for s in sources]
        type_scores = {
            "official": 1.0,
            "wikipedia": 0.8,
            "media": 0.7,
            "platform": 0.6,
            "other": 0.3
        }
        
        avg_type_score = sum(type_scores.get(t, 0.3) for t in source_types) / len(source_types)
        
        # 檢查 URL 格式
        valid_urls = sum(1 for s in sources if s.get("url", "").startswith("http"))
        url_validity = valid_urls / len(sources) if sources else 0
        
        # 綜合評分
        confidence = (avg_type_score * 0.6 + url_validity * 0.4)
        
        return {
            "status": "verified" if confidence >= 0.7 else "partially_verified",
            "confidence": confidence,
            "reason": "logic_check",
            "source_count": source_count,
            "avg_type_score": avg_type_score,
            "url_validity": url_validity
        }
    
    async def _ai_verification(
        self,
        information: str,
        sources: List[Dict[str, Any]],
        language: str
    ) -> Dict[str, Any]:
        """
        第二層：AI 驗證（500-800 Token）
        
        使用 AI 檢查資訊真實性和來源可信度
        """
        try:
            ai_service = self._get_ai_service()
            
            # 語言標籤
            lang_labels = {
                "zh-TW": "繁體中文",
                "en": "English",
                "ja": "日本語"
            }
            
            # 建構來源列表
            sources_text = "\n".join([
                f"{i+1}. {s.get('url', '')} ({s.get('type', 'unknown')})"
                for i, s in enumerate(sources)
            ])
            
            # 建構 Prompt
            prompt = f"""作為資訊驗證專家，請評估以下資訊的真實性和來源可信度。

**要驗證的資訊**：
{information}

**來源列表**：
{sources_text}

**要求**：
1. 評估資訊是否真實可信
2. 評估每個來源的可信度（0-100 分）
3. 檢查來源是否支持該資訊
4. 判斷是否有衝突或可疑之處

**輸出格式（嚴格遵守 JSON 格式）**：
{{
  "verified": true/false,
  "confidence": 0.0-1.0,
  "reason": "驗證理由",
  "sources_credibility": [
    {{
      "url": "來源 URL",
      "credibility_score": 0-100,
      "supports_info": true/false
    }}
  ],
  "conflicts": ["衝突描述（如有）"],
  "warnings": ["警告訊息（如有）"]
}}

只返回 JSON，不要返回其他內容。輸出語言：{lang_labels.get(language, "繁體中文")}"""
            
            # 調用 AI
            if hasattr(ai_service, '_call_api'):
                response = await ai_service._call_api(prompt)
            else:
                logger.warning("AI 服務不支援 _call_api，跳過 AI 驗證層")
                return {
                    "status": "partially_verified",
                    "confidence": 0.5,
                    "reason": "ai_service_unavailable"
                }
            
            # 解析 AI 回應
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                ai_data = json.loads(json_str)
                
                return {
                    "status": "verified" if ai_data.get("verified", False) else "partially_verified",
                    "confidence": ai_data.get("confidence", 0.5),
                    "reason": ai_data.get("reason", "ai_verification"),
                    "sources_credibility": ai_data.get("sources_credibility", []),
                    "conflicts": ai_data.get("conflicts", []),
                    "warnings": ai_data.get("warnings", [])
                }
            else:
                logger.warning("AI 回應格式錯誤，無法解析")
                return {
                    "status": "partially_verified",
                    "confidence": 0.5,
                    "reason": "ai_response_parse_error"
                }
                
        except Exception as e:
            logger.error(f"AI 驗證失敗: {e}")
            return {
                "status": "partially_verified",
                "confidence": 0.5,
                "reason": f"ai_verification_error: {str(e)}"
            }
    
    def _cross_reference(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        第三層：交叉比對（零成本）
        
        檢查項目：
        1. 至少 2 個獨立來源確認同一資訊
        2. 來源之間的 URL 域名不同（確保獨立性）
        """
        if len(sources) < 2:
            return {
                "status": "unverified",
                "confidence": 0.3,
                "reason": "insufficient_cross_reference"
            }
        
        # 提取域名
        domains = []
        for source in sources:
            url = source.get("url", "")
            if url.startswith("http"):
                try:
                    domain = urlparse(url).netloc
                    # 移除 www. 前綴
                    domain = domain.replace("www.", "")
                    domains.append(domain)
                except Exception:
                    pass
        
        # 檢查獨立域名數量
        unique_domains = len(set(domains))
        
        if unique_domains >= 2:
            return {
                "status": "verified",
                "confidence": 0.9,
                "reason": "cross_referenced",
                "unique_domains": unique_domains
            }
        elif unique_domains == 1:
            return {
                "status": "partially_verified",
                "confidence": 0.6,
                "reason": "single_domain",
                "unique_domains": unique_domains
            }
        else:
            return {
                "status": "unverified",
                "confidence": 0.3,
                "reason": "no_valid_domains"
            }
    
    def _combine_results(
        self,
        layer1: Dict[str, Any],
        layer2: Optional[Dict[str, Any]],
        layer3: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        綜合三層驗證結果
        
        權重：
        - Layer 1（邏輯判斷）：30%
        - Layer 2（AI 驗證）：50%（如果可用）
        - Layer 3（交叉比對）：20%
        """
        # 計算綜合信心度
        confidence = 0.0
        
        # Layer 1: 30%
        confidence += layer1.get("confidence", 0.0) * 0.3
        
        # Layer 2: 50%（如果可用）
        if layer2:
            confidence += layer2.get("confidence", 0.5) * 0.5
        else:
            # 如果 AI 驗證不可用，將權重分配給其他層
            confidence += layer1.get("confidence", 0.0) * 0.25
            confidence += layer3.get("confidence", 0.0) * 0.25
        
        # Layer 3: 20%
        confidence += layer3.get("confidence", 0.0) * 0.2
        
        # 確定最終狀態
        if confidence >= 0.8:
            status = "verified"
        elif confidence >= 0.5:
            status = "partially_verified"
        else:
            status = "unverified"
        
        # 為每個來源添加可信度分數
        verified_sources = []
        for i, source in enumerate(sources):
            source_credibility = 0.7  # 預設值
            
            # 如果有 AI 驗證結果，使用 AI 的評分
            if layer2 and layer2.get("sources_credibility"):
                for cred in layer2["sources_credibility"]:
                    if cred.get("url") == source.get("url"):
                        source_credibility = cred.get("credibility_score", 70) / 100.0
                        break
            
            verified_sources.append({
                **source,
                "credibility_score": source_credibility,
                "verification_status": "verified" if source_credibility >= 0.7 else "partially_verified"
            })
        
        return {
            "status": status,
            "confidence": confidence,
            "sources": verified_sources,
            "verification_details": {
                "layer1": layer1,
                "layer2": layer2,
                "layer3": layer3
            }
        }


# 建立全域實例
inspiration_source_verification_service = InspirationSourceVerificationService()

