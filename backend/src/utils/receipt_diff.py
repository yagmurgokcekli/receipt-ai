import re
from typing import Optional, Tuple, Dict, List
from collections import defaultdict

from src.schemas.receipt import ReceiptItem
from src.schemas.receipt import ReceiptSchema
from src.schemas.receipt_compare_response import (
    ItemDiff,
    ReceiptDiffReport,
    FieldDiff,
)


def normalize_item_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    # collapse whitespace into single spaces
    text = re.sub(r"\s+", " ", name).strip()
    return text.casefold()


def normalize_number(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    # round to 2 decimal places
    return round(float(x), 2)


def item_key(
    item: ReceiptItem,
) -> Tuple[Optional[str], Optional[float], Optional[float]]:
    return (
        normalize_item_name(item.name),
        normalize_number(item.quantity),
        normalize_number(item.price),
    )


def build_diff(di: ReceiptSchema, openai: ReceiptSchema) -> ReceiptDiffReport:
    """
    Build a strict, deterministic diff between Document Intelligence and OpenAI
    receipt extraction results.

    Top-level fields are compared by direct equality.
    Line items are matched using a strict key (normalized name, quantity, price)
    without semantic or fuzzy inference.
    """

    def eq(a, b) -> bool:
        return a == b

    fields = [
        FieldDiff(
            field="merchant",
            di=di.merchant,
            openai=openai.merchant,
            match=eq(di.merchant, openai.merchant),
        ),
        FieldDiff(
            field="total",
            di=di.total,
            openai=openai.total,
            match=eq(di.total, openai.total),
        ),
        FieldDiff(
            field="currency",
            di=di.currency,
            openai=openai.currency,
            match=eq(di.currency, openai.currency),
        ),
        FieldDiff(
            field="transaction_date",
            di=di.transaction_date,
            openai=openai.transaction_date,
            match=eq(di.transaction_date, openai.transaction_date),
        ),
    ]

    di_items = di.items or []
    oai_items = openai.items or []

    # index items by key
    di_index: Dict[tuple, List[ReceiptItem]] = defaultdict(list)
    for it in di_items:
        di_index[item_key(it)].append(it)

    oai_index: Dict[tuple, List[ReceiptItem]] = defaultdict(list)
    for it in oai_items:
        oai_index[item_key(it)].append(it)

    all_keys = set(di_index.keys()) | set(oai_index.keys())

    item_diffs: List[ItemDiff] = []
    matched = changed = missing_di = missing_openai = 0

    for k in sorted(all_keys, key=lambda x: (x[0] or "", x[1] or 0, x[2] or 0)):
        di_list = di_index.get(k, [])
        oai_list = oai_index.get(k, [])

        # consume pairs for duplicates
        while di_list or oai_list:
            di_item = di_list.pop() if di_list else None
            oai_item = oai_list.pop() if oai_list else None

            if di_item and oai_item:
                # both present -> matched
                matched += 1
                item_diffs.append(
                    ItemDiff(
                        key=str(k),
                        di_item=di_item,
                        openai_item=oai_item,
                        status="matched",
                    )
                )
            elif di_item and not oai_item:
                missing_openai += 1
                item_diffs.append(
                    ItemDiff(
                        key=str(k),
                        di_item=di_item,
                        openai_item=None,
                        status="missing_in_openai",
                    )
                )
            elif oai_item and not di_item:
                missing_di += 1
                item_diffs.append(
                    ItemDiff(
                        key=str(k),
                        di_item=None,
                        openai_item=oai_item,
                        status="missing_in_di",
                    )
                )

    # summary string
    mismatches = [f.field for f in fields if not f.match]
    summary_parts = []
    if mismatches:
        summary_parts.append(f"Field mismatches: {', '.join(mismatches)}")
    else:
        summary_parts.append("Top-level fields match.")

    summary_parts.append(
        f"Items: matched={matched}, missing_in_di={missing_di}, missing_in_openai={missing_openai}"
    )

    return ReceiptDiffReport(
        fields=fields,
        items=item_diffs,
        matched_count=matched,
        changed_count=changed,
        missing_in_di_count=missing_di,
        missing_in_openai_count=missing_openai,
        summary=" | ".join(summary_parts),
    )
