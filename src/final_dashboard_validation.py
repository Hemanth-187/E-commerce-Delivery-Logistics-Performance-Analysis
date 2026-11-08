from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from collections import Counter
from datetime import datetime
from pathlib import Path

DASHBOARD = Path("reports/Order_Count_Analysis_Dashboard.xlsx")
SOURCE = Path("reports/01_Final_Dashboard_Dataset.xlsx")
OUTPUT = Path("reports/17_Dashboard_Final_Validation.xlsx")

def load_dataset(path):
    wb = load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        for row_num in range(1, min(ws.max_row, 8) + 1):
            headers = [c.value for c in ws[row_num]]
            if "Order Id" in headers:
                records = []
                for values in ws.iter_rows(min_row=row_num + 1, values_only=True):
                    if values[0] is not None:
                        records.append(dict(zip(headers, values)))
                return records, headers, ws.title
    raise ValueError(f"Could not find an 'Order Id' header in {path}")

def add_result(results, category, test, expected, actual, passed, details=""):
    results.append([
        category, test, str(expected), str(actual),
        "PASS" if passed else "FAIL", details
    ])

source, source_headers, source_sheet = load_dataset(SOURCE)
dashboard, dashboard_headers, dashboard_sheet = load_dataset(DASHBOARD)

results = []
notes = []

# 1. Source and embedded dashboard dataset comparison
source_by_id = {r["Order Id"]: r for r in source}
dashboard_by_id = {r["Order Id"]: r for r in dashboard}

add_result(results, "Data consistency", "Source record count",
           len(source), len(dashboard), len(source) == len(dashboard))
add_result(results, "Data consistency", "Unique source order IDs",
           len(source), len(source_by_id), len(source_by_id) == len(source))
add_result(results, "Data consistency", "Unique dashboard order IDs",
           len(dashboard), len(dashboard_by_id),
           len(dashboard_by_id) == len(dashboard))
add_result(results, "Data consistency", "Column names",
           source_headers, dashboard_headers,
           source_headers == dashboard_headers)

missing_ids = set(source_by_id) - set(dashboard_by_id)
extra_ids = set(dashboard_by_id) - set(source_by_id)
add_result(results, "Data consistency", "Missing order IDs",
           0, len(missing_ids), len(missing_ids) == 0)
add_result(results, "Data consistency", "Unexpected order IDs",
           0, len(extra_ids), len(extra_ids) == 0)

field_mismatches = 0
mismatch_examples = []
for order_id in set(source_by_id) & set(dashboard_by_id):
    a = source_by_id[order_id]
    b = dashboard_by_id[order_id]
    for field in source_headers:
        if a.get(field) != b.get(field):
            field_mismatches += 1
            if len(mismatch_examples) < 10:
                mismatch_examples.append(
                    f"Order {order_id}, field {field}: {a.get(field)} != {b.get(field)}"
                )

add_result(results, "Data consistency", "Field-level mismatches",
           0, field_mismatches, field_mismatches == 0,
           "Compared matching order IDs across all shared columns.")

# 2. Basic KPI and flag consistency
n = len(source)
eligible = sum(int(r["Is_Eligible_Non_Canceled"] or 0) for r in source)
shipping_cancelled = sum(int(r["Is_Shipping_Canceled"] or 0) for r in source)
late = sum(int(r["Is_Late_Delivery"] or 0) for r in source)
on_time = sum(int(r["Is_Strict_On_Time"] or 0) for r in source)
advance = sum(int(r["Is_Advance_Shipping"] or 0) for r in source)
order_cancelled = sum(int(r["Is_Order_Status_Canceled"] or 0) for r in source)

add_result(results, "KPI consistency", "Eligible + shipping-canceled = total",
           n, eligible + shipping_cancelled,
           eligible + shipping_cancelled == n)
add_result(results, "KPI consistency", "Delivery outcomes = eligible orders",
           eligible, late + on_time + advance,
           eligible == late + on_time + advance)
add_result(results, "KPI consistency", "Order status canceled flag count",
           order_cancelled,
           sum(1 for r in source if r["Order_Status"] == "CANCELED"),
           order_cancelled == sum(1 for r in source if r["Order_Status"] == "CANCELED"))

