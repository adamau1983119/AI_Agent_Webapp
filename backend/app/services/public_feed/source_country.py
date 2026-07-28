"""
RSS 來源國別推斷（PF-M · 僅 metadata 伏筆）
"""
from typing import Optional


def infer_source_country(feed_url: str, source_name: str) -> Optional[str]:
    url = (feed_url or "").lower()
    name = (source_name or "").lower()
    if ".co.uk" in url or "bbc" in name or "guardian" in name:
        return "GB"
    if ".jp" in url or "japan" in name or "nikkei" in name:
        return "JP"
    if ".hk" in url or "hong kong" in name:
        return "HK"
    if ".tw" in url or "taiwan" in name:
        return "TW"
    if ".au" in url or "australia" in name:
        return "AU"
    return "US"
