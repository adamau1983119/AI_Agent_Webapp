"""
展示時尚趨勢來源網站
"""
import asyncio
import sys
import io
from app.services.automation.topic_collector import TopicCollector
from app.models.topic import Category

# 設置 UTF-8 編碼輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


async def show_fashion_sources():
    """展示時尚趨勢來源網站"""
    collector = TopicCollector()
    
    print("=" * 80)
    print("📰 時尚趨勢來源網站")
    print("=" * 80)
    print()
    
    # 1. 顯示 RSS Feed 來源
    print("1️⃣ RSS Feed 來源（主要來源）")
    print("-" * 80)
    fashion_feeds = collector.rss_feeds.get(Category.FASHION, [])
    for idx, feed_url in enumerate(fashion_feeds, 1):
        print(f"   {idx}. {feed_url}")
    print()
    
    # 2. 顯示備用關鍵字
    print("2️⃣ 備用關鍵字（當 RSS 無法取得時使用）")
    print("-" * 80)
    fallback_keywords = collector.fallback_keywords.get(Category.FASHION, [])
    for idx, keyword in enumerate(fallback_keywords, 1):
        print(f"   {idx}. {keyword}")
    print()
    
    # 3. 測試實際收集（可選）
    print("3️⃣ 測試實際收集（從 RSS Feed 收集最新主題）")
    print("-" * 80)
    print("正在從 RSS Feed 收集最新時尚主題...\n")
    
    try:
        topics = await collector.collect_topics(
            category=Category.FASHION,
            count=3,
            use_fallback=False  # 只使用 RSS，不使用備用關鍵字
        )
        
        if topics:
            print(f"✅ 成功收集到 {len(topics)} 個主題：\n")
            for idx, topic in enumerate(topics, 1):
                print(f"📌 主題 {idx}:")
                print(f"   標題: {topic.get('title', 'N/A')}")
                print(f"   來源: {topic.get('source', 'N/A')}")
                print(f"   摘要: {topic.get('description', 'N/A')}")
                
                # 顯示來源資訊
                sources = topic.get('sources', [])
                if sources:
                    source = sources[0]
                    print(f"   原文連結: {source.get('url', 'N/A')}")
                    images = source.get('images', [])
                    if images:
                        print(f"   原文圖片: {len(images)} 張")
                        for img_idx, img_url in enumerate(images[:2], 1):
                            print(f"      {img_idx}. {img_url[:80]}...")
                    if source.get('original_content'):
                        content_len = len(source.get('original_content', ''))
                        print(f"   原文內容: {content_len} 字")
                    if source.get('language'):
                        print(f"   語言: {source.get('language')}")
                    if source.get('style'):
                        style = source.get('style')
                        if isinstance(style, dict):
                            print(f"   風格: {style.get('tone', 'N/A')}")
                print()
        else:
            print("⚠️  未能收集到主題（可能 RSS Feed 暫時無法訪問）")
            print("   系統會自動使用備用關鍵字生成主題")
    except Exception as e:
        print(f"❌ 收集失敗: {e}")
        print("   系統會自動使用備用關鍵字生成主題")
    
    print()
    print("=" * 80)
    print("📋 總結")
    print("=" * 80)
    print()
    print("✅ 主要來源（RSS Feed）:")
    print("   • Vogue - 全球頂級時尚雜誌")
    print("   • Elle - 國際時尚與生活方式雜誌")
    print("   • Harper's Bazaar - 高端時尚雜誌")
    print()
    print("✅ 備用方案:")
    print("   • 當 RSS Feed 無法訪問時，使用 AI 生成主題")
    print("   • 基於預設的時尚關鍵字生成中文標題和摘要")
    print()
    print("✅ 改進功能:")
    print("   • 自動提取原文圖片（og:image 和 <img> 標籤）")
    print("   • 自動提取原文內容（用於 AI 改寫）")
    print("   • 自動檢測語言和風格")
    print("   • 保存原文連結（確保可追溯性）")
    print()
    print("💡 這些網站的文章會被:")
    print("   1. 提取原文圖片和內容")
    print("   2. 翻譯標題為中文")
    print("   3. 基於原文內容生成中文文章")
    print("   4. 引用原文連結")
    print("   5. 保存原文圖片作為 source 類型圖片")


if __name__ == "__main__":
    asyncio.run(show_fashion_sources())