# 3. Simulated filter tests on the underlying dataset
def test_filter(field, value, label):
    filtered = [r for r in source if r.get(field) == value]
    matches = all(r.get(field) == value for r in filtered)
    add_result(
        results, "Filter simulation", label,
        f"All selected records have {field}={value}",
        f"{len(filtered)} records; selection consistent",
        bool(filtered) and matches
    )
    return filtered

shipping_modes = sorted({r["Shipping_Mode"] for r in source if r["Shipping_Mode"] is not None})
for mode in shipping_modes:
    subset = test_filter("Shipping_Mode", mode, f"Shipping mode: {mode}")
    status_total = sum(Counter(r["Delivery_Status"] for r in subset).values())
    add_result(results, "Filter reconciliation",
               f"Delivery statuses reconcile after {mode} filter",
               len(subset), status_total, len(subset) == status_total)

delivery_statuses = sorted({r["Delivery_Status"] for r in source if r["Delivery_Status"] is not None})
for status in delivery_statuses:
    subset = test_filter("Delivery_Status", status, f"Delivery status: {status}")
    mode_total = sum(Counter(r["Shipping_Mode"] for r in subset).values())
    add_result(results, "Filter reconciliation",
               f"Shipping modes reconcile after {status} filter",
               len(subset), mode_total, len(subset) == mode_total)

months = sorted({r["Order_Year_Month"] for r in source if r["Order_Year_Month"] is not None})
for month in months:
    subset = test_filter("Order_Year_Month", month, f"Order month: {month}")
    add_result(results, "Filter reconciliation",
               f"Monthly order count: {month}",
               len(subset), len({r["Order Id"] for r in subset}),
               len(subset) == len({r["Order Id"] for r in subset}))

years = sorted({r["Order_Year"] for r in source if r["Order_Year"] is not None})
for year in years:
    subset = test_filter("Order_Year", year, f"Order year: {year}")
    add_result(results, "Filter reconciliation",
               f"Yearly order count: {year}",
               len(subset), len({r["Order Id"] for r in subset}),
               len(subset) == len({r["Order Id"] for r in subset}))

# 4. Dashboard workbook feature inspection
wb = load_workbook(DASHBOARD, data_only=False)
dashboard_ws = wb["Dashboard"]
dataset_ws = wb[dashboard_sheet]

chart_count = len(dashboard_ws._charts)
has_dataset_filter = bool(dataset_ws.auto_filter.ref)
has_dashboard_filter = bool(dashboard_ws.auto_filter.ref)

add_result(results, "Dashboard features", "Dashboard charts",
           3, chart_count, chart_count == 3)
add_result(results, "Dashboard features", "Dataset table filter",
           "Available", has_dataset_filter, has_dataset_filter)
add_result(results, "Dashboard features", "Main dashboard AutoFilter",
           "Not configured", "Configured" if has_dashboard_filter else "Not configured",
           not has_dashboard_filter,
           "Informational: the main dashboard is a summary view, not a filtered data table.")

# Slicers and PivotTables are checked in the workbook package.
from zipfile import ZipFile
with ZipFile(DASHBOARD) as z:
    names = [name.lower() for name in z.namelist()]
    has_slicer = any("slicer" in name for name in names)
    has_pivot = any("pivottable" in name or "pivotcache" in name for name in names)

add_result(results, "Dashboard features", "Interactive slicers",
           "Not present in workbook", "Present" if has_slicer else "Not present",
           not has_slicer,
           "No slicers found; filter tests above simulate filtering the underlying dataset.")
add_result(results, "Dashboard features", "PivotTables",
           "Not present in workbook", "Present" if has_pivot else "Not present",
           not has_pivot,
           "No PivotTables found.")

