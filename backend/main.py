"""AI API 代理服务 — 入口文件

启动方式：
  cd backend
  source venv/Scripts/activate
  uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import models, connection, configs
from db import init_db

# ── 启动时初始化数据库 ────────────────────────────────────
init_db()

# ── 应用实例 ──────────────────────────────────────────────
app = FastAPI(
    title="AI API 代理服务",
    description="""
## 简介

本服务作为**中间代理层**，统一转发前端请求到各 AI 服务商的 API。

前端不再直接调用 AI 服务商，而是通过本代理服务完成：
- **获取模型列表**：屏蔽各服务商 API 差异，返回统一的模型 ID 列表
- **测试连接**：验证 API 密钥和模型是否可用，返回耗时和评级
- **配置管理**：持久化保存 API 配置（SQLite 存储，密钥加密）

## 支持的服务商

| 服务商 | 标识 |
|--------|------|
| DeepSeek | `deepseek` |
| OpenAI | `openai` |
| Claude (Anthropic) | `claude` |
| Gemini (Google) | `gemini` |
| 通义千问 (阿里) | `qwen` |
| 月之暗面 (Moonshot) | `moonshot` |
| 阶跃星辰 (StepFun) | `stepfun` |

## 注意事项

- **安全提示**：API 密钥在前端和传输过程中为明文，存储到数据库后使用 Fernet 加密
- 所有请求超时时间统一为 15 秒
""",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "模型列表",
            "description": "从各 AI 服务商拉取可用的模型 ID 列表。成功时返回模型 ID 数组；失败时建议前端自动切换到手动输入模式。",
        },
        {
            "name": "连接测试",
            "description": "向 AI 服务商发送一个最小请求（如 1–5 个 token 的对话），验证 API 密钥、端点和模型是否可用。返回成功/失败状态、耗时（毫秒）和速度评级。",
        },
        {
            "name": "配置管理",
            "description": "API 配置的 CRUD 接口。密钥在数据库中使用 Fernet 加密存储，读取时自动解密为明文。",
        },
    ],
)

# ── CORS 跨域 ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://nlysyy.github.io",
        "http://8.163.8.184",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 注册路由 ──────────────────────────────────────────────
app.include_router(models.router, prefix="/api")
app.include_router(connection.router, prefix="/api")
app.include_router(configs.router, prefix="/api")


@app.get(
    "/api/health",
    summary="健康检查",
    tags=["系统"],
)
def health():
    """检查服务是否在正常运行。

    可用于：
    - 前端启动时检测后端是否可达
    - 运维监控 / 心跳检测
    """
    return {
        "status": "ok",
        "version": "0.2.0",
        "message": "AI API 代理服务运行正常",
    }
