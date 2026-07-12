<template>
  <div class="card status-card" :class="{ valid: store.isValid }">
    <div class="status-row">
      <span class="status-icon">{{ store.isValid ? '✅' : '⚠️' }}</span>
      <div class="status-info">
        <div class="status-text" :class="store.isValid ? 'valid' : 'invalid'">
          {{ store.isValid ? '配置完成' : '未完整配置' }}
        </div>
        <div class="status-detail">{{ store.currentProvider.name }} • {{ store.displayModel }}</div>
      </div>
      <span class="status-badge">使用中</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useConfigStore } from '@/stores/configStore'

const store = useConfigStore()
</script>

<style scoped>

</style>