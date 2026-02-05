"""
Phase 5B 測試 - 智能圖片匹配
"""
import pytest
from app.services.images.image_matcher import ImageMatcher, KeywordExtractor


class TestKeywordExtractor:
    """關鍵字提取器測試"""
    
    def test_extract_from_title_english(self):
        """測試從英文標題提取關鍵字"""
        title = "Fashion Trends: The Rise of Sustainable Style in 2025"
        
        keywords = KeywordExtractor.extract_from_title(title)
        
        assert len(keywords) > 0
        assert "fashion" in [k.lower() for k in keywords]
        assert "trends" in [k.lower() for k in keywords]
        assert "sustainable" in [k.lower() for k in keywords]
    
    def test_extract_from_title_chinese(self):
        """測試從中文標題提取關鍵字"""
        title = "2025年時尚趨勢：可持續風格的崛起"
        
        keywords = KeywordExtractor.extract_from_title(title)
        
        assert len(keywords) > 0
        # 應該提取中文詞
        assert any(len(k) >= 2 and ord(k[0]) > 127 for k in keywords)
    
    def test_extract_from_content(self):
        """測試從內容提取關鍵字"""
        content = """
        Fashion is evolving rapidly with sustainability at its core.
        Designers are embracing eco-friendly materials and ethical production.
        The fashion industry is transforming to meet environmental challenges.
        """
        
        keywords = KeywordExtractor.extract_from_content(content)
        
        assert len(keywords) > 0
        assert "fashion" in [k.lower() for k in keywords]
    
    def test_extract_entities(self):
        """測試提取專有名詞"""
        text = "Valentino and Gucci showcased their collections at Paris Fashion Week"
        
        entities = KeywordExtractor.extract_entities(text)
        
        assert len(entities) > 0
        assert "Valentino" in entities or "Gucci" in entities or "Paris" in entities
    
    def test_stop_words_filtered(self):
        """測試停用詞被過濾"""
        title = "The best fashion trends for the summer"
        
        keywords = KeywordExtractor.extract_from_title(title)
        
        assert "the" not in [k.lower() for k in keywords]
        assert "for" not in [k.lower() for k in keywords]


