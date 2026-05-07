<template>
  <div class="preview-page">
    <el-card v-if="!uploadResult">
      <el-empty description="暂无解析结果，请先上传文件">
        <el-button type="primary" @click="goUpload">返回上传页</el-button>
      </el-empty>
    </el-card>

    <template v-else>
      <el-card class="section-card">
        <template #header>
          <div class="card-header">
            <h2>解析预览页面</h2>
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

        <el-descriptions :column="1" border>
          <el-descriptions-item label="文件名">{{ uploadResult.filename }}</el-descriptions-item>
          <el-descriptions-item label="file_id">{{ uploadResult.file_id }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card v-for="sheet in sheets" :key="sheet.sheet_name" class="section-card">
        <template #header>
          <h3>{{ sheet.sheet_name }}</h3>
        </template>

        <el-descriptions class="sheet-info" :column="2" border>
          <el-descriptions-item label="表头行">{{ sheet.header_row }}</el-descriptions-item>
          <el-descriptions-item label="行数">{{ sheet.row_count }}</el-descriptions-item>
        </el-descriptions>

        <h4>字段识别结果</h4>
        <el-table :data="matchedColumnRows(sheet.matched_columns)" border size="small">
          <el-table-column prop="field" label="字段" />
          <el-table-column prop="column" label="列" width="120" />
        </el-table>

        <h4>原始数据预览</h4>
        <el-table :data="sheet.source_preview_rows || []" border size="small" empty-text="暂无原始数据预览">
          <el-table-column prop="start_connector" label="起点插件" min-width="160" />
          <el-table-column prop="start_pin" label="起点针脚" width="100" />
          <el-table-column prop="start_content" label="起点内容" min-width="160" />
          <el-table-column prop="end_connector" label="终点插件" min-width="160" />
          <el-table-column prop="end_pin" label="终点针脚" width="100" />
          <el-table-column prop="end_content" label="终点内容" min-width="160" />
          <el-table-column prop="signal_type" label="信号性质" width="100" />
          <el-table-column prop="remark" label="备注" min-width="120" />
        </el-table>

        <h4>转换结果预览</h4>
        <el-table :data="sheet.converted_preview_rows || []" border size="small" empty-text="暂无转换结果预览">
          <el-table-column prop="net" label="Net 编号" width="120" />
          <el-table-column prop="sub" label="Sub 编号" width="120" />
          <el-table-column prop="start" label="起点" min-width="160" />
          <el-table-column prop="end" label="终点" min-width="160" />
          <el-table-column prop="remark" label="备注" min-width="120" />
        </el-table>
      </el-card>

      <el-card class="section-card">
        <template #header>
          <h3>提示信息</h3>
        </template>

        <el-alert
          v-for="warning in warnings"
          :key="warning"
          class="message-alert"
          :title="warning"
          type="warning"
          show-icon
          :closable="false"
        />
        <el-alert
          v-for="error in errors"
          :key="error"
          class="message-alert"
          :title="error"
          type="error"
          show-icon
          :closable="false"
        />
        <el-empty v-if="warnings.length === 0 && errors.length === 0" description="暂无警告或错误" />
      </el-card>

      <div class="actions">
        <el-button :disabled="loading" @click="goUpload">返回重新上传</el-button>
        <el-button type="primary" :loading="loading" @click="handleConfirmConvert">确认转换</el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { convertFile } from '../api/fileApi'

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const uploadResult = ref(readUploadResult())

const sheets = computed(() => uploadResult.value?.sheets || [])
const warnings = computed(() => uploadResult.value?.warnings || [])
const errors = computed(() => uploadResult.value?.errors || [])

const fieldLabels = {
  start_connector: '起点插件',
  start_pin: '起点针脚',
  start_content: '起点内容',
  end_connector: '终点插件',
  end_pin: '终点针脚',
  end_content: '终点内容',
  signal_type: '信号性质',
  remark: '备注',
}

function readUploadResult() {
  const raw = sessionStorage.getItem('upload_result')
  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function matchedColumnRows(matchedColumns = {}) {
  return Object.entries(matchedColumns).map(([field, column]) => ({
    field: fieldLabels[field] || field,
    column,
  }))
}

function goUpload() {
  router.push('/upload')
}

async function handleConfirmConvert() {
  if (!uploadResult.value?.file_id) {
    errorMessage.value = '缺少 file_id，无法确认转换'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await convertFile(uploadResult.value.file_id)
    sessionStorage.setItem('convert_result', JSON.stringify(response.data))
    router.push('/result')
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '转换失败，请检查后端服务是否正常运行'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.preview-page {
  width: 100%;
}

.section-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h2,
.section-card h3,
.section-card h4 {
  margin: 0;
}

.sheet-info,
.section-card h4 {
  margin-bottom: 12px;
}

.section-card h4 {
  margin-top: 20px;
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
