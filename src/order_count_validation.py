from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/DataCoSupplyChainDataset.csv"
OUTPUT = ROOT / "reports/13_Order_Count_Validation.xlsx"

FIELDS = ["Order Id", "Order Status", "Delivery Status"]
df = pd.read_csv(SOURCE, encoding="latin1", usecols=FIELDS)

source_rows = len(df)
missing_order_ids = int(df["Order Id"].isna().sum())
distinct_orders = int(df["Order Id"].nunique())

# Validate whether order-level status fields are consistent across item rows.
grouped = df.groupby("Order Id", dropna=False)
delivery_conflicts = int((grouped["Delivery Status"].nunique() > 1).sum())
order_status_conflicts = int((grouped["Order Status"].nunique() > 1).sum())

# Use one record per order only after confirming status consistency.
orders = df.drop_duplicates(subset=["Order Id"]).copy()

delivery_counts = (
    orders.groupby("Delivery Status")["Order Id"]
    .nunique()
    .sort_index()
    .rename("Distinct Orders")
    .reset_index()
)
order_status_counts = (
    orders.groupby("Order Status")["Order Id"]
    .nunique()
    .sort_index()
    .rename("Distinct Orders")
    .reset_index()
)

CANCELLED_DELIVERY = "Shipping canceled"
cancelled_delivery_orders = int(
    orders["Delivery Status"].eq(CANCELLED_DELIVERY).sum()
)
eligible_delivered_orders = distinct_orders - cancelled_delivery_orders

cancelled_order_status = int(orders["Order Status"].eq("CANCELED").sum())

summary = pd.DataFrame([
    ["Source data rows (order-item records)", source_rows,
     "Each row represents an order item, not necessarily a unique order."],
    ["Distinct orders", distinct_orders,
     "Count of unique non-missing Order Id values."],
    ["Eligible delivered orders", eligible_delivered_orders,
     "Distinct orders excluding Delivery Status = Shipping canceled."],
    ["Shipping-canceled orders", cancelled_delivery_orders,
     "Counted using Delivery Status, not Order Status."],
    ["Order Status = CANCELED", cancelled_order_status,
     "Separate order-processing status; do not substitute for Shipping canceled."],
    ["Missing Order Id rows", missing_order_ids,
     "Rows without an order identifier cannot be assigned to a distinct order."],
], columns=["Measure", "Value", "Definition"])

# Select up to 10 distinct IDs deterministically and show their source records.
sample_ids = sorted(orders["Order Id"].dropna().unique())[:10]
samples = df[df["Order Id"].isin(sample_ids)].copy()
samples = samples.sort_values(["Order Id", "Order Status", "Delivery Status"])
samples["Order Item Rows for Sample Order"] = (
    samples.groupby("Order Id")["Order Id"].transform("size")
)
samples["Manual Check"] = "Compare each row to the raw CSV; confirm the order ID and status labels."
samples = samples[
    ["Order Id", "Order Status", "Delivery Status",
     "Order Item Rows for Sample Order", "Manual Check"]
]

delivery_total = int(delivery_counts["Distinct Orders"].sum())
order_status_total = int(order_status_counts["Distinct Orders"].sum())

checks = [
    ["Source row count", source_rows, 180519, source_rows == 180519,
     "Compared with the established source profile."],
    ["Distinct order count", distinct_orders, 65752, distinct_orders == 65752,
     "Recalculated from unique Order Id values."],
    ["Missing Order Id rows", missing_order_ids, 0, missing_order_ids == 0,
     "Must be zero for complete distinct-order counting."],
    ["Conflicting delivery statuses per order", delivery_conflicts, 0,
     delivery_conflicts == 0, "Checks order-level status consistency."],
    ["Conflicting order statuses per order", order_status_conflicts, 0,
     order_status_conflicts == 0, "Checks order-level order-status consistency."],
    ["Delivery status counts reconcile", delivery_total, distinct_orders,
     delivery_total == distinct_orders,
     "Sum of distinct orders across delivery status categories."],
    ["Order status counts reconcile", order_status_total, distinct_orders,
     order_status_total == distinct_orders,
     "Sum of distinct orders across order status categories."],
    ["Eligible + shipping-canceled orders reconcile",
     eligible_delivered_orders + cancelled_delivery_orders, distinct_orders,
     eligible_delivered_orders + cancelled_delivery_orders == distinct_orders,
     "Eligible count excludes Shipping canceled only."],
    ["Sample contains selected distinct orders", samples["Order Id"].nunique(),
     len(sample_ids), samples["Order Id"].nunique() == len(sample_ids),
     "Sample records are selected directly from the raw source rows."],
]
validation = pd.DataFrame(
    checks, columns=["Check", "Actual", "Expected", "Passed", "Notes"]
)

definitions = pd.DataFrame([
    ["Source", "data/raw/DataCoSupplyChainDataset.csv",
     "Read-only input; this script does not modify the raw dataset."],
    ["Source row", "One order-item record",
     "The 180,519 source rows must not be reported as distinct orders."],
    ["Distinct order", "Unique Order Id",
     "65,752 distinct orders in the independently rechecked source."],
    ["Eligible delivered orders", "Distinct orders excluding Shipping canceled",
     "62,897 using the supplied delivery-status categories."],
    ["Shipping-canceled order", "Delivery Status = Shipping canceled",
     "2,855 distinct orders; excluded from the eligible delivered-order denominator."],
    ["Order Status = CANCELED", "Order Status equals CANCELED",
     "1,367 distinct orders; a different field and definition from Shipping canceled."],
    ["Reconciliation", "Status-level distinct-order counts sum to total distinct orders",
     "This relies on the checked order-level status consistency."],
    ["Manual sample", "First 10 sorted distinct Order Id values",
     "Sample rows are provided for direct inspection against the source CSV; this is a trace sample, not a random statistical sample."],
], columns=["Topic", "Rule", "Explanation"])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
    summary.to_excel(writer, sheet_name="Order Count Summary", index=False)
    delivery_counts.to_excel(writer, sheet_name="Delivery Status Reconciliation", index=False)
    order_status_counts.to_excel(writer, sheet_name="Order Status Reconciliation", index=False)
    samples.to_excel(writer, sheet_name="Manual Sample Checks", index=False)
    validation.to_excel(writer, sheet_name="Validation Checks", index=False)
    definitions.to_excel(writer, sheet_name="Definitions and Limits", index=False)

wb = load_workbook(OUTPUT)
for ws in wb.worksheets:
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="244062")
    for col_cells in ws.columns:
        width = max(
            len(str(c.value)) if c.value is not None else 0
            for c in col_cells
        )
        ws.column_dimensions[get_column_letter(col_cells[0].column)].width = min(
            max(width + 2, 12), 55
        )
wb.save(OUTPUT)

print(f"Workbook created: {OUTPUT}")
print(f"Source rows: {source_rows:,}")
print(f"Distinct orders: {distinct_orders:,}")
print(f"Eligible delivered orders: {eligible_delivered_orders:,}")
print(f"Shipping-canceled orders: {cancelled_delivery_orders:,}")
print(f"Order Status = CANCELED: {cancelled_order_status:,}")
print(f"Delivery-status conflicts: {delivery_conflicts}")
print(f"Order-status conflicts: {order_status_conflicts}")
print("\nValidation results:")
print(validation[["Check", "Actual", "Expected", "Passed"]].to_string(index=False))
print(f"\nAll validation checks passed: {validation['Passed'].all()}")
