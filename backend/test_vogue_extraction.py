"""
測試 Vogue 文章提取和內容生成
演示新的改進功能
"""
import asyncio
import sys
import io
from datetime import datetime
from app.utils.article_extractor import ArticleExtractor
from app.prompts.article_prompt import build_article_prompt
from app.config import settings
from app.services.ai.ai_service_factory import AIServiceFactory

# 設置 UTF-8 編碼輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


async def test_vogue_extraction():
    """測試 Vogue 文章提取"""
    url = "https://www.vogue.com/slideshow/an-exclusive-look-at-the-best-backstage-moments-from-the-ralph-lauren-fall-2026-menswear-show#intcid=_vogue-gallery-bottom-recirc_240e2bfc-6c73-4b4e-8688-21872c1e2553_text2vec1"
    
    print("=" * 80)
    print("📰 Vogue 文章提取測試")
    print("=" * 80)
    print(f"\n🔗 來源連結: {url}\n")
    
    # 1. 提取文章資訊
    print("1️⃣ 正在提取文章資訊...")
    extractor = ArticleExtractor()
    article_info = await extractor.extract_article_info(url)
    
    if not article_info.get("success"):
        print(f"❌ 提取失敗: {article_info.get('error')}")
        return
    
    print("✅ 提取成功！\n")
    
    # 2. 顯示提取的圖片
    images = article_info.get("images", [])
    print(f"📸 提取到的圖片 ({len(images)} 張):")
    for idx, img_url in enumerate(images[:5], 1):  # 只顯示前5張
        print(f"   {idx}. {img_url}")
    if len(images) > 5:
        print(f"   ... 還有 {len(images) - 5} 張圖片")
    print()
    
    # 3. 顯示提取的內容（前500字）
    original_content = article_info.get("original_content", "")
    print(f"📝 提取的原文內容 (前500字):")
    print("-" * 80)
    print(original_content[:500])
    if len(original_content) > 500:
        print(f"\n... (總共 {len(original_content)} 字)")
    print("-" * 80)
    print()
    
    # 4. 顯示語言和風格分析
    language = article_info.get("language", "unknown")
    style = article_info.get("style", {})
    print(f"🌐 檢測語言: {language}")
    print(f"🎨 風格分析:")
    print(f"   - 語調: {style.get('tone', 'N/A')}")
    print(f"   - 結構: {style.get('structure', 'N/A')}")
    print(f"   - 詞彙: {style.get('vocabulary', 'N/A')}")
    print()
    
    # 5. 構建主題資訊（模擬從 RSS 收集的主題）
    topic_title = "Ralph Lauren 重返米蘭秀場！獨家直擊2026秋冬男裝秀後台精彩瞬間"
    topic_category = "fashion"
    keywords = ["Ralph Lauren", "米蘭", "男裝週", "後台", "2026秋冬", "Purple Label", "Polo"]
    source_urls = [url]
    
    print("=" * 80)
    print("📝 內容生成測試")
    print("=" * 80)
    print(f"\n📌 主題: {topic_title}")
    print(f"🏷️  分類: {topic_category}")
    print(f"🔑 關鍵字: {', '.join(keywords)}\n")
    
    # 6. 構建改進的 Prompt
    prompt = build_article_prompt(
        topic_title=topic_title,
        topic_category=topic_category,
        keywords=keywords,
        target_length=500,
        original_content=original_content[:2000] if original_content else None,  # 限制長度
        source_urls=source_urls,
        original_language=language,
        style_info=style
    )
    
    print("🤖 AI Prompt (前800字):")
    print("-" * 80)
    print(prompt[:800])
    if len(prompt) > 800:
        print(f"\n... (總共 {len(prompt)} 字)")
    print("-" * 80)
    print()
    
    # 7. 生成內容（如果配置了 AI 服務）
    print("7️⃣ 正在生成中文內容...")
    try:
        ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
        print(f"   使用 AI 服務: {settings.AI_SERVICE}")
        
        generated_article = await ai_service._call_api(prompt)
        
        print("\n✅ 生成成功！\n")
        print("=" * 80)
        print("📄 生成的中文文章:")
        print("=" * 80)
        print(generated_article)
        print("=" * 80)
        print(f"\n📊 字數: {len(generated_article)} 字")
        
    except Exception as e:
        print(f"⚠️  AI 生成跳過（可能未配置 API Key）: {e}")
        print("\n💡 提示: 這只是展示提取的資訊，實際生成需要配置 AI 服務")
    
    # 8. 總結
    print("\n" + "=" * 80)
    print("📋 總結")
    print("=" * 80)
    print(f"✅ 原文連結: {url}")
    print(f"✅ 提取圖片: {len(images)} 張")
    print(f"✅ 原文內容: {len(original_content)} 字")
    print(f"✅ 語言: {language}")
    print(f"✅ 風格: {style.get('tone', 'N/A')}")
    print("\n💡 這些資訊會被保存到 Topic 的 sources 中，")
    print("   並用於生成基於原文的中文內容，確保真實性和可追溯性。")


if __name__ == "__main__":
    asyncio.run(test_vogue_extraction())

