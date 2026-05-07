import re


PAREN_PATTERN = re.compile(r"[（(].*?[）)]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_connector(value):
    if value is None:
        return ""

    text = str(value)
    text = PAREN_PATTERN.sub("", text)
    text = text.replace("-", "_")
    text = WHITESPACE_PATTERN.sub("", text)
    return text
