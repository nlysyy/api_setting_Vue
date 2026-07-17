<template>
  <div class="action-row">
    <button class="btn btn-primary" @click="testConnection" :disabled="!store.isValid || isTesting">
      {{ isTesting ? '测试中...' : '🔗 测试连接' }}
    </button>
    <button class="btn btn-success" @click="saveConfig">💾 保存配置</button>
    <button class="btn btn-danger-outline" @click="showConfirm = true">🗑️ 清除配置</button>
  </div>

  <!-- 测试结果 -->
  <div v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'fail'">
    <div class="result-row">
      <span class="result-icon">{{ testResult.success ? '✅' : '❌' }}</span>
      <div class="result-info">
        <div class="result-title">{{ testResult.success ? '连接测试成功' : '连接测试失败' }}</div>
        <div class="result-detail">
          耗时: {{ testResult.duration }}ms • {{ testResult.speedRating }}
        </div>
      </div>
    </div>
    <div v-if="!testResult.success && testResult.error" class="result-error">
      {{ testResult.error }}
    </div>
  </div>

  <!-- 确认弹窗 -->
  <div class="confirm-overlay" v-if="showConfirm" @click.self="showConfirm = false">
    <div class="confirm-box">
      <h3>清除配置</h3>
      <p>确定要清除当前配置吗？此操作不可恢复。</p>
      <div class="confirm-actions">
        <button class="btn-cancel" @click="showConfirm = false">取消</button>
        <button class="btn-confirm-danger" @click="clearConfig">清除</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useConfigStore } from '@/stores/configStore'
import { apiPost } from '@/api'

const store = useConfigStore()
const isTesting = ref(false)
const showConfirm = ref(false)

interface TestResult {
  success: boolean
  duration: number
  speedRating: string
  error?: string
  message?: string
}

const testResult = ref<TestResult | null>(null)

// ============================================================
// 测试连接（通过后端代理）
// ============================================================
async function testConnection() {
  if (!store.isValid || isTesting.value) return

  const provider = store.currentProvider
  const endpoint = store.endpoint || provider.defaultEndpoint
  const apiKey = store.apiKey
  const model = store.model

  // 检查必要参数
  if (!apiKey) {
    testResult.value = {
      success: false,
      duration: 0,
      speedRating: '失败 ❌',
      error: '请先填写 API 密钥',
    }
    return
  }

  if (!model) {
    testResult.value = {
      success: false,
      duration: 0,
      speedRating: '失败 ❌',
      error: '请先选择模型',
    }
    return
  }

  isTesting.value = true
  testResult.value = null

  try {
    const result = await apiPost<TestResult>('/api/connection/test', {
      providerId: provider.id,
      endpoint,
      apiKey,
      model,
    })

    testResult.value = {
      success: result.success,
      duration: result.duration,
      speedRating: result.speedRating,
      error: result.success ? undefined : result.error,
    }
  } catch (error: any) {
    testResult.value = {
      success: false,
      duration: 0,
      speedRating: '失败 ❌',
      error: error.message || '连接超时，请检查网络或后端服务是否启动',
    }
    console.error('❌ 测试异常:', error)
  } finally {
    isTesting.value = false
  }
}

// ============================================================
// 保存 & 清除
// ============================================================
function saveConfig() {
  if (!store.isValid) return
  const btn = document.activeElement as HTMLElement
  const original = btn.textContent

  store.saveConfig().then((saved) => {
    btn.textContent = saved ? '✅ 已保存到云端' : '✅ 已保存'
    setTimeout(() => { btn.textContent = original }, 2000)
  }).catch(() => {
    btn.textContent = '❌ 保存失败'
    setTimeout(() => { btn.textContent = original }, 2000)
  })
}

async function clearConfig() {
  await store.clearConfig()
  testResult.value = null
  showConfirm.value = false
}
</script>

<style scoped>
/* 所有样式已经在 App.vue 里定义 */
</style>