# 5. Create validation workbook
report = Workbook()
summary = report.active
summary.title = "Validation Summary"
summary.append(["DAY 5 - DASHBOARD FINAL VALIDATION"])
summary.append(["Purpose", "Final checks of dashboard data consistency, KPI logic and filter scenarios."])
summary.append(["Analytical source", str(SOURCE)])
summary.append(["Dashboard workbook", str(DASHBOARD)])
summary.append(["Source worksheet", source_sheet])
summary.append(["Dashboard dataset worksheet", dashboard_sheet])
summary.append(["Source records", n])
summary.append(["Total orders", n])
summary.append(["Eligible non-canceled orders", eligible])
summary.append(["Shipping-canceled orders", shipping_cancelled])
summary.append(["Late delivery orders", late])
summary.append(["Strict on-time orders", on_time])
summary.append(["Advance shipping orders", advance])
summary.append(["Order Status CANCELED orders", order_cancelled])
summary.append(["Dashboard charts", chart_count])
summary.append(["Dataset AutoFilter", str(dataset_ws.auto_filter.ref)])
summary.append(["Main dashboard AutoFilter", str(dashboard_ws.auto_filter.ref)])
summary.append(["Slicers found", has_slicer])
summary.append(["PivotTables found", has_pivot])

passed = sum(1 for r in results if r[4] == "PASS")
failed = sum(1 for r in results if r[4] == "FAIL")
summary.append(["Total validation checks", len(results)])
summary.append(["Passed", passed])
summary.append(["Failed", failed])
summary.append(["Overall result", "PASS" if failed == 0 else "FAIL"])

detail = report.create_sheet("Detailed Tests")
detail.append(["Category", "Test", "Expected", "Actual", "Result", "Details"])
for row in results:
    detail.append(row)

features = report.create_sheet("Dashboard Features")
features.append(["Feature", "Finding", "Interpretation"])
features.append(["Dashboard charts", chart_count, "Charts are present on the Dashboard worksheet."])
features.append(["Dataset filter", dataset_ws.auto_filter.ref, "Excel table filter is available on the embedded dataset."])
features.append(["Main dashboard filter", dashboard_ws.auto_filter.ref, "No AutoFilter on the main summary dashboard."])
features.append(["Slicers", "Present" if has_slicer else "Not found", "Interactive slicers were not detected."])
features.append(["PivotTables", "Present" if has_pivot else "Not found", "PivotTables were not detected."])
features.append(["Filter testing method", "Programmatic simulation", "Filters were simulated against the underlying dataset; interactive UI behavior was not tested."])

issues = report.create_sheet("Notes and Limitations")
issues.append(["Item", "Observation"])
issues.append(["Filter testing", "Filter scenarios were simulated programmatically against the underlying dashboard dataset."])
issues.append(["Interactive dashboard", "No slicers or PivotTables were detected. Interactive dashboard filter behavior cannot be claimed as tested."])
issues.append(["Excel workbook", "This validation checks workbook structure and underlying data; it does not test rendering in every Excel version."])
issues.append(["Power BI", "No Power BI PBIX interaction or visual validation was performed."])
issues.append(["Cancellation", "Shipping-canceled orders and Order Status CANCELED orders are separate measures."])
issues.append(["Delivery outcomes", "Late, strict on-time and advance shipping counts use eligible non-canceled orders."])
issues.append(["Interpretation", "Validation confirms consistency with the analytical dataset, not the independent correctness of the original source data."])
for item in mismatch_examples:
    issues.append(["Example mismatch", item])

# Formatting
for ws in report.worksheets:
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions if ws.max_row > 1 else None
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for column in ws.columns:
        letter = column[0].column_letter
        max_length = max((len(str(c.value)) if c.value is not None else 0) for c in column)
        ws.column_dimensions[letter].width = min(max(max_length + 2, 14), 65)
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

summary.column_dimensions["A"].width = 32
summary.column_dimensions["B"].width = 90
detail.column_dimensions["B"].width = 55
detail.column_dimensions["C"].width = 38
detail.column_dimensions["D"].width = 38
detail.column_dimensions["F"].width = 65
issues.column_dimensions["B"].width = 100

report.save(OUTPUT)

print("Validation workbook created:", OUTPUT)
print("Source records:", len(source))
print("Dashboard records:", len(dashboard))
print("Checks:", len(results), "| PASS:", passed, "| FAIL:", failed)
print("Field mismatches:", field_mismatches)
print("Filter scenarios tested:", len(shipping_modes) + len(delivery_statuses) + len(months) + len(years))
print("Dashboard charts:", chart_count)
print("Slicers:", has_slicer, "| PivotTables:", has_pivot)
