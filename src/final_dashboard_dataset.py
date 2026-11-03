"""Build the Power BI-ready Day 1 dashboard dataset from the validated KPI workbook."""

from pathlib import Path
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "17_Final_KPI_Dataset.xlsx"
OUTPUT = ROOT / "reports" / "01_Final_Dashboard_Dataset.xlsx"

def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source workbook not found: {SOURCE}")

    print("Reading validated KPI workbook...")
    orders = pd.read_excel(SOURCE, sheet_name="Order-Level KPI Dataset")
    kpis = pd.read_excel(SOURCE, sheet_name="KPI Summary")
    delivery = pd.read_excel(SOURCE, sheet_name="Delivery Status Breakdown")
    shipping = pd.read_excel(SOURCE, sheet_name="Shipping Mode Comparison")

    required = [
        "Order Id", "Order_Status", "Delivery_Status", "Shipping_Mode",
        "Actual_Shipping_Days", "Scheduled_Shipping_Days",
        "Late_Delivery_Risk", "Order_Date", "Shipping_Date",
        "Source_Item_Rows", "Distinct_Order_Item_IDs",
        "Duration_Variance_Days", "Order_to_Shipment_Elapsed_Days"
    ]
    missing = sorted(set(required) - set(orders.columns))
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    orders["Order_Date"] = pd.to_datetime(orders["Order_Date"], errors="coerce")
    orders["Shipping_Date"] = pd.to_datetime(orders["Shipping_Date"], errors="coerce")

    # Power BI-friendly date attributes derived from the order date.
    orders["Order_Year"] = orders["Order_Date"].dt.year.astype("Int64")
    orders["Order_Month_Number"] = orders["Order_Date"].dt.month.astype("Int64")
    orders["Order_Month_Name"] = orders["Order_Date"].dt.month_name()
    orders["Order_Year_Month"] = orders["Order_Date"].dt.strftime("%Y-%m")
    orders["Order_Weekday_Number"] = orders["Order_Date"].dt.weekday + 1
    orders["Order_Weekday_Name"] = orders["Order_Date"].dt.day_name()

    delivery_status = orders["Delivery_Status"].astype("string").str.strip()
    order_status = orders["Order_Status"].astype("string").str.strip()

    # Numeric 1/0 flags are convenient for Power BI measures.
    orders["Is_Shipping_Canceled"] = delivery_status.eq("Shipping canceled").astype("int8")
    orders["Is_Eligible_Non_Canceled"] = (1 - orders["Is_Shipping_Canceled"]).astype("int8")
    orders["Is_Late_Delivery"] = delivery_status.eq("Late delivery").astype("int8")
    orders["Is_Strict_On_Time"] = delivery_status.eq("Shipping on time").astype("int8")
    orders["Is_Advance_Shipping"] = delivery_status.eq("Advance shipping").astype("int8")
    orders["Is_Order_Status_Canceled"] = order_status.eq("CANCELED").astype("int8")

    total_orders = len(orders)
    eligible = int(orders["Is_Eligible_Non_Canceled"].sum())
    canceled = int(orders["Is_Shipping_Canceled"].sum())
    late = int(orders["Is_Late_Delivery"].sum())
    on_time = int(orders["Is_Strict_On_Time"].sum())
    advance = int(orders["Is_Advance_Shipping"].sum())

    checks = [
        ("Order-level row count", total_orders, 65752, total_orders == 65752,
         "Expected one row per distinct Order Id."),
        ("Unique Order Id count", int(orders["Order Id"].nunique()), total_orders,
         orders["Order Id"].is_unique, "Order Id must be unique in this dataset."),
        ("Missing Order Id values", int(orders["Order Id"].isna().sum()), 0,
         orders["Order Id"].notna().all(), "No missing order identifiers allowed."),
        ("Eligible plus shipping-canceled", eligible + canceled, total_orders,
         eligible + canceled == total_orders,
         "Eligible excludes Delivery_Status = Shipping canceled."),
        ("Delivery status flags reconcile", late + on_time + advance + canceled,
         total_orders, late + on_time + advance + canceled == total_orders,
         "Checks the four recognized delivery status categories."),
        ("Order dates parse", int(orders["Order_Date"].isna().sum()), 0,
         orders["Order_Date"].notna().all(), "All order dates should parse."),
        ("Shipping dates parse", int(orders["Shipping_Date"].isna().sum()), 0,
         orders["Shipping_Date"].notna().all(), "All shipping dates should parse."),
        ("No shipping date before order date",
         int((orders["Shipping_Date"] < orders["Order_Date"]).sum()), 0,
         (orders["Shipping_Date"] >= orders["Order_Date"]).all(),
         "Checks timestamp order."),
        ("KPI flag values are binary",
         int((~orders[["Is_Shipping_Canceled", "Is_Eligible_Non_Canceled",
                       "Is_Late_Delivery", "Is_Strict_On_Time",
                       "Is_Advance_Shipping", "Is_Order_Status_Canceled"]]
              .isin([0, 1])).sum().sum()), 0,
         orders[["Is_Shipping_Canceled", "Is_Eligible_Non_Canceled",
                 "Is_Late_Delivery", "Is_Strict_On_Time",
                 "Is_Advance_Shipping", "Is_Order_Status_Canceled"]]
              .isin([0, 1]).all().all(),
         "All dashboard indicator fields must contain 0 or 1."),
    ]
    validation = pd.DataFrame(
        checks, columns=["Check", "Actual", "Expected", "Passed", "Notes"]
    )

    dashboard_kpis = pd.DataFrame([
        ("Total Orders", total_orders, "orders",
         "Count of unique Order Id values."),
        ("Eligible Non-Canceled Orders", eligible, "orders",
         "Orders excluding Delivery_Status = Shipping canceled."),
        ("Shipping-Canceled Orders", canceled, "orders",
         "Delivery_Status = Shipping canceled."),
        ("Late Delivery Orders", late, "orders",
         "Delivery_Status = Late delivery."),
        ("Strict On-Time Orders", on_time, "orders",
         "Delivery_Status = Shipping on time; Advance shipping excluded."),
        ("Advance Shipping Orders", advance, "orders",
         "Kept separate from strict on-time."),
        ("Strict On-Time Status Rate", on_time / eligible * 100 if eligible else None,
         "%", "Strict on-time orders / eligible non-canceled orders × 100."),
        ("Late Delivery Status Rate", late / eligible * 100 if eligible else None,
         "%", "Late delivery orders / eligible non-canceled orders × 100."),
        ("On-Time-or-Early Status Rate",
         (on_time + advance) / eligible * 100 if eligible else None,
         "%", "(Strict on-time + advance shipping) / eligible orders × 100."),
        ("Order Status CANCELED Orders",
         int(orders["Is_Order_Status_Canceled"].sum()), "orders",
         "Separate from Delivery_Status = Shipping canceled."),
    ], columns=["KPI", "Value", "Unit", "Definition"])

    definitions = pd.DataFrame([
        ("Analysis grain", "One row per distinct Order Id.",
         "Source CSV rows represent order items, not orders."),
        ("Date filtering", "Order_Date is the primary reporting date.",
         "Year, month, year-month and weekday columns are derived from Order_Date."),
        ("Strict on-time", "Delivery_Status = Shipping on time.",
         "Advance shipping is not included in strict on-time."),
        ("Eligible denominator", "All orders except Delivery_Status = Shipping canceled.",
         "Provisional eligibility rule; confirm with the project team."),
        ("Cancellation", "Order_Status = CANCELED and Delivery_Status = Shipping canceled are separate.",
         "Do not combine these fields or treat them as interchangeable."),
        ("Shipping mode", "Shipping_Mode is a shipping service category.",
         "It is not a carrier identifier; carrier-level performance is unavailable."),
        ("Duration variance", "Actual_Shipping_Days minus Scheduled_Shipping_Days.",
         "Do not describe as timestamp-based delivery delay."),
        ("Order-to-shipment elapsed time", "Shipping_Date minus Order_Date.",
         "Not automatically equivalent to warehouse processing time."),
        ("Late delivery risk", "Source-provided 0/1 field.",
         "Retained as supplied; not independently validated as a predictive measure."),
        ("Unavailable KPI", "Customer rating by delivery outcome.",
         "No verified customer-rating field or order-level rating linkage identified."),
        ("Unavailable KPI", "Timestamp-based delivery delay.",
         "No separate actual-delivery and promised-delivery timestamps identified."),
        ("Privacy", "No direct customer identifiers included.",
         "Do not add customer names, emails, passwords or customer IDs."),
        ("Interpretation", "Descriptive analysis only.",
         "Segment differences do not prove causes."),
    ], columns=["Topic", "Rule", "Explanation"])

    if not validation["Passed"].all():
        raise ValueError(
            "Dashboard dataset validation failed:\n"
            + validation.loc[~validation["Passed"]].to_string(index=False)
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT, engine="openpyxl",
                       datetime_format="yyyy-mm-dd hh:mm:ss") as writer:
        orders.to_excel(writer, sheet_name="Dashboard Dataset", index=False)
        dashboard_kpis.to_excel(writer, sheet_name="Dashboard KPI Summary", index=False)
        delivery.to_excel(writer, sheet_name="Delivery Status Breakdown", index=False)
        shipping.to_excel(writer, sheet_name="Shipping Mode Comparison", index=False)
        validation.to_excel(writer, sheet_name="Validation Checks", index=False)
        definitions.to_excel(writer, sheet_name="Definitions and Limits", index=False)
        kpis.to_excel(writer, sheet_name="Original KPI Reference", index=False)

        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            ws.sheet_view.showGridLines = False
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="1F4E78")
                cell.alignment = Alignment(wrap_text=True, vertical="center")
            ws.row_dimensions[1].height = 30
            for col_idx, cells in enumerate(ws.columns, start=1):
                width = max(
                    (len(str(c.value)) if c.value is not None else 0)
                    for c in list(cells)[:200]
                )
                ws.column_dimensions[get_column_letter(col_idx)].width = min(
                    max(width + 2, 12), 38
                )

    # Reopen the generated workbook to verify its structure and row count.
    check = pd.read_excel(OUTPUT, sheet_name="Dashboard Dataset")
    if len(check) != total_orders or not check["Order Id"].is_unique:
        raise ValueError("Generated workbook failed its final read-back check.")

    print(f"\nCreated: {OUTPUT}")
    print(f"Dashboard dataset rows: {len(check):,}")
    print(f"Dashboard dataset columns: {len(check.columns)}")
    print(f"Eligible non-canceled orders: {eligible:,}")
    print(f"Shipping-canceled orders: {canceled:,}")
    print(f"Validation checks passed: {int(validation['Passed'].sum())}/{len(validation)}")
    print("Final workbook read-back check: PASS")

if __name__ == "__main__":
    main()
