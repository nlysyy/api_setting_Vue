<template>
  <div class="card">
    <div class="card-title">
      <span class="icon">🔌</span>
      <span>选择AI服务商</span>
    </div>
    <div class="select-wrapper">
      <select v-model="store.providerId" @change="onProviderChange">
        <option v-for="p in PROVIDERS" :key="p.id" :value="p.id">
          {{ p.emoji }} {{ p.name }}
        </option>
      </select>
    </div>
    <div class="hint-text">{{ store.currentProvider!.hint }}</div>
  </div>
</template>

<script setup lang="ts">
import { useConfigStore, PROVIDERS } from '@/stores/configStore'

const store = useConfigStore()

function onProviderChange() {
  const p = store.currentProvider!
  store.endpoint = ''
  store.apiKey = ''
  store.model = p.defaultModel
  window.showToast(` 已切换到  ${p.name}`, 'success')
}
</script>