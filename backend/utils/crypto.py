"""加密工具 — Fernet 对称加密"""

import os

from cryptography.fernet import Fernet

_ENV_KEY = os.getenv("ENCRYPTION_KEY", "")

if _ENV_KEY:
    _fernet = Fernet(_ENV_KEY.encode())
else:
    _temp_key = Fernet.generate_key()
    _fernet = Fernet(_temp_key)
    print("=" * 60)
    print("[WARN] ENCRYPTION_KEY 未设置，已生成临时密钥。")
    print("       重启后已加密的数据将无法解密！")
    print("       请将以下 export 加入启动脚本：")
    print(f"       export ENCRYPTION_KEY={_temp_key.decode()}")
    print("=" * 60)


def encrypt(plaintext: str) -> str:
    """加密明文 → 返回 base64 密文字符串"""
    if not plaintext:
        return ""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """解密密文 → 返回原始明文字符串"""
    if not ciphertext:
        return ""
    return _fernet.decrypt(ciphertext.encode()).decode()
