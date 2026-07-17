"""数据库初始化 — SQLite

数据库文件: backend/data/configs.db
"""

import os
import sqlite3
from datetime import datetime, timezone

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DB_DIR, "configs.db")


def get_connection() -> sqlite3.Connection:
    """获取数据库连接（每次调用新建，用完记得关）"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """建表（幂等 — 表不存在才建）"""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS configs (
                id              TEXT PRIMARY KEY,
                name            TEXT NOT NULL DEFAULT '',
                provider_id     TEXT NOT NULL,
                endpoint        TEXT NOT NULL DEFAULT '',
                api_key         TEXT NOT NULL DEFAULT '',
                model           TEXT NOT NULL DEFAULT '',
                temperature     REAL NOT NULL DEFAULT 0.7,
                is_manual_model INTEGER NOT NULL DEFAULT 0,
                created_at      TEXT NOT NULL,
                updated_at      TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
