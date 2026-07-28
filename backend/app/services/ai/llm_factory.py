"""
LLM Factory — namespace 路由與 Flash-only 防禦（AE-0 頻道區塊 7 · PD-AE1-04）
"""
from __future__ import annotations

from typing import Literal, Optional, Union

from app.config import settings
from app.services.ai.deepseek import DeepSeekService

Namespace = Literal["alter_ego", "v7_generate", "default"]


class AlterEgoLLMClient:
    """Alter Ego 管線專用：assert Flash-only；Pro 调用即报错。"""

    def __init__(self, inner: DeepSeekService, flash_model: str, pro_model: str) -> None:
        self._inner = inner
        self._flash_model = flash_model
        self._pro_model = pro_model
        self.model = flash_model

    def _reject_pro(self, model: Optional[str]) -> None:
        use = model or self.model
        if use == self._pro_model or "pro" in (use or "").lower():
            raise ValueError("alter_ego_namespace_pro_forbidden")

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        self._reject_pro(model)
        return await self._inner.generate(prompt, model=self._flash_model)

    async def _call_api(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        self._reject_pro(model)
        return await self._inner._call_api(prompt, model=self._flash_model, max_tokens=max_tokens)


def get_llm_client(namespace: Namespace = "default") -> Union[DeepSeekService, AlterEgoLLMClient]:
    """
    依 namespace 回傳 AI client。
    alter_ego：AlterEgoLLMClient（Flash-only；Pro 即 ValueError）。
    """
    inner = DeepSeekService()
    flash_model = getattr(settings, "DEEPSEEK_MODEL_FLASH", None) or settings.DEEPSEEK_MODEL
    pro_model = getattr(settings, "DEEPSEEK_MODEL_PRO", "deepseek-v4-pro")

    if namespace == "alter_ego":
        if inner.model == pro_model or "pro" in (inner.model or "").lower():
            raise ValueError("alter_ego namespace requires Flash-only model")
        return AlterEgoLLMClient(inner, flash_model, pro_model)

    if namespace == "v7_generate":
        inner.model = pro_model
        return inner

    return inner
