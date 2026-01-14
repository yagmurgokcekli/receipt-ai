from typing import List, Optional

from src.schemas.receipt import ReceiptSchema, ReceiptItem
from src.utils.money_utils import parse_total_and_currency, parse_money_value
from src.utils.date_utils import parse_date


def normalize_di_receipt(raw: dict) -> ReceiptSchema:
    """
    Normalize Azure Document Intelligence receipt output
    into the canonical ReceiptSchema.
    """

    merchant: Optional[str] = raw.get("merchant")
    total_raw = raw.get("total")
    date_raw = raw.get("transaction_date")
    items_raw = raw.get("items")

    # money normalization
    total_value, currency = parse_total_and_currency(total_raw)

    # date normalization
    transaction_date = parse_date(date_raw) or date_raw

    items: Optional[List[ReceiptItem]] = None

    if items_raw:
        normalized_items: List[ReceiptItem] = []

        for item in items_raw:
            price = parse_money_value(item.get("total_price"))
            normalized_items.append(
                ReceiptItem(
                    name=item.get("description"),
                    quantity=item.get("quantity"),
                    price=price,
                )
            )

        items = normalized_items or None

    return ReceiptSchema(
        merchant=merchant,
        total=total_value,
        currency=currency,
        transaction_date=transaction_date,
        items=items,
        source="di", 
    )
