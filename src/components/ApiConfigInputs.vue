<template>
  <!-- API端点 -->
  <div class="card" v-if="store.currentProvider.showUrl">
    <div class="card-title">
      <span class="icon">🔗</span>
      <span>API端点 (URL)</span>
    </div>
    <div class="input-group">
      <div class="input-row">
        <input
          type="text"
          v-model="store.endpoint"
          :placeholder="store.currentProvider.defaultEndpoint"
        />
        <button class="toggle-btn" @click="resetEndpoint" title="恢复默认值">↺</button>
      </div>
    </div>
  </div>

  <!-- API密钥 -->
  <div class="card" v-if="store.currentProvider.showKey">
    <div class="card-title">
      <span class="icon">🔑</span>
      <span>API密钥</span>
    </div>
    <div class="input-group">
      <div class="input-row">
        <span class="prefix">{{ store.currentProvider.keyPrefix }}</span>
        <input
          :type="keyVisible ? 'text' : 'password'"
          v-model="store.apiKey"
          placeholder="输入API密钥..."
        />
        <button class="toggle-btn" @click="keyVisible = !keyVisible">
          {{ keyVisible ? '🙈' : '👁️' }}
        </button>
      </div>
      <div class="input-error" v-if="!store.apiKey && showError">请输入API密钥</div>
    </div>
    <div class="hint-text">密钥存储在本地浏览器中，不会上传到任何服务器</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useConfigStore } from '@/stores/configStore'

const store = useConfigStore()
const keyVisible = ref(false)
const showError = ref(false)

function resetEndpoint() {
  store.endpoint = store.currentProvider.defaultEndpoint
}
</script>

<style scoped>

</style>