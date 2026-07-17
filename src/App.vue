<template>
  <div class="container">
    <AppBar @openHelp="handleOpenHelp" />
    

    <StatusCard />
    <ProviderSelect />
    <ApiConfigInputs />
    <ModelConfig />
    <TemperatureSlider />
    <ActionButtons />
  </div>

  <!-- ===== 帮助弹窗 ===== -->
  <div v-if="helpVisible" class="help-overlay" @click.self="helpVisible = false">
    <div class="help-modal">
      <div class="help-header">
        <h2>📖 使用帮助</h2>
        <button class="help-close" @click="helpVisible = false">✕</button>
      </div>
      <div class="help-body">
        <div class="help-section">
          <h3>🔑 如何获取 API 密钥？</h3>
          <p>1. 访问对应服务商官网注册账号</p>
          <p>2. 在 API 密钥管理页面创建新密钥</p>
          <p>3. 复制密钥粘贴到此应用</p>
        </div>
        <div class="help-section">
          <h3>🌐 各服务商文档链接</h3>
          <p>• <a href="https://platform.deepseek.com/api-docs" target="_blank">DeepSeek</a></p>
          <p>• <a href="https://platform.openai.com/docs/api-reference" target="_blank">OpenAI</a></p>
          <p>• <a href="https://docs.anthropic.com/claude/reference" target="_blank">Claude</a></p>
          <p>• <a href="https://ai.google.dev/gemini-api/docs" target="_blank">Gemini</a></p>
        </div>
        <div class="help-section">
          <h3>🌡️ 温度参数说明</h3>
          <p>• <strong>0.0–0.5</strong>：严谨，适合事实问答</p>
          <p>• <strong>0.5–1.0</strong>：平衡，适合一般对话</p>
          <p>• <strong>1.0–2.0</strong>：创意，适合角色扮演和写作</p>
        </div>
        <div class="help-section">
          <h3>🔒 隐私安全提示</h3>
          <p>• API 密钥仅加密存储在您的设备本地</p>
          <p>• 绝不上传到任何服务器</p>
          <p>• 建议定期更换 API 密钥</p>
        </div>
      </div>
      <div class="help-footer">
        <button class="help-btn-primary" @click="helpVisible = false">我知道了</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppBar from './components/AppBar.vue'
import StatusCard from './components/StatusCard.vue'
import ProviderSelect from './components/ProviderSelect.vue'
import ApiConfigInputs from './components/ApiConfigInputs.vue'
import ModelConfig from './components/ModelConfig.vue'
import TemperatureSlider from './components/TemperatureSlider.vue'
import ActionButtons from './components/ActionButtons.vue'
import { useConfigStore } from './stores/configStore'

const store = useConfigStore()

// ===== 帮助弹窗 =====
const helpVisible = ref(false)

function handleOpenHelp() {
  helpVisible.value = true
}

// ===== 全局 Toast（动态创建，挂到 body 上） =====
function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
  // 移除已有的 Toast
  const existing = document.querySelector('.global-toast-body')
  if (existing) existing.remove()

  // 创建 Toast 元素
  const toast = document.createElement('div')
  toast.className = `global-toast-body ${type}`
  toast.textContent = message

  // 直接挂到 body 上
  document.body.appendChild(toast)

  // 3 秒后移除
  setTimeout(() => {
    if (toast.parentNode) toast.remove()
  }, 3000)
}

// @ts-ignore
window.showToast = showToast

onMounted(() => {
  store.loadConfig()       // 后端优先，不可用时降级到 localStorage
})
</script>

<style>
/* ===== CSS 变量（主题系统）===== */
:root {
  --bg: #f5f7fa;
  --card-bg: #ffffff;
  --text: #1a1a2e;
  --text-secondary: #555;
  --text-muted: #9ca3af;
  --text-label: #374151;
  --border: #e8ecf1;
  --border-focus: #d1d5db;
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --primary-light: #eff6ff;
  --primary-disabled: #93b4f0;
  --primary-shadow: rgba(37, 99, 235, 0.1);
  --success: #22c55e;
  --success-hover: #16a34a;
  --success-bg: #f0fdf4;
  --success-border: #bbf7d0;
  --danger: #ef4444;
  --danger-hover: #dc2626;
  --danger-bg: #fef2f2;
  --danger-border: #fecaca;
  --warning: #f59e0b;
  --warning-bg: #fffbeb;
  --shadow: rgba(0, 0, 0, 0.08);
  --shadow-lg: rgba(0, 0, 0, 0.3);
  --input-bg: #fff;
  --input-prefix-bg: #f3f4f6;
  --hover-bg: #f0f0f0;
  --hover-bg-2: #f3f4f6;
  --hover-bg-3: #f9fafb;
  --tag-bg: #dbeafe;
  --tag-text: #2563eb;
  --modal-overlay: rgba(0, 0, 0, 0.4);
  --toast-shadow: rgba(0, 0, 0, 0.2);
  --demo-notice-border: #f0f0f0;
  --secondary-btn-bg: #f3f4f6;
  --secondary-btn-hover: #e5e7eb;
  --secondary-btn-text: #374151;
}

