from openpyxl.utils import get_column_letter

DIRECTION_KEYWORDS = {
    "start": ("起点", "采集", "start", "输入"),
    "end": ("终点", "产品", "end", "输出"),
}

FIELD_KEYWORDS = {
    "connector": ("插件", "连接器", "connector"),
    "pin": ("针", "引脚", "位", "pin"),
    "content": ("内容", "信号", "说明"),
}

SIGNAL_KEYWORDS = ("信号性质", "信号规格", "线径", "规格")
REMARK_KEYWORDS = ("备注", "说明", "特殊")
REQUIRED_FIELDS = ("start_connector", "start_pin", "end_connector", "end_pin")
ALL_FIELDS = (
    "start_connector",
    "start_pin",
    "end_connector",
    "end_pin",
    "start_content",
    "end_content",
    "signal_type",
    "remark",
)


def detect_columns(rows):
    best = None

    for index, row in enumerate(rows):
        matched = detect_row_columns(row)
        score = sum(1 for field in ALL_FIELDS if field in matched)
        required_score = sum(1 for field in REQUIRED_FIELDS if field in matched)

        if required_score == 0:
            continue

        candidate = {
            "header_row": index + 1,
            "matched_columns": matched,
            "score": score,
            "required_score": required_score,
        }

        if not best or (required_score, score) > (best["required_score"], best["score"]):
            best = candidate

    if not best:
        return {
            "valid": False,
            "header_row": None,
            "matched_columns": {},
        }

    return {
        "valid": all(field in best["matched_columns"] for field in REQUIRED_FIELDS),
        "header_row": best["header_row"],
        "matched_columns": best["matched_columns"],
    }


def detect_row_columns(row):
    matched = {}

    for column_index, value in enumerate(row):
        text = normalize_text(value)
        if not text:
            continue

        side = detect_side(text)
        field_type = detect_field_type(text)

        if side and field_type:
            field = f"{side}_{field_type}"
            matched.setdefault(field, get_column_letter(column_index + 1))
            continue

        if any(keyword in text for keyword in SIGNAL_KEYWORDS):
            matched.setdefault("signal_type", get_column_letter(column_index + 1))
            continue

        if any(keyword in text for keyword in REMARK_KEYWORDS):
            matched.setdefault("remark", get_column_letter(column_index + 1))

    return matched


def detect_side(text):
    for side, keywords in DIRECTION_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return side
    return None


def detect_field_type(text):
    for field_type, keywords in FIELD_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return field_type
    return None


def normalize_text(value):
    return str(value or "").strip().replace(" ", "").replace("\n", "").lower()
