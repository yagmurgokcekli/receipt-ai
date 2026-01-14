from typing import Optional
from datetime import datetime

DATE_FORMATS = [
    ("%m/%d/%Y %H:%M", True),  # time included
    ("%m/%d/%Y", False),
    ("%d.%m.%Y", False),
    ("%Y-%m-%d", False),
]


def parse_date(value: Optional[str]) -> Optional[str]:
    """
    Normalize date into ISO format.

    - Returns YYYY-MM-DD if time is not explicitly present
    - Returns YYYY-MM-DDTHH:MM:SS if time is explicitly present
    """
    if not value or not isinstance(value, str):
        return None

    text = value.strip()

    for fmt, has_time in DATE_FORMATS:
        try:
            dt = datetime.strptime(text, fmt)
            if has_time:
                return dt.isoformat()
            return dt.date().isoformat()
        except ValueError:
            continue

    return None
