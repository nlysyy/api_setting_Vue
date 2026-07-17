"""配置持久化 — 路由器

5 个 REST 接口：

    POST   /api/configs           — 新建配置
    GET    /api/configs           — 列出所有配置（不含密钥明文）
    GET    /api/configs/{id}      — 获取单个配置（含解密后的 apiKey）
    PUT    /api/configs/{id}      — 更新配置
    DELETE /api/configs/{id}      — 删除配置
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db import get_connection, now_iso
from utils.crypto import encrypt, decrypt

router = APIRouter()


# ── 请求 / 响应模型 ──────────────────────────────────────

class ConfigCreate(BaseModel):
    name: str = Field(default="", description="配置名称（可选，默认为空）", example="我的 DeepSeek 配置")
    providerId: str = Field(..., example="deepseek")
    endpoint: str = Field(default="", example="https://api.deepseek.com/v1")
    apiKey: str = Field(..., example="sk-xxxxxxxxxxxxxxxx")
    model: str = Field(default="", example="deepseek-chat")
    temperature: float = Field(default=0.7, example=0.7)
    isManualModel: bool = Field(default=False)


class ConfigUpdate(BaseModel):
    """所有字段可选 — 只更新传入的字段"""
    name: Optional[str] = None
    providerId: Optional[str] = None
    endpoint: Optional[str] = None
    apiKey: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    isManualModel: Optional[bool] = None


class ConfigSummary(BaseModel):
    """列表视图 — 不含 apiKey"""
    id: str
    name: str
    providerId: str
    model: str
    updatedAt: str


class ConfigDetail(BaseModel):
    """详情视图 — 含解密后的 apiKey"""
    id: str
    name: str
    providerId: str
    endpoint: str
    apiKey: str
    model: str
    temperature: float
    isManualModel: bool
    createdAt: str
    updatedAt: str


# ── 路由 ─────────────────────────────────────────────────

@router.post(
    "/configs",
    response_model=ConfigDetail,
    summary="新建配置",
    description="创建一条新的 API 配置。apiKey 在存储前会用 Fernet 加密。",
    tags=["配置管理"],
)
def create_config(body: ConfigCreate):
    conn = get_connection()
    try:
        config_id = uuid.uuid4().hex[:12]
        now = now_iso()
        encrypted_key = encrypt(body.apiKey)

        conn.execute(
            """INSERT INTO configs (id, name, provider_id, endpoint, api_key, model, temperature, is_manual_model, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                config_id,
                body.name,
                body.providerId,
                body.endpoint,
                encrypted_key,
                body.model,
                body.temperature,
                1 if body.isManualModel else 0,
                now,
                now,
            ),
        )
        conn.commit()

        return ConfigDetail(
            id=config_id,
            name=body.name,
            providerId=body.providerId,
            endpoint=body.endpoint,
            apiKey=body.apiKey,          # 返回明文
            model=body.model,
            temperature=body.temperature,
            isManualModel=body.isManualModel,
            createdAt=now,
            updatedAt=now,
        )
    finally:
        conn.close()


@router.get(
    "/configs",
    response_model=List[ConfigSummary],
    summary="列出所有配置",
    description="返回所有已保存的配置摘要列表（不包含 apiKey）。按更新时间倒序排列。",
    tags=["配置管理"],
)
def list_configs():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name, provider_id, model, updated_at FROM configs ORDER BY updated_at DESC"
        ).fetchall()

        return [
            ConfigSummary(
                id=r["id"],
                name=r["name"],
                providerId=r["provider_id"],
                model=r["model"],
                updatedAt=r["updated_at"],
            )
            for r in rows
        ]
    finally:
        conn.close()


@router.get(
    "/configs/{config_id}",
    response_model=ConfigDetail,
    summary="获取单个配置",
    description="返回指定配置的完整信息，apiKey 字段已解密为明文。",
    tags=["配置管理"],
)
def get_config(config_id: str):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM configs WHERE id = ?", (config_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="配置不存在")

        return ConfigDetail(
            id=row["id"],
            name=row["name"],
            providerId=row["provider_id"],
            endpoint=row["endpoint"],
            apiKey=decrypt(row["api_key"]),     # 解密
            model=row["model"],
            temperature=row["temperature"],
            isManualModel=bool(row["is_manual_model"]),
            createdAt=row["created_at"],
            updatedAt=row["updated_at"],
        )
    finally:
        conn.close()


@router.put(
    "/configs/{config_id}",
    response_model=ConfigDetail,
    summary="更新配置",
    description="部分更新指定配置，只更新传入的非空字段。",
    tags=["配置管理"],
)
def update_config(config_id: str, body: ConfigUpdate):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM configs WHERE id = ?", (config_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="配置不存在")

        # 对比 body 和现有值，构建 SET 子句
        sets: List[str] = []
        values: list = []

        if body.name is not None:
            sets.append("name = ?"); values.append(body.name)
        if body.providerId is not None:
            sets.append("provider_id = ?"); values.append(body.providerId)
        if body.endpoint is not None:
            sets.append("endpoint = ?"); values.append(body.endpoint)
        if body.apiKey is not None:
            sets.append("api_key = ?"); values.append(encrypt(body.apiKey))
        if body.model is not None:
            sets.append("model = ?"); values.append(body.model)
        if body.temperature is not None:
            sets.append("temperature = ?"); values.append(body.temperature)
        if body.isManualModel is not None:
            sets.append("is_manual_model = ?"); values.append(1 if body.isManualModel else 0)

        if sets:
            now = now_iso()
            sets.append("updated_at = ?"); values.append(now)
            values.append(config_id)
            conn.execute(f"UPDATE configs SET {', '.join(sets)} WHERE id = ?", values)
            conn.commit()

        # 重新查询，返回完整数据
        row = conn.execute("SELECT * FROM configs WHERE id = ?", (config_id,)).fetchone()
        return ConfigDetail(
            id=row["id"],
            name=row["name"],
            providerId=row["provider_id"],
            endpoint=row["endpoint"],
            apiKey=decrypt(row["api_key"]),
            model=row["model"],
            temperature=row["temperature"],
            isManualModel=bool(row["is_manual_model"]),
            createdAt=row["created_at"],
            updatedAt=row["updated_at"],
        )
    finally:
        conn.close()


@router.delete(
    "/configs/{config_id}",
    summary="删除配置",
    description="永久删除指定配置。",
    tags=["配置管理"],
)
def delete_config(config_id: str):
    conn = get_connection()
    try:
        row = conn.execute("SELECT id FROM configs WHERE id = ?", (config_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="配置不存在")
        conn.execute("DELETE FROM configs WHERE id = ?", (config_id,))
        conn.commit()
        return {"success": True, "message": f"配置 {config_id} 已删除"}
    finally:
        conn.close()
