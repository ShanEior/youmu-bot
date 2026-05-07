<template>
  <div class="result-page">
    <el-card v-if="!convertResult" class="result-card" shadow="never">
      <el-empty description="暂无转换结果，请先上传并转换文件">
        <el-button type="primary" @click="goUpload">返回上传页</el-button>
      </el-empty>
    </el-card>

    <el-card v-else class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <h2>转换完成</h2>
            <p class="card-description">编程表已生成，可直接下载结果文件，或返回重新上传新的 Excel。</p>
          </div>
        </div>
      </template>

      <el-alert
        v-if="errorMessage"
        class="message-alert"
        :title="errorMessage"
        type="error"
        show-icon
        :closable="false"
      />
      <el-alert
        v-if="downloadMessage"
        class="message-alert"
        :title="downloadMessage"
        type="success"
        show-icon
        :closable="false"
      />

      <el-result icon="success" title="转换成功" sub-title="已生成真实 Excel 文件，可直接下载结果" />

      <div class="result-summary">
        <span class="summary-label">输出文件名</span>
        <strong class="summary-value">{{ convertResult.output_filename }}</strong>
      </div>

      <div class="actions">
        <el-button type="primary" size="large" :loading="loading" @click="handleDownload">下载结果</el-button>
        <el-button size="large" :disabled="loading" @click="resetAndUpload">重新上传</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { downloadFile } from '../api/fileApi'

const router = useRouter()
const convertResult = ref(readConvertResult())
const loading = ref(false)
const errorMessage = ref('')
const downloadMessage = ref('')

function readConvertResult() {
  const raw = sessionStorage.getItem('convert_result')
  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function goUpload() {
  router.push('/upload')
}

function resetAndUpload() {
  sessionStorage.removeItem('upload_result')
  sessionStorage.removeItem('convert_result')
  router.push('/upload')
}

async function handleDownload() {
  if (!convertResult.value?.output_file_id) {
    errorMessage.value = '缺少 output_file_id，无法下载结果'
    return
  }

  loading.value = true
  errorMessage.value = ''
  downloadMessage.value = ''

  try {
    const response = await downloadFile(convertResult.value.output_file_id)
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const downloadUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = convertResult.value.output_filename || 'converted.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(downloadUrl)
    downloadMessage.value = '下载已开始，请检查浏览器下载内容'
  } catch (error) {
    errorMessage.value = '下载失败，请检查后端服务是否正常运行'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.result-page {
  width: 100%;
}

.result-card {
  width: 100%;
  border: none;
  border-radius: 18px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.card-description {
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.message-alert {
  margin-bottom: 16px;
}

.result-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
  padding: 18px 20px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #ebeef5;
}

.summary-label {
  font-size: 13px;
  color: #909399;
}

.summary-value {
  font-size: 18px;
  color: #303133;
  word-break: break-all;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 28px;
}
</style>
