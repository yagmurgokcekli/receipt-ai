from typing import Optional
from datetime import datetime

DATE_FORMATS = [
    ("%m/%d/%Y %H:%M", True),  
    ("%m/%d/%Y", False),
    ("%d.%m.%Y", False),
    ("%Y-%m-%d", False),
]


from datetime import datetime, date
from typing import Optional


def parse_date(value: Optional[str]) -> Optional[date]:
    """
    Parse a date string into a date object.

    Returns:
    - date if parsing succeeds
    - None if parsing fails
    """
    if not value or not isinstance(value, str):
        return None

    text = value.strip()

    for fmt, has_time in DATE_FORMATS:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.date()
        except ValueError:
            continue

    return None
