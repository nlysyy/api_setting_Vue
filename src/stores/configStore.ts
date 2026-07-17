import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { apiPost, apiGet, apiPut, apiDelete } from '@/api'

// ============================================================
// 1. 数据类型定义
// ============================================================

export interface Provider {
  id: string
  name: string
  emoji: string
  defaultEndpoint: string
  keyPrefix: string
  defaultModel: string
  hint: string
  showUrl: boolean
  showKey: boolean
  requiresKey: boolean
}

export interface ApiConfig {
  providerId: string
  endpoint: string
  apiKey: string
  model: string
  temperature: number
  isManualModel: boolean
}

/** 后端返回的配置详情 */
export interface ConfigDetail {
  id: string
  name: string
  providerId: string
  endpoint: string
  apiKey: string
  model: string
  temperature: number
  isManualModel: boolean
  createdAt: string
  updatedAt: string
}

/** 后端返回的配置摘要（列表用） */
export interface ConfigSummary {
  id: string
  name: string
  providerId: string
  model: string
  updatedAt: string
}

// ============================================================
// 2. 服务商数据
// ============================================================

export const PROVIDERS: Provider[] = [
  {
    id: 'deepseek',
    name: 'DeepSeek',
    emoji: '🔍',
    defaultEndpoint: 'https://api.deepseek.com/v1',
    keyPrefix: 'sk-',
    defaultModel: 'deepseek-chat',
    hint: 'DeepSeek：性价比高，中文友好',
    showUrl: true,
    showKey: true,
    requiresKey: true,
  },
  {
    id: 'openai',
    name: 'OpenAI',
    emoji: '⚡',
    defaultEndpoint: 'https://api.openai.com/v1',
    keyPrefix: 'sk-',
    defaultModel: 'gpt-4o-mini',
    hint: 'OpenAI：通用能力强，生态成熟',
    showUrl: true,
    showKey: true,
    requiresKey: true,
  },
  {
    id: 'claude',
    name: 'Claude (Anthropic)',
    emoji: '🤖',
    defaultEndpoint: 'https://api.anthropic.com/v1',
    keyPrefix: 'sk-',
    defaultModel: 'claude-3-haiku-20240307',
    hint: 'Claude：细腻自然，擅长长文本',
    showUrl: true,
    showKey: true,
    requiresKey: true,
  },
  {
    id: 'gemini',
    name: 'Gemini (Google)',
    emoji: '✨',
    defaultEndpoint: 'https://generativelanguage.googleapis.com/v1beta',
    keyPrefix: 'AIza',
    defaultModel: 'gemini-1.5-flash',
    hint: 'Gemini：多模态能力，Google生态',
    showUrl: true,
    showKey: true,
    requiresKey: true,
  },
  {
    id: 'qwen',
    name: '通义千问',
    emoji: '🔮',
    defaultEndpoint: 'https://dashscope.aliyuncs.com/api/v1',
    keyPrefix: 'sk-',
    defaultModel: 'qwen-turbo',
    hint: '通义千问：阿里出品，中文优化好',
    showUrl: true,
    showKey: true,
    requiresKey: true,
  },
  {
    id: 'moonshot',
    name: '月之暗面 (Moonshot)',
    emoji: '🌙',
    defaultEndpoint: 'https://api.moonshot.cn/v1',
    keyPrefix: 'sk-',
    defaultModel: 'moonshot-v1-8k',
    hint: 'Moonshot：月之暗面，长文本处理',
    showUrl: true,
    showKey: true,
    requiresKey: true,
  },
  {
    id: 'stepfun',
    name: '阶跃星辰 (StepFun)',
    emoji: '⭐',
    defaultEndpoint: 'https://api.stepfun.com/v1',
    keyPrefix: 'sk-',
    defaultModel: 'step-1-8k',
    hint: 'StepFun：阶跃星辰，多模态大模型',
    showUrl: true,
    showKey: true,
    requiresKey: true,
  },
]

// ============================================================
// 3. Pinia Store
// ============================================================

