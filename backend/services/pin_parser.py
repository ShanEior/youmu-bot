import re


PIN_SPLIT_PATTERN = re.compile(r"[,，]")
WHITESPACE_PATTERN = re.compile(r"\s+")
NUMERIC_RANGE_PATTERN = re.compile(r"^(\d+)(?:-|~|～|至)(\d+)$")
NOTE_KEYWORDS = ("一分", "点一分", "一一对应", "点一一对应")


def parse_pins(value):
    if value is None:
        return []

    text = str(value).strip()
    if not text:
        return []

    if any(keyword in text for keyword in NOTE_KEYWORDS):
        return []

    pins = []
    for part in PIN_SPLIT_PATTERN.split(text):
        cleaned = WHITESPACE_PATTERN.sub("", part)
        if not cleaned:
            continue

        pins.extend(expand_pin_token(cleaned))

    return pins


def expand_pin_token(token):
    matched = NUMERIC_RANGE_PATTERN.fullmatch(token)
    if not matched:
        return [token]

    start = int(matched.group(1))
    end = int(matched.group(2))
    if start > end:
        return [token]

    return [str(number) for number in range(start, end + 1)]
