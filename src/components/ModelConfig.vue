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
import { apiPost } from '@/api'

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
// 拉取模型列表（通过后端代理，带智能降级）
// ============================================================

interface FetchModelsResult {
  success: boolean
  models: string[]
  provider: string
  error: string
  message?: string
}

async function fetchModels() {
  const provider = store.currentProvider!

  // 1. 检查 API 密钥
  if (provider.requiresKey && !store.apiKey) {
    window.showToast('⚠️ 请先填写 API 密钥', 'error')
    return
  }

  // 2. 检查端点
  if (provider.showUrl && !store.endpoint) {
    window.showToast('⚠️ 请先填写 API 端点 URL', 'error')
    return
  }

  // 3. 检查是否正在加载
  if (isFetching.value || !canFetch.value) return

  const endpoint = store.endpoint || provider.defaultEndpoint

  isFetching.value = true
  fetchError.value = null

  try {
    const result = await apiPost<FetchModelsResult>('/api/models/fetch', {
      providerId: provider.id,
      endpoint,
      apiKey: store.apiKey,
    })

    if (result.success && result.models.length > 0) {
      modelList.value = result.models
      if (!store.model || !result.models.includes(store.model)) {
        store.model = result.models[0]!
      }
      window.showToast(result.message || `✅ 成功拉取 ${result.models.length} 个模型`, 'success')
    } else {
      // ⭐ 降级：自动切换到手动输入模式
      store.isManualModel = true
      const defaultModel = provider.defaultModel
      if (defaultModel && !store.model) {
        store.model = defaultModel
      }
      fetchError.value = result.error || '该 API 不支持拉取模型列表，请手动输入模型名称'
      window.showToast(result.message || '💡 该 API 不支持拉取模型列表，已切换至手动输入模式', 'info')
    }
  } catch (error: any) {
    console.error('❌ 拉取模型失败:', error)
    // ⭐ 降级：自动切换到手动输入模式
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
</script>

<style scoped>
.fetch-error {
  font-size: 12px;
  color: var(--danger);
  margin-top: 6px;
}
</style>