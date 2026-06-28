<template>
  <div class="error-page">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面未找到</h2>
      <p class="error-desc">抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="router.push('/')">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style lang="scss" scoped>
.error-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);

  .error-content {
    text-align: center;

    .error-code {
      font-size: 120px;
      font-weight: 700;
      color: #409EFF;
      margin: 0;
      line-height: 1;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }

    .error-title {
      font-size: 32px;
      color: #303133;
      margin: 20px 0 10px;
    }

    .error-desc {
      font-size: 16px;
      color: #909399;
      margin-bottom: 30px;
    }
  }
}
</style>
