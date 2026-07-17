"""Claude (Anthropic) 适配器

- 获取模型:   Claude 不提供 /models 端点，改为验证 API 密钥后用硬编码列表
- 测试连接:   POST /v1/messages
"""

from __future__ import annotations

import httpx
from services.base_provider import BaseProvider

TIMEOUT = 15

# Claude 已知模型列表（Anthropic 没有 /models 端点）
CLAUDE_MODELS = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]


class ClaudeProvider(BaseProvider):

    def fetch_models(self, endpoint: str, api_key: str) -> list[str]:
        # Claude 没有 /models 端点，改为发一个最小请求验证密钥
        # 验证通过就返回已知模型列表
        url = self._concat_url(endpoint, "messages")
        try:
            resp = httpx.post(
                url,
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "hi"}],
                },
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return CLAUDE_MODELS
            raise RuntimeError(f"HTTP {resp.status_code}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP {e.response.status_code}")

    def test_connection(self, endpoint: str, api_key: str, model: str) -> None:
        url = self._concat_url(endpoint, "messages")
        resp = httpx.post(
            url,
            json={
                "model": model,
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "test"}],
            },
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
