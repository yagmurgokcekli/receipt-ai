from typing import List

from src.utils.money_utils import parse_total_and_currency
from src.utils.date_utils import parse_date


def normalize_di_receipt(raw: dict) -> dict:
    """
    Normalize Document Intelligence receipt output
    into canonical receipt schema.
    """

    merchant = raw.get("merchant")
    total_raw = raw.get("total")
    date_raw = raw.get("transaction_date")
    items_raw = raw.get("items")

    # normalize money
    total_value, currency = parse_total_and_currency(total_raw)

    # normalize date
    normalized_date = parse_date(date_raw) or date_raw

    items: List[dict] = []

    if items_raw:
        for item in items_raw:
            items.append(
                {
                    "name": item.get("description"),
                    "quantity": item.get("quantity"),
                    "price": item.get("total_price"),
                }
            )

    return {
        "merchant": merchant,
        "total": total_value,
        "currency": currency,
        "transaction_date": normalized_date,
        "items": items or None,
        "engine": "di",
        "raw": raw,
    }
