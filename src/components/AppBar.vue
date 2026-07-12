<template>
  <div class="app-bar">
    <!-- 左边：返回按钮（图标） -->
    <button class="icon-btn" @click="goBack" aria-label="返回">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </button>

    <!-- 中间：标题 -->
    <h1>API设置</h1>

    <!-- 右边：主题切换 + 帮助按钮（图标） -->
    <div class="right-actions">
      <button class="icon-btn" @click="toggleTheme" aria-label="切换主题">
        <svg v-if="isDark" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
      </button>

      <button class="icon-btn" @click="openHelp" aria-label="帮助">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isDark = ref(false)

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
}

const emit = defineEmits<{
  (e: 'openHelp'): void
}>()

function openHelp() {
  emit('openHelp')
}

function goBack() {
  // 模拟返回
  window.history.back()
}
</script>

<style scoped>
.app-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0 12px 0;
  margin-bottom: 4px;
}

h1 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
  flex: 1;
  text-align: center;
}

.right-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ===== 无框图标按钮样式 ===== */
.icon-btn {
  background: transparent;
  border: none;
  padding: 8px;
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  line-height: 1;
}

.icon-btn:hover {
  background: var(--hover-bg);
  color: var(--text);
}

.icon-btn:active {
  background: var(--hover-bg-2);
  transform: scale(0.95);
}

/* 调整右侧两个按钮的间距 */
.right-actions .icon-btn {
  margin-left: 2px;
}
</style>