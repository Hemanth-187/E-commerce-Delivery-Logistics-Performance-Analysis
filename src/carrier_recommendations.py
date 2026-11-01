from pathlib import Path
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

SOURCE = Path("reports/09_Carrier_Performance.xlsx")
OUTPUT = Path("reports/17_Carrier_Recommendations.xlsx")

if not SOURCE.exists():
    raise FileNotFoundError(f"Required source workbook not found: {SOURCE}")

source_wb = load_workbook(SOURCE, data_only=True)
source_ws = source_wb["Shipping Mode Summary"]

source_rows = list(source_ws.iter_rows(values_only=True))
headers = list(source_rows[0])
records = [dict(zip(headers, row)) for row in source_rows[1:] if row[0]]

required = {
    "Shipping Mode", "Total Orders", "Eligible Delivered Orders",
    "Canceled Orders", "Late Orders", "Strictly On-Time Orders",
    "Advance Shipping Orders", "On-Time or Early Orders",
    "Strict On-Time Rate", "On-Time or Early Rate",
    "Late Delivery Rate", "Average Actual Shipping Days",
    "Average Scheduled Shipping Days",
    "Average Schedule Variance (days)"
}
missing = required - set(headers)
if missing:
    raise ValueError(f"Missing required source columns: {sorted(missing)}")

validation_ws = source_wb["Validation Checks"]
validation_rows = list(validation_ws.iter_rows(values_only=True))
validation_passes = all(
    row[3] is True for row in validation_rows[1:] if row[0]
)

if not validation_passes:
    raise ValueError("Source workbook contains failed validation checks.")

total_orders = sum(r["Total Orders"] for r in records)
eligible_orders = sum(r["Eligible Delivered Orders"] for r in records)
late_orders = sum(r["Late Orders"] for r in records)
canceled_orders = sum(r["Canceled Orders"] for r in records)

if total_orders != 65752 or eligible_orders != 62897 or late_orders != 36048:
    raise ValueError("Source totals do not match the validated project baseline.")

wb = Workbook()
summary = wb.active
summary.title = "Executive Summary"
evidence = wb.create_sheet("Shipping Mode Evidence")
recommendations = wb.create_sheet("Prioritized Recommendations")
gaps = wb.create_sheet("Carrier Data Gaps")
actions = wb.create_sheet("Follow-up Action Plan")
definitions = wb.create_sheet("Definitions and Limitations")

navy = "1F4E78"
blue = "D9EAF7"
light = "F3F6F9"
orange = "FCE4D6"
red = "F4CCCC"
green = "E2F0D9"
white = "FFFFFF"
thin = Side(style="thin", color="D9E1F2")

def format_sheet(ws, widths=None):
    ws.freeze_panes = "A2"
    ws.sheet_view.showGridLines = False
    for cell in ws[1]:
        cell.font = Font(bold=True, color=white)
        cell.fill = PatternFill("solid", fgColor=navy)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[1].height = 32
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = Border(bottom=thin)
    if widths:
        for col, width in widths.items():
            ws.column_dimensions[col].width = width
    else:
        for col in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(col)].width = 22

def add_table(ws, headers, rows):
    ws.append(headers)
    for row in rows:
        ws.append(row)
    format_sheet(ws)

# Executive Summary
summary.append(["Metric", "Validated Result", "Interpretation"])
summary_rows = [
    ["Distinct orders", total_orders, "Each order counted once."],
    ["Eligible delivered orders", eligible_orders, "Excludes Shipping canceled."],
    ["Late delivery orders", late_orders, "Delivery Status = Late delivery."],
    ["Overall late delivery rate", late_orders / eligible_orders,
     "Late orders divided by eligible delivered orders."],
    ["Canceled orders", canceled_orders, "Reported separately from delivered orders."],
    ["Source validation", "PASS" if validation_passes else "FAIL",
     "All checks in the source shipping-mode workbook passed."],
    ["Carrier-level evidence", "Unavailable",
     "No carrier identifier is present in the analyzed source fields."],
]
for row in summary_rows:
    summary.append(row)
format_sheet(summary, {"A": 30, "B": 24, "C": 72})
summary["B5"].number_format = "0.00%"

