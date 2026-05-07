from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS
from openpyxl.utils import column_index_from_string
from werkzeug.utils import secure_filename

from services.cable_converter import build_preview_rows
from services.column_detector import detect_columns
from services.excel_reader import read_workbook

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


def build_parse_result(file_path):
    sheets = []
    warnings = []
    valid_sheet_count = 0

    for sheet in read_workbook(file_path):
        rows = sheet["data"]
        detection = detect_columns(rows)
        matched_columns = detection["matched_columns"]
        header_row = detection["header_row"]
        valid = detection["valid"]
        source_preview_rows = []
        converted_preview_rows = []

        if valid:
            source_preview_rows = build_source_preview_rows(rows, header_row, matched_columns)
            if source_preview_rows:
                valid_sheet_count += 1
                converted_preview_rows, preview_warnings = build_preview_rows(
                    source_preview_rows,
                    matched_columns,
                    limit=20,
                )
                warnings.extend(f"Sheet {sheet['sheet_name']}：{warning}" for warning in preview_warnings)
            else:
                valid = False
                warnings.append(f"Sheet {sheet['sheet_name']} 未识别到有效数据行")
        else:
            warnings.append(f"Sheet {sheet['sheet_name']} 未识别到起点/终点插件和针脚关键字段")

        sheets.append({
            "sheet_name": sheet["sheet_name"],
            "valid": valid,
            "header_row": header_row,
            "row_count": len(source_preview_rows),
            "matched_columns": matched_columns,
            "source_preview_rows": source_preview_rows[:20],
            "converted_preview_rows": converted_preview_rows,
        })

    errors = []
    if valid_sheet_count == 0:
        errors.append("未识别到有效 Sheet")

    return sheets, warnings, errors


def build_source_preview_rows(rows, header_row, matched_columns):
    preview_rows = []
    field_columns = {
        field: column_index_from_string(column_letter) - 1
        for field, column_letter in matched_columns.items()
    }

    for row in rows[header_row:]:
        item = {
            "start_connector": get_row_value(row, field_columns.get("start_connector")),
            "start_pin": get_row_value(row, field_columns.get("start_pin")),
            "start_content": get_row_value(row, field_columns.get("start_content")),
            "end_connector": get_row_value(row, field_columns.get("end_connector")),
            "end_pin": get_row_value(row, field_columns.get("end_pin")),
            "end_content": get_row_value(row, field_columns.get("end_content")),
            "signal_type": get_row_value(row, field_columns.get("signal_type")),
            "remark": get_row_value(row, field_columns.get("remark")),
        }

        if is_valid_source_row(item):
            preview_rows.append(item)

        if len(preview_rows) >= 20:
            break

    return preview_rows


def get_row_value(row, column_index):
    if column_index is None or column_index >= len(row):
        return ""
    return row[column_index]


def is_valid_source_row(row):
    has_connector = bool(row["start_connector"] or row["end_connector"])
    has_pin = bool(row["start_pin"] or row["end_pin"])
    return has_connector and has_pin


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

    try:
        sheets, warnings, errors = build_parse_result(save_path)
    except Exception:
        return jsonify({"error": "Excel 文件读取失败，请检查文件格式是否正确"}), 400

    return jsonify({
        "file_id": file_id,
        "filename": original_filename,
        "sheets": sheets,
        "warnings": warnings,
        "errors": errors,
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
