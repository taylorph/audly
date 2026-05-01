import re


ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def clean_message(message: str) -> str:
    if not message:
        return ""

    text = ANSI_PATTERN.sub("", str(message))
    text = text.replace("ERROR: ", "")
    text = text.replace("[0m", "")
    text = text.replace("[download] Got error:", "Download error:")
    text = text.replace("[download]", "Download:")
    text = re.sub(r"\s+", " ", text).strip()
    return text
