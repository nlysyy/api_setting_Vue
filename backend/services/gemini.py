"""Gemini (Google) 适配器

- 获取模型:   GET /v1beta/models?key=xxx
- 测试连接:   POST /v1beta/models/gemini-1.5-flash:generateContent?key=xxx
"""

from __future__ import annotations

import httpx
from services.base_provider import BaseProvider

TIMEOUT = 15


class GeminiProvider(BaseProvider):

    def fetch_models(self, endpoint: str, api_key: str) -> list[str]:
        # 去掉可能已经拼上的 /models 路径，拿到基础 URL
        base = endpoint.rstrip("/")
        base = base.rsplit("/models", 1)[0]
        url = f"{base}/models?key={api_key}"

        try:
            resp = httpx.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            all_models = self._extract_models(resp.json())
            # 只保留 gemini 开头的模型
            return [m for m in all_models if "gemini" in m.lower()][:20]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP {e.response.status_code}")

    def test_connection(self, endpoint: str, api_key: str, model: str) -> None:
        # 去掉可能拼上的 /models 路径
        base = endpoint.rstrip("/")
        base = base.rsplit("/models", 1)[0]
        url = f"{base}/models/{model}:generateContent?key={api_key}"

        resp = httpx.post(
            url,
            json={
                "contents": [{"parts": [{"text": "test"}]}],
            },
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
