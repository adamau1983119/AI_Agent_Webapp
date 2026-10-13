"""個人成長、旅遊的在地 RSS。列入的 URL 於 2026-10-14 確認抓得到文章。"""
from __future__ import annotations

from typing import Dict, List


def _local(name: str, url: str) -> dict:
    return {"name": name, "url": url, "role": "local", "verified": True}


def travel_local_map() -> Dict[str, List[dict]]:
    return {
        "hong_kong": [
            _local("新假期旅遊", "https://www.weekendhk.com/category/travel/feed/"),
        ],
        "japan": [
            _local("朝日新聞トラベル", "https://www.asahi.com/rss/asahi/travel.rdf"),
            _local("MATCHA", "https://matcha-jp.com/jp/feed"),
        ],
        "china": [
            _local("CGTN Travel", "https://www.cgtn.com/subscribe/rss/section/travel.xml"),
        ],
        "usa": [
            _local("NYT Travel", "https://rss.nytimes.com/services/xml/rss/nyt/Travel.xml"),
            _local("Condé Nast Traveler", "https://www.cntraveler.com/feed/rss"),
        ],
        "uk": [
            _local("The Guardian Travel", "https://www.theguardian.com/travel/rss"),
            _local("Condé Nast Traveller", "https://www.cntraveller.com/feed/rss"),
        ],
        "taiwan": [
            _local("Yahoo奇摩旅遊", "https://tw.news.yahoo.com/rss/travel"),
            _local("Taiwan Obsessed", "https://www.taiwanobsessed.com/feed/"),
            _local("Tricky Taipei", "https://www.trickytaipei.com/feed/"),
            _local("Life of Taiwan", "https://lifeoftaiwan.com/feed/"),
        ],
        "korea": [
            _local("여행신문", "https://www.traveltimes.co.kr/rss/allArticle.xml"),
            _local("Trazy", "https://blog.trazy.com/feed/"),
            _local("South of Seoul", "https://blog.southofseoul.net/feed/"),
        ],
    }


def growth_local_map() -> Dict[str, List[dict]]:
    return {
        "taiwan": [
            _local("經理人", "https://www.managertoday.com.tw/rss"),
            _local("換日線", "https://crossing.cw.com.tw/rss"),
            _local("閱讀前哨站", "https://readingoutpost.com/feed"),
        ],
        "japan": [
            _local("STUDY HACKER", "https://studyhacker.net/feed"),
            _local("ライフハッカー・ジャパン", "https://www.lifehacker.jp/feed/"),
        ],
        "usa": [
            _local("James Clear", "https://jamesclear.com/feed"),
            _local("Farnam Street", "https://fs.blog/feed/"),
            _local("Mark Manson", "https://markmanson.net/feed"),
            _local("Ryan Holiday", "https://ryanholiday.net/feed/"),
            _local("Tim Ferriss", "https://tim.blog/feed/"),
            _local("Scott Young", "https://www.scotthyoung.com/blog/feed/"),
            _local("The Marginalian", "https://www.themarginalian.org/feed/"),
        ],
        "uk": [
            _local("Stylist", "https://www.stylist.co.uk/feed"),
            _local("The Guardian Life", "https://www.theguardian.com/lifeandstyle/rss"),
        ],
        "hong_kong": [
            _local("明報作家專欄", "https://news.mingpao.com/rss/pns/s00018.xml"),
        ],
        "korea": [
            _local("독서신문", "https://www.readersnews.com/rss/allArticle.xml"),
            _local("THE STARTUP BIBLE", "https://www.thestartupbible.com/feed/"),
            _local("OUTSTANDING", "https://outstanding.kr/feed"),
        ],
    }
