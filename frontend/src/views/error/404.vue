<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面未找到</h2>
      <p class="error-description">抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
.not-found-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .not-found-content {
    text-align: center;
    color: #fff;
    
    .error-code {
      font-size: 120px;
      font-weight: 700;
      margin: 0;
      line-height: 1;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .error-title {
      font-size: 32px;
      font-weight: 500;
      margin: 20px 0 10px;
    }
    
    .error-description {
      font-size: 16px;
      margin-bottom: 30px;
      opacity: 0.8;
    }
  }
}
</style>
