<template>
  <div class="result-page">
    <el-card v-if="!convertResult">
      <el-empty description="暂无转换结果，请先上传并转换文件">
        <el-button type="primary" @click="goUpload">返回上传页</el-button>
      </el-empty>
    </el-card>

    <el-card v-else>
      <template #header>
        <div class="card-header">
          <h2>转换完成</h2>
          <el-tag type="warning">Mock 数据</el-tag>
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

      <el-result icon="success" title="转换成功" sub-title="当前为 mock 下载流程，暂不生成真实 Excel 文件" />

      <el-descriptions :column="1" border>
        <el-descriptions-item label="输出文件">{{ convertResult.output_filename }}</el-descriptions-item>
      </el-descriptions>

      <div class="actions">
        <el-button type="primary" :loading="loading" @click="handleDownload">下载结果</el-button>
        <el-button :disabled="loading" @click="resetAndUpload">重新上传</el-button>
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
    downloadMessage.value = response.data?.message || 'mock 下载接口调用成功'
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '下载失败，请检查后端服务是否正常运行'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.result-page {
  width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h2 {
  margin: 0;
}

.message-alert {
  margin-bottom: 12px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}
</style>
