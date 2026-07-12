import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

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

// ============================================================
// 2. 服务商数据（从你的HTML里迁移过来的）
// ============================================================

const PROVIDERS: Provider[] = [
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
]

// ============================================================
// 3. Pinia Store
// ============================================================

export const useConfigStore = defineStore('config', () => {
  // ---------- 状态（State） ----------
  const providerId = ref('deepseek')
  const endpoint = ref('')
  const apiKey = ref('')
  const model = ref('')
  const temperature = ref(0.7)
  const isManualModel = ref(false)

  // ---------- 计算属性（Getters） ----------
  const currentProvider = computed(() => {
    return PROVIDERS.find(p => p.id === providerId.value) || PROVIDERS[0]
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

  // ---------- 方法（Actions） ----------
  function setProvider(id: string) {
    const p = PROVIDERS.find(p => p.id === id)
    if (!p) return
    providerId.value = id
    endpoint.value = ''
    apiKey.value = ''
    model.value = p.defaultModel
    isManualModel.value = false
  }

  function loadFromStorage() {
    try {
      const saved = localStorage.getItem('api_config')
      if (!saved) return
      const config = JSON.parse(saved)
      providerId.value = config.providerId || 'deepseek'
      endpoint.value = config.endpoint || ''
      apiKey.value = config.apiKey || ''
      model.value = config.model || ''
      temperature.value = config.temperature ?? 0.7
      isManualModel.value = config.isManualModel ?? false
    } catch (e) {
      console.warn('加载配置失败:', e)
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
      console.warn('保存配置失败:', e)
    }
  }

  function clearConfig() {
    apiKey.value = ''
    endpoint.value = ''
    model.value = currentProvider.value.defaultModel
    isManualModel.value = false
    localStorage.removeItem('api_config')
  }

  // ---------- 返回所有内容 ----------
  return {
    // 状态
    providerId,
    endpoint,
    apiKey,
    model,
    temperature,
    isManualModel,
    // 计算属性
    currentProvider,
    isValid,
    displayModel,
    // 方法
    setProvider,
    loadFromStorage,
    saveToStorage,
    clearConfig,
  }
})