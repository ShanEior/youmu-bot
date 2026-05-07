# 后端服务

本目录用于存放线缆点位测试表转换软件的 Flask 后端代码。

## 当前状态

当前仅完成基础结构初始化，并提供健康检查接口：

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

## 启动方式

```bash
cd backend
pip install -r requirements.txt
python app.py
```

服务默认运行在 `http://localhost:5000`。

## 说明

Excel 解析、字段识别、转换和导出逻辑尚未实现，相关文件目前仅作为后续开发占位。
