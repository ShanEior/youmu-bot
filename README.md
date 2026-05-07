# 线缆点位测试表转换软件

本项目用于将人工线缆接线 Excel 表转换为测试仪可识别的标准编程表。MVP 目标是支持 Excel 上传、解析、字段识别、转换预览、结果导出和下载。

当前阶段只完成项目结构初始化，暂未实现具体 Excel 解析、转换和导出业务逻辑。

## 技术栈

- 后端：Python + Flask + pandas + openpyxl
- 前端：Vue 3 + Element Plus
- 文档与原型：Markdown + Pencil 原型文件

## 目录结构

```text
.
├── README.md
├── spec.md
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── README.md
│   ├── uploads/
│   ├── outputs/
│   └── services/
│       ├── __init__.py
│       ├── excel_reader.py
│       ├── merged_cell_handler.py
│       ├── column_detector.py
│       ├── connector_normalizer.py
│       ├── pin_parser.py
│       ├── cable_converter.py
│       └── excel_writer.py
├── frontend/
└── docs/
    ├── DEV_LOG.md
    ├── TODO.md
    └── prototype/
```

## 启动方式

### 后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

健康检查接口：

```http
GET /api/health
```

返回：

```json
{
  "status": "ok",
  "message": "backend is running"
}
```

### 前端

前端项目尚未初始化，后续将基于 Vue 3 和 Element Plus 创建。
