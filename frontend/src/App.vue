<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-inner">
        <div class="brand-block">
          <p class="eyebrow">MVP 工作流</p>
          <h1>线缆点位测试表转换软件</h1>
          <p class="subtitle">上传 Excel、预览转换结果并导出编程表。</p>
        </div>
      </div>
    </el-header>
    <el-main class="app-main">
      <div class="page-container">
        <router-view />
      </div>
    </el-main>
  </el-container>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.app-header {
  height: auto;
  padding: 28px 24px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #ffffff;
}

.header-inner {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.brand-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.eyebrow {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
  letter-spacing: 0.08em;
}

.app-header h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
  color: #303133;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.app-main {
  display: flex;
  justify-content: center;
  padding: 32px 24px 40px;
}

.page-container {
  width: 100%;
  max-width: 1200px;
}

@media (max-width: 768px) {
  .app-header {
    padding: 24px 16px 18px;
  }

  .app-header h1 {
    font-size: 24px;
  }

  .app-main {
    padding: 20px 12px 32px;
  }
}
</style>
