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

const store = useConfigStore()
const isTesting = ref(false)
const showConfirm = ref(false)

interface TestResult {
  success: boolean
  duration: number
  speedRating: string
  error?: string
}

const testResult = ref<TestResult | null>(null)

// ============================================================
// 真实 API 测试连接（从 Flutter 翻译过来）
// ============================================================
async function testConnection() {
  if (!store.isValid || isTesting.value) return

  const provider = store.currentProvider
  const endpoint = store.endpoint || provider.defaultEndpoint
  const apiKey = store.apiKey
  const model = store.model

  // 本地模型直接返回成功
  if (provider.id === 'localBuiltin') {
    testResult.value = {
      success: true,
      duration: 50,
      speedRating: '极快 🚀',
    }
    return
  }

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
  const startTime = Date.now()

  try {
    // 构建请求 URL
    let url = endpoint
    if (!url.endsWith('/chat/completions')) {
      url = url.endsWith('/') ? url + 'chat/completions' : url + '/chat/completions'
    }

    // 构建请求体（OpenAI 兼容格式）
    const requestBody = {
      model: model,
      messages: [{ role: 'user', content: 'test' }],
      max_tokens: 5,
    }

    console.log('📡 测试连接:', { url, model })

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      signal: AbortSignal.timeout(10000), // 10 秒超时
    })

    const duration = Date.now() - startTime

    // 处理响应
    if (response.ok) {
      // 尝试解析响应，验证是否为有效 JSON
      try {
        const data = await response.json()
        console.log('✅ 测试成功:', data)
        testResult.value = {
          success: true,
          duration: duration,
          speedRating: getSpeedRating(duration),
        }
      } catch {
        // 响应不是 JSON，但也算是成功
        testResult.value = {
          success: true,
          duration: duration,
          speedRating: getSpeedRating(duration),
        }
      }
    } else {
      // 尝试解析错误信息
      let errorMsg = `HTTP ${response.status}`
      try {
        const errorData = await response.json()
        if (errorData.error?.message) {
          errorMsg = errorData.error.message
        } else if (errorData.message) {
          errorMsg = errorData.message
        }
      } catch {
        // 无法解析错误信息，使用状态码
      }

      testResult.value = {
        success: false,
        duration: duration,
        speedRating: '失败 ❌',
        error: errorMsg,
      }
      console.error('❌ 测试失败:', response.status, errorMsg)
    }
  } catch (error: any) {
    const duration = Date.now() - startTime
    let errorMsg = '连接超时或网络错误'

    if (error.name === 'TimeoutError' || error.name === 'AbortError') {
      errorMsg = '请求超时，请检查网络或 API 配置'
    } else if (error.message) {
      errorMsg = error.message
    }

    testResult.value = {
      success: false,
      duration: duration,
      speedRating: '失败 ❌',
      error: errorMsg,
    }
    console.error('❌ 测试异常:', error)
  } finally {
    isTesting.value = false
  }
}

// ============================================================
// 速度评级
// ============================================================
function getSpeedRating(duration: number): string {
  if (duration < 300) return '极快 🚀'
  if (duration < 800) return '快速 ⚡'
  if (duration < 1500) return '正常 ✅'
  if (duration < 3000) return '较慢 🐢'
  return '很慢 ⚠️'
}

// ============================================================
// 保存 & 清除
// ============================================================
function saveConfig() {
  if (!store.isValid) return
  store.saveToStorage()
  const btn = document.activeElement as HTMLElement
  const original = btn.textContent
  btn.textContent = '✅ 已保存'
  setTimeout(() => { btn.textContent = original }, 1500)
}

function clearConfig() {
  store.clearConfig()
  testResult.value = null
  showConfirm.value = false
}
</script>

<style scoped>
/* 所有样式已经在 App.vue 里定义，这里留空即可 */
</style>