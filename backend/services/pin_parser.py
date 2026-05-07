import re


PIN_SPLIT_PATTERN = re.compile(r"[,，]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def parse_pins(value):
    if value is None:
        return []

    text = str(value).strip()
    if not text:
        return []

    return [
        cleaned
        for cleaned in (WHITESPACE_PATTERN.sub("", part) for part in PIN_SPLIT_PATTERN.split(text))
        if cleaned
    ]
