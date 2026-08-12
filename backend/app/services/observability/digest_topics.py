"""Digest 產卡摘要（永不拋出；MD-M2）。"""
from __future__ import annotations

import logging

logger = logging.getLogger("observability.digest_topics")


async def topics_hkt_summary() -> tuple[int, int, int]:
    """(世代內今日卡數, 含舊卡今日總數, 預期每日上限)。永不拋出。"""
    expected = 15
    gen_today = -1
    gen_v8 = -1
    try:
        from app.services.automation.topic_day_hkt import (
            expected_topics_today,
            hkt_day_utc_bounds,
        )
        from app.services.repositories.topic_repository import TopicRepository
        from app.utils.topic_pipeline import list_topics_generation_filter

        try:
            expected = int(expected_topics_today())
        except Exception as exc:  # noqa: BLE001
            logger.warning("expected_topics_today failed: %s", exc)

        start, end = hkt_day_utc_bounds()
        day_clause = {"generated_at": {"$gte": start, "$lte": end}}
        repo = TopicRepository()
        gen_today = await repo.count(day_clause)
        gen_f = list_topics_generation_filter(include_legacy=False)
        gen_v8 = (
            await repo.count({"$and": [day_clause, gen_f]}) if gen_f else gen_today
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("topics_hkt_summary count failed: %s", exc)
    return gen_v8, gen_today, expected
