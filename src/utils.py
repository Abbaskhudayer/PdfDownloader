import re
from urllib.parse import urlparse

def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()

def make_safe_filename(value: str, max_length: int = 120) -> str:
    value = clean_text(value)

    if not value:
        return "untitled"

    value = re.sub(r'[<>:"/\\|?*]', "_", value)
    value = value.strip(" .")

    if len(value) > max_length:
        value = value[:max_length].rstrip()

    return value or "untitled"

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"