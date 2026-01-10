import re
from typing import Optional, Tuple

CURRENCY_SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₺": "TRY",
}

TEXT_CURRENCY_MAP = {
    "TRY": "TRY",
    "TL": "TRY",
    "USD": "USD",
    "EUR": "EUR",
}


def parse_total_and_currency(
    text: Optional[str],
) -> Tuple[Optional[float], Optional[str]]:
    """
    Parse a monetary value into (amount, currency).
    """
    if not text or not isinstance(text, str):
        return None, None

    raw = text.strip()
    if not raw:
        return None, None

    currency = None

    # symbol prefix
    if raw[0] in CURRENCY_SYMBOL_MAP:
        currency = CURRENCY_SYMBOL_MAP[raw[0]]
        raw = raw[1:].strip()

    # text prefix (USD12.50, TL14,99)
    upper = raw.upper()
    for key, code in TEXT_CURRENCY_MAP.items():
        if upper.startswith(key):
            currency = code
            raw = raw[len(key) :].strip()
            break

    # text suffix (12.50 USD, 14,99 TL)
    upper = raw.upper()
    for key, code in TEXT_CURRENCY_MAP.items():
        if upper.endswith(" " + key):
            currency = code
            raw = raw[: -len(key)].strip()
            break

    # normalize spaces
    raw = raw.replace(" ", "")
    if not raw:
        return None, currency

    # normalize commas and dots
    if "," in raw and "." in raw:
        # assume thousand separator
        raw = raw.replace(",", "")
    elif "," in raw and "." not in raw:
        # comma decimal
        raw = raw.replace(",", ".")

    try:
        value = float(raw)
    except ValueError:
        return None, currency

    return value, currency


def parse_money_value(value) -> Optional[float]:
    """
    Parse a money-like value into float.

    This parser assumes US-style formatting when both ',' and '.' are present
    (e.g. '1,203.39'). European formats such as '1.203,39' are not fully supported
    and may require upstream normalization.
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None

        cleaned = re.sub(r"[^\d.,]", "", raw)
        if not cleaned:
            return None

        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(",", "")
        elif "," in cleaned and "." not in cleaned:
            cleaned = cleaned.replace(",", ".")

        try:
            return float(cleaned)
        except ValueError:
            return None

    return None
