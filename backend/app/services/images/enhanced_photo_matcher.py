"""
增強版照片匹配器
改進版：使用 ImageServiceManager、動態關鍵字提取、降低匹配度閾值
"""
import re
import logging
from typing import Dict, Any, List, Optional
from app.services.images.image_service_manager import ImageServiceManager
from app.models.image import ImageSource

logger = logging.getLogger(__name__)


class EnhancedPhotoMatcher:
    """增強版照片匹配器（改進版）"""
    
    def __init__(self):
        # 改用 ImageServiceManager，支援 Google Custom Search
        self.image_service = ImageServiceManager()
    
    async def match_photos_with_layers(
        self,
        article_text: str,
        topic_id: str,
        min_count: int = 8
    ) -> Dict[str, Any]:
        """
        分層匹配度檢查（改進版）
        
        Args:
            article_text: 文章內容
            topic_id: 主題 ID
            min_count: 最少照片數量
            
        Returns:
            匹配結果（包含 matched_photos 和 summary）
        """
        logger.info(f"[{topic_id}] 開始匹配照片，文章長度: {len(article_text)} 字")
        
        # 提取核心與非核心要素
        core_features = self._extract_core_features(article_text)
        non_core_features = self._extract_non_core_features(article_text)
        logger.info(f"[{topic_id}] 核心要素: {core_features}")
        logger.info(f"[{topic_id}] 非核心要素: {non_core_features}")
        
        # 如果核心要素為空，使用文章前100字作為備援關鍵字
        if not core_features:
            logger.warning(f"[{topic_id}] ⚠️ 核心要素為空，使用文章前100字作為備援關鍵字")
            fallback_keywords = article_text[:100].strip()
            if fallback_keywords:
                core_features = [fallback_keywords]
        
        all_photos = []
        
        # 搜尋核心要素相關照片
        for core_item in core_features:
            try:
                result = await self.image_service.search_images(
                    keywords=core_item,
                    source=None,  # 讓 ImageServiceManager 自動選擇
                    page=1,
                    limit=5,
                    trace_id=topic_id
                )
                photos = result.get("items", [])
                all_photos.extend(photos)
                logger.info(f"[{topic_id}] 為關鍵字 '{core_item}' 搜尋到 {len(photos)} 張照片 (來源: {result.get('source', 'unknown')})")
            except Exception as e:
                logger.warning(f"[{topic_id}] 搜尋關鍵字 '{core_item}' 失敗: {e}")
                continue
        
        # 為非核心要素搜尋照片（補充）
        for non_core_item in non_core_features[:3]:  # 只搜尋前3個非核心要素
            try:
                result = await self.image_service.search_images(
                    keywords=non_core_item,
                    source=None,
                    page=1,
                    limit=3,
                    trace_id=topic_id
                )
                photos = result.get("items", [])
                all_photos.extend(photos)
                logger.info(f"[{topic_id}] 為關鍵字 '{non_core_item}' 搜尋到 {len(photos)} 張照片 (來源: {result.get('source', 'unknown')})")
            except Exception as e:
                logger.warning(f"[{topic_id}] 搜尋關鍵字 '{non_core_item}' 失敗: {e}")
                continue
        
        logger.info(f"[{topic_id}] 總共搜尋到 {len(all_photos)} 張照片")
        
        matched_photos = []
        
        # 動態閾值調整機制
        thresholds = [
            (0.6, 0.5),  # 初始閾值（核心≥0.6，非核心≥0.5）
            (0.5, 0.4),  # 第一次降低
            (0.4, 0.3),  # 第二次降低
        ]
        
        for core_threshold, non_core_threshold in thresholds:
            logger.info(f"[{topic_id}] 嘗試閾值: 核心≥{core_threshold}, 非核心≥{non_core_threshold}，當前已匹配 {len(matched_photos)} 張")
            
            for photo in all_photos:
                # 跳過已經匹配的照片
                if any(p.get("url") == photo.get("url") for p in matched_photos):
                    continue
                
                core_score = self._calculate_core_match_score(core_features, photo)
                # 如果核心要素為空或只有備援關鍵字，降低要求
                if not core_features or (len(core_features) == 1 and len(core_features[0]) > 50):
                    # 使用備援關鍵字時，只要非核心匹配就通過
                    if non_core_score < non_core_threshold:
                        continue
                elif core_score < core_threshold:
                    continue
                
                non_core_score = self._calculate_non_core_match_score(non_core_features, photo)
                if non_core_score < non_core_threshold:
                    continue
                
                # 計算整體分數
                overall_score = (core_score * 0.6 + non_core_score * 0.4)
                
                matched_photos.append({
                    **photo,
                    "core_match_score": core_score,
                    "non_core_match_score": non_core_score,
                    "overall_score": overall_score,
                    "matches_item": self._find_matched_item(core_features, photo)
                })
                
                if len(matched_photos) >= min_count:
                    break
            
            if len(matched_photos) >= min_count:
                break
        
        if len(matched_photos) < min_count:
            logger.warning(f"[{topic_id}] ⚠️ 匹配照片數量不足: {len(matched_photos)}/{min_count} 張")
            logger.warning(f"[{topic_id}] 診斷資訊: 核心要素={len(core_features)}個, 非核心要素={len(non_core_features)}個, 搜尋到={len(all_photos)}張")
            if not core_features:
                logger.warning(f"[{topic_id}] ⚠️ 核心要素為空，無法進行匹配")
            if not all_photos:
                logger.warning(f"[{topic_id}] ⚠️ 沒有搜尋到任何照片，請檢查圖片服務配置")
        else:
            logger.info(f"[{topic_id}] ✅ 匹配成功 {len(matched_photos)}/{min_count} 張照片")
        
        # 返回與 API 端點兼容的格式
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
        提取核心要素（改進版：動態提取專有名詞）
        
        例如：Alessandro Michele、Valentino、元朗、時尚
        """
        core_keywords = []
        
        # 1. 提取英文專有名詞（大寫字母開頭）
        english_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        core_keywords.extend(english_names)
        
        # 2. 提取中文詞語（2-4字）
        chinese_names = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        # 過濾停用詞
        stop_words = ['這個', '那個', '這些', '那些', '一個', '一種', '可以', '應該', '能夠', 
                     '如果', '但是', '然而', '因為', '所以', '而且', '或者', '還是',
                     '讓', '的', '是', '在', '有', '和', '與', '及', '或', '也', '都', '就',
                     '會', '要', '能', '可', '為', '了', '而', '但', '卻', '只', '還', '更',
                     '最', '很', '非常', '十分', '比較', '相當', '特別', '尤其', '更加']
        chinese_names = [name for name in chinese_names if name not in stop_words]
        # 優先提取較長的詞（3-4字），然後是2字詞
        chinese_3_4 = [name for name in chinese_names if len(name) >= 3]
        chinese_2 = [name for name in chinese_names if len(name) == 2]
        core_keywords.extend(chinese_3_4[:3])  # 優先3-4字詞
        core_keywords.extend(chinese_2[:5])  # 然後2字詞
        
        # 3. 品牌名稱（擴展列表）
        brands = ["Dior", "Gucci", "Chanel", "LV", "Prada", "Valentino", "Alessandro Michele",
                 "Hermès", "Burberry", "Versace", "Armani", "Balenciaga", "Saint Laurent"]
        for brand in brands:
            if brand.lower() in text.lower():
                core_keywords.append(brand)
        
        # 4. 保留一些硬編碼的關鍵模式（如果存在）
        core_patterns = [
            "白色喱士裙", "燒賣皇后", "元朗", "地址",
            "top 3", "排行榜", "第1", "第2", "第3"
        ]
        for pattern in core_patterns:
            if pattern in text:
                core_keywords.append(pattern)
        
        # 去重並限制數量
        result = list(set(core_keywords))[:10]
        if not result:
            logger.warning(f"⚠️ 未能提取到任何核心要素，文章內容: {text[:100]}...")
        return result
    
    def _extract_non_core_features(self, text: str) -> List[str]:
        """
        提取非核心要素（風格、氛圍、材質推測）
        
        例如：優雅、浪漫、現代、休閒
        """
        non_core_keywords = []
        
        # 風格描述（擴展列表）
        style_keywords = [
            "優雅", "浪漫", "現代", "休閒", "正式", "時尚", "經典",
            "簡約", "奢華", "復古", "前衛", "自然", "精緻", "大氣",
            "清新", "溫暖", "冷靜", "活潑", "沉穩", "輕鬆"
        ]
        for keyword in style_keywords:
            if keyword in text:
                non_core_keywords.append(keyword)
        
        # 氛圍描述（擴展列表）
        atmosphere_keywords = [
            "溫馨", "熱鬧", "安靜", "活潑", "沉穩", "輕鬆",
            "優雅", "浪漫", "現代", "經典", "舒適", "愉悅"
        ]
        for keyword in atmosphere_keywords:
            if keyword in text:
                non_core_keywords.append(keyword)
        
        # 去重並限制數量
        result = list(set(non_core_keywords))[:8]
        return result
    
    def _calculate_core_match_score(
        self,
        core_features: List[str],
        photo: Dict[str, Any]
    ) -> float:
        """
        計算核心要素匹配分數（改進版：考慮標題、描述、關鍵字）
        """
        if not core_features:
            return 1.0  # 沒有核心要素，視為匹配
        
        photo_desc = photo.get("description", "").lower()
        photo_title = photo.get("title", "").lower()
        photo_keywords = photo.get("keywords", [])
        
        matches = 0
        total = len(core_features)
        
        for feature in core_features:
            f = feature.lower()
            # 標題匹配權重最高
            if f in photo_title:
                matches += 1.5
            # 描述匹配
            elif f in photo_desc:
                matches += 1.0
            # 關鍵字匹配
            elif any(f in kw.lower() for kw in photo_keywords):
                matches += 0.8
        
        # 計算匹配比例
        match_ratio = matches / total if total > 0 else 0.0
        
        # 返回 0.0-1.0 範圍的分數（不再強制最低值）
        return min(1.0, max(0.0, match_ratio))
    
    def _calculate_non_core_match_score(
        self,
        non_core_features: List[str],
        photo: Dict[str, Any]
    ) -> float:
        """
        計算非核心要素匹配分數（改進版）
        """
        if not non_core_features:
            return 1.0  # 沒有非核心要素，視為匹配
        
        photo_desc = photo.get("description", "").lower()
        photo_keywords = photo.get("keywords", [])
        
        matches = 0
        total = len(non_core_features)
        
        for feature in non_core_features:
            f = feature.lower()
            if f in photo_desc or any(f in kw.lower() for kw in photo_keywords):
                matches += 1
        
        # 計算匹配比例
        match_ratio = matches / total if total > 0 else 0.0
        
        # 返回 0.0-1.0 範圍的分數（不再強制最低值）
        return min(1.0, max(0.0, match_ratio))
    
    def _find_matched_item(
        self,
        core_features: List[str],
        photo: Dict[str, Any]
    ) -> Optional[str]:
        """找出匹配的核心要素"""
        photo_description = photo.get("description", "").lower()
        photo_title = photo.get("title", "").lower()
        photo_keywords = photo.get("keywords", [])
        
        for feature in core_features:
            feature_lower = feature.lower()
            if (feature_lower in photo_title or
                feature_lower in photo_description or
                any(feature_lower in kw.lower() for kw in photo_keywords)):
                return feature
        
        return None
