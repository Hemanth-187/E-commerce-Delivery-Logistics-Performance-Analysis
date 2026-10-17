"""Analyze order and delivery fields for Member 4 Day 1."""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.load_data import load_csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"

DATA_FILE = "DataCoSupplyChainDataset.csv"

ORDER_FIELDS = [
    "Order Id",
    "Order Item Id",
    "Order Status",
    "order date (DateOrders)",
]

DELIVERY_FIELDS = [
    "shipping date (DateOrders)",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Delivery Status",
    "Late_delivery_risk",
]


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_csv(DATA_FILE, encoding="latin1", low_memory=False)

    fields = ORDER_FIELDS + DELIVERY_FIELDS
    rows = []

    for field in fields:
        if field not in df.columns:
            rows.append({
                "field": field,
                "available": False,
                "data_type": "",
                "missing_count": "",
                "missing_percent": "",
                "unique_values": "",
                "notes": "Field not found in source dataset",
            })
            continue

        series = df[field]
        notes = ""

        if field in ["Order Id", "Order Item Id"]:
            notes = "Repeated order IDs may represent multiple order items."
        elif field in [
            "order date (DateOrders)",
            "shipping date (DateOrders)",
        ]:
            notes = "Date field; parsing and chronological order are checked."
        elif field == "Days for shipping (real)":
            notes = "Actual shipping duration in days; not necessarily end-to-end delivery time."
        elif field == "Days for shipment (scheduled)":
            notes = "Scheduled shipping duration in days."
        elif field == "Late_delivery_risk":
            notes = "Risk indicator; inspect its relationship to Delivery Status separately."

        rows.append({
            "field": field,
            "available": True,
            "data_type": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "missing_percent": round(series.isna().mean() * 100, 2),
            "unique_values": int(series.nunique(dropna=True)),
            "notes": notes,
        })

    inventory = pd.DataFrame(rows)
    inventory.to_csv(
        REPORTS_DIR / "order_delivery_field_inventory.csv",
        index=False,
    )

    lines = [
        "# Order and Delivery Field Analysis",
        "",
        "## Purpose",
        "",
        "Inventory the order and delivery fields available in the source dataset.",
        "This is a profiling report; it does not modify the source data.",
        "",
        "## Dataset overview",
        "",
        f"- Rows: {len(df):,}",
        f"- Columns: {len(df.columns):,}",
        f"- Unique order IDs: {df['Order Id'].nunique(dropna=True):,}"
        if "Order Id" in df.columns else "- Unique order IDs: field unavailable",
        f"- Unique order-item IDs: {df['Order Item Id'].nunique(dropna=True):,}"
        if "Order Item Id" in df.columns else "- Unique order-item IDs: field unavailable",
        "",
        "## Field inventory",
        "",
        "| Field | Available | Data type | Missing | Missing % | Unique values |",
        "|---|---|---|---:|---:|---:|",
    ]

    for row in rows:
        lines.append(
            f"| {row['field']} | {row['available']} | {row['data_type']} "
            f"| {row['missing_count']} | {row['missing_percent']} "
            f"| {row['unique_values']} |"
        )

    if "Order Status" in df.columns:
        status_counts = df["Order Status"].value_counts(dropna=False)
        lines += ["", "## Order status distribution", "", "| Order status | Rows |", "|---|---:|"]
        for status, count in status_counts.items():
            lines.append(f"| {status} | {count:,} |")

    if "Delivery Status" in df.columns:
        delivery_counts = df["Delivery Status"].value_counts(dropna=False)
        lines += ["", "## Delivery status distribution", "", "| Delivery status | Rows |", "|---|---:|"]
        for status, count in delivery_counts.items():
            lines.append(f"| {status} | {count:,} |")

    date_fields = [
        "order date (DateOrders)",
        "shipping date (DateOrders)",
    ]
    date_results = {}

    for field in date_fields:
        if field not in df.columns:
            continue
        parsed = pd.to_datetime(df[field], errors="coerce")
        date_results[field] = parsed
        lines += [
            "",
            f"## {field}",
            "",
            f"- Valid parsed dates: {parsed.notna().sum():,}",
            f"- Unparseable or missing dates: {parsed.isna().sum():,}",
            f"- Earliest date: {parsed.min() if parsed.notna().any() else 'N/A'}",
            f"- Latest date: {parsed.max() if parsed.notna().any() else 'N/A'}",
        ]

    order_field = "order date (DateOrders)"
    shipping_field = "shipping date (DateOrders)"
    if order_field in date_results and shipping_field in date_results:
        order_dates = date_results[order_field]
        shipping_dates = date_results[shipping_field]
        comparable = order_dates.notna() & shipping_dates.notna()
        before_order = comparable & (shipping_dates < order_dates)
        lines += [
            "",
            "## Date consistency check",
            "",
            f"- Rows with both dates parseable: {comparable.sum():,}",
            f"- Shipping dates earlier than order dates: {before_order.sum():,}",
        ]

    lines += [
        "",
        "## Interpretation and limitations",
        "",
        "- Order IDs can repeat because the dataset records order items, not just one row per order.",
        "- Order Item Id is useful for distinguishing individual line items.",
        "- Order status and delivery status are separate fields and should not be treated as interchangeable.",
        "- Actual and scheduled shipping durations are distinct measures.",
        "- The shipping-duration field should not automatically be described as total customer delivery time.",
        "- Date parsing and chronology checks are initial diagnostics, not proof that every record is operationally correct.",
        "- This report describes available fields and does not apply cleaning rules.",
        "",
        "## Output files",
        "",
        "- `reports/order_delivery_field_inventory.csv`",
        "- `reports/order_delivery_field_analysis.md`",
        "",
    ]

    report_path = REPORTS_DIR / "order_delivery_field_analysis.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Rows analyzed: {len(df):,}")
    print(f"Field inventory: {REPORTS_DIR / 'order_delivery_field_inventory.csv'}")
    print(f"Analysis report: {report_path}")


if __name__ == "__main__":
    main()
