<template>
  <el-card class="upload-card">
    <template #header>
      <div class="card-header">
        <h2>上传 Excel 文件</h2>
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
      <div class="el-upload__text">拖拽 Excel 文件到此处，或<em>点击选择</em></div>
      <template #tip>
        <div class="el-upload__tip">仅支持 .xlsx 和 .xls 文件</div>
      </template>
    </el-upload>

    <div v-if="selectedFile" class="selected-file">
      已选择文件：{{ selectedFile.name }}
    </div>

    <div class="actions">
      <el-button
        type="primary"
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
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.upload-alert {
  margin-bottom: 16px;
}

.selected-file {
  margin-top: 16px;
  color: #606266;
}

.actions {
  margin-top: 24px;
  text-align: center;
}
</style>
