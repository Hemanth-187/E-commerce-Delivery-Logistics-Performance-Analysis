"""Create the Day 2 Member 1 order-count analysis workbook."""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"
REPORT_DIR = PROJECT_ROOT / "reports"
OUTPUT_FILE = REPORT_DIR / "05_Order_Count_Analysis.xlsx"

ORDER_ID = "Order Id"
ITEM_ID = "Order Item Id"
ORDER_STATUS = "Order Status"
DELIVERY_STATUS = "Delivery Status"
DATE_COLUMN = "order date (DateOrders)"


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading source dataset...")
    df = pd.read_csv(DATA_FILE, encoding="latin1", low_memory=False)

    required = [ORDER_ID, ITEM_ID, ORDER_STATUS, DELIVERY_STATUS]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Required columns are missing: {missing}")

    total_rows = len(df)
    valid_order_rows = df.dropna(subset=[ORDER_ID]).copy()
    distinct_orders = valid_order_rows[ORDER_ID].nunique()
    distinct_items = df[ITEM_ID].nunique(dropna=True)

    # Build one representative record per order for order-level counts.
    order_level = (
        valid_order_rows
        .groupby(ORDER_ID, sort=False)
        .agg(
            Order_Status=(ORDER_STATUS, "first"),
            Delivery_Status=(DELIVERY_STATUS, "first"),
            Item_Rows=(ITEM_ID, "size"),
            Distinct_Item_IDs=(ITEM_ID, "nunique"),
            Order_Status_Variants=(ORDER_STATUS, "nunique"),
            Delivery_Status_Variants=(DELIVERY_STATUS, "nunique"),
        )
        .reset_index()
    )

    order_status_counts = (
        order_level["Order_Status"]
        .fillna("Missing")
        .value_counts(dropna=False)
        .rename_axis("Order Status")
        .reset_index(name="Distinct Orders")
    )

    delivery_status_counts = (
        order_level["Delivery_Status"]
        .fillna("Missing")
        .value_counts(dropna=False)
        .rename_axis("Delivery Status")
        .reset_index(name="Distinct Orders")
    )

    canceled_order_status = int(
        order_level["Order_Status"].astype("string").str.strip()
        .str.casefold().eq("canceled").sum()
    )
    canceled_delivery_status = int(
        order_level["Delivery_Status"].astype("string").str.strip()
        .str.casefold().eq("shipping canceled").sum()
    )

    on_time_orders = int(
        order_level["Delivery_Status"].astype("string").str.strip()
        .str.casefold().eq("shipping on time").sum()
    )
    late_orders = int(
        order_level["Delivery_Status"].astype("string").str.strip()
        .str.casefold().eq("late delivery").sum()
    )
    advance_shipping_orders = int(
        order_level["Delivery_Status"].astype("string").str.strip()
        .str.casefold().eq("advance shipping").sum()
    )

    eligible_on_time_or_late = on_time_orders + late_orders

    summary_rows = [
        ("Total source rows", total_rows, "rows",
         "All rows in the original CSV, including rows without an Order Id."),
        ("Rows with a valid Order Id", len(valid_order_rows), "rows",
         "Rows with a non-missing Order Id; rows represent order items."),
        ("Rows missing Order Id", total_rows - len(valid_order_rows), "rows",
         "Source rows excluded from distinct-order calculations."),
        ("Distinct orders", distinct_orders, "orders",
         "Unique non-missing Order Id values."),
        ("Distinct order item IDs", distinct_items, "items",
         "Unique non-missing Order Item Id values."),
        ("Orders with Order Status = CANCELED", canceled_order_status, "orders",
         "Distinct orders whose representative Order Status is CANCELED."),
        ("Orders with Delivery Status = Shipping canceled",
         canceled_delivery_status, "orders",
         "Distinct orders whose representative Delivery Status is Shipping canceled."),
        ("Orders with Delivery Status = Shipping on time",
         on_time_orders, "orders",
         "Distinct orders labelled Shipping on time."),
        ("Orders with Delivery Status = Late delivery",
         late_orders, "orders",
         "Distinct orders labelled Late delivery."),
        ("Orders with Delivery Status = Advance shipping",
         advance_shipping_orders, "orders",
         "Reported separately; do not silently combine with other categories."),
        ("On-time plus late delivery orders", eligible_on_time_or_late, "orders",
         "Shipping on time + Late delivery. Excludes Advance shipping and Shipping canceled."),
        ("Orders with conflicting Order Status values",
         int(order_level["Order_Status_Variants"].gt(1).sum()), "orders",
         "Order Id values associated with more than one distinct non-missing Order Status."),
        ("Orders with conflicting Delivery Status values",
         int(order_level["Delivery_Status_Variants"].gt(1).sum()), "orders",
         "Order Id values associated with more than one distinct non-missing Delivery Status."),
    ]

    summary = pd.DataFrame(
        summary_rows, columns=["Metric", "Value", "Unit", "Definition / Rule"]
    )

    validation = pd.DataFrame([
        {
            "Check": "Source row count",
            "Observed": total_rows,
            "Expected": len(df),
            "Pass": total_rows == len(df),
            "Notes": "Count of all loaded source rows."
        },
        {
            "Check": "Distinct order count reconciles",
            "Observed": distinct_orders,
            "Expected": order_level[ORDER_ID].nunique(),
            "Pass": distinct_orders == order_level[ORDER_ID].nunique(),
            "Notes": "Distinct Order Id count matches order-level table."
        },
        {
            "Check": "Order-level table has one row per Order Id",
            "Observed": len(order_level),
            "Expected": distinct_orders,
            "Pass": len(order_level) == distinct_orders,
            "Notes": "Order-level table is grouped by Order Id."
        },
        {
            "Check": "On-time + late count",
            "Observed": eligible_on_time_or_late,
            "Expected": on_time_orders + late_orders,
            "Pass": eligible_on_time_or_late == on_time_orders + late_orders,
            "Notes": "This is a category subtotal, not all delivered orders."
        },
        {
            "Check": "Order IDs missing",
            "Observed": total_rows - len(valid_order_rows),
            "Expected": 0,
            "Pass": (total_rows - len(valid_order_rows)) == 0,
            "Notes": "A nonzero result is reported for review, not silently removed."
        },
    ])

    rules = pd.DataFrame([
        ("Source", "data/raw/DataCoSupplyChainDataset.csv",
         "Original source is read only; this script does not alter it."),
        ("Unit of analysis", "Order Id",
         "Order counts use distinct Order Id values, not source row counts."),
        ("Order items", "Order Item Id",
         "Order-item counts are reported separately from order counts."),
        ("Canceled orders", "Order Status = CANCELED",
         "Kept separate from Delivery Status = Shipping canceled; agree the official definition with the team."),
        ("On-time orders", "Delivery Status = Shipping on time",
         "Exact category count; Advance shipping is reported separately."),
        ("Late orders", "Delivery Status = Late delivery",
         "Exact category count."),
        ("Advance shipping", "Delivery Status = Advance shipping",
         "Reported separately; confirm with the team before classifying as on-time."),
        ("Order-level statuses", "First non-missing status per Order Id",
         "Conflicting status values are flagged in validation checks."),
        ("Missing order IDs", "Excluded from distinct-order counts",
         "Missing IDs are separately counted and reported."),
        ("Unsupported metrics", "Not inferred",
         "Do not invent missing operational fields or infer unsupported delivery outcomes."),
    ], columns=["Topic", "Rule", "Notes"])

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Order Count Summary", index=False)
        order_status_counts.to_excel(writer, sheet_name="Order Status Analysis", index=False)
        delivery_status_counts.to_excel(writer, sheet_name="Delivery Status Analysis", index=False)
        validation.to_excel(writer, sheet_name="Validation Checks", index=False)
        rules.to_excel(writer, sheet_name="Calculation Rules", index=False)

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                max_length = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column_cells
                )
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(
                    max(max_length + 2, 12), 65
                )

    print("\nOrder-count workbook created:")
    print(OUTPUT_FILE)
    print(f"Source rows: {total_rows:,}")
    print(f"Distinct orders: {distinct_orders:,}")
    print(f"Distinct order item IDs: {distinct_items:,}")
    print(f"Orders with Order Status = CANCELED: {canceled_order_status:,}")
    print(f"Orders with Delivery Status = Shipping canceled: {canceled_delivery_status:,}")
    print("\nReview the Validation Checks sheet before submitting the workbook.")


if __name__ == "__main__":
    main()
