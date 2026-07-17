"""获取模型列表

    POST /api/models/fetch

请求体:
{
    "providerId": "deepseek",
    "endpoint":   "https://api.deepseek.com/v1",
    "apiKey":     "sk-xxx"
}

成功响应:
    { "success": true, "models": ["deepseek-chat", "deepseek-coder"], "provider": "deepseek" }

失败响应:
    { "success": false, "models": [], "error": "该 API 不支持拉取模型列表" }
"""

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.provider_factory import ProviderFactory

router = APIRouter()


# ── 请求 / 响应模型 ──────────────────────────────────────

class FetchModelsRequest(BaseModel):
    providerId: str = Field(
        ...,
        description="服务商标识，如 deepseek / openai / claude / gemini / qwen / moonshot / stepfun",
        example="deepseek",
    )
    endpoint: str = Field(
        ...,
        description="API 端点 URL（用户自定义或使用默认值）",
        example="https://api.deepseek.com/v1",
    )
    apiKey: str = Field(
        ...,
        description="API 密钥 / Access Token",
        example="sk-xxxxxxxxxxxxxxxx",
    )


class FetchModelsResponse(BaseModel):
    success: bool = Field(..., description="是否成功获取到模型列表")
    models: List[str] = Field(default_factory=list, description="模型 ID 列表", example=["deepseek-chat", "deepseek-coder"])
    provider: str = Field(default="", description="当前服务商标识", example="deepseek")
    error: str = Field(default="", description="失败原因（仅 success=false 时有值）", example="该 API 不支持拉取模型列表")
    message: Optional[str] = Field(default=None, description="前端展示用提示信息（中文）", example="成功拉取 5 个模型")


# ── 路由 ─────────────────────────────────────────────────

@router.post(
    "/models/fetch",
    response_model=FetchModelsResponse,
    summary="拉取模型列表",
    description="根据服务商标识、API 端点和密钥，向对应 AI 服务商请求模型列表。成功后返回模型 ID 数组；失败时返回错误信息，前端应自动切换到手动输入模式。",
    tags=["模型列表"],
)
def fetch_models(req: FetchModelsRequest):
    provider = ProviderFactory.get(req.providerId)

    try:
        models = provider.fetch_models(req.endpoint, req.apiKey)
        if models:
            return FetchModelsResponse(
                success=True,
                models=models,
                provider=req.providerId,
                message=f"成功拉取 {len(models)} 个模型（若部分模型未显示，可切换手动输入模式）",
            )
        else:
            return FetchModelsResponse(
                success=False,
                models=[],
                provider=req.providerId,
                error="该 API 不支持拉取模型列表",
                message="该 API 不支持拉取模型列表，已切换至手动输入模式",
            )
    except Exception as e:
        return FetchModelsResponse(
            success=False,
            models=[],
            provider=req.providerId,
            error=str(e),
            message=f"拉取失败，已切换至手动输入模式",
        )
