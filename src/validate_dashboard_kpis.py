from collections import Counter
from datetime import datetime
from pathlib import Path
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

SOURCE = Path("reports/01_Final_Dashboard_Dataset.xlsx")
DASHBOARD = Path("reports/Order_Count_Analysis_Dashboard.xlsx")
KPI_FILE = Path("reports/17_Final_KPI_Dataset.xlsx")
OUTPUT = Path("reports/09_Dashboard_KPI_Validation.xlsx")

for path in (SOURCE, DASHBOARD, KPI_FILE):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

def read_dataset(path, sheet, header_row):
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    rows = ws.iter_rows(min_row=header_row, values_only=True)
    headers = list(next(rows))
    records = [dict(zip(headers, row)) for row in rows if row and row[0] is not None]
    wb.close()
    return headers, records

def read_sheet(path, sheet):
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    return rows

def find_header(rows, first_cell):
    for i, row in enumerate(rows):
        if row and row[0] == first_cell:
            return i
    return None

def read_breakdown(path, sheet, first_cell, value_col=1):
    rows = read_sheet(path, sheet)
    idx = find_header(rows, first_cell)
    if idx is None:
        return {}
    result = {}
    for row in rows[idx + 1:]:
        if len(row) > value_col and row[0] is not None:
            result[str(row[0])] = row[value_col]
    return result