export const useConfigStore = defineStore('config', () => {
  // ── 运行时状态 ──────────────────────────────────────────
  const configId = ref<string | null>(null)   // 数据库记录 ID（null = 未保存到后端）
  const providerId = ref('deepseek')
  const endpoint = ref('')
  const apiKey = ref('')
  const model = ref('')
  const temperature = ref(0.7)
  const isManualModel = ref(false)
  const configLoading = ref(false)            // 是否正在从后端加载

  // ── 计算属性 ────────────────────────────────────────────
  const currentProvider = computed(() => {
    return (PROVIDERS.find(p => p.id === providerId.value) ?? PROVIDERS[0]) as Provider
  })

  const isValid = computed(() => {
    const p = currentProvider.value
    if (p.requiresKey && !apiKey.value) return false
    if (!model.value) return false
    return true
  })

  const displayModel = computed(() => {
    return model.value || currentProvider.value.defaultModel
  })

  // ── 工具：把 Store 状态组装成纯对象 ──────────────────────
  function _toObject(): ApiConfig {
    return {
      providerId: providerId.value,
      endpoint: endpoint.value,
      apiKey: apiKey.value,
      model: model.value,
      temperature: temperature.value,
      isManualModel: isManualModel.value,
    }
  }

  // ── 工具：用对象恢复到 Store 状态 ────────────────────────
  function _fromObject(config: ApiConfig & { id?: string | null }) {
    if (config.id) configId.value = config.id
    providerId.value = config.providerId || 'deepseek'
    endpoint.value = config.endpoint || ''
    apiKey.value = config.apiKey || ''
    model.value = config.model || ''
    temperature.value = config.temperature ?? 0.7
    isManualModel.value = config.isManualModel ?? false
  }

  // ── 切换服务商 ──────────────────────────────────────────
  function setProvider(id: string) {
    const p = PROVIDERS.find(p => p.id === id)
    if (!p) return
    providerId.value = id
    endpoint.value = ''
    apiKey.value = ''
    model.value = p.defaultModel
    isManualModel.value = false
  }

  // ────────────────────────────────────────────────────────
  // 加载配置（后端优先 → localStorage 降级）
  // ────────────────────────────────────────────────────────

  /** 列出后端所有配置（按更新时间倒序） */
  async function listRemoteConfigs(): Promise<ConfigSummary[]> {
    try {
      return await apiGet<ConfigSummary[]>('/api/configs')
    } catch {
      return []
    }
  }

  /** 从后端获取指定配置详情 */
  async function getRemoteConfig(id: string): Promise<ConfigDetail> {
    return apiGet<ConfigDetail>(`/api/configs/${id}`)
  }

  /** 加载最近一条配置：后端 → localStorage 降级 */
  async function loadConfig(): Promise<void> {
    // 1. 尝试从后端加载最近一条配置
    try {
      const list = await listRemoteConfigs()
      if (list.length > 0) {
        const detail = await getRemoteConfig(list[0]!.id)
        _fromObject({
          id: detail.id,
          providerId: detail.providerId,
          endpoint: detail.endpoint,
          apiKey: detail.apiKey,
          model: detail.model,
          temperature: detail.temperature,
          isManualModel: detail.isManualModel,
        })
        return // ✅ 后端加载成功
      }
    } catch {
      // 后端不可用 → 降级
    }

    // 2. 降级：从 localStorage 加载
    loadFromStorage()
  }

  // ────────────────────────────────────────────────────────
  // 保存配置（后端优先 → localStorage 降级）
  // ────────────────────────────────────────────────────────

  /** 保存到后端（新建或更新） */
  async function saveConfig(): Promise<boolean> {
    if (!isValid.value) return false

    const payload = {
      providerId: providerId.value,
      endpoint: endpoint.value || currentProvider.value.defaultEndpoint,
      apiKey: apiKey.value,
      model: model.value,
      temperature: temperature.value,
      isManualModel: isManualModel.value,
    }

    try {
      if (configId.value) {
        // 已有记录 → 更新
        await apiPut(`/api/configs/${configId.value}`, payload)
      } else {
        // 没有记录 → 新建
        const result = await apiPost<ConfigDetail>('/api/configs', payload)
        configId.value = result.id
        // 同时更新 localStorage（给降级场景用）
        _syncLocalStorage()
      }
      return true // ✅ 后端保存成功
    } catch {
      // 后端不可用 → 降级到 localStorage
      saveToStorage()
      return false
    }
  }

  // ────────────────────────────────────────────────────────
  // 清除配置（后端 + localStorage）
  // ────────────────────────────────────────────────────────

  /** 清除当前配置 */
  async function clearConfig(): Promise<void> {
    // 1. 尝试删除后端记录
    if (configId.value) {
      try {
        await apiDelete(`/api/configs/${configId.value}`)
      } catch { /* 后端不可用就跳过 */ }
    }

    // 2. 重置状态
    configId.value = null
    apiKey.value = ''
    endpoint.value = ''
    model.value = currentProvider.value.defaultModel
    temperature.value = 0.7
    isManualModel.value = false

    // 3. 清除 localStorage
    try { localStorage.removeItem('api_config') } catch { /* ignore */ }
  }

  // ────────────────────────────────────────────────────────
  // localStorage 降级方法（后端不可用时使用）
  // ────────────────────────────────────────────────────────

  function loadFromStorage() {
    try {
      const saved = localStorage.getItem('api_config')
      if (!saved) return
      const config = JSON.parse(saved)
      configId.value = null  // localStorage 没有数据库 id
      providerId.value = config.providerId || 'deepseek'
      endpoint.value = config.endpoint || ''
      apiKey.value = config.apiKey || ''
      model.value = config.model || ''
      temperature.value = config.temperature ?? 0.7
      isManualModel.value = config.isManualModel ?? false
    } catch (e) {
      console.warn('从 localStorage 加载配置失败:', e)
    }
  }

  function saveToStorage() {
    try {
      const config = {
        providerId: providerId.value,
        endpoint: endpoint.value || currentProvider.value.defaultEndpoint,
        apiKey: apiKey.value,
        model: model.value,
        temperature: temperature.value,
        isManualModel: isManualModel.value,
        savedAt: new Date().toISOString(),
      }
      localStorage.setItem('api_config', JSON.stringify(config))
    } catch (e) {
      console.warn('保存到 localStorage 失败:', e)
    }
  }

  /** 同步当前状态到 localStorage（作为降级备份） */
  function _syncLocalStorage() {
    saveToStorage()
  }

  // ── 返回 ────────────────────────────────────────────────
  return {
    // 状态
    configId,
    providerId,
    endpoint,
    apiKey,
    model,
    temperature,
    isManualModel,
    configLoading,
    // 计算属性
    currentProvider,
    isValid,
    displayModel,
    // 后端 API 操作
    loadConfig,
    saveConfig,
    clearConfig,
    listRemoteConfigs,
    getRemoteConfig,
    // localStorage 降级（暴露以备调试）
    loadFromStorage,
    saveToStorage,
    // 简单操作
    setProvider,
  }
})
