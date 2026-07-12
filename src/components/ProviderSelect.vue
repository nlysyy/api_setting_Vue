<template>
  <div class="card">
    <div class="card-title">
      <span class="icon">🔌</span>
      <span>选择AI服务商</span>
    </div>
    <div class="select-wrapper">
      <select v-model="store.providerId" @change="onProviderChange">
        <option v-for="p in providers" :key="p.id" :value="p.id">
          {{ p.emoji }} {{ p.name }}
        </option>
      </select>
    </div>
    <div class="hint-text">{{ store.currentProvider.hint }}</div>
  </div>
</template>

<script setup lang="ts">
import { useConfigStore } from '@/stores/configStore'

const store = useConfigStore()

const providers = [
  { id: 'deepseek', name: 'DeepSeek', emoji: '🔍' },
  { id: 'openai', name: 'OpenAI', emoji: '⚡' },
  { id: 'claude', name: 'Claude (Anthropic)', emoji: '🤖' },
  { id: 'gemini', name: 'Gemini (Google)', emoji: '✨' },
  { id: 'qwen', name: '通义千问', emoji: '🔮' },
]

function onProviderChange() {
  // 清空旧的密钥和端点
  store.endpoint = ''
  store.apiKey = ''
  store.model = store.currentProvider.defaultModel

  // 新增：切换成功提示
  const providerName = store.currentProvider.name
  const emoji = store.currentProvider.emoji
  window.showToast(` 已切换到  ${providerName}`, 'success')
}
</script>