[data-theme="dark"] {
  --bg: #0f0f1a;
  --card-bg: #1e1e2e;
  --text: #e5e7eb;
  --text-secondary: #b0b7c3;
  --text-muted: #6b7280;
  --text-label: #cbd5e1;
  --border: #2d2d44;
  --border-focus: #4b5563;
  --primary: #3b82f6;
  --primary-hover: #2563eb;
  --primary-light: #1e293b;
  --primary-disabled: #475569;
  --primary-shadow: rgba(59, 130, 246, 0.2);
  --success: #34d399;
  --success-hover: #10b981;
  --success-bg: #064e3b;
  --success-border: #065f46;
  --danger: #f87171;
  --danger-hover: #ef4444;
  --danger-bg: #7f1d1d;
  --danger-border: #991b1b;
  --warning: #fbbf24;
  --warning-bg: #78350f;
  --shadow: rgba(0, 0, 0, 0.3);
  --shadow-lg: rgba(0, 0, 0, 0.5);
  --input-bg: #2d2d44;
  --input-prefix-bg: #1e1e2e;
  --hover-bg: #3d3d5c;
  --hover-bg-2: #2d2d44;
  --hover-bg-3: #262638;
  --tag-bg: #1e3a5f;
  --tag-text: #60a5fa;
  --modal-overlay: rgba(0, 0, 0, 0.6);
  --toast-shadow: rgba(0, 0, 0, 0.4);
  --demo-notice-border: #2d2d44;
  --secondary-btn-bg: #2d2d44;
  --secondary-btn-hover: #3d3d5c;
  --secondary-btn-text: #cbd5e1;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  padding: 0;
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  overflow-y: scroll;
  transition: background 0.3s, color 0.3s;
}

.container {
  max-width: 100%;
  width: 100%;
  min-height: 100vh;
  background: var(--card-bg);
  border-radius: 0;
  box-shadow: none;
  padding: 16px 16px 32px;
  transition: background 0.3s;
  margin: 0 auto;
}

.demo-notice {
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  padding: 6px 0 10px 0;
  border-bottom: 1px solid var(--demo-notice-border);
  margin-bottom: 16px;
}

/* ===== 卡片 ===== */
.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 4px var(--shadow);
  transition: border-color 0.2s, background 0.3s, box-shadow 0.3s;
  width: 100%;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text);
}

.card-title .icon {
  font-size: 20px;
}

/* ===== 状态卡片 ===== */
.status-card {
  border-left: 4px solid var(--warning);
  transition: border-left-color 0.3s, background 0.3s;
}
.status-card.valid {
  border-left-color: var(--success);
}
.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.status-icon {
  font-size: 28px;
}
.status-info {
  flex: 1;
}
.status-info .status-text {
  font-size: 16px;
  font-weight: 600;
  transition: color 0.3s;
}
.status-info .status-text.valid {
  color: var(--success);
}
.status-info .status-text.invalid {
  color: var(--warning);
}
.status-info .status-detail {
  font-size: 14px;
  color: var(--text-secondary);
}
.status-badge {
  font-size: 12px;
  background: var(--tag-bg);
  color: var(--tag-text);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
  transition: background 0.3s, color 0.3s;
}

/* ===== 下拉选择 ===== */
.select-wrapper {
  border: 1px solid var(--border-focus);
  border-radius: 6px;
  padding: 0 12px;
  background: var(--input-bg);
  transition: background 0.3s, border-color 0.2s;
  width: 100%;
}
.select-wrapper select {
  width: 100%;
  padding: 10px 0;
  border: none;
  background: transparent;
  font-size: 15px;
  color: var(--text);
  outline: none;
  cursor: pointer;
}
.select-wrapper select option {
  padding: 8px;
  background: var(--card-bg);
  color: var(--text);
}

/* ===== 输入框 ===== */
.input-group {
  margin-bottom: 4px;
  width: 100%;
}
.input-row {
  display: flex;
  align-items: center;
  border: 1px solid var(--border-focus);
  border-radius: 6px;
  background: var(--input-bg);
  transition: border-color 0.2s, background 0.3s;
  width: 100%;
}
.input-row:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-shadow);
}
.input-row .prefix {
  font-size: 12px;
  color: var(--text-muted);
  padding: 0 8px 0 12px;
  background: var(--input-prefix-bg);
  border-radius: 6px 0 0 6px;
  height: 100%;
  display: flex;
  align-items: center;
  white-space: nowrap;
  border-right: 1px solid var(--border-focus);
  transition: background 0.3s;
}
.input-row input {
  flex: 1;
  padding: 10px 12px;
  border: none;
  background: transparent;
  font-size: 15px;
  outline: none;
  color: var(--text);
  min-width: 0;
  transition: color 0.3s;
}
.input-row input::placeholder {
  color: var(--text-muted);
}
.input-row .toggle-btn {
  background: none;
  border: none;
  padding: 0 12px;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-muted);
  transition: color 0.2s;
}
.input-row .toggle-btn:hover {
  color: var(--text);
}
.input-error {
  font-size: 12px;
  color: var(--danger);
  margin-top: 4px;
}
.hint-text {
  font-size: 13px;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 6px;
}

