<template>
  <div class="card">
    <div class="card-title">
      <span class="icon">🧠</span>
      <span>模型配置</span>
      <button class="fetch-btn" @click="fetchModels" :disabled="isFetching || !canFetch">
        {{ isFetching ? '加载中...' : '拉取模型列表' }}
      </button>
    </div>

    <!-- 模式切换 -->
    <div class="mode-toggle">
      <div class="mode-option" :class="{ active: !store.isManualModel }" @click="store.isManualModel = false">
        <span class="dot"></span> 从列表选择
      </div>
      <div class="mode-option" :class="{ active: store.isManualModel }" @click="store.isManualModel = true">
        <span class="dot"></span> 手动输入
      </div>
    </div>

    <!-- 列表模式 -->
    <div v-if="!store.isManualModel">
      <div class="select-wrapper">
        <select v-model="store.model">
          <option v-if="modelList.length === 0" value="">请先拉取模型列表</option>
          <option v-for="m in modelList" :key="m" :value="m">{{ m }}</option>
          <option v-if="customModel && !modelList.includes(customModel)" :value="customModel">
            {{ customModel }} (自定义)
          </option>
        </select>
      </div>
      <div v-if="fetchError" class="fetch-error">
        ⚠️ {{ fetchError }}
      </div>
    </div>

    <!-- 手动模式 -->
    <div v-else>
      <div class="input-group">
        <div class="input-row">
          <input type="text" v-model="store.model" placeholder="例如: gpt-4, claude-3-opus" />
        </div>
      </div>
      <div v-if="fetchError" class="fetch-error">
        💡 {{ fetchError }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useConfigStore } from '@/stores/configStore'

const store = useConfigStore()
const isFetching = ref(false)
const fetchError = ref<string | null>(null)
const modelList = ref<string[]>([])

const canFetch = computed(() => {
  const provider = store.currentProvider
  if (provider.id === 'localBuiltin') return false
  if (provider.requiresKey && !store.apiKey) return false
  if (provider.showUrl && !store.endpoint) return false
  return true
})

const customModel = computed(() => {
  const val = store.model
  if (!val) return ''
  return modelList.value.includes(val) ? '' : val
})

watch(() => store.providerId, () => {
  modelList.value = []
  fetchError.value = null
})

watch(() => store.apiKey, () => {
  modelList.value = []
  fetchError.value = null
})

// ============================================================
// 主函数：拉取模型列表（带智能降级）
// ============================================================
async function fetchModels() {
  // 1. 检查 API 密钥
  if (store.currentProvider.requiresKey && !store.apiKey) {
    window.showToast('⚠️ 请先填写 API 密钥', 'error')
    return
  }

  // 2. 检查端点
  if (store.currentProvider.showUrl && !store.endpoint) {
    window.showToast('⚠️ 请先填写 API 端点 URL', 'error')
    return
  }

  // 3. 检查是否正在加载
  if (isFetching.value || !canFetch.value) return

  const provider = store.currentProvider!
  const endpoint = store.endpoint || provider.defaultEndpoint
  const apiKey = store.apiKey

  isFetching.value = true
  fetchError.value = null

  try {
    console.log('📡 拉取模型列表:', provider.id)

    let models: string[] = []

    switch (provider.id) {
      case 'deepseek':
        models = await fetchDeepSeekModels(endpoint, apiKey)
        break
      case 'openai':
        models = await fetchOpenAIModels(endpoint, apiKey)
        break
      case 'claude':
        models = await fetchClaudeModels(endpoint, apiKey)
        break
      case 'gemini':
        models = await fetchGeminiModels(endpoint, apiKey)
        break
      case 'qwen':
        models = await fetchQwenModels(endpoint, apiKey)
        break
      case 'moonshot':
        models = await fetchMoonshotModels(endpoint, apiKey)
        break
      case 'stepfun':
        models = await fetchStepfunModels(endpoint, apiKey)
        break
      default:
        models = await fetchCustomModels(endpoint, apiKey)
    }

    if (models.length > 0) {
      modelList.value = models
      if (!store.model || !models.includes(store.model)) {
        store.model = models[0]!
      }
      window.showToast(`✅ 成功拉取 ${models.length} 个模型（若部分模型未显示，可切换手动输入模式）`, 'success')
    } else {
      store.isManualModel = true
      const defaultModel = provider.defaultModel
      if (defaultModel && !store.model) {
        store.model = defaultModel
      }
      fetchError.value = '该 API 不支持拉取模型列表，请手动输入模型名称'
      window.showToast('💡 该 API 不支持拉取模型列表，已切换至手动输入模式', 'info')
    }
  } catch (error: any) {
    console.error('❌ 拉取模型失败:', error)
    store.isManualModel = true
    const defaultModel = provider.defaultModel
    if (defaultModel && !store.model) {
      store.model = defaultModel
    }
    fetchError.value = error.message || '拉取失败，请手动输入模型名称'
    window.showToast('💡 ' + (error.message || '拉取失败，已切换至手动输入模式'), 'error')
  } finally {
    isFetching.value = false
  }
}

