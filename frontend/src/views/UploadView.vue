<template>
  <el-card class="upload-card" shadow="never">
    <template #header>
      <div class="card-header">
        <div>
          <h2>上传 Excel 文件</h2>
          <p class="card-description">支持拖拽或选择线缆测试表文件，解析后进入预览页面核对转换结果。</p>
        </div>
      </div>
    </template>

    <el-alert
      v-if="errorMessage"
      class="upload-alert"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="false"
    />

    <div class="upload-section">
      <el-upload
        drag
        action="#"
        accept=".xlsx,.xls"
        :auto-upload="false"
        :limit="1"
        :file-list="fileList"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :on-exceed="handleFileExceed"
      >
        <div class="upload-text">拖拽 Excel 文件到此处，或<em>点击选择</em></div>
        <template #tip>
          <div class="upload-tip">仅支持 .xlsx 和 .xls 文件</div>
        </template>
      </el-upload>
    </div>

    <div class="file-summary">
      <span class="file-summary-label">当前文件</span>
      <span class="file-summary-name">{{ selectedFile ? selectedFile.name : '尚未选择文件' }}</span>
    </div>

    <div class="actions">
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!selectedFile || loading"
        @click="handleStartParse"
      >
        开始解析
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadFile } from '../api/fileApi'

const router = useRouter()
const selectedFile = ref(null)
const fileList = ref([])
const loading = ref(false)
const errorMessage = ref('')

function isExcelFile(fileName) {
  return /\.(xlsx|xls)$/i.test(fileName)
}

function handleFileChange(uploadFile) {
  errorMessage.value = ''

  if (!isExcelFile(uploadFile.name)) {
    selectedFile.value = null
    fileList.value = []
    errorMessage.value = '仅支持 .xlsx 和 .xls 文件'
    return
  }

  selectedFile.value = uploadFile.raw
  fileList.value = [uploadFile]
}

function handleFileRemove() {
  selectedFile.value = null
  fileList.value = []
  errorMessage.value = ''
}

function handleFileExceed(files) {
  const file = files[0]

  if (!isExcelFile(file.name)) {
    selectedFile.value = null
    fileList.value = []
    errorMessage.value = '仅支持 .xlsx 和 .xls 文件'
    return
  }

  selectedFile.value = file
  fileList.value = [
    {
      name: file.name,
      raw: file,
    },
  ]
  errorMessage.value = ''
}

async function handleStartParse() {
  if (!selectedFile.value) {
    errorMessage.value = '请先选择 Excel 文件'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await uploadFile(selectedFile.value)
    sessionStorage.setItem('upload_result', JSON.stringify(response.data))
    router.push('/preview')
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '上传失败，请检查后端服务是否正常运行'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.upload-card {
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

.upload-alert {
  margin-bottom: 20px;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-text {
  font-size: 15px;
  color: #606266;
}

.upload-tip {
  margin-top: 8px;
  color: #909399;
}

.file-summary {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px 18px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #ebeef5;
}

.file-summary-label {
  font-size: 13px;
  color: #909399;
}

.file-summary-name {
  font-size: 15px;
  color: #303133;
  word-break: break-all;
}

.actions {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}
</style>
