<template>
  <div class="card">
    <div class="card-title" @click="collapsed = !collapsed" style="cursor:pointer;justify-content:space-between;">
      <span><span class="icon">⚙️</span> 高级设置</span>
      <span>{{ collapsed ? '▶' : '▼' }}</span>
    </div>
    <div v-show="!collapsed">
      <div class="slider-header">
        <span class="label">温度 (Temperature)</span>
        <span class="value" :class="tempColor">{{ store.temperature.toFixed(1) }}</span>
      </div>
      <input type="range" v-model.number="store.temperature" min="0" max="2" step="0.1" />
      <div class="slider-labels">
        <span><span>0.0</span><br /><small>严谨</small></span>
        <span><span>1.0</span><br /><small>平衡</small></span>
        <span><span>2.0</span><br /><small>创意</small></span>
      </div>
      <div class="slider-desc">{{ tempDesc }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useConfigStore } from '@/stores/configStore'

const store = useConfigStore()
const collapsed = ref(true)

const tempColor = computed(() => {
  const t = store.temperature
  if (t < 0.5) return 'green'
  if (t < 1.0) return 'blue'
  if (t < 1.5) return 'orange'
  return 'red'
})

const tempDesc = computed(() => {
  const t = store.temperature
  if (t < 0.3) return '输出非常稳定、可预测，适合事实性问答'
  if (t < 0.7) return '输出较为稳定，适合一般对话'
  if (t < 1.2) return '平衡创造性和稳定性，适合角色扮演'
  if (t < 1.7) return '更具创造性，输出多样化'
  return '非常创造性，输出高度随机，适合创意写作'
})
</script>

<style scoped>

</style>