class TestImageMatcher:
    """圖片匹配器測試"""
    
    def setup_method(self):
        """每個測試前初始化"""
        self.matcher = ImageMatcher()
    
    @pytest.mark.asyncio
    async def test_match_images_basic(self, sample_topic, sample_images):
        """測試基本圖片匹配功能"""
        matched = await self.matcher.match_images(
            topic=sample_topic,
            candidate_images=sample_images,
            target_count=5
        )
        
        assert len(matched) <= 5
        assert all("score" in img for img in matched)
        assert all("score_breakdown" in img for img in matched)
    
    @pytest.mark.asyncio
    async def test_score_calculation_with_diversity(self, sample_topic, sample_images):
        """測試評分計算包含多樣性加權"""
        matched = await self.matcher.match_images(
            topic=sample_topic,
            candidate_images=sample_images,
            target_count=5
        )
        
        # 檢查評分明細
        for img in matched:
            breakdown = img["score_breakdown"]
            assert "keyword" in breakdown
            assert "trust" in breakdown
            assert "quality" in breakdown
            assert "diversity" in breakdown
    
    @pytest.mark.asyncio
    async def test_diversity_bonus_different_source(self, sample_topic, sample_images):
        """測試不同來源的圖片獲得多樣性加分"""
        matched = await self.matcher.match_images(
            topic=sample_topic,
            candidate_images=sample_images,
            target_count=5
        )
        
        # 第一張圖片應該獲得多樣性加分 (D = 1.0)
        if matched:
            first_diversity = matched[0]["score_breakdown"]["diversity"]
            assert first_diversity == 1.0
    
    @pytest.mark.asyncio
    async def test_diversity_bonus_same_source(self, sample_topic):
        """測試相同來源的圖片不獲得多樣性加分"""
        # 創建全部來自同一來源的圖片
        same_source_images = [
            {
                "url": f"https://vogue.com/image{i}.jpg",
                "alt": f"Fashion image {i}",
                "source": "Vogue",
                "width": 1920,
                "height": 1080,
            }
            for i in range(5)
        ]
        
        matched = await self.matcher.match_images(
            topic=sample_topic,
            candidate_images=same_source_images,
            target_count=5
        )
        
        # 除了第一張，其他圖片的多樣性加分應該為 0
        if len(matched) > 1:
            for img in matched[1:]:
                assert img["score_breakdown"]["diversity"] == 0.0
    
    @pytest.mark.asyncio
    async def test_top_10_selection_diverse(self, sample_topic):
        """測試選擇前 10 張圖片時優先選擇多樣來源"""
        # 創建來自不同來源的圖片
        diverse_images = []
        sources = ["Vogue", "Elle", "Hypebeast", "WWD", "BoF", "Unsplash", "Pexels"]
        
        for i, source in enumerate(sources):
            diverse_images.append({
                "url": f"https://{source.lower()}.com/image{i}.jpg",
                "alt": f"Fashion sustainable trends design",
                "source": source,
                "width": 1920,
                "height": 1080,
            })
        
        matched = await self.matcher.match_images(
            topic=sample_topic,
            candidate_images=diverse_images,
            target_count=7
        )
        
        # 應該從不同來源選擇圖片
        selected_sources = set(img["source"] for img in matched)
        assert len(selected_sources) >= min(len(sources), 7)
    
    @pytest.mark.asyncio
    async def test_images_sorted_by_score(self, sample_topic, sample_images):
        """測試圖片按分數降序排列"""
        matched = await self.matcher.match_images(
            topic=sample_topic,
            candidate_images=sample_images,
            target_count=5
        )
        
        if len(matched) > 1:
            scores = [img["score"] for img in matched]
            assert scores == sorted(scores, reverse=True)
    
    def test_compute_keyword_score(self, sample_topic):
        """測試關鍵字匹配分數計算"""
        image = {
            "alt": "Fashion sustainable eco-friendly design",
            "caption": "Sustainable fashion trends",
            "filename": "fashion_trend.jpg",
            "url": "https://example.com/fashion_trend.jpg",
        }
        keywords = ["fashion", "sustainable", "trends", "eco-friendly"]
        
        score = self.matcher._compute_keyword_score(image, keywords)
        
        assert score > 0.5  # 有多個匹配
    
    def test_compute_trust_score_tier_s(self):
        """測試 Tier S 來源的信任度分數"""
        image = {"source": "Vogue"}
        
        score = self.matcher._compute_trust_score(image)
        
        assert score >= 0.9
    
    def test_compute_trust_score_external(self):
        """測試外部圖片庫的信任度分數"""
        image = {"source": "Unsplash"}
        
        score = self.matcher._compute_trust_score(image)
        
        assert score >= 0.6
        assert score <= 0.8
    
    def test_compute_quality_score_high_res(self):
        """測試高解析度圖片的品質分數"""
        image = {"width": 1920, "height": 1080}
        
        score = self.matcher._compute_quality_score(image)
        
        assert score == 1.0
    
    def test_compute_quality_score_low_res(self):
        """測試低解析度圖片的品質分數"""
        image = {"width": 400, "height": 300}
        
        score = self.matcher._compute_quality_score(image)
        
        assert score <= 0.4
    
    def test_generate_caption(self, sample_topic):
        """測試圖片標題生成"""
        image_with_caption = {"caption": "Original Caption", "alt": "Alt Text"}
        image_without_caption = {"alt": "Alt Text"}
        image_empty = {}
        
        # 優先使用 caption
        assert self.matcher.generate_caption(image_with_caption, sample_topic) == "Original Caption"
        
        # 其次使用 alt
        assert self.matcher.generate_caption(image_without_caption, sample_topic) == "Alt Text"
        
        # 使用主題標題
        caption = self.matcher.generate_caption(image_empty, sample_topic)
        assert len(caption) > 0

