<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <h1>线缆点位测试表转换软件</h1>
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
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e4e7ed;
  background: #ffffff;
}

.app-header h1 {
  margin: 0;
  font-size: 22px;
}

.app-main {
  display: flex;
  justify-content: center;
}

.page-container {
  width: 100%;
  max-width: 860px;
}
</style>
