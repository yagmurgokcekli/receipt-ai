from typing import Optional
from datetime import datetime

DATE_FORMATS = [
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y",
    "%d.%m.%Y",
    "%Y-%m-%d",
]


def parse_date(value: Optional[str]) -> Optional[str]:
    """
    Normalize date/time into ISO-8601 string.

    Returns None when parsing fails.
    """
    if not value or not isinstance(value, str):
        return None

    text = value.strip()

    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    return None
