"""测试连接

    POST /api/connection/test

请求体:
{
    "providerId": "deepseek",
    "endpoint":   "https://api.deepseek.com/v1",
    "apiKey":     "sk-xxx",
    "model":      "deepseek-chat"
}

成功响应:
    { "success": true, "duration": 342, "speedRating": "快速 ⚡" }

失败响应:
    { "success": false, "duration": 0,  "error": "401 Unauthorized", "speedRating": "失败 ❌" }
"""

import time
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.provider_factory import ProviderFactory

router = APIRouter()


# ── 请求 / 响应模型 ──────────────────────────────────────

class TestConnectionRequest(BaseModel):
    providerId: str = Field(
        ...,
        description="服务商标识",
        example="deepseek",
    )
    endpoint: str = Field(
        ...,
        description="API 端点 URL",
        example="https://api.deepseek.com/v1",
    )
    apiKey: str = Field(
        ...,
        description="API 密钥 / Access Token",
        example="sk-xxxxxxxxxxxxxxxx",
    )
    model: str = Field(
        ...,
        description="要测试的模型 ID",
        example="deepseek-chat",
    )


class TestConnectionResponse(BaseModel):
    success: bool = Field(..., description="连接是否成功")
    duration: int = Field(default=0, description="请求耗时（毫秒）", example=342)
    speedRating: str = Field(default="", description="速度评级（中文 + emoji）", example="快速 ⚡")
    error: str = Field(default="", description="失败原因（仅 success=false 时有值）", example="401 Unauthorized")
    message: Optional[str] = Field(default=None, description="前端展示用提示信息", example="连接测试成功，耗时 342ms")


# ── 辅助函数 ─────────────────────────────────────────────

def _speed_rating(ms: int) -> str:
    if ms < 300:
        return "极快 🚀"
    if ms < 800:
        return "快速 ⚡"
    if ms < 1500:
        return "正常 ✅"
    if ms < 3000:
        return "较慢 🐢"
    return "很慢 ⚠️"


# ── 路由 ─────────────────────────────────────────────────

@router.post(
    "/connection/test",
    response_model=TestConnectionResponse,
    summary="测试连接",
    description="向指定的 AI 服务商发送一个最小对话请求（1–5 个 token），验证 API 密钥、端点和模型是否配置正确。返回成功/失败状态、请求耗时和速度评级。",
    tags=["连接测试"],
)
def test_connection(req: TestConnectionRequest):
    """测试与指定服务商的 API 连接"""
    provider = ProviderFactory.get(req.providerId)
    start = time.perf_counter()

    try:
        provider.test_connection(req.endpoint, req.apiKey, req.model)
        duration_ms = int((time.perf_counter() - start) * 1000)
        rating = _speed_rating(duration_ms)
        return TestConnectionResponse(
            success=True,
            duration=duration_ms,
            speedRating=rating,
            message=f"连接测试成功，耗时 {duration_ms}ms，评级：{rating}",
        )
    except Exception as e:
        duration_ms = int((time.perf_counter() - start) * 1000)
        return TestConnectionResponse(
            success=False,
            duration=duration_ms,
            speedRating="失败 ❌",
            error=str(e),
            message=f"连接测试失败：{e}",
        )
