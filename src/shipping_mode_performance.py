from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/DataCoSupplyChainDataset.csv"
OUTPUT = ROOT / "reports/09_Carrier_Performance.xlsx"

FIELDS = [
    "Order Id",
    "Shipping Mode",
    "Delivery Status",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
]

df = pd.read_csv(SOURCE, encoding="latin1", usecols=FIELDS)
source_rows = len(df)
missing_values = int(df[FIELDS].isna().sum().sum())

# Confirm that every order has consistent values before deduplicating.
grouped = df.groupby("Order Id", dropna=False)
conflicts_by_field = grouped[FIELDS[1:]].nunique().gt(1).sum()
conflicting_orders = int(
    grouped[FIELDS[1:]].nunique().gt(1).any(axis=1).sum()
)

# One row per order is appropriate because the consistency checks passed.
orders = df.drop_duplicates(subset=["Order Id"]).copy()
orders["Schedule Variance (days)"] = (
    orders["Days for shipping (real)"]
    - orders["Days for shipment (scheduled)"]
)

cancelled_label = "Shipping canceled"
late_label = "Late delivery"
advance_label = "Advance shipping"
ontime_label = "Shipping on time"

orders["Is Canceled"] = orders["Delivery Status"].eq(cancelled_label)
orders["Is Late"] = orders["Delivery Status"].eq(late_label)
orders["Is Strictly On Time"] = orders["Delivery Status"].eq(ontime_label)
orders["Is On Time or Early"] = orders["Delivery Status"].isin(
    [ontime_label, advance_label]
)
orders["Is Delivered Eligible"] = ~orders["Is Canceled"]

eligible = orders[orders["Is Delivered Eligible"]].copy()

summary_rows = []
for mode, all_mode_orders in orders.groupby("Shipping Mode", sort=True):
    delivered = all_mode_orders[all_mode_orders["Is Delivered Eligible"]]
    n_all = len(all_mode_orders)
    n_delivered = len(delivered)

    summary_rows.append({
        "Shipping Mode": mode,
        "Total Orders": n_all,
        "Eligible Delivered Orders": n_delivered,
        "Canceled Orders": int(all_mode_orders["Is Canceled"].sum()),
        "Late Orders": int(delivered["Is Late"].sum()),
        "Strictly On-Time Orders": int(delivered["Is Strictly On Time"].sum()),
        "Advance Shipping Orders": int(
            delivered["Delivery Status"].eq(advance_label).sum()
        ),
        "On-Time or Early Orders": int(delivered["Is On Time or Early"].sum()),
        "Strict On-Time Rate": (
            delivered["Is Strictly On Time"].mean() if n_delivered else None
        ),
        "On-Time or Early Rate": (
            delivered["Is On Time or Early"].mean() if n_delivered else None
        ),
        "Late Delivery Rate": (
            delivered["Is Late"].mean() if n_delivered else None
        ),
        "Average Actual Shipping Days": (
            delivered["Days for shipping (real)"].mean()
            if n_delivered else None
        ),
        "Average Scheduled Shipping Days": (
            delivered["Days for shipment (scheduled)"].mean()
            if n_delivered else None
        ),
        "Average Schedule Variance (days)": (
            delivered["Schedule Variance (days)"].mean()
            if n_delivered else None
        ),
    })

summary = pd.DataFrame(summary_rows)

status_counts = (
    orders.groupby(["Shipping Mode", "Delivery Status"])["Order Id"]
    .nunique()
    .unstack(fill_value=0)
    .reset_index()
)
status_counts.columns.name = None

# Validation checks: explicit expected values and reconciliation.
checks = [
    {
        "Check": "Source row count",
        "Actual": source_rows,
        "Expected": 180519,
        "Passed": source_rows == 180519,
        "Notes": "Compared with previously profiled source row count.",
    },
    {
        "Check": "Distinct order count",
        "Actual": orders["Order Id"].nunique(),
        "Expected": 65752,
        "Passed": orders["Order Id"].nunique() == 65752,
        "Notes": "One record per distinct Order Id.",
    },
    {
        "Check": "Order-level conflicts across analyzed fields",
        "Actual": conflicting_orders,
        "Expected": 0,
        "Passed": conflicting_orders == 0,
        "Notes": "Shipping mode, status, actual days, scheduled days.",
    },
    {
        "Check": "Missing values in analyzed fields",
        "Actual": missing_values,
        "Expected": 0,
        "Passed": missing_values == 0,
        "Notes": "Checked all five source fields used by this analysis.",
    },
    {
        "Check": "Shipping-mode totals reconcile to distinct orders",
        "Actual": int(summary["Total Orders"].sum()),
        "Expected": int(orders["Order Id"].nunique()),
        "Passed": int(summary["Total Orders"].sum()) == int(orders["Order Id"].nunique()),
        "Notes": "Each order belongs to one consistent shipping mode.",
    },
    {
        "Check": "Status totals reconcile to distinct orders",
        "Actual": int(status_counts.drop(columns=["Shipping Mode"]).to_numpy().sum()),
        "Expected": int(orders["Order Id"].nunique()),
        "Passed": int(status_counts.drop(columns=["Shipping Mode"]).to_numpy().sum())
                  == int(orders["Order Id"].nunique()),
        "Notes": "Counts each order once under its consistent delivery status.",
    },
    {
        "Check": "All source order IDs present",
        "Actual": int(orders["Order Id"].isna().sum()),
        "Expected": 0,
        "Passed": int(orders["Order Id"].isna().sum()) == 0,
        "Notes": "Order IDs are required for order-level counting.",
    },
]
validation = pd.DataFrame(checks)

