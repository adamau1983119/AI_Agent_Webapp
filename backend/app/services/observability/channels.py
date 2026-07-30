"""
Observability 三通道定義（crash / cost / customer）。
唯讀設定；不寄信、不掛 main。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

_RECIPE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "observability_channels.json"
)


class AlertChannel(str, Enum):
    CRASH = "crash"
    COST = "cost"
    CUSTOMER = "customer"


@dataclass(frozen=True)
class ChannelSpec:
    id: str
    label: str
    saas_name: str
    env_enable: str
    default: str
    triggers: tuple[str, ...]


def load_recipe() -> dict[str, Any]:
    return json.loads(_RECIPE.read_text(encoding="utf-8"))


def channel_specs() -> dict[AlertChannel, ChannelSpec]:
    raw = load_recipe()["channels"]
    out: dict[AlertChannel, ChannelSpec] = {}
    for ch in AlertChannel:
        row = raw[ch.value]
        out[ch] = ChannelSpec(
            id=row["id"],
            label=row["label"],
            saas_name=row["saas_name"],
            env_enable=row["env_enable"],
            default=row["default"],
            triggers=tuple(row["triggers"]),
        )
    return out


def master_enabled() -> bool:
    recipe = load_recipe()
    key = recipe["master_switch_env"]
    default = recipe["master_switch_default"]
    return os.getenv(key, default).lower() == "true"


def channel_enabled(channel: AlertChannel) -> bool:
    if not master_enabled():
        return False
    spec = channel_specs()[channel]
    return os.getenv(spec.env_enable, spec.default).lower() == "true"


def ops_email() -> str:
    recipe = load_recipe()
    return os.getenv(
        recipe["ops_email_env"],
        recipe["ops_email_default"],
    )
