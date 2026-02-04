from typing import Optional

CURRENCY_SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "₺": "TRY",
}


def resolve_currency_from_text(text: str) -> Optional[str]:
    """
    Resolve ISO currency code from visible currency symbols in text.
    """
    if not text:
        return None

    for symbol, code in CURRENCY_SYMBOL_MAP.items():
        if symbol in text:
            return code

    return None
