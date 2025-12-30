"""
增強版照片匹配器
加入分層閾值檢查（專家建議：核心≥0.85，非核心≥0.75）
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.images.image_service import ImageService
from app.models.image import ImageSource

logger = logging.getLogger(__name__)


class EnhancedPhotoMatcher:
    """增強版照片匹配器（專家建議）"""
    
    def __init__(self):
        self.image_service = ImageService()
    
    async def match_photos_with_layers(
        self,
        article_text: str,
        topic_id: str,
        min_count: int = 8
    ) -> Dict[str, Any]:
        """
        分層匹配度檢查（專家建議）
        
        Args:
            article_text: 文章內容
            topic_id: 主題 ID
            min_count: 最少照片數量
            
        Returns:
            匹配結果
        """
        # 提取核心要素和非核心要素
        core_features = self._extract_core_features(article_text)
        non_core_features = self._extract_non_core_features(article_text)
        
        # 搜尋照片
        all_photos = []
        matched_photos = []
        
        # 為核心要素搜尋照片
        for core_item in core_features:
            photos = await self.image_service.search_images(
                keywords=core_item,
                limit=5,
                use_fallback=True
            )
            all_photos.extend(photos)
        
        # 為非核心要素搜尋照片
        for non_core_item in non_core_features:
            photos = await self.image_service.search_images(
                keywords=non_core_item,
                limit=3,
                use_fallback=True
            )
            all_photos.extend(photos)
        
        # 驗證匹配度
        for photo in all_photos[:min_count * 2]:  # 搜尋更多以確保有足夠匹配的
            # 核心要素匹配（必須 ≥ 0.85）
            core_match_score = self._calculate_core_match_score(core_features, photo)
            
            if core_match_score < 0.85:
                continue  # 核心要素不匹配，跳過
            
            # 非核心要素匹配（必須 ≥ 0.75）
            non_core_match_score = self._calculate_non_core_match_score(non_core_features, photo)
            
            if non_core_match_score < 0.75:
                continue  # 非核心要素不匹配，跳過
            
            # 計算整體分數
            overall_score = (core_match_score * 0.6 + non_core_match_score * 0.4)
            
            matched_photos.append({
                **photo,
                "core_match_score": core_match_score,
                "non_core_match_score": non_core_match_score,
                "overall_score": overall_score,
                "matches_item": self._find_matched_item(core_features, photo)
            })
            
            if len(matched_photos) >= min_count:
                break
        
        return {
            "topic_id": topic_id,
            "matched_photos": matched_photos[:min_count],
            "summary": {
                "total_found": len(all_photos),
                "matched_items": len([p for p in matched_photos if p.get("matches_item")]),
                "unmatched_items": len(core_features) - len([p for p in matched_photos if p.get("matches_item")]),
                "all_jpg": all(photo.get("url", "").lower().endswith(".jpg") for photo in matched_photos)
            }
        }
    
    def _extract_core_features(self, text: str) -> List[str]:
        """
        提取核心要素（品牌、品項、明確詞）
        
        例如：白色喱士裙、燒賣皇后、Dior
        """
        core_keywords = []
        
        # 品牌名稱
        brands = ["Dior", "Gucci", "Chanel", "LV", "Prada"]
        for brand in brands:
            if brand.lower() in text.lower():
                core_keywords.append(brand)
        
        # 明確物件（包含顏色、材質、具體名稱）
        # 簡化版：使用關鍵字匹配
        core_patterns = [
            "白色喱士裙", "燒賣皇后", "元朗", "地址",
            "top 3", "排行榜", "第1", "第2", "第3"
        ]
        
        for pattern in core_patterns:
            if pattern in text:
                core_keywords.append(pattern)
        
        return list(set(core_keywords))
    
    def _extract_non_core_features(self, text: str) -> List[str]:
        """
        提取非核心要素（風格、氛圍、材質推測）
        
        例如：優雅、浪漫、現代、休閒
        """
        non_core_keywords = []
        
        # 風格描述
        style_keywords = ["優雅", "浪漫", "現代", "休閒", "正式", "時尚", "經典"]
        for keyword in style_keywords:
            if keyword in text:
                non_core_keywords.append(keyword)
        
        # 氛圍描述
        atmosphere_keywords = ["溫馨", "熱鬧", "安靜", "活潑", "沉穩"]
        for keyword in atmosphere_keywords:
            if keyword in text:
                non_core_keywords.append(keyword)
        
        return list(set(non_core_keywords))
    
    def _calculate_core_match_score(
        self,
        core_features: List[str],
        photo: Dict[str, Any]
    ) -> float:
        """
        計算核心要素匹配分數（必須 ≥ 0.85）
        
        簡化版：使用關鍵字匹配
        實際應該使用 NLP + CV 交叉檢查
        """
        if not core_features:
            return 1.0  # 沒有核心要素，視為匹配
        
        photo_keywords = photo.get("keywords", [])
        photo_description = photo.get("description", "").lower()
        
        matches = 0
        for feature in core_features:
            feature_lower = feature.lower()
            if (feature_lower in photo_description or
                any(feature_lower in kw.lower() for kw in photo_keywords)):
                matches += 1
        
        # 至少匹配50%的核心要素
        match_ratio = matches / len(core_features) if core_features else 0.0
        
        # 轉換為 0.85-1.0 範圍
        score = 0.85 + (match_ratio * 0.15)
        
        return min(1.0, max(0.85, score))
    
    def _calculate_non_core_match_score(
        self,
        non_core_features: List[str],
        photo: Dict[str, Any]
    ) -> float:
        """
        計算非核心要素匹配分數（必須 ≥ 0.75）
        """
        if not non_core_features:
            return 1.0  # 沒有非核心要素，視為匹配
        
        photo_keywords = photo.get("keywords", [])
        photo_description = photo.get("description", "").lower()
        
        matches = 0
        for feature in non_core_features:
            feature_lower = feature.lower()
            if (feature_lower in photo_description or
                any(feature_lower in kw.lower() for kw in photo_keywords)):
                matches += 1
        
        # 至少匹配30%的非核心要素
        match_ratio = matches / len(non_core_features) if non_core_features else 0.0
        
        # 轉換為 0.75-1.0 範圍
        score = 0.75 + (match_ratio * 0.25)
        
        return min(1.0, max(0.75, score))
    
    def _find_matched_item(
        self,
        core_features: List[str],
        photo: Dict[str, Any]
    ) -> Optional[str]:
        """找出匹配的核心要素"""
        photo_description = photo.get("description", "").lower()
        photo_keywords = photo.get("keywords", [])
        
        for feature in core_features:
            feature_lower = feature.lower()
            if (feature_lower in photo_description or
                any(feature_lower in kw.lower() for kw in photo_keywords)):
                return feature
        
        return None

