from .connector_normalizer import normalize_connector
from .pin_parser import parse_pins


NOTE_KEYWORDS = ("一一对应", "点一一对应")


def build_preview_rows(source_rows, matched_columns, limit=20):
    preview_rows, warnings = build_rows(source_rows, matched_columns, limit=limit)
    return preview_rows, warnings


def build_all_rows(source_rows, matched_columns, warnings=None):
    all_rows, collected_warnings = build_rows(source_rows, matched_columns)
    if warnings is not None:
        warnings.extend(collected_warnings)
    return all_rows


def build_rows(source_rows, matched_columns, limit=None):
    preview_rows = []
    warnings = []
    row_number = 1

    for index, source_row in enumerate(source_rows, start=1):
        if is_footer_or_note_row(source_row):
            continue

        start_connector = normalize_connector(source_row.get("start_connector"))
        end_connector = normalize_connector(source_row.get("end_connector"))
        start_pins = parse_pins(source_row.get("start_pin"))
        end_pins = parse_pins(source_row.get("end_pin"))
        remark = source_row.get("remark", "")

        if not start_connector or not end_connector:
            warnings.append(f"第 {index} 条预览数据缺少标准化后的起点或终点连接器，已跳过")
            continue

        if not start_pins or not end_pins:
            warnings.append(f"第 {index} 条预览数据缺少可配对的起点或终点针脚，已跳过")
            continue

        pair_count = min(len(start_pins), len(end_pins))
        if len(start_pins) != len(end_pins):
            warnings.append(f"第 {index} 条预览数据起点/终点针脚数量不一致，已按较短数量生成")

        for pair_index in range(pair_count):
            preview_rows.append({
                "net": f"Net{row_number}",
                "sub": f"*Sub {row_number}",
                "start": format_endpoint(start_connector, start_pins[pair_index]),
                "end": format_endpoint(end_connector, end_pins[pair_index]),
                "remark": remark,
            })
            row_number += 1

            if limit is not None and len(preview_rows) >= limit:
                return preview_rows, warnings

    return preview_rows, warnings


def is_footer_or_note_row(row):
    start_connector = normalize_connector(row.get("start_connector"))
    end_connector = normalize_connector(row.get("end_connector"))
    if start_connector or end_connector:
        return False

    texts = []
    for value in row.values():
        text = str(value or "").strip()
        if text:
            texts.append(text)

    return any(keyword in text for text in texts for keyword in NOTE_KEYWORDS)


def format_endpoint(connector, pin):
    return f"{connector}:{pin}"
