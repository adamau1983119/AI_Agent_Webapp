"""Probed interest-pack feeds. URLs below returned entries on 2026-10-09."""
from __future__ import annotations

from typing import Any, Dict, List


def _f(name: str, url: str, role: str = "global") -> dict:
    return {"name": name, "url": url, "role": role, "verified": True}


def _fill(local: List[dict], pool: List[dict], n: int = 8) -> List[dict]:
    out = [dict(row) for row in local]
    seen = {row["url"] for row in out}
    for row in pool:
        if len(out) >= n:
            break
        if row["url"] in seen:
            continue
        out.append(dict(row))
        seen.add(row["url"])
    return out


_BEAUTY = [
    _f("Allure", "https://www.allure.com/feed/rss"),
    _f("Elle", "https://www.elle.com/rss/all.xml"),
    _f("Vogue", "https://www.vogue.com/feed/rss"),
    _f("Glamour", "https://www.glamour.com/feed/rss"),
    _f("Refinery29", "https://www.refinery29.com/rss.xml"),
    _f("Highsnobiety", "https://www.highsnobiety.com/feeds/rss"),
    _f("Hypebeast", "https://hypebeast.com/feed"),
]
_GAMES = [
    _f("Polygon", "https://www.polygon.com/rss/index.xml"),
    _f("GameSpot", "https://www.gamespot.com/feeds/mashup/"),
    _f("Eurogamer", "https://www.eurogamer.net/feed"),
    _f("PC Gamer", "https://www.pcgamer.com/rss/"),
    _f("Nintendo Life", "https://www.nintendolife.com/feeds/news"),
    _f("Rock Paper Shotgun", "https://www.rockpapershotgun.com/feed"),
    _f("VG247", "https://www.vg247.com/feed"),
    _f("Destructoid", "https://www.destructoid.com/feed/"),
    _f("GamesRadar", "https://www.gamesradar.com/rss/"),
]
_TRAVEL = [
    _f("Condé Nast Traveler", "https://www.cntraveler.com/feed/rss"),
    _f("Nomadic Matt", "https://www.nomadicmatt.com/travel-blog/feed/"),
    _f("Skift", "https://skift.com/feed/"),
    _f("The Points Guy", "https://thepointsguy.com/feed/"),
    _f("Condé Nast Traveller", "https://www.cntraveller.com/feed/rss"),
    _f("The Guardian Travel", "https://www.theguardian.com/travel/rss"),
    _f("Atlas Obscura", "https://www.atlasobscura.com/feeds/latest"),
    _f("Matador Network", "https://matadornetwork.com/feed/"),
]
_GROWTH = [
    _f("James Clear", "https://jamesclear.com/feed"),
    _f("Farnam Street", "https://fs.blog/feed/"),
    _f("Mark Manson", "https://markmanson.net/feed"),
    _f("Ryan Holiday", "https://ryanholiday.net/feed/"),
    _f("Tim Ferriss", "https://tim.blog/feed/"),
    _f("Scott Young", "https://www.scotthyoung.com/blog/feed/"),
    _f("The Marginalian", "https://www.themarginalian.org/feed/"),
]
_LEGO = [
    _f("The Brothers Brick", "https://www.brothers-brick.com/feed/"),
    _f("The Brick Blogger", "https://thebrickblogger.com/feed/"),
]
_COSPLAY = [
    _f("Anime News Network", "https://www.animenewsnetwork.com/all/rss.xml"),
    _f("Kotaku", "https://kotaku.com/rss"),
    _f("Siliconera", "https://www.siliconera.com/feed/"),
    _f("Nintendo Life", "https://www.nintendolife.com/feeds/news"),
]


def _regions(local_map: Dict[str, List[dict]], pool: List[dict], n: int = 8) -> Dict[str, List[dict]]:
    """台港日只留在地來源。沒有在地來源時不把全球清單抄進該國。"""
    out = {key: [dict(row) for row in rows] for key, rows in local_map.items()}
    deep = ("hong_kong", "taiwan", "japan")
    for key in deep:
        out.setdefault(key, [])
    global_rows = _as_global(_fill([], pool, max(n, len(pool))))
    out["global"] = global_rows
    for key in ("korea", "china", "usa", "uk"):
        out[key] = _as_global(_fill([], pool, min(4, n)))
    return out


def _as_global(rows: List[dict]) -> List[dict]:
    copied = []
    for row in rows:
        item = dict(row)
        if item.get("role") not in ("local", "kpop"):
            item["role"] = "global"
        copied.append(item)
    return copied


def extra_packs() -> Dict[str, Dict[str, List[dict]]]:
    return {
        "beauty": _regions(
            {
                "taiwan": [_f("BEAUTY美人圈", "https://www.beauty321.com/feed", "local")],
                "hong_kong": [_f("SCMP Style", "https://www.scmp.com/rss/91/feed/", "local")],
                "japan": [_f("WWD Japan", "https://www.wwdjapan.com/feed", "local")],
            },
            _BEAUTY,
        ),
        "games": _regions(
            {
                "taiwan": [_f("巴哈姆特 GNN", "https://gnn.gamer.com.tw/rss.xml", "local")],
                "japan": [
                    _f("4Gamer", "https://www.4gamer.net/rss/index.xml", "local"),
                    _f("AUTOMATON", "https://automaton-media.com/feed/", "local"),
                ],
                "hong_kong": [],
            },
            _GAMES,
        ),
        "travel": _regions({}, _TRAVEL),
        "growth": _regions({}, _GROWTH),
        "lego": _regions({}, _LEGO, n=2),
        "cosplay": _regions({}, _COSPLAY, n=4),
    }


def relabel_global_reprints(sources: Dict[Any, Any]) -> None:
    for regions in sources.values():
        for region, feeds in regions.items():
            region_name = getattr(region, "value", region)
            for feed in feeds:
                url = (feed.get("url") or "").lower()
                if "variety.com" in url and region_name != "usa":
                    feed["name"] = "Variety"
                    feed["role"] = "global"
                if "theverge.com" in url and region_name not in ("usa", "global"):
                    feed["name"] = "The Verge"
                    feed["role"] = "global"


def deepen_primary_markets(sources: Dict[Any, Any], region_enum: Any) -> None:
    """不把全球來源抄進台港日。沒有在地來源時，讀取端改用全球包。"""
    del sources, region_enum


def install_interest_packs(sources: Dict[Any, Any], category_enum: Any, region_enum: Any) -> None:
    relabel_global_reprints(sources)
    for cat_name, regions in extra_packs().items():
        sources[category_enum(cat_name)] = {
            region_enum(region): feeds for region, feeds in regions.items()
        }
    deepen_primary_markets(sources, region_enum)
