"""
建立 topic_translations 唯一索引（topic_id, lang, type）
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.repositories.topic_translation_repository import TopicTranslationRepository


async def main() -> None:
    repo = TopicTranslationRepository()
    await repo.ensure_indexes()
    print("[OK] topic_translations indexes ensured")


if __name__ == "__main__":
    asyncio.run(main())
