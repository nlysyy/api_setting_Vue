"""阶跃星辰 (StepFun) 适配器

- 获取模型:   GET /v1/models       (OpenAI 兼容)
- 测试连接:   POST /v1/chat/completions
"""

from __future__ import annotations

import httpx
from services.base_provider import BaseProvider

TIMEOUT = 15


class StepfunProvider(BaseProvider):

    def fetch_models(self, endpoint: str, api_key: str) -> list[str]:
        url = self._concat_url(endpoint, "models")
        try:
            resp = httpx.get(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return self._extract_models(resp.json())
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP {e.response.status_code}")

    def test_connection(self, endpoint: str, api_key: str, model: str) -> None:
        url = self._concat_url(endpoint, "chat/completions")
        resp = httpx.post(
            url,
            json={
                "model": model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5,
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
