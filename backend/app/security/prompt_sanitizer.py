def sanitize(text: str) -> str:
    return text.replace(";", "").replace("--", "")