rules = pd.DataFrame([
    ["Assigned deliverable", "09_Carrier_Performance.xlsx"],
    ["Carrier availability", "No carrier identifier exists in the source fields inspected."],
    ["Proxy segment", "Shipping Mode; this is not a carrier-level comparison."],
    ["Unit of analysis", "Distinct Order Id; each order has consistent analyzed values."],
    ["Eligible delivered orders", "All orders except Delivery Status = Shipping canceled."],
    ["Strict on-time rate", "Shipping on time orders / eligible delivered orders."],
    ["On-time-or-early rate", "(Shipping on time + Advance shipping) / eligible delivered orders."],
    ["Late delivery rate", "Late delivery orders / eligible delivered orders."],
    ["Average actual duration", "Mean Days for shipping (real) among eligible delivered orders."],
    ["Average scheduled duration", "Mean Days for shipment (scheduled) among eligible delivered orders."],
    ["Schedule variance", "Actual shipping days minus scheduled shipping days; positive means later than scheduled."],
    ["Cancellation handling", "Canceled orders are counted separately and excluded from delivered-order rate denominators."],
    ["Interpretation", "Descriptive comparisons only; differences do not establish causation."],
    ["Limitations", "Shipping mode is not carrier identity. Source delivery-status labels are used as supplied."],
], columns=["Item", "Definition / Limitation"])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
    summary.to_excel(writer, sheet_name="Shipping Mode Summary", index=False)
    status_counts.to_excel(writer, sheet_name="Delivery Status Counts", index=False)
    validation.to_excel(writer, sheet_name="Validation Checks", index=False)
    rules.to_excel(writer, sheet_name="Definitions and Limits", index=False)

# Format sheets for readability.
wb = load_workbook(OUTPUT)
for ws in wb.worksheets:
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="244062")
    for column_cells in ws.columns:
        max_length = max(
            (len(str(cell.value)) if cell.value is not None else 0)
            for cell in column_cells
        )
        ws.column_dimensions[get_column_letter(column_cells[0].column)].width = min(
            max(max_length + 2, 12), 48
        )

# Display rates as percentages and durations to two decimals.
ws = wb["Shipping Mode Summary"]
headers = {cell.value: cell.column for cell in ws[1]}
for name in ["Strict On-Time Rate", "On-Time or Early Rate", "Late Delivery Rate"]:
    col = headers[name]
    for row in range(2, ws.max_row + 1):
        ws.cell(row, col).number_format = "0.0%"
for name in [
    "Average Actual Shipping Days",
    "Average Scheduled Shipping Days",
    "Average Schedule Variance (days)",
]:
    col = headers[name]
    for row in range(2, ws.max_row + 1):
        ws.cell(row, col).number_format = "0.00"

# Chart 1: on-time-or-early rate by shipping mode.
chart1 = BarChart()
chart1.type = "bar"
chart1.style = 10
chart1.title = "On-Time or Early Delivery Rate by Shipping Mode"
chart1.y_axis.title = "Shipping Mode"
chart1.x_axis.title = "Rate"
data = Reference(ws, min_col=headers["On-Time or Early Rate"],
                 min_row=1, max_row=ws.max_row)
cats = Reference(ws, min_col=headers["Shipping Mode"],
                 min_row=2, max_row=ws.max_row)
chart1.add_data(data, titles_from_data=True)
chart1.set_categories(cats)
chart1.height = 7
chart1.width = 15
chart1.x_axis.numFmt = "0%"
ws.add_chart(chart1, "A10")

# Chart 2: average actual and scheduled duration by shipping mode.
chart2 = BarChart()
chart2.type = "col"
chart2.style = 11
chart2.title = "Average Actual vs Scheduled Shipping Days"
chart2.y_axis.title = "Days"
chart2.x_axis.title = "Shipping Mode"
duration_cols = [
    headers["Average Actual Shipping Days"],
    headers["Average Scheduled Shipping Days"],
]
for col in duration_cols:
    data = Reference(ws, min_col=col, min_row=1, max_row=ws.max_row)
    chart2.add_data(data, titles_from_data=True)
chart2.set_categories(cats)
chart2.height = 7
chart2.width = 15
ws.add_chart(chart2, "J10")

wb.save(OUTPUT)

print(f"Workbook created: {OUTPUT}")
print(f"Source rows: {source_rows:,}")
print(f"Distinct orders: {orders['Order Id'].nunique():,}")
print(f"Orders with field conflicts: {conflicting_orders}")
print(f"Missing values in analyzed fields: {missing_values}")
print("\nShipping-mode summary:")
print(summary.to_string(index=False))
print("\nValidation results:")
print(validation[["Check", "Actual", "Expected", "Passed"]].to_string(index=False))
print(f"\nAll checks passed: {validation['Passed'].all()}")
