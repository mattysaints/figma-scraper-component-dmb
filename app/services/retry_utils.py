from typing import Optional


def parse_retry_after(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None

    try:
        seconds = int(value)
        return seconds if seconds >= 0 else None
    except ValueError:
        return None
