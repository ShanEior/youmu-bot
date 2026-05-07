import re


PAREN_PATTERN = re.compile(r"[（(].*?[）)]")
WHITESPACE_PATTERN = re.compile(r"\s+")
NOTE_TEXT_PATTERN = re.compile(r"的\d+点一分|一分[二三四]?|点一分|一一对应|点一一对应")
CONNECTOR_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def normalize_connector(value):
    if value is None:
        return ""

    text = str(value)
    text = PAREN_PATTERN.sub("", text)
    text = text.replace("-", "_")
    text = WHITESPACE_PATTERN.sub("", text)

    if not text:
        return ""

    if NOTE_TEXT_PATTERN.search(text) and not CONNECTOR_PATTERN.fullmatch(text):
        return ""

    return text
