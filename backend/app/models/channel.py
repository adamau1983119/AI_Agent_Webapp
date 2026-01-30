"""
Channel 頻道模型
Phase 3: 內容功能
會員自定義頻道（最多 3 個）

更新: 2026-01-30 - RSS 驗證後修復失效來源
"""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ChannelCategory(str, Enum):
    """頻道類別"""
    FASHION = "fashion"       # 時尚
    FOOD = "food"             # 美食
    TREND = "trend"           # 趨勢
    FINANCE = "finance"       # 財經
    SPORTS = "sports"         # 運動
    TECH = "tech"             # 科技
    ENTERTAINMENT = "entertainment"  # 娛樂
    OTHER = "other"           # 其他（自定義關鍵字）


class ChannelRegion(str, Enum):
    """頻道地區"""
    HONG_KONG = "hong_kong"       # 香港
    TAIWAN = "taiwan"             # 台灣
    JAPAN = "japan"               # 日本
    KOREA = "korea"               # 韓國
    CHINA = "china"               # 中國大陸
    USA = "usa"                   # 美國
    UK = "uk"                     # 英國
    GLOBAL = "global"             # 全球


class ChannelStatus(str, Enum):
    """頻道狀態"""
    ACTIVE = "active"         # 啟用中
    PAUSED = "paused"         # 暫停
    DELETED = "deleted"       # 已刪除


class ChannelCollectionStatus(str, Enum):
    """頻道收集狀態"""
    IDLE = "idle"             # 閒置
    COLLECTING = "collecting" # 收集中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失敗


# ============================================
# Channel 相關 Schema
# ============================================

class ChannelBase(BaseModel):
    """頻道基礎資料"""
    name: str = Field(..., min_length=1, max_length=50, description="頻道名稱")
    category: ChannelCategory = Field(..., description="頻道類別")
    region: ChannelRegion = Field(default=ChannelRegion.GLOBAL, description="頻道地區")
    custom_keywords: List[str] = Field(default=[], description="自定義關鍵字（當類別為 other 時使用）")
    description: Optional[str] = Field(None, max_length=200, description="頻道描述")


class ChannelCreate(ChannelBase):
    """建立頻道請求"""
    pass


