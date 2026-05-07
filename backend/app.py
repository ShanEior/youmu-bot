from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}

app = Flask(__name__)
CORS(app)

uploaded_files = {}
converted_files = {}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_file_id(filename):
    suffix = Path(filename).suffix.lower()
    return f"file_{uuid4().hex}{suffix}"


def build_output_filename(filename):
    path = Path(filename)
    return f"{path.stem}编程表.xlsx"


@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "ok",
        "message": "backend is running",
    })


@app.post("/api/files/upload")
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "未上传文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "未选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "仅支持 .xlsx 或 .xls 文件"}), 400

    original_filename = file.filename
    safe_filename = secure_filename(original_filename)
    file_id = generate_file_id(safe_filename)
    saved_filename = f"{Path(file_id).stem}_{safe_filename}"
    save_path = UPLOAD_DIR / saved_filename
    file.save(save_path)

    uploaded_files[file_id] = {
        "filename": original_filename,
        "saved_filename": saved_filename,
        "path": str(save_path),
    }

    return jsonify({
        "file_id": file_id,
        "filename": original_filename,
        "sheets": [
            {
                "sheet_name": "Sheet1",
                "header_row": 5,
                "row_count": 3,
                "matched_columns": {
                    "start_connector": "A",
                    "start_pin": "B",
                    "start_content": "C",
                    "end_connector": "D",
                    "end_pin": "E",
                    "end_content": "F",
                    "signal_type": "G",
                    "remark": "H",
                },
                "source_preview_rows": [
                    {
                        "start_connector": "PW01-X40(J30J-74TJSL7)",
                        "start_pin": "45,63",
                        "start_content": "电推控制器电源开指令",
                        "end_connector": "PK09-X01(J30J-51ZKSL7)",
                        "end_pin": "1,2",
                        "end_content": "控制器电源开指令",
                        "signal_type": "26#",
                        "remark": "mock 数据",
                    }
                ],
                "converted_preview_rows": [
                    {
                        "net": "Net1",
                        "sub": "*Sub 1",
                        "connection": "PW01_X40:45::PK09_X01:1",
                    }
                ],
            }
        ],
        "warnings": ["当前为 mock 解析结果，尚未执行真实 Excel 解析"],
        "errors": [],
    })


@app.post("/api/files/convert")
def convert_file():
    data = request.get_json(silent=True) or {}
    file_id = data.get("file_id")

    if not file_id:
        return jsonify({"error": "缺少 file_id"}), 400

    if file_id not in uploaded_files:
        return jsonify({"error": "file_id 不存在"}), 404

    filename = uploaded_files[file_id]["filename"]
    output_file_id = f"output_{uuid4().hex}"
    output_filename = build_output_filename(filename)

    converted_files[output_file_id] = {
        "file_id": file_id,
        "output_filename": output_filename,
    }

    return jsonify({
        "success": True,
        "output_file_id": output_file_id,
        "output_filename": output_filename,
        "message": "当前为 mock 转换结果，尚未执行真实 Excel 转换",
    })


@app.get("/api/files/download/<output_file_id>")
def download_file(output_file_id):
    if output_file_id not in converted_files:
        return jsonify({"error": "output_file_id 不存在"}), 404

    return jsonify({
        "output_file_id": output_file_id,
        "output_filename": converted_files[output_file_id]["output_filename"],
        "message": "下载功能待实现，当前未生成真实 Excel 文件",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
