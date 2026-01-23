"""
品牌名稱配置 (Phase 6.5)
用於 Hashtag 提取
"""

# 時尚品牌
FASHION_BRANDS = [
    # 奢侈品牌
    "Chanel", "Louis Vuitton", "Gucci", "Prada", "Hermès", "Dior",
    "Valentino", "Balenciaga", "Burberry", "Versace", "Fendi",
    "Givenchy", "Saint Laurent", "YSL", "Bottega Veneta", "Loewe",
    "Celine", "Alexander McQueen", "Tom Ford", "Dolce & Gabbana",
    "Armani", "Giorgio Armani", "Emporio Armani", "Miu Miu",
    "Salvatore Ferragamo", "Balmain", "Lanvin", "Kenzo", "Moschino",
    "Oscar de la Renta", "Carolina Herrera", "Elie Saab",
    
    # 運動/街頭品牌
    "Nike", "Adidas", "Puma", "New Balance", "Reebok",
    "Supreme", "Off-White", "A Bathing Ape", "BAPE", "Stüssy",
    "Palace", "Fear of God", "Essentials", "Yeezy", "Jordan",
    
    # 快時尚
    "Zara", "H&M", "Uniqlo", "COS", "& Other Stories",
    "Massimo Dutti", "Mango", "ASOS", "Topshop",
    
    # 設計師品牌
    "Comme des Garçons", "CDG", "Issey Miyake", "Yohji Yamamoto",
    "Rick Owens", "Maison Margiela", "Acne Studios", "Raf Simons",
    "Jil Sander", "The Row", "Jacquemus", "Lemaire",
    
    # 珠寶/配飾
    "Cartier", "Tiffany", "Bulgari", "Van Cleef & Arpels",
    "Harry Winston", "Chopard", "Rolex", "Omega", "Patek Philippe",
]

# 食品品牌
FOOD_BRANDS = [
    # 餐廳/連鎖
    "Michelin", "Noma", "El Bulli", "French Laundry",
    "Nobu", "Momofuku", "Blue Bottle", "Starbucks",
    
    # 食材/調味
    "Whole Foods", "Trader Joe's", "Eataly",
    
    # 廚具
    "Le Creuset", "All-Clad", "KitchenAid", "Vitamix",
]

# 科技品牌
TECH_BRANDS = [
    "Apple", "Google", "Microsoft", "Amazon", "Meta", "Facebook",
    "Tesla", "SpaceX", "OpenAI", "Anthropic", "NVIDIA",
    "Samsung", "Sony", "LG", "Huawei", "Xiaomi",
    "Netflix", "Spotify", "TikTok", "Instagram", "Twitter", "X",
    "Uber", "Airbnb", "DoorDash", "Instacart",
]

# 時尚週/活動
FASHION_EVENTS = [
    "Paris Fashion Week", "PFW",
    "Milan Fashion Week", "MFW",
    "New York Fashion Week", "NYFW",
    "London Fashion Week", "LFW",
    "Met Gala", "Oscars", "Golden Globes", "Cannes",
    "Couture Week", "Haute Couture",
]

# 食品活動
FOOD_EVENTS = [
    "James Beard", "World's 50 Best",
    "Food & Wine", "Bon Appétit",
]

# 科技活動
TECH_EVENTS = [
    "CES", "WWDC", "Google I/O", "AWS re:Invent",
    "MWC", "IFA", "Computex",
]

# 時尚術語
FASHION_TERMS = [
    "Runway", "Couture", "Ready-to-Wear", "RTW",
    "Spring/Summer", "Fall/Winter", "SS", "FW", "AW",
    "Resort", "Cruise", "Pre-Fall",
    "Streetwear", "Athleisure", "Minimalist", "Maximalist",
    "Sustainable", "Eco-friendly", "Vintage", "Retro",
    "Capsule Collection", "Limited Edition", "Collaboration",
]

# 食品術語
FOOD_TERMS = [
    "Farm-to-Table", "Organic", "Vegan", "Plant-based",
    "Gluten-free", "Keto", "Paleo", "Mediterranean",
    "Fusion", "Molecular", "Gastronomy",
    "Michelin Star", "Tasting Menu", "Prix Fixe",
]

# 科技術語
TECH_TERMS = [
    "AI", "Artificial Intelligence", "Machine Learning", "ML",
    "Blockchain", "Crypto", "NFT", "Web3",
    "VR", "AR", "XR", "Metaverse",
    "5G", "IoT", "Cloud", "SaaS",
    "Startup", "Unicorn", "IPO", "Series A",
]

# 停用詞（不應作為 hashtag）
STOP_WORDS = {
    # 英文停用詞
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "shall", "can",
    "this", "that", "these", "those", "it", "its", "they", "them",
    "he", "she", "him", "her", "his", "hers", "we", "us", "our",
    "you", "your", "yours", "i", "me", "my", "mine",
    "what", "which", "who", "whom", "whose", "where", "when", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "just", "also", "now", "here", "there",
    "new", "first", "last", "long", "great", "little", "own", "other",
    "old", "right", "big", "high", "different", "small", "large",
    "next", "early", "young", "important", "few", "public", "bad",
    "same", "able",
    
    # 常見但不適合作為 hashtag 的詞
    "today", "yesterday", "tomorrow", "week", "month", "year",
    "time", "way", "day", "thing", "man", "woman", "child",
    "world", "life", "hand", "part", "place", "case", "week",
    "company", "system", "program", "question", "work", "government",
    "number", "night", "point", "home", "water", "room", "mother",
    "area", "money", "story", "fact", "month", "lot", "right",
    "study", "book", "eye", "job", "word", "business", "issue",
    "side", "kind", "head", "house", "service", "friend", "father",
    "power", "hour", "game", "line", "end", "member", "law", "car",
    "city", "community", "name",
    
    # 中文停用詞
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一",
    "一個", "上", "也", "很", "到", "說", "要", "去", "你", "會", "著",
    "沒有", "看", "好", "自己", "這", "那", "她", "他", "它", "們",
}

# 所有品牌（合併）
ALL_BRANDS = set(
    FASHION_BRANDS + FOOD_BRANDS + TECH_BRANDS +
    FASHION_EVENTS + FOOD_EVENTS + TECH_EVENTS +
    FASHION_TERMS + FOOD_TERMS + TECH_TERMS
)

# 按分類的品牌
BRANDS_BY_CATEGORY = {
    "fashion": set(FASHION_BRANDS + FASHION_EVENTS + FASHION_TERMS),
    "food": set(FOOD_BRANDS + FOOD_EVENTS + FOOD_TERMS),
    "trend": set(TECH_BRANDS + TECH_EVENTS + TECH_TERMS),
}


def get_brands_for_category(category: str) -> set:
    """
    獲取特定分類的品牌列表
    
    Args:
        category: 分類名稱
        
    Returns:
        品牌集合
    """
    return BRANDS_BY_CATEGORY.get(category.lower(), ALL_BRANDS)


def is_brand(text: str) -> bool:
    """
    檢查文字是否為品牌名稱
    
    Args:
        text: 要檢查的文字
        
    Returns:
        是否為品牌
    """
    return text in ALL_BRANDS or text.title() in ALL_BRANDS


def is_stop_word(text: str) -> bool:
    """
    檢查文字是否為停用詞
    
    Args:
        text: 要檢查的文字
        
    Returns:
        是否為停用詞
    """
    return text.lower() in STOP_WORDS

