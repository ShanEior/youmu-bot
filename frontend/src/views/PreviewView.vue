<template>
  <div class="preview-page">
    <el-card v-if="!uploadResult" class="section-card" shadow="never">
      <el-empty description="暂无解析结果，请先上传文件">
        <el-button type="primary" @click="goUpload">返回上传页</el-button>
      </el-empty>
    </el-card>

    <template v-else>
      <el-card class="section-card" shadow="never">
        <template #header>
          <div class="card-header top-header">
            <div>
              <h2>解析预览</h2>
              <p class="card-description">默认展示转换结果预览，需要排查字段识别时可切换到详细模式。</p>
            </div>
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="simple">精简</el-radio-button>
              <el-radio-button label="detailed">详细</el-radio-button>
            </el-radio-group>
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

        <template v-if="viewMode === 'simple'">
          <div class="summary-grid">
            <div class="summary-item">
              <span class="summary-label">文件名</span>
              <strong class="summary-value">{{ uploadResult.filename }}</strong>
            </div>
            <div class="summary-item small">
              <span class="summary-label">有效 Sheet</span>
              <strong class="summary-value">{{ validSheetCount }}</strong>
            </div>
            <div class="summary-item small">
              <span class="summary-label">警告数量</span>
              <strong class="summary-value">{{ warningCount }}</strong>
            </div>
          </div>

          <div class="sheet-switcher">
            <span class="switcher-label">当前 Sheet</span>
            <el-select
              v-model="currentSheetName"
              class="sheet-select"
              placeholder="请选择 Sheet"
              :disabled="validSheets.length === 0"
            >
              <el-option
                v-for="sheet in validSheets"
                :key="sheet.sheet_name"
                :label="sheet.sheet_name"
                :value="sheet.sheet_name"
              />
            </el-select>
          </div>

          <div v-if="currentSheet" class="sheet-preview">
            <div class="sheet-preview-header">
              <div>
                <h3>{{ currentSheet.sheet_name }}</h3>
                <p>仅展示转换后的预览结果，方便快速核对导出内容。</p>
              </div>
            </div>

            <el-table
              :data="currentSheet.converted_preview_rows || []"
              border
              height="420"
              empty-text="当前 Sheet 暂无转换结果预览"
            >
              <el-table-column prop="net" label="Net" width="120" />
              <el-table-column prop="sub" label="Sub" width="120" />
              <el-table-column prop="start" label="Start" min-width="220" />
              <el-table-column prop="end" label="End" min-width="220" />
              <el-table-column prop="remark" label="Remark" min-width="160" />
            </el-table>
          </div>

          <el-empty
            v-else
            class="sheet-empty"
            description="暂无可预览的有效 Sheet，请切换到详细模式查看解析信息"
          />

          <el-alert
            v-if="warningCount > 0"
            class="inline-tip"
            :title="`当前共有 ${warningCount} 条警告，可切换到详细模式查看全部内容。`"
            type="warning"
            show-icon
            :closable="false"
          />
        </template>

        <template v-else>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="文件名">{{ uploadResult.filename }}</el-descriptions-item>
            <el-descriptions-item label="file_id">{{ uploadResult.file_id }}</el-descriptions-item>
          </el-descriptions>
        </template>
      </el-card>

      <template v-if="viewMode === 'detailed'">
        <el-card v-for="sheet in sheets" :key="sheet.sheet_name" class="section-card" shadow="never">
          <template #header>
            <div class="card-header">
              <h3>{{ sheet.sheet_name }}</h3>
              <el-tag :type="sheet.valid ? 'success' : 'info'">{{ sheet.valid ? '有效' : '未识别' }}</el-tag>
            </div>
          </template>

          <el-descriptions class="sheet-info" :column="2" border>
            <el-descriptions-item label="表头行">{{ sheet.header_row }}</el-descriptions-item>
            <el-descriptions-item label="行数">{{ sheet.row_count }}</el-descriptions-item>
          </el-descriptions>

          <div class="detail-section">
            <h4>字段识别结果</h4>
            <el-table
              :data="matchedColumnRows(sheet.matched_columns)"
              border
              size="small"
              empty-text="暂无字段识别结果"
            >
              <el-table-column prop="field" label="字段" />
              <el-table-column prop="column" label="列" width="120" />
            </el-table>
          </div>

          <div class="detail-section">
            <h4>原始数据预览</h4>
            <el-table
              :data="sheet.source_preview_rows || []"
              border
              size="small"
              height="320"
              empty-text="暂无原始数据预览"
            >
              <el-table-column prop="start_connector" label="起点插件" min-width="160" />
              <el-table-column prop="start_pin" label="起点针脚" width="100" />
              <el-table-column prop="start_content" label="起点内容" min-width="160" />
              <el-table-column prop="end_connector" label="终点插件" min-width="160" />
              <el-table-column prop="end_pin" label="终点针脚" width="100" />
              <el-table-column prop="end_content" label="终点内容" min-width="160" />
              <el-table-column prop="signal_type" label="信号性质" width="100" />
              <el-table-column prop="remark" label="备注" min-width="120" />
            </el-table>
          </div>

          <div class="detail-section">
            <h4>转换结果预览</h4>
            <el-table
              :data="sheet.converted_preview_rows || []"
              border
              size="small"
              height="320"
              empty-text="暂无转换结果预览"
            >
              <el-table-column prop="net" label="Net" width="120" />
              <el-table-column prop="sub" label="Sub" width="120" />
              <el-table-column prop="start" label="Start" min-width="180" />
              <el-table-column prop="end" label="End" min-width="180" />
              <el-table-column prop="remark" label="Remark" min-width="140" />
            </el-table>
          </div>
        </el-card>

        <el-card class="section-card" shadow="never">
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
      </template>

      <div class="actions">
        <el-button size="large" :disabled="loading" @click="goUpload">返回重新上传</el-button>
        <el-button type="primary" size="large" :loading="loading" @click="handleConfirmConvert">确认转换</el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { convertFile } from '../api/fileApi'

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const uploadResult = ref(readUploadResult())
const viewMode = ref('simple')

