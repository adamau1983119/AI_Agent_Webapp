"""One-time USD credit packs (Checkout mode=payment, not subscription)."""
from __future__ import annotations

from typing import Dict, List

PACKS: Dict[str, dict] = {
    "usd3": {"id": "usd3", "credits": 180, "amount_cents": 300, "currency": "usd"},
    "usd5": {"id": "usd5", "credits": 350, "amount_cents": 500, "currency": "usd"},
    "usd10": {"id": "usd10", "credits": 800, "amount_cents": 1000, "currency": "usd"},
}


def get_pack(pack_id: str) -> dict:
    pack = PACKS.get(pack_id)
    if not pack:
        raise KeyError("unknown_pack")
    return dict(pack)


def list_packs() -> List[dict]:
    return [dict(row) for row in PACKS.values()]