# Shipping Mode Evidence
evidence_headers = [
    "Shipping Mode", "Total Orders", "Eligible Delivered Orders",
    "Canceled Orders", "Late Orders", "Strictly On-Time Orders",
    "Advance Shipping Orders", "On-Time or Early Orders",
    "Strict On-Time Rate", "On-Time or Early Rate", "Late Delivery Rate",
    "Average Actual Shipping Days", "Average Scheduled Shipping Days",
    "Average Schedule Variance (days)"
]
add_table(evidence, evidence_headers, [
    [r[h] for h in evidence_headers] for r in records
])
for row in range(2, evidence.max_row + 1):
    for col in (9, 10, 11):
        evidence.cell(row, col).number_format = "0.00%"
format_sheet(evidence)

# Prioritized Recommendations
rec_rows = [
    [
        "P1 - Critical investigation",
        "First Class",
        "9,602 eligible orders; 9,602 late; late rate 100%.",
        "Investigate the status assignment, promised delivery dates, scheduled duration, and operational records. Verify whether the pattern reflects genuine late delivery or a data/rule issue.",
        "Validated late-delivery rate; count of records reviewed; confirmed exception rate.",
        "Do not conclude that a carrier caused the result."
    ],
    [
        "P1 - High",
        "Second Class",
        "12,256 eligible orders; 9,803 late; late rate approximately 79.99%.",
        "Review late-order samples, dispatch timing, actual versus scheduled duration, and route or facility handoffs where those records are available.",
        "Monthly late rate; late-order count; schedule variance.",
        "Shipping mode is a segment, not a carrier."
    ],
    [
        "P2 - High",
        "Same Day",
        "3,407 eligible orders; 1,648 late; late rate approximately 48.37%. Scheduled duration averages zero days.",
        "Check the meaning and calculation of zero-day scheduled duration. Review promised-time definitions and timestamp granularity before judging service performance.",
        "Late rate; zero-day schedule records reviewed; timestamp completeness.",
        "A zero-day schedule may require interpretation before comparison."
    ],
    [
        "P2 - Medium",
        "Standard Class",
        "37,632 eligible orders; 14,995 late; late rate approximately 39.85%.",
        "Monitor this high-volume segment. Investigate late orders by month, region, and other available operational dimensions before proposing interventions.",
        "Late-order count and rate; monthly trend; regional breakdown where supported.",
        "Large volume means a substantial late-order count even with a lower rate."
    ],
    [
        "P1 - Data requirement",
        "All shipping modes",
        "No carrier identifier is available in the analyzed source fields.",
        "Obtain carrier ID/name, shipment-to-carrier assignment, pickup and delivery scan timestamps, service-level commitment, and exception reason.",
        "Carrier-level eligible orders, late rate, on-time rate, cancellation rate, and sample size.",
        "Do not rank or attribute performance to individual carriers without these fields."
    ],
]
add_table(
    recommendations,
    ["Priority", "Segment / Issue", "Supporting Evidence",
     "Recommended Follow-up", "Monitoring Measure", "Interpretation Safeguard"],
    rec_rows
)
format_sheet(recommendations, {
    "A": 22, "B": 22, "C": 48, "D": 70, "E": 48, "F": 48
})

# Carrier Data Gaps
gap_rows = [
    ["Carrier identifier/name", "Not available in analyzed fields",
     "Join shipment records to a carrier master or assignment table."],
    ["Carrier assignment history", "Not available",
     "Capture the carrier assigned to each shipment and any reassignment."],
    ["Pickup and delivery scan timestamps", "Not established by this analysis",
     "Capture event-level timestamps to measure transit stages."],
    ["Promised delivery timestamp", "Not established at carrier level",
     "Store the committed delivery date/time for each shipment."],
    ["Exception / delay reason", "Not available in analyzed fields",
     "Record standardized delay reason codes and supporting notes."],
    ["Route and facility handoffs", "Not established",
     "Capture origin, destination, route, and facility event history."],
    ["Carrier service type", "Not established",
     "Record the contracted service and service-level commitment."],
]
add_table(gaps, ["Required Field", "Current Availability", "Recommended Data Collection"], gap_rows)
format_sheet(gaps, {"A": 32, "B": 34, "C": 75})