// ============================================================
// 1. DeepSeek 模型拉取（真实 API）
// ============================================================
async function fetchDeepSeekModels(endpoint: string, apiKey: string): Promise<string[]> {
  try {
    const url = buildUrl(endpoint, 'models')
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(8000),
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    return extractModels(data)
  } catch (error) {
    console.warn('⚠️ DeepSeek 拉取失败:', error)
    return []
  }
}

// ============================================================
// 2. OpenAI 模型拉取（真实 API）
// ============================================================
async function fetchOpenAIModels(endpoint: string, apiKey: string): Promise<string[]> {
  try {
    const url = buildUrl(endpoint, 'models')
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(8000),
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    const models = extractModels(data)
    return models.filter(m => m.includes('gpt') || m.includes('text-')).slice(0, 30)
  } catch (error) {
    console.warn('⚠️ OpenAI 拉取失败:', error)
    return []
  }
}

// ============================================================
// 3. Claude 模型拉取（真实 API 验证）
// ============================================================
async function fetchClaudeModels(endpoint: string, apiKey: string): Promise<string[]> {
  try {
    const testUrl = buildUrl(endpoint, 'messages')
    const response = await fetch(testUrl, {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'claude-3-haiku-20240307',
        max_tokens: 1,
        messages: [{ role: 'user', content: 'test' }],
      }),
      signal: AbortSignal.timeout(5000),
    })

    if (response.ok) {
      return [
        'claude-3-5-sonnet-20241022',
        'claude-3-5-haiku-20241022',
        'claude-3-opus-20240229',
        'claude-3-sonnet-20240229',
        'claude-3-haiku-20240307',
      ]
    }
    return []
  } catch (error) {
    console.warn('⚠️ Claude 拉取失败:', error)
    return []
  }
}

// ============================================================
// 4. Gemini 模型拉取（真实 API）
// ============================================================
async function fetchGeminiModels(endpoint: string, apiKey: string): Promise<string[]> {
  try {
    let baseUrl = endpoint.replace(/\/models.*$/, '')
    if (baseUrl.endsWith('/')) baseUrl = baseUrl.slice(0, -1)
    const url = `${baseUrl}/models?key=${apiKey}`
    const response = await fetch(url, { signal: AbortSignal.timeout(8000) })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    const list = data.models || []
    return list
      .filter((m: any) => m.name && m.name.includes('gemini'))
      .map((m: any) => m.name.split('/').pop())
      .slice(0, 20)
  } catch (error) {
    console.warn('⚠️ Gemini 拉取失败:', error)
    return []
  }
}

// ============================================================
// 5. 通义千问 模型拉取（真实 API）
// ============================================================
async function fetchQwenModels(endpoint: string, apiKey: string): Promise<string[]> {
  try {
    const url = buildUrl(endpoint, 'models')
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(8000),
    })
    if (response.ok) {
      const data = await response.json()
      const models = extractModels(data)
      if (models.length > 0) return models
    }
    return []
  } catch (error) {
    console.warn('⚠️ 通义千问 拉取失败:', error)
    return []
  }
}

// ============================================================
// 6. 月之暗面 模型拉取（真实 API）
// ============================================================
async function fetchMoonshotModels(endpoint: string, apiKey: string): Promise<string[]> {
  try {
    const url = buildUrl(endpoint, 'models')
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(8000),
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    return extractModels(data)
  } catch (error) {
    console.warn('⚠️ 月之暗面 拉取失败:', error)
    return []
  }
}

// ============================================================
// 7. 阶跃星辰 模型拉取（真实 API）
// ============================================================
async function fetchStepfunModels(endpoint: string, apiKey: string): Promise<string[]> {
  try {
    const url = buildUrl(endpoint, 'models')
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(8000),
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    return extractModels(data)
  } catch (error) {
    console.warn('⚠️ 阶跃星辰 拉取失败:', error)
    return []
  }
}

// ============================================================
// 8. 自定义 API（尝试 OpenAI 兼容格式）
// ============================================================
async function fetchCustomModels(endpoint: string, apiKey: string): Promise<string[]> {
  try {
    const url = buildUrl(endpoint, 'models')
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(8000),
    })
    if (!response.ok) return []
    const data = await response.json()
    return extractModels(data)
  } catch (error) {
    console.warn('⚠️ 自定义 API 拉取失败:', error)
    return []
  }
}

// ============================================================
// 工具函数
// ============================================================

function buildUrl(endpoint: string, path: string): string {
  let url = endpoint
  if (!url.endsWith('/' + path)) {
    url = url.endsWith('/') ? url + path : url + '/' + path
  }
  return url
}

function extractModels(data: any): string[] {
  if (data.data && Array.isArray(data.data)) {
    return data.data
      .filter((m: any) => m.id)
      .map((m: any) => m.id)
  }
  if (data.models && Array.isArray(data.models)) {
    return data.models
      .filter((m: any) => m.name)
      .map((m: any) => m.name.split('/').pop() || m.name)
  }
  if (Array.isArray(data)) {
    return data.map((m: any) => String(m.id || m.name || m))
  }
  if (data.result && Array.isArray(data.result)) {
    return data.result.map((m: any) => String(m))
  }
  return []
}
</script>

<style scoped>
.fetch-error {
  font-size: 12px;
  color: var(--danger);
  margin-top: 6px;
}
</style>