from pathlib import Path

from openpyxl import load_workbook

from .merged_cell_handler import fill_merged_cells


class ExcelReadError(Exception):
    pass


def read_workbook(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".xls":
        raise ExcelReadError("当前 MVP 暂不支持 .xls，请转换为 .xlsx 后上传")

    if suffix != ".xlsx":
        raise ExcelReadError(f"不支持的 Excel 文件格式: {suffix or 'unknown'}")

    workbook = load_workbook(path, data_only=True, read_only=False)
    sheets = []

    for worksheet in workbook.worksheets:
        data = read_sheet_data(worksheet)
        sheets.append({
            "sheet_name": worksheet.title,
            "data": data,
        })

    workbook.close()
    return sheets


def read_sheet_data(worksheet):
    filled_values = fill_merged_cells(worksheet)
    rows = []

    for row in worksheet.iter_rows():
        row_values = []
        for cell in row:
            value = filled_values.get((cell.row, cell.column), cell.value)
            row_values.append(format_cell_value(value))
        rows.append(trim_empty_tail(row_values))

    return trim_empty_rows(rows)


def format_cell_value(value):
    if value is None:
        return ""

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    return str(value).strip()


def trim_empty_tail(row):
    values = list(row)
    while values and values[-1] == "":
        values.pop()
    return values


def trim_empty_rows(rows):
    values = list(rows)
    while values and not any(values[-1]):
        values.pop()
    return values