# Follow-up Action Plan
action_rows = [
    ["1", "Data / Analytics", "Confirm delivery-status and scheduled-duration rules, especially First Class and Same Day.", "Before carrier-level comparison", "Documented definitions and exception review."],
    ["2", "Operations", "Review First Class late-order records and verify promised delivery expectations.", "High priority", "Reviewed sample and confirmed issue categories."],
    ["3", "Operations", "Investigate Second Class late orders and compare actual with scheduled duration.", "High priority", "Documented operational hypotheses."],
    ["4", "Data / IT", "Add carrier identifiers and shipment assignment history to the analysis dataset.", "Required prerequisite", "Carrier ID populated and validated."],
    ["5", "Analytics", "Build carrier-level KPIs only after carrier data and assignment history are available.", "After data availability", "Carrier-level rates with eligible denominators and sample sizes."],
    ["6", "Operations / Analytics", "Monitor monthly shipping-mode trends and investigate changes rather than assuming causes.", "Ongoing", "Monthly trend review and documented follow-ups."],
]
add_table(actions, ["Step", "Owner / Function", "Action", "Priority / Timing", "Completion Evidence"], action_rows)
format_sheet(actions, {"A": 10, "B": 24, "C": 78, "D": 28, "E": 55})

# Definitions and Limitations
definition_rows = [
    ["Unit of analysis", "Distinct Order Id; each order is counted once."],
    ["Eligible delivered orders", "All orders except Delivery Status = Shipping canceled."],
    ["Late delivery rate", "Late delivery orders / eligible delivered orders."],
    ["Strict on-time rate", "Shipping on time orders / eligible delivered orders."],
    ["On-time-or-early rate", "(Shipping on time + Advance shipping) / eligible delivered orders."],
    ["Schedule variance", "Average actual shipping days minus average scheduled shipping days; positive indicates later than scheduled."],
    ["Shipping mode", "A service/shipping category; it is not a carrier identity."],
    ["Carrier availability", "No carrier identifier exists in the source fields inspected for the existing analysis."],
    ["Cancellation handling", "Shipping canceled orders are counted separately and excluded from delivered-order rate denominators."],
    ["Interpretation", "The comparisons are descriptive. They do not establish causation or prove that a carrier or shipping mode caused delays."],
    ["Source", "reports/09_Carrier_Performance.xlsx; Shipping Mode Summary, Validation Checks, and Definitions and Limits."],
    ["Data baseline", f"{total_orders:,} distinct orders; {eligible_orders:,} eligible delivered orders; {late_orders:,} late orders."],
]
add_table(definitions, ["Item", "Definition / Limitation"], definition_rows)
format_sheet(definitions, {"A": 30, "B": 105})

# Apply visual cues to recommendation priorities.
for row in range(2, recommendations.max_row + 1):
    priority = recommendations.cell(row, 1).value
    fill = red if "Critical" in priority else orange if "High" in priority else green
    recommendations.cell(row, 1).fill = PatternFill("solid", fgColor=fill)
    recommendations.cell(row, 1).font = Font(bold=True)

# Add a chart of late delivery rates by shipping mode.
chart = BarChart()
chart.type = "bar"
chart.style = 10
chart.title = "Late Delivery Rate by Shipping Mode"
chart.y_axis.title = "Shipping Mode"
chart.x_axis.title = "Late Delivery Rate"
chart.height = 7
chart.width = 14
data = Reference(evidence, min_col=11, min_row=1, max_row=evidence.max_row)
cats = Reference(evidence, min_col=1, min_row=2, max_row=evidence.max_row)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.x_axis.numFmt = "0%"
summary.add_chart(chart, "E2")

for ws in wb.worksheets:
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_view.zoomScale = 90

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUTPUT)

# Reopen and verify workbook structure.
check = load_workbook(OUTPUT, data_only=True)
expected_sheets = [
    "Executive Summary", "Shipping Mode Evidence",
    "Prioritized Recommendations", "Carrier Data Gaps",
    "Follow-up Action Plan", "Definitions and Limitations"
]
if check.sheetnames != expected_sheets:
    raise AssertionError(f"Unexpected workbook sheets: {check.sheetnames}")
if check["Shipping Mode Evidence"].max_row != len(records) + 1:
    raise AssertionError("Shipping-mode evidence row count mismatch.")
if check["Prioritized Recommendations"].max_row != len(rec_rows) + 1:
    raise AssertionError("Recommendation row count mismatch.")

print(f"WORKBOOK CREATED: {OUTPUT}")
print("SHEETS:", check.sheetnames)
print("SHIPPING MODES:", len(records))
print("RECOMMENDATIONS:", len(rec_rows))
print("SOURCE VALIDATION CHECKS: PASS")
print("WORKBOOK STRUCTURAL CHECKS: PASS")
