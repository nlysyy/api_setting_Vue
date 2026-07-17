"""Provider 抽象基类 — 所有服务商适配器必须实现这两个方法"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """AI 服务商基类"""

    @abstractmethod
    def fetch_models(self, endpoint: str, api_key: str) -> list[str]:
        """拉取模型列表

        成功 → 返回模型 id 列表
        失败 → 抛出异常（路由器会 catch 并返回 error）
        """
        ...

    @abstractmethod
    def test_connection(self, endpoint: str, api_key: str, model: str) -> None:
        """测试连接

        成功 → 正常返回（不返回数据）
        失败 → 抛出异常
        """
        ...

    # ── 工具方法，子类复用 ───────────────────────────────

    @staticmethod
    def _concat_url(endpoint: str, path: str) -> str:
        """把 endpoint 和 path 拼成完整 URL

        例: _concat_url('https://api.x.com/v1', 'models')
              → 'https://api.x.com/v1/models'
        """
        url = endpoint.rstrip("/")
        if not url.endswith("/" + path):
            url += "/" + path
        return url

    @staticmethod
    def _extract_models(data) -> list[str]:
        """从各种 API 响应格式中提取模型 id

        兼容 OpenAI/DeepSeek/通义千问/Moonshot/StepFun 等
        """
        # OpenAI 兼容格式: { "data": [{"id": "..."}, ...] }
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            return [m["id"] for m in data["data"] if isinstance(m, dict) and m.get("id")]

        # Gemini 格式: { "models": [{"name": "models/xxx"}, ...] }
        if isinstance(data, dict) and isinstance(data.get("models"), list):
            return [
                m["name"].rsplit("/", 1)[-1]
                for m in data["models"]
                if isinstance(m, dict) and m.get("name")
            ]

        # 纯数组: ["model-a", "model-b"]
        if isinstance(data, list):
            return [str(m.get("id", m.get("name", m))) if isinstance(m, dict) else str(m) for m in data]

        # 其他格式: { "result": [...] }
        if isinstance(data, dict) and isinstance(data.get("result"), list):
            return [str(m) for m in data["result"]]

        return []