/* ===== 模型配置 ===== */
.mode-toggle {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.mode-option {
  flex: 1;
  padding: 8px 0;
  text-align: center;
  border: 1px solid var(--border-focus);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-muted);
  background: var(--hover-bg-3);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.mode-option .dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid var(--border-focus);
  display: inline-block;
  transition: all 0.2s;
}
.mode-option.active {
  border-color: var(--primary);
  background: var(--primary-light);
  color: var(--primary);
}
.mode-option.active .dot {
  border-color: var(--primary);
  background: var(--primary);
  border-width: 4px;
}
.fetch-btn {
  margin-left: auto;
  background: var(--primary);
  color: #fff;
  border: none;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: opacity 0.2s;
}
.fetch-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== 温度滑块 ===== */
.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.slider-header .value {
  font-weight: 600;
  padding: 2px 12px;
  border-radius: 4px;
  background: var(--input-prefix-bg);
}
.slider-header .value.green { color: var(--success); }
.slider-header .value.blue { color: var(--primary); }
.slider-header .value.orange { color: var(--warning); }
.slider-header .value.red { color: var(--danger); }

input[type="range"] {
  width: 100%;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--border-focus);
  border-radius: 4px;
  outline: none;
  margin: 8px 0 12px;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: 2px solid var(--card-bg);
  box-shadow: 0 1px 4px var(--shadow);
}
.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-muted);
}
.slider-desc {
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 8px;
}

/* ===== 操作按钮 ===== */
.action-row {
  display: flex;
  gap: 12px;
  margin-top: 4px;
}
.action-row .btn {
  flex: 1;
  padding: 12px 0;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.btn-primary {
  background: var(--primary);
  color: #fff;
}
.btn-primary:hover {
  background: var(--primary-hover);
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-success {
  background: var(--success);
  color: #fff;
}
.btn-success:hover {
  background: var(--success-hover);
}
.btn-danger-outline {
  background: transparent;
  color: var(--danger);
  border: 1.5px solid var(--danger);
}
.btn-danger-outline:hover {
  background: var(--danger-bg);
}

/* ===== 测试结果 ===== */
.test-result {
  padding: 12px 16px;
  border-radius: 10px;
  margin-top: 12px;
  transition: all 0.3s;
}
.test-result.success {
  background: var(--success-bg);
  border: 1px solid var(--success-border);
  color: var(--success);
}
.test-result.fail {
  background: var(--danger-bg);
  border: 1px solid var(--danger-border);
  color: var(--danger);
}
.result-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.result-icon { font-size: 22px; }
.result-info { flex: 1; }
.result-title { font-weight: 600; font-size: 15px; }
.result-detail { font-size: 13px; opacity: 0.8; }

/* ===== 确认弹窗 ===== */
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
  padding: 20px;
}
.confirm-box {
  background: var(--card-bg);
  border-radius: 16px;
  max-width: 380px;
  width: 100%;
  padding: 24px 20px 20px;
  box-shadow: 0 20px 60px var(--shadow-lg);
}
.confirm-box h3 { font-size: 17px; margin-bottom: 6px; color: var(--text); }
.confirm-box p { font-size: 14px; color: var(--text-secondary); margin-bottom: 16px; }
.confirm-actions { display: flex; gap: 10px; }
.confirm-actions button {
  flex: 1;
  padding: 10px 0;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
}
.btn-cancel {
  background: var(--secondary-btn-bg);
  color: var(--secondary-btn-text);
}
.btn-cancel:hover { background: var(--secondary-btn-hover); }
.btn-confirm-danger {
  background: var(--danger);
  color: #fff;
}
.btn-confirm-danger:hover { background: var(--danger-hover); }

/* ===== 帮助弹窗 ===== */
.help-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  padding: 20px;
  animation: fadeIn 0.25s ease;
}

.help-modal {
  background: var(--card-bg);
  border-radius: 16px;
  max-width: 520px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  padding: 24px 28px 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.25s ease;
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.help-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.help-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.help-close:hover {
  background: var(--hover-bg);
  color: var(--text);
}

.help-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.help-section h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 6px;
}

.help-section p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 2px 0;
  line-height: 1.6;
}

.help-section a {
  color: var(--primary);
  text-decoration: none;
}

.help-section a:hover {
  text-decoration: underline;
}

.help-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.help-btn-primary {
  background: var(--primary);
  color: #fff;
  border: none;
  padding: 10px 28px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.help-btn-primary:hover {
  background: var(--primary-hover);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ===== 响应式：手机端适配 ===== */
@media (max-width: 480px) {
  .container {
    padding: 12px 12px 20px;
  }
  .card {
    padding: 12px;
  }
  .action-row {
    flex-direction: column;
    gap: 8px;
  }
  .mode-toggle {
    flex-direction: row;
  }
}
</style>