def normalize(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value

source_headers, source = read_dataset(
    SOURCE, "Dashboard Dataset", 1
)
dashboard_headers, dashboard_data = read_dataset(
    DASHBOARD, "Dashboard Dataset", 3
)

if source_headers != dashboard_headers:
    raise ValueError("Source and dashboard dataset column headers do not match.")

def count_field(field):
    return Counter(str(r[field]) for r in source if r.get(field) is not None)

delivery_counts = count_field("Delivery_Status")
order_status_counts = count_field("Order_Status")
shipping_counts = count_field("Shipping_Mode")
monthly_counts = count_field("Order_Year_Month")

total_orders = len(source)
eligible = sum(1 for r in source if r["Is_Eligible_Non_Canceled"] == 1)
shipping_canceled = sum(1 for r in source if r["Is_Shipping_Canceled"] == 1)
late = sum(1 for r in source if r["Is_Late_Delivery"] == 1)
strict_on_time = sum(1 for r in source if r["Is_Strict_On_Time"] == 1)
advance = sum(1 for r in source if r["Is_Advance_Shipping"] == 1)
order_canceled = sum(1 for r in source if r["Is_Order_Status_Canceled"] == 1)
total_items = sum(r["Source_Item_Rows"] or 0 for r in source)

kpis = [
    ("Total distinct orders", total_orders, 65752),
    ("Eligible non-canceled orders", eligible, 62897),
    ("Shipping-canceled orders", shipping_canceled, 2855),
    ("Late delivery orders", late, 36048),
    ("Strict on-time orders", strict_on_time, 11722),
    ("Advance shipping orders", advance, 15127),
    ("Order Status CANCELED orders", order_canceled, 1367),
    ("Total source item rows", total_items, 180519),
    ("Delivery status categories reconcile", sum(delivery_counts.values()), total_orders),
    ("Order status categories reconcile", sum(order_status_counts.values()), total_orders),
    ("Shipping mode categories reconcile", sum(shipping_counts.values()), total_orders),
    ("Monthly trend categories reconcile", sum(monthly_counts.values()), total_orders),
]

dashboard_summary_rows = read_sheet(DASHBOARD, "Order Count Summary")
dashboard_summary = {}
for row in dashboard_summary_rows:
    if len(row) >= 2 and row[0] is not None and row[1] is not None:
        dashboard_summary[str(row[0]).strip()] = row[1]

summary_mapping = {
    "Total distinct orders": "Total Orders",
    "Eligible non-canceled orders": "Eligible Delivered Orders",
    "Shipping-canceled orders": "Shipping Canceled Orders",
    "Late delivery orders": "Late Delivery Orders",
    "Strict on-time orders": "Strict On-Time Orders",
    "Advance shipping orders": "Advance Shipping Orders",
    "Order Status CANCELED orders": "Order Status Canceled",
    "Total source item rows": "Total Order Items",
}

delivery_dashboard = read_breakdown(
    DASHBOARD, "Delivery Status", "Delivery_Status"
)
order_dashboard = read_breakdown(
    DASHBOARD, "Order Status", "Order_Status"
)
shipping_dashboard = read_breakdown(
    DASHBOARD, "Shipping Mode", "Shipping_Mode"
)
monthly_dashboard = read_breakdown(
    DASHBOARD, "Monthly Trend", "Order_Year_Month"
)

checks = []

def add_check(category, item, expected, actual, note=""):
    passed = expected == actual
    checks.append([
        category, item, expected, actual,
        "PASS" if passed else "FAIL", note
    ])

for label, actual, expected in kpis:
    add_check("Source dataset integrity", label, expected, actual)

for label, dashboard_label in summary_mapping.items():
    actual = dict((x[0], x[1]) for x in kpis)[label]
    dashboard_value = dashboard_summary.get(dashboard_label)
    add_check(
        "Dashboard KPI Summary", label,
        actual, dashboard_value,
        f"Dashboard label: {dashboard_label}"
    )

for status, count in delivery_counts.items():
    add_check(
        "Delivery Status", status, count,
        delivery_dashboard.get(status)
    )

for status, count in order_status_counts.items():
    add_check(
        "Order Status", status, count,
        order_dashboard.get(status)
    )

for mode, count in shipping_counts.items():
    add_check(
        "Shipping Mode", mode, count,
        shipping_dashboard.get(mode)
    )

for month, count in monthly_counts.items():
    add_check(
        "Monthly Trend", month, count,
        monthly_dashboard.get(month)
    )

# Compare the dashboard's embedded order-level dataset with the final source.
source_by_id = {r["Order Id"]: r for r in source}
dashboard_by_id = {r["Order Id"]: r for r in dashboard_data}

add_check(
    "Dataset Reconciliation", "Dashboard dataset record count",
    len(source), len(dashboard_data)
)
add_check(
    "Dataset Reconciliation", "Dashboard unique Order Id count",
    len(source_by_id), len(dashboard_by_id)
)

missing_ids = set(source_by_id) - set(dashboard_by_id)
extra_ids = set(dashboard_by_id) - set(source_by_id)
add_check(
    "Dataset Reconciliation", "Order Ids missing from dashboard",
    0, len(missing_ids)
)
add_check(
    "Dataset Reconciliation", "Extra Order Ids in dashboard",
    0, len(extra_ids)
)

field_mismatches = []
for order_id in set(source_by_id) & set(dashboard_by_id):
    left = source_by_id[order_id]
    right = dashboard_by_id[order_id]
    for field in source_headers:
        if normalize(left.get(field)) != normalize(right.get(field)):
            field_mismatches.append((order_id, field, left.get(field), right.get(field)))
            if len(field_mismatches) >= 100:
                break
    if len(field_mismatches) >= 100:
        break

add_check(
    "Dataset Reconciliation",
    "Matching Order Id records with identical fields (first 100 mismatches checked)",
    0, len(field_mismatches),
    "Comparison covers all shared Order Ids and all 25 fields; mismatch list capped at 100."
)

# Create the validation workbook.
wb = Workbook()
ws = wb.active
ws.title = "KPI Validation Summary"

ws.append(["DASHBOARD KPI VALIDATION REPORT"])
ws.append(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")])
ws.append(["Purpose", "Independent comparison of dashboard values against the final order-level analytical dataset."])
ws.append(["Scope", "Validates numerical values and embedded data; does not validate visual design or a Power BI PBIX file."])
ws.append([])
ws.append(["Category", "Check", "Expected / Source", "Dashboard / Actual", "Result", "Notes"])
for row in checks:
    ws.append(row)

# Detailed breakdown sheets.
def add_detail_sheet(name, title, source_counts, dashboard_counts):
    sh = wb.create_sheet(name)
    sh.append([title])
    sh.append(["Category", "Source Dataset Count", "Dashboard Count", "Result"])
    for key in sorted(source_counts):
        expected = source_counts[key]
        actual = dashboard_counts.get(key)
        sh.append([
            key, expected, actual,
            "PASS" if expected == actual else "FAIL"
        ])
    return sh

add_detail_sheet("Delivery Status", "DELIVERY STATUS VALIDATION", delivery_counts, delivery_dashboard)
add_detail_sheet("Order Status", "ORDER STATUS VALIDATION", order_status_counts, order_dashboard)
add_detail_sheet("Shipping Mode", "SHIPPING MODE VALIDATION", shipping_counts, shipping_dashboard)
add_detail_sheet("Monthly Trend", "MONTHLY DISTINCT ORDER VALIDATION", monthly_counts, monthly_dashboard)

# Record known limitations and observations.
notes = wb.create_sheet("Issues and Notes")
notes.append(["ISSUES, OBSERVATIONS AND LIMITATIONS"])
notes.append(["Item", "Observation"])
notes.append(["First Class delivery status", "All 9,602 eligible First Class orders are classified as Late delivery in the supplied dataset. This is an observation to investigate, not automatically a data error."])
notes.append(["KPI denominator", "Status rates should clearly state whether the denominator is all orders or eligible non-canceled orders."])
notes.append(["Order cancellation distinction", "Shipping-canceled orders (2,855) and Order Status CANCELED orders (1,367) are different measures. Do not combine them."])
notes.append(["Unavailable measures", "Customer rating by delivery outcome and timestamp-based delivery delay are unavailable in the supplied KPI dataset."])
notes.append(["Validation scope", "This workbook checks numerical values and dataset reconciliation. It does not validate chart appearance, dashboard usability, or a native Power BI PBIX file."])
notes.append(["Source workbook", str(SOURCE)])
notes.append(["Dashboard workbook", str(DASHBOARD)])
notes.append(["Final KPI workbook", str(KPI_FILE)])

# Formatting.
for sh in wb.worksheets:
    sh.freeze_panes = "A7" if sh.title == "KPI Validation Summary" else "A3"
    sh.sheet_view.showGridLines = False
    for cell in sh[1]:
        cell.font = Font(bold=True, color="FFFFFF", size=14)
        cell.fill = PatternFill("solid", fgColor="1F4E78")
    header_row = 6 if sh.title == "KPI Validation Summary" else (2 if sh.title != "Issues and Notes" else 2)
    if sh.max_row >= header_row:
        for cell in sh[header_row]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="4472C4")
    for row in sh.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if cell.value in ("PASS",):
                cell.fill = PatternFill("solid", fgColor="E2F0D9")
            elif cell.value in ("FAIL",):
                cell.fill = PatternFill("solid", fgColor="FCE4D6")
    for col in range(1, sh.max_column + 1):
        values = [
            len(str(sh.cell(r, col).value or ""))
            for r in range(1, min(sh.max_row, 100) + 1)
        ]
        sh.column_dimensions[get_column_letter(col)].width = min(max(max(values, default=12) + 3, 14), 55)
    sh.auto_filter.ref = sh.dimensions if sh.title != "Issues and Notes" else "A2:B9"

wb.save(OUTPUT)

passed = sum(1 for row in checks if row[4] == "PASS")
failed = sum(1 for row in checks if row[4] == "FAIL")
print("Validation workbook created:", OUTPUT)
print("Checks:", len(checks), "| PASS:", passed, "| FAIL:", failed)
print("Source orders:", total_orders, "| Dashboard records:", len(dashboard_data))
print("Field mismatches found (up to 100):", len(field_mismatches))
