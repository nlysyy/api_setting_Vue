/**
 * 后端 API 封装
 *
 * 所有请求统一走 apiPost / apiGet / apiPut / apiDelete，不直接 fetch。
 */

/** 后端 API 基础地址 */
export const API_BASE = import.meta.env.VITE_API_BASE || 'http://8.163.8.184:8000'

// ── 私有工具 ────────────────────────────────────────────

async function request<T = any>(method: string, path: string, body?: unknown): Promise<T> {
  const opts: RequestInit = {
    method,
    headers: { 'Content-Type': 'application/json' },
    signal: AbortSignal.timeout(15000),
  }
  if (body !== undefined) {
    opts.body = JSON.stringify(body)
  }

  const response = await fetch(`${API_BASE}${path}`, opts)

  if (!response.ok) {
    // 尝试解析后端的错误详情
    let detail = ''
    try {
      const err = await response.json()
      detail = err.detail || ''
    } catch { /* ignore */ }
    throw new Error(detail || `HTTP ${response.status}：服务器异常，请稍后重试`)
  }

  return response.json() as Promise<T>
}

// ── 公开方法 ────────────────────────────────────────────

export function apiPost<T = any>(path: string, body: unknown): Promise<T> {
  return request<T>('POST', path, body)
}

export function apiGet<T = any>(path: string): Promise<T> {
  return request<T>('GET', path)
}

export function apiPut<T = any>(path: string, body: unknown): Promise<T> {
  return request<T>('PUT', path, body)
}

export function apiDelete<T = any>(path: string): Promise<T> {
  return request<T>('DELETE', path)
}