class ChannelUpdate(BaseModel):
    """更新頻道請求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    custom_keywords: Optional[List[str]] = None
    description: Optional[str] = Field(None, max_length=200)
    status: Optional[ChannelStatus] = None


class ChannelResponse(ChannelBase):
    """頻道回應"""
    id: str
    user_id: str
    status: ChannelStatus = ChannelStatus.ACTIVE
    topic_count: int = 0
    last_collected_at: Optional[datetime] = None
    collection_status: ChannelCollectionStatus = ChannelCollectionStatus.IDLE
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChannelListResponse(BaseModel):
    """頻道列表回應"""
    channels: List[ChannelResponse]
    total: int
    max_channels: int = 3  # 最大頻道數


class ChannelTopicsResponse(BaseModel):
    """頻道主題回應"""
    channel: ChannelResponse
    topics: List[dict]  # Topic 列表
    total: int
    page: int
    limit: int


# ============================================
# 預設 RSS 來源配置
# ============================================
# 更新日期: 2026-01-30
# 經過驗證測試，移除失效來源，添加可靠替代
# 驗證結果: 117/216 (54.2%) 成功
# ============================================

DEFAULT_RSS_SOURCES = {
    # ============================================
    # 時尚類（8 地區）- 2026-01-30 驗證修復
    # ============================================
    ChannelCategory.FASHION: {
        ChannelRegion.HONG_KONG: [
            # ✅ 驗證通過
            {"name": "SCMP Style", "url": "https://www.scmp.com/rss/91/feed/", "role": "local", "verified": True},
            {"name": "Hypebeast", "url": "https://hypebeast.com/feed", "role": "streetwear", "verified": True},
            # 🔄 替代來源（原 Tatler/Lifestyle Asia 失效）
            {"name": "Vogue Global", "url": "https://www.vogue.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Elle Global", "url": "https://www.elle.com/rss/all.xml", "role": "authority", "verified": True},
            {"name": "Business of Fashion", "url": "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml", "role": "industry", "verified": True},
        ],
        ChannelRegion.TAIWAN: [
            # ✅ 驗證通過
            {"name": "BEAUTY美人圈", "url": "https://www.beauty321.com/feed", "role": "local", "verified": True},
            # 🔄 替代來源（原 ELLE/Vogue/GQ Taiwan 失效）
            {"name": "Vogue Global", "url": "https://www.vogue.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Elle Global", "url": "https://www.elle.com/rss/all.xml", "role": "authority", "verified": True},
            {"name": "Hypebeast", "url": "https://hypebeast.com/feed", "role": "streetwear", "verified": True},
            {"name": "Business of Fashion", "url": "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml", "role": "industry", "verified": True},
        ],
        ChannelRegion.JAPAN: [
            # ✅ 驗證通過
            {"name": "WWD Japan", "url": "https://www.wwdjapan.com/feed", "role": "industry", "verified": True},
            # 🔄 替代來源（原 SPUR/Fashion Press/VOGUE Japan 失效）
            {"name": "Vogue Global", "url": "https://www.vogue.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Hypebeast", "url": "https://hypebeast.com/feed", "role": "streetwear", "verified": True},
            {"name": "Highsnobiety", "url": "https://www.highsnobiety.com/feeds/rss", "role": "streetwear", "verified": True},
            {"name": "Business of Fashion", "url": "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml", "role": "industry", "verified": True},
        ],
        ChannelRegion.KOREA: [
            # ✅ 驗證通過
            {"name": "W Korea", "url": "https://www.wkorea.com/feed/", "role": "authority", "verified": True},
            {"name": "Vogue Korea", "url": "https://www.vogue.co.kr/feed/", "role": "authority", "verified": True},
            # 🔄 替代來源（原 Harper's Bazaar/Elle Korea 空內容）
            {"name": "Hypebeast", "url": "https://hypebeast.com/feed", "role": "streetwear", "verified": True},
            {"name": "Highsnobiety", "url": "https://www.highsnobiety.com/feeds/rss", "role": "streetwear", "verified": True},
            {"name": "Business of Fashion", "url": "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml", "role": "industry", "verified": True},
        ],
        ChannelRegion.CHINA: [
            # ✅ 驗證通過
            {"name": "Hypebeast CN", "url": "https://hypebeast.cn/feed", "role": "streetwear", "verified": True},
            # 🔄 替代來源（原 Vogue/ELLE/GQ China 失效）
            {"name": "Vogue Global", "url": "https://www.vogue.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Elle Global", "url": "https://www.elle.com/rss/all.xml", "role": "authority", "verified": True},
            {"name": "Hypebeast", "url": "https://hypebeast.com/feed", "role": "streetwear", "verified": True},
            {"name": "Business of Fashion", "url": "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml", "role": "industry", "verified": True},
        ],
        ChannelRegion.USA: [
            # ✅ 全部驗證通過
            {"name": "Vogue", "url": "https://www.vogue.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Elle", "url": "https://www.elle.com/rss/all.xml", "role": "authority", "verified": True},
            {"name": "Harper's Bazaar", "url": "https://www.harpersbazaar.com/rss/all.xml", "role": "authority", "verified": True},
            {"name": "Who What Wear", "url": "https://www.whowhatwear.com/feeds.xml", "role": "practical", "verified": True},
            {"name": "Fashionista", "url": "https://fashionista.com/.rss/excerpt/", "role": "practical", "verified": True},
        ],
        ChannelRegion.UK: [
            # ✅ 驗證通過
            {"name": "British Vogue", "url": "https://www.vogue.co.uk/feed/rss", "role": "authority", "verified": True},
            {"name": "The Guardian Fashion", "url": "https://www.theguardian.com/fashion/rss", "role": "analysis", "verified": True},
            {"name": "Dazed Digital", "url": "https://www.dazeddigital.com/rss", "role": "culture", "verified": True},
            # 🔄 替代來源（原 Elle UK/i-D 失效）
            {"name": "Elle Global", "url": "https://www.elle.com/rss/all.xml", "role": "authority", "verified": True},
            {"name": "Highsnobiety", "url": "https://www.highsnobiety.com/feeds/rss", "role": "streetwear", "verified": True},
        ],
        ChannelRegion.GLOBAL: [
            # ✅ 全部驗證通過
            {"name": "Vogue", "url": "https://www.vogue.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Elle", "url": "https://www.elle.com/rss/all.xml", "role": "authority", "verified": True},
            {"name": "Hypebeast", "url": "https://hypebeast.com/feed", "role": "streetwear", "verified": True},
            {"name": "Highsnobiety", "url": "https://www.highsnobiety.com/feeds/rss", "role": "streetwear", "verified": True},
            {"name": "Business of Fashion", "url": "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml", "role": "industry", "verified": True},
        ],
    },
    
    # ============================================
    # 美食類（8 地區）- 2026-01-30 驗證修復
    # ============================================
    ChannelCategory.FOOD: {
        ChannelRegion.HONG_KONG: [
            # 🔄 全部替代（原有來源全部失效）
            {"name": "SCMP Lifestyle", "url": "https://www.scmp.com/rss/91/feed/", "role": "local", "verified": True},
            {"name": "BBC Good Food", "url": "https://www.bbcgoodfood.com/feed", "role": "authority", "verified": True},
            {"name": "Eater", "url": "https://www.eater.com/rss/index.xml", "role": "authority", "verified": True},
            {"name": "Bon Appétit", "url": "https://www.bonappetit.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Food52", "url": "https://food52.com/blog.rss", "role": "community", "verified": True},
        ],
        ChannelRegion.TAIWAN: [
            # ✅ 驗證通過
            {"name": "上下游", "url": "https://www.newsmarket.com.tw/feed/", "role": "culture", "verified": True},
            # 🔄 替代來源（原 愛料理/食力/窩客島/ETtoday 失效）
            {"name": "BBC Good Food", "url": "https://www.bbcgoodfood.com/feed", "role": "authority", "verified": True},
            {"name": "Eater", "url": "https://www.eater.com/rss/index.xml", "role": "authority", "verified": True},
            {"name": "Bon Appétit", "url": "https://www.bonappetit.com/feed/rss", "role": "authority", "verified": True},
            {"name": "The Kitchn", "url": "https://www.thekitchn.com/main.rss", "role": "practical", "verified": True},
        ],
        ChannelRegion.JAPAN: [
            # 🔄 全部替代（原有來源全部失效）
            {"name": "BBC Good Food", "url": "https://www.bbcgoodfood.com/feed", "role": "authority", "verified": True},
            {"name": "Eater", "url": "https://www.eater.com/rss/index.xml", "role": "authority", "verified": True},
            {"name": "Bon Appétit", "url": "https://www.bonappetit.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Food52", "url": "https://food52.com/blog.rss", "role": "community", "verified": True},
            {"name": "The Kitchn", "url": "https://www.thekitchn.com/main.rss", "role": "practical", "verified": True},
        ],
        ChannelRegion.KOREA: [
            # ✅ 驗證通過
            {"name": "Yonhap Food", "url": "https://en.yna.co.kr/RSS/culture.xml", "role": "authority", "verified": True},
            # 🔄 替代來源（原有多數失效）
            {"name": "BBC Good Food", "url": "https://www.bbcgoodfood.com/feed", "role": "authority", "verified": True},
            {"name": "Eater", "url": "https://www.eater.com/rss/index.xml", "role": "authority", "verified": True},
            {"name": "Bon Appétit", "url": "https://www.bonappetit.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Food52", "url": "https://food52.com/blog.rss", "role": "community", "verified": True},
        ],
        ChannelRegion.CHINA: [
            # ✅ 驗證通過
            {"name": "CGTN Culture", "url": "https://www.cgtn.com/subscribe/rss/section/culture.xml", "role": "official", "verified": True},
            # 🔄 替代來源（原 Time Out/China Daily 失效）
            {"name": "BBC Good Food", "url": "https://www.bbcgoodfood.com/feed", "role": "authority", "verified": True},
            {"name": "Eater", "url": "https://www.eater.com/rss/index.xml", "role": "authority", "verified": True},
            {"name": "Bon Appétit", "url": "https://www.bonappetit.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Food52", "url": "https://food52.com/blog.rss", "role": "community", "verified": True},
        ],
        ChannelRegion.USA: [
            # ✅ 驗證通過
            {"name": "Eater", "url": "https://www.eater.com/rss/index.xml", "role": "authority", "verified": True},
            {"name": "Bon Appétit", "url": "https://www.bonappetit.com/feed/rss", "role": "authority", "verified": True},
            {"name": "Epicurious", "url": "https://www.epicurious.com/feed/rss", "role": "professional", "verified": True},
            # 🔄 替代來源（原 Food & Wine/Serious Eats 失效）
            {"name": "Food52", "url": "https://food52.com/blog.rss", "role": "community", "verified": True},
            {"name": "The Kitchn", "url": "https://www.thekitchn.com/main.rss", "role": "practical", "verified": True},
        ],
        ChannelRegion.UK: [
            # ✅ 驗證通過
            {"name": "BBC Good Food", "url": "https://www.bbcgoodfood.com/feed", "role": "authority", "verified": True},
            {"name": "The Guardian Food", "url": "https://www.theguardian.com/food/rss", "role": "analysis", "verified": True},
            {"name": "Olive Magazine", "url": "https://www.olivemagazine.com/feed", "role": "mainstream", "verified": True},
            # 🔄 替代來源（原 Great British Chefs/Delicious 失效）
            {"name": "Food52", "url": "https://food52.com/blog.rss", "role": "community", "verified": True},
            {"name": "The Kitchn", "url": "https://www.thekitchn.com/main.rss", "role": "practical", "verified": True},
        ],
        ChannelRegion.GLOBAL: [
            # ✅ 全部驗證通過
            {"name": "Eater", "url": "https://www.eater.com/rss/index.xml", "role": "authority", "verified": True},
            {"name": "Bon Appétit", "url": "https://www.bonappetit.com/feed/rss", "role": "authority", "verified": True},
            {"name": "BBC Good Food", "url": "https://www.bbcgoodfood.com/feed", "role": "authority", "verified": True},
            {"name": "Food52", "url": "https://food52.com/blog.rss", "role": "community", "verified": True},
            {"name": "The Kitchn", "url": "https://www.thekitchn.com/main.rss", "role": "practical", "verified": True},
        ],
    },
    
    # ============================================
    # 趨勢類（8 地區）- 2026-01-30 驗證修復
    # ============================================
    ChannelCategory.TREND: {
        ChannelRegion.HONG_KONG: [
            # ✅ 驗證通過
            {"name": "SCMP Tech", "url": "https://www.scmp.com/rss/36/feed", "role": "tech", "verified": True},
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "authority", "verified": True},
            # 🔄 替代來源（原 unwire.hk/e-zone 失效）
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Hacker News", "url": "https://news.ycombinator.com/rss", "role": "community", "verified": True},
        ],
        ChannelRegion.TAIWAN: [
            # ✅ 驗證通過
            {"name": "科技新報", "url": "https://technews.tw/feed/", "role": "tech", "verified": True},
            {"name": "iThome", "url": "https://www.ithome.com.tw/rss", "role": "tech", "verified": True},
            {"name": "TechOrange", "url": "https://buzzorange.com/techorange/feed/", "role": "startup", "verified": True},
            # 🔄 替代來源（原 數位時代/Inside 失效）
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.JAPAN: [
            # ✅ 驗證通過
            {"name": "CNET Japan", "url": "https://japan.cnet.com/rss/index.rdf", "role": "tech", "verified": True},
            # 🔄 替代來源（原 Japan Times Tech/TechCrunch Japan/Engadget Japan 失效）
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "role": "analysis", "verified": True},
        ],
        ChannelRegion.KOREA: [
            # ✅ 驗證通過
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            # 🔄 全部替代（原 Korea Herald Tech/ZDNet Korea 等全部失效）
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "role": "analysis", "verified": True},
            {"name": "Hacker News", "url": "https://news.ycombinator.com/rss", "role": "community", "verified": True},
        ],
        ChannelRegion.CHINA: [
            # ✅ 驗證通過
            {"name": "36Kr", "url": "https://36kr.com/feed", "role": "startup", "verified": True},
            {"name": "TechNode", "url": "https://technode.com/feed/", "role": "authority", "verified": True},
            # 🔄 替代來源（原 PingWest/Caixin Tech/CGTN Tech 失效）
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "Rest of World", "url": "https://restofworld.org/feed/latest/", "role": "global", "verified": True},
        ],
        ChannelRegion.USA: [
            # ✅ 全部驗證通過
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "role": "analysis", "verified": True},
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "role": "science", "verified": True},
        ],
        ChannelRegion.UK: [
            # ✅ 驗證通過
            {"name": "BBC Tech", "url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "role": "mainstream", "verified": True},
            {"name": "The Guardian Tech", "url": "https://www.theguardian.com/uk/technology/rss", "role": "analysis", "verified": True},
            {"name": "TechRadar", "url": "https://www.techradar.com/rss", "role": "reviews", "verified": True},
            {"name": "The Register", "url": "https://www.theregister.com/headlines.atom", "role": "industry", "verified": True},
            # 🔄 替代來源（原 Wired UK 失效）
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
        ],
        ChannelRegion.GLOBAL: [
            # ✅ 全部驗證通過
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Hacker News", "url": "https://news.ycombinator.com/rss", "role": "community", "verified": True},
            {"name": "Rest of World", "url": "https://restofworld.org/feed/latest/", "role": "global", "verified": True},
        ],
    },
    
    # ============================================
    # 財經類（8 地區）- 2026-01-30 驗證修復
    # ============================================
    ChannelCategory.FINANCE: {
        ChannelRegion.HONG_KONG: [
            # ✅ 全部驗證通過
            {"name": "SCMP Business", "url": "https://www.scmp.com/rss/91/feed", "role": "mainstream", "verified": True},
            {"name": "HKET", "url": "https://www.hket.com/rss/finance", "role": "local", "verified": True},
            {"name": "Bloomberg Asia", "url": "https://feeds.bloomberg.com/markets/news.rss", "role": "authority", "verified": True},
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home/uk", "role": "authority", "verified": True},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.TAIWAN: [
            # ✅ 驗證通過
            {"name": "經濟日報", "url": "https://money.udn.com/rssfeed/news/1001/5591", "role": "mainstream", "verified": True},
            # 🔄 替代來源（原 商業周刊/鉅亨網 失效）
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "role": "authority", "verified": True},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "role": "mainstream", "verified": True},
            {"name": "WSJ", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "role": "authority", "verified": True},
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home/uk", "role": "authority", "verified": True},
        ],
        ChannelRegion.JAPAN: [
            # ✅ 驗證通過
            {"name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar", "role": "authority", "verified": True},
            # 🔄 替代來源（原 Japan Times Business/Reuters Japan 失效）
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "role": "authority", "verified": True},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "role": "mainstream", "verified": True},
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home/uk", "role": "authority", "verified": True},
            {"name": "The Economist", "url": "https://www.economist.com/finance-and-economics/rss.xml", "role": "analysis", "verified": True},
        ],
        ChannelRegion.KOREA: [
            # 🔄 全部替代（原 Korea Herald/Pulse News/Yonhap Business 全部失效）
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "role": "authority", "verified": True},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "role": "mainstream", "verified": True},
            {"name": "WSJ", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "role": "authority", "verified": True},
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home/uk", "role": "authority", "verified": True},
            {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.CHINA: [
            # ✅ 驗證通過
            {"name": "CGTN Business", "url": "https://www.cgtn.com/subscribe/rss/section/business.xml", "role": "mainstream", "verified": True},
            # 🔄 替代來源（原 Caixin/Xinhua Finance 失效）
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "role": "authority", "verified": True},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "role": "mainstream", "verified": True},
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home/uk", "role": "authority", "verified": True},
            {"name": "The Economist", "url": "https://www.economist.com/finance-and-economics/rss.xml", "role": "analysis", "verified": True},
        ],
        ChannelRegion.USA: [
            # ✅ 全部驗證通過
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "role": "authority", "verified": True},
            {"name": "WSJ", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "role": "authority", "verified": True},
            {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "role": "mainstream", "verified": True},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "role": "mainstream", "verified": True},
            {"name": "The Economist", "url": "https://www.economist.com/finance-and-economics/rss.xml", "role": "analysis", "verified": True},
        ],
        ChannelRegion.UK: [
            # ✅ 全部驗證通過
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home/uk", "role": "authority", "verified": True},
            {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml", "role": "mainstream", "verified": True},
            {"name": "The Economist", "url": "https://www.economist.com/finance-and-economics/rss.xml", "role": "analysis", "verified": True},
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "role": "authority", "verified": True},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.GLOBAL: [
            # ✅ 驗證通過
            {"name": "Bloomberg Global", "url": "https://feeds.bloomberg.com/markets/news.rss", "role": "authority", "verified": True},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "role": "mainstream", "verified": True},
            # 🔄 替代來源（原 Reuters Finance 失效）
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home/uk", "role": "authority", "verified": True},
            {"name": "The Economist", "url": "https://www.economist.com/finance-and-economics/rss.xml", "role": "analysis", "verified": True},
            {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "role": "mainstream", "verified": True},
        ],
    },
    
    # ============================================
    # 運動類（8 地區）- 2026-01-30 驗證修復
    # ============================================
    ChannelCategory.SPORTS: {
        ChannelRegion.HONG_KONG: [
            # ✅ 驗證通過
            {"name": "SCMP Sport", "url": "https://www.scmp.com/rss/92/feed", "role": "local", "verified": True},
            {"name": "ESPN Asia", "url": "https://www.espn.com/espn/rss/news", "role": "authority", "verified": True},
            # 🔄 替代來源（原 Now Sports 失效）
            {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "role": "authority", "verified": True},
            {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "role": "mainstream", "verified": True},
            {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/rss/", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.TAIWAN: [
            # ✅ 驗證通過
            {"name": "ESPN Taiwan", "url": "https://www.espn.com/espn/rss/news", "role": "authority", "verified": True},
            # 🔄 替代來源（原 ETtoday/自由體育 失效）
            {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "role": "authority", "verified": True},
            {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/rss/", "role": "mainstream", "verified": True},
            {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "role": "mainstream", "verified": True},
            {"name": "The Guardian Sport", "url": "https://www.theguardian.com/uk/sport/rss", "role": "analysis", "verified": True},
        ],
        ChannelRegion.JAPAN: [
            # ✅ 驗證通過
            {"name": "ESPN Japan", "url": "https://www.espn.com/espn/rss/news", "role": "authority", "verified": True},
            # 🔄 替代來源（原 Japan Times Sports/Sportsnavi 失效）
            {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "role": "authority", "verified": True},
            {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/rss/", "role": "mainstream", "verified": True},
            {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "role": "mainstream", "verified": True},
            {"name": "The Guardian Sport", "url": "https://www.theguardian.com/uk/sport/rss", "role": "analysis", "verified": True},
        ],
        ChannelRegion.KOREA: [
            # ✅ 驗證通過
            {"name": "Yonhap Sports", "url": "https://en.yna.co.kr/RSS/sports.xml", "role": "authority", "verified": True},
            {"name": "ESPN Korea", "url": "https://www.espn.com/espn/rss/news", "role": "global", "verified": True},
            # 🔄 替代來源（原 Korea Herald Sports 失效）
            {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "role": "authority", "verified": True},
            {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/rss/", "role": "mainstream", "verified": True},
            {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.CHINA: [
            # ✅ 驗證通過
            {"name": "CGTN Sports", "url": "https://www.cgtn.com/subscribe/rss/section/sports.xml", "role": "mainstream", "verified": True},
            {"name": "ESPN China", "url": "https://www.espn.com/espn/rss/news", "role": "global", "verified": True},
            # 🔄 替代來源（原 Xinhua Sports 失效）
            {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "role": "authority", "verified": True},
            {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/rss/", "role": "mainstream", "verified": True},
            {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.USA: [
            # ✅ 驗證通過
            {"name": "ESPN", "url": "https://www.espn.com/espn/rss/news", "role": "authority", "verified": True},
            # 🔄 替代來源（原 Sports Illustrated/Bleacher Report 失效）
            {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "role": "authority", "verified": True},
            {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/rss/", "role": "mainstream", "verified": True},
            {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "role": "mainstream", "verified": True},
            {"name": "The Guardian Sport", "url": "https://www.theguardian.com/uk/sport/rss", "role": "analysis", "verified": True},
        ],
        ChannelRegion.UK: [
            # ✅ 全部驗證通過
            {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "role": "authority", "verified": True},
            {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "role": "mainstream", "verified": True},
            {"name": "The Guardian Sport", "url": "https://www.theguardian.com/uk/sport/rss", "role": "analysis", "verified": True},
            {"name": "ESPN", "url": "https://www.espn.com/espn/rss/news", "role": "authority", "verified": True},
            {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/rss/", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.GLOBAL: [
            # ✅ 驗證通過
            {"name": "ESPN Global", "url": "https://www.espn.com/espn/rss/news", "role": "authority", "verified": True},
            {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/rss/", "role": "mainstream", "verified": True},
            # 🔄 替代來源（原 Reuters Sports 失效）
            {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "role": "authority", "verified": True},
            {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "role": "mainstream", "verified": True},
            {"name": "The Guardian Sport", "url": "https://www.theguardian.com/uk/sport/rss", "role": "analysis", "verified": True},
        ],
    },
    
    # ============================================
    # 科技類（8 地區）- 2026-01-30 驗證修復
    # ============================================
    ChannelCategory.TECH: {
        ChannelRegion.HONG_KONG: [
            # ✅ 全部驗證通過
            {"name": "SCMP Tech", "url": "https://www.scmp.com/rss/36/feed", "role": "local", "verified": True},
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "role": "analysis", "verified": True},
        ],
        ChannelRegion.TAIWAN: [
            # ✅ 驗證通過
            {"name": "科技新報", "url": "https://technews.tw/feed/", "role": "mainstream", "verified": True},
            # 🔄 替代來源（原 數位時代/Inside 失效）
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "role": "analysis", "verified": True},
        ],
        ChannelRegion.JAPAN: [
            # 🔄 全部替代（原有來源全部失效）
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "role": "analysis", "verified": True},
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "role": "science", "verified": True},
        ],
        ChannelRegion.KOREA: [
            # ✅ 驗證通過
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            # 🔄 替代來源（原 Korea Herald Tech/ZDNet Korea 失效）
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "role": "analysis", "verified": True},
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "role": "science", "verified": True},
        ],
        ChannelRegion.CHINA: [
            # ✅ 驗證通過
            {"name": "36Kr", "url": "https://36kr.com/feed", "role": "startup", "verified": True},
            {"name": "TechNode", "url": "https://technode.com/feed/", "role": "authority", "verified": True},
            # 🔄 替代來源（原 Caixin Tech 失效）
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "Rest of World", "url": "https://restofworld.org/feed/latest/", "role": "global", "verified": True},
        ],
        ChannelRegion.USA: [
            # ✅ 全部驗證通過
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "role": "analysis", "verified": True},
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "role": "science", "verified": True},
        ],
        ChannelRegion.UK: [
            # ✅ 全部驗證通過
            {"name": "BBC Tech", "url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "role": "mainstream", "verified": True},
            {"name": "The Guardian Tech", "url": "https://www.theguardian.com/uk/technology/rss", "role": "analysis", "verified": True},
            {"name": "TechRadar", "url": "https://www.techradar.com/rss", "role": "reviews", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "The Register", "url": "https://www.theregister.com/headlines.atom", "role": "industry", "verified": True},
        ],
        ChannelRegion.GLOBAL: [
            # ✅ 全部驗證通過
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "role": "authority", "verified": True},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "role": "mainstream", "verified": True},
            {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "role": "analysis", "verified": True},
            {"name": "WIRED", "url": "https://www.wired.com/feed/rss", "role": "innovation", "verified": True},
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "role": "science", "verified": True},
        ],
    },
    
    # ============================================
    # 娛樂類（8 地區）- 2026-01-30 驗證修復
    # ============================================
    ChannelCategory.ENTERTAINMENT: {
        ChannelRegion.HONG_KONG: [
            # ✅ 全部驗證通過
            {"name": "SCMP Entertainment", "url": "https://www.scmp.com/rss/72/feed", "role": "local", "verified": True},
            {"name": "Variety Asia", "url": "https://variety.com/feed/", "role": "authority", "verified": True},
            {"name": "Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/", "role": "industry", "verified": True},
            {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "role": "mainstream", "verified": True},
            {"name": "The Guardian Film", "url": "https://www.theguardian.com/uk/film/rss", "role": "analysis", "verified": True},
        ],
        ChannelRegion.TAIWAN: [
            # 🔄 全部替代（原 ETtoday/ELLE/GQ Taiwan 失效）
            {"name": "Variety", "url": "https://variety.com/feed/", "role": "authority", "verified": True},
            {"name": "Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/", "role": "industry", "verified": True},
            {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "role": "mainstream", "verified": True},
            {"name": "The Guardian Film", "url": "https://www.theguardian.com/uk/film/rss", "role": "analysis", "verified": True},
            {"name": "NME", "url": "https://www.nme.com/feed", "role": "music", "verified": True},
        ],
        ChannelRegion.JAPAN: [
            # ✅ 驗證通過
            {"name": "Variety Japan", "url": "https://variety.com/feed/", "role": "authority", "verified": True},
            {"name": "Natalie", "url": "https://natalie.mu/music/feed/news", "role": "local", "verified": True},
            # 🔄 替代來源（原 Japan Times Entertainment 失效）
            {"name": "Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/", "role": "industry", "verified": True},
            {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "role": "mainstream", "verified": True},
            {"name": "NME", "url": "https://www.nme.com/feed", "role": "music", "verified": True},
        ],
        ChannelRegion.KOREA: [
            # ✅ 驗證通過
            {"name": "Soompi", "url": "https://www.soompi.com/feed", "role": "kpop", "verified": True},
            # 🔄 替代來源（原 Korea Herald Entertainment/AllKPop 失效）
            {"name": "Variety", "url": "https://variety.com/feed/", "role": "authority", "verified": True},
            {"name": "Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/", "role": "industry", "verified": True},
            {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "role": "mainstream", "verified": True},
            {"name": "NME", "url": "https://www.nme.com/feed", "role": "music", "verified": True},
        ],
        ChannelRegion.CHINA: [
            # ✅ 全部驗證通過
            {"name": "CGTN Entertainment", "url": "https://www.cgtn.com/subscribe/rss/section/culture.xml", "role": "official", "verified": True},
            {"name": "Variety China", "url": "https://variety.com/feed/", "role": "authority", "verified": True},
            {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/72/feed", "role": "mainstream", "verified": True},
            {"name": "Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/", "role": "industry", "verified": True},
            {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "role": "mainstream", "verified": True},
        ],
        ChannelRegion.USA: [
            # ✅ 驗證通過
            {"name": "Variety", "url": "https://variety.com/feed/", "role": "authority", "verified": True},
            {"name": "Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/", "role": "industry", "verified": True},
            # 🔄 替代來源（原 Entertainment Weekly 失效）
            {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "role": "mainstream", "verified": True},
            {"name": "The Guardian Film", "url": "https://www.theguardian.com/uk/film/rss", "role": "analysis", "verified": True},
            {"name": "NME", "url": "https://www.nme.com/feed", "role": "music", "verified": True},
        ],
        ChannelRegion.UK: [
            # ✅ 全部驗證通過
            {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "role": "mainstream", "verified": True},
            {"name": "The Guardian Film", "url": "https://www.theguardian.com/uk/film/rss", "role": "analysis", "verified": True},
            {"name": "NME", "url": "https://www.nme.com/feed", "role": "music", "verified": True},
            {"name": "Variety", "url": "https://variety.com/feed/", "role": "authority", "verified": True},
            {"name": "Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/", "role": "industry", "verified": True},
        ],
        ChannelRegion.GLOBAL: [
            # ✅ 驗證通過
            {"name": "Variety", "url": "https://variety.com/feed/", "role": "authority", "verified": True},
            {"name": "Hollywood Reporter", "url": "https://www.hollywoodreporter.com/feed/", "role": "industry", "verified": True},
            # 🔄 替代來源（原 Rolling Stone 超時）
            {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "role": "mainstream", "verified": True},
            {"name": "The Guardian Film", "url": "https://www.theguardian.com/uk/film/rss", "role": "analysis", "verified": True},
            {"name": "NME", "url": "https://www.nme.com/feed", "role": "music", "verified": True},
        ],
    },
}

# 類別備用映射（當主類別 RSS 不可用時）
CATEGORY_FALLBACK_MAP = {
    ChannelCategory.FINANCE: [ChannelCategory.TECH, ChannelCategory.TREND],
    ChannelCategory.SPORTS: [ChannelCategory.ENTERTAINMENT, ChannelCategory.TREND],
    ChannelCategory.TECH: [ChannelCategory.TREND, ChannelCategory.FINANCE],
    ChannelCategory.ENTERTAINMENT: [ChannelCategory.TREND, ChannelCategory.SPORTS],
    ChannelCategory.FASHION: [ChannelCategory.ENTERTAINMENT, ChannelCategory.TREND],
    ChannelCategory.FOOD: [ChannelCategory.ENTERTAINMENT, ChannelCategory.TREND],
    ChannelCategory.TREND: [ChannelCategory.TECH, ChannelCategory.ENTERTAINMENT],
    ChannelCategory.OTHER: [ChannelCategory.TREND, ChannelCategory.TECH],
}

# 地區語言映射
REGION_LANGUAGE_MAP = {
    ChannelRegion.HONG_KONG: "zh-TW",  # 繁體中文
    ChannelRegion.TAIWAN: "zh-TW",
    ChannelRegion.JAPAN: "ja",
    ChannelRegion.KOREA: "ko",
    ChannelRegion.CHINA: "zh-CN",
    ChannelRegion.USA: "en",
    ChannelRegion.UK: "en",
    ChannelRegion.GLOBAL: "en",
}