const sheets = computed(() => uploadResult.value?.sheets || [])
const warnings = computed(() => uploadResult.value?.warnings || [])
const errors = computed(() => uploadResult.value?.errors || [])
const validSheets = computed(() => sheets.value.filter((sheet) => sheet.valid))
const validSheetCount = computed(() => validSheets.value.length)
const warningCount = computed(() => warnings.value.length)
const currentSheetName = ref(validSheets.value[0]?.sheet_name || '')

const currentSheet = computed(() => {
  if (!currentSheetName.value) {
    return validSheets.value[0] || null
  }

  return validSheets.value.find((sheet) => sheet.sheet_name === currentSheetName.value) || validSheets.value[0] || null
})

watch(
  validSheets,
  (nextSheets) => {
    if (!nextSheets.length) {
      currentSheetName.value = ''
      return
    }

    if (!nextSheets.some((sheet) => sheet.sheet_name === currentSheetName.value)) {
      currentSheetName.value = nextSheets[0].sheet_name
    }
  },
  { immediate: true },
)

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
  margin-bottom: 20px;
  border: none;
  border-radius: 18px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.top-header {
  flex-wrap: wrap;
}

.card-header h2,
.card-header h3,
.detail-section h4 {
  margin: 0;
}

.card-description {
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.message-alert {
  margin-bottom: 12px;
}

.summary-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) repeat(2, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 20px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #ebeef5;
}

.summary-item.small {
  justify-content: center;
}

.summary-label,
.switcher-label {
  font-size: 13px;
  color: #909399;
}

.summary-value {
  font-size: 18px;
  line-height: 1.5;
  color: #303133;
  word-break: break-all;
}

.sheet-switcher {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.sheet-select {
  width: 320px;
  max-width: 100%;
}

.sheet-preview {
  padding: 20px;
  border-radius: 16px;
  border: 1px solid #ebeef5;
  background: #ffffff;
}

.sheet-preview-header {
  margin-bottom: 16px;
}

.sheet-preview-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.sheet-preview-header p {
  margin: 8px 0 0;
  font-size: 14px;
  color: #606266;
}

.sheet-empty,
.inline-tip {
  margin-top: 20px;
}

.sheet-info {
  margin-bottom: 16px;
}

.detail-section + .detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin-bottom: 12px;
  font-size: 16px;
  color: #303133;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 28px;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .sheet-switcher {
    flex-direction: column;
    align-items: flex-start;
  }

  .sheet-select {
    width: 100%;
  }
}
</style>
