# 开发日志

## 当前完成内容

- 已阅读 `spec.md`，确认当前阶段仅做项目结构初始化。
- 已创建基础目录：`backend/`、`backend/services/`、`backend/uploads/`、`backend/outputs/`、`frontend/`、`docs/`、`docs/prototype/`。
- 已创建后端基础文件和服务占位文件。
- 已实现后端健康检查接口 `GET /api/health`。
- 已创建根目录 `README.md` 和后端 `README.md`。
- 已完成后端 API 骨架：
  - `GET /api/health`
  - `POST /api/files/upload`
  - `POST /api/files/convert`
  - `GET /api/files/download/<output_file_id>`
- 已接入 Flask-CORS，允许前端跨域访问。
- 已实现上传文件基础校验、文件名安全处理和保存到 `backend/uploads/`。
- 已完成前端 Vue 3 + Vite 项目初始化。
- 已声明前端依赖：`vue`、`vite`、`element-plus`、`axios`、`vue-router`。
- 已配置基础路由：`/upload`、`/preview`、`/result`，根路径 `/` 重定向到 `/upload`。
- 已创建上传、解析预览、转换完成三个页面占位。
- 已创建 `frontend/src/api/fileApi.js`，封装后端接口方法占位。
- 已完成上传页面 UI，支持选择或拖拽 `.xlsx` / `.xls` 文件。
- 已完成上传页面与后端 `POST /api/files/upload` mock 接口联调。
- 上传成功后会将后端 mock 解析结果保存到 `sessionStorage.upload_result` 并跳转 `/preview`。
- 已完成解析预览页面，支持展示 `upload_result` 中的文件名、Sheet 信息、字段识别结果、原始预览、转换预览、warnings 和 errors。
- 已接入后端 `POST /api/files/convert` mock 接口，确认转换后保存 `sessionStorage.convert_result` 并跳转 `/result`。
- 已添加 `.gitignore`，忽略 `node_modules/`、构建产物、Python 缓存和上传/输出目录内容，并通过 `.gitkeep` 保留目录。

## 下一步计划

- 实现转换完成页面和下载占位逻辑。
- 设计后端 Excel 读取、合并单元格处理、字段识别、连接器标准化、针脚拆分、转换和导出模块。
- 补充前后端接口联调。
- 根据样例文件验证解析与转换结果。

## 注意事项

- 当前仍是 mock 阶段，不实现真实 Excel 解析、转换、导出业务逻辑。
- 上传页面当前使用后端 mock 解析结果。
- 解析预览页面当前展示的是 `sessionStorage.upload_result` 中的 mock 数据。
- `POST /api/files/upload` 返回的是 mock 解析结果。
- `POST /api/files/convert` 返回的是 mock 转换结果。
- `GET /api/files/download/<output_file_id>` 暂不生成真实 Excel，仅返回 JSON 提示。
- `backend/services/` 下文件均为占位文件，仅用于后续开发承接。
