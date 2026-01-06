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

    Examples
    --------
    "$ 12.50"      -> (12.50, "USD")
    "14,99 TL"     -> (14.99, "TRY")
    "EUR 1 203,39" -> (1203.39, "EUR")
    "$2,516.28"    -> (2516.28, "USD")
    """
    if not text or not isinstance(text, str):
        return None, None

    raw = text.strip()
    currency = None

    # symbol prefix
    if raw[0] in CURRENCY_SYMBOL_MAP:
        currency = CURRENCY_SYMBOL_MAP[raw[0]]
        raw = raw[1:].strip()

    # text prefix
    for key, code in TEXT_CURRENCY_MAP.items():
        if raw.upper().startswith(key + " "):
            currency = code
            raw = raw[len(key) :].strip()
            break

    # normalize spaces
    raw = raw.replace(" ", "")

    # normalize commas and dots
    if "," in raw and "." in raw:
        raw = raw.replace(",", "")

    # comma-only decimal
    elif "," in raw and "." not in raw:
        raw = raw.replace(",", ".")

    # final parse
    try:
        value = float(raw)
    except ValueError:
        return None, currency

    return value, currency
