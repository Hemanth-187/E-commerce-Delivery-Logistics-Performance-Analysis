"""Validate order dates, shipping durations, and delivery statuses.

This script reads the raw source dataset without modifying it.
Generated reports contain aggregate validation results only.
"""
from pathlib import Path

import pandas as pd

from src.load_data import load_csv, PROJECT_ROOT

DATA_FILE = "DataCoSupplyChainDataset.csv"
REPORT_DIR = PROJECT_ROOT / "reports"

ORDER_DATE = "order date (DateOrders)"
SHIP_DATE = "shipping date (DateOrders)"
ACTUAL_DAYS = "Days for shipping (real)"
SCHEDULED_DAYS = "Days for shipment (scheduled)"
DELIVERY_STATUS = "Delivery Status"
RISK = "Late_delivery_risk"

EXPECTED_DELIVERY_STATUSES = {
    "Late delivery",
    "Advance shipping",
    "Shipping on time",
    "Shipping canceled",
}


def add_check(results, name, field, mask, total, interpretation):
    """Append one aggregate check result."""
    count = int(mask.fillna(False).sum())
    results.append({
        "check": name,
        "field": field,
        "issue_count": count,
        "rows_checked": int(total),
        "issue_percent": round(count / total * 100, 4) if total else 0.0,
        "interpretation": interpretation,
    })


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_csv(DATA_FILE, encoding="latin1", low_memory=False)
    total = len(df)
    results = []

    required = [
        ORDER_DATE, SHIP_DATE, ACTUAL_DAYS,
        SCHEDULED_DAYS, DELIVERY_STATUS, RISK,
    ]
    missing_columns = [col for col in required if col not in df.columns]
    if missing_columns:
        raise ValueError(
            "Required validation columns are missing: "
            + ", ".join(missing_columns)
        )

    order_dates = pd.to_datetime(df[ORDER_DATE], errors="coerce")
    ship_dates = pd.to_datetime(df[SHIP_DATE], errors="coerce")
    actual = pd.to_numeric(df[ACTUAL_DAYS], errors="coerce")
    scheduled = pd.to_numeric(df[SCHEDULED_DAYS], errors="coerce")
    status = df[DELIVERY_STATUS].astype("string").str.strip()
    risk = pd.to_numeric(df[RISK], errors="coerce")

    add_check(
        results, "Missing or unparseable order dates", ORDER_DATE,
        order_dates.isna(), total,
        "Review rows where the order date is unavailable or cannot be parsed.",
    )
    add_check(
        results, "Missing or unparseable shipping dates", SHIP_DATE,
        ship_dates.isna(), total,
        "Review rows where the shipping date is unavailable or cannot be parsed.",
    )

    valid_dates = order_dates.notna() & ship_dates.notna()
    add_check(
        results, "Shipping date before order date", f"{SHIP_DATE} vs {ORDER_DATE}",
        valid_dates & (ship_dates < order_dates), total,
        "Potential chronology issue; investigate before deciding whether to exclude.",
    )

    for field, values in [
        (ACTUAL_DAYS, actual),
        (SCHEDULED_DAYS, scheduled),
    ]:
        add_check(
            results, "Missing or nonnumeric duration", field,
            values.isna(), total,
            "Duration is missing or could not be converted to a number.",
        )
        add_check(
            results, "Negative duration", field,
            values < 0, total,
            "Negative durations are potential data-quality issues.",
        )
        add_check(
            results, "Zero duration", field,
            values == 0, total,
            "Flagged for review only; zero may be valid under the dataset's conventions.",
        )

    add_check(
        results, "Unexpected delivery status", DELIVERY_STATUS,
        status.isna() | ~status.isin(EXPECTED_DELIVERY_STATUSES),
        total,
        "Expected labels are based on the four observed delivery-status categories.",
    )

    add_check(
        results, "Risk flag missing or nonnumeric", RISK,
        risk.isna(), total,
        "Review rows where the risk flag is unavailable or nonnumeric.",
    )
    add_check(
        results, "Risk flag outside expected 0/1 values", RISK,
        risk.notna() & ~risk.isin([0, 1]), total,
        "This dataset's observed risk flag uses 0 and 1.",
    )

    canceled = status.eq("Shipping canceled")
    add_check(
        results, "Canceled delivery with risk flag 1",
        f"{DELIVERY_STATUS} + {RISK}",
        canceled & risk.eq(1), total,
        "Review this combination; do not assume it is invalid without business rules.",
    )

    late = status.eq("Late delivery")
    add_check(
        results, "Late delivery with risk flag 0",
        f"{DELIVERY_STATUS} + {RISK}",
        late & risk.eq(0), total,
        "Review potential disagreement between delivery label and risk flag.",
    )
    non_late = status.isin({"Advance shipping", "Shipping on time"})
    add_check(
        results, "Non-late delivery with risk flag 1",
        f"{DELIVERY_STATUS} + {RISK}",
        non_late & risk.eq(1), total,
        "Review potential disagreement between delivery label and risk flag.",
    )

    # Compare integer calendar-day difference with reported actual duration.
    # The dataset may use a different duration convention, so mismatches are
    # review flags rather than automatic errors.
    calendar_days = (
        ship_dates.dt.normalize() - order_dates.dt.normalize()
    ).dt.days
    comparable = valid_dates & actual.notna()
    add_check(
        results, "Calendar-day difference vs reported actual duration mismatch",
        f"{ORDER_DATE}, {SHIP_DATE}, {ACTUAL_DAYS}",
        comparable & (calendar_days != actual),
        total,
        "Review mismatches; date-based calendar days may differ from the source's duration definition.",
    )

    summary = pd.DataFrame(results)
    summary_path = REPORT_DIR / "date_status_validation_summary.csv"
    summary.to_csv(summary_path, index=False)

    lines = [
        "# Date and Status Validation Report",
        "",
        "## Scope",
        "",
        f"- Source: `data/raw/{DATA_FILE}`",
        f"- Rows checked: {total:,}",
        "- The source CSV was read only; no source rows were modified.",
        "- This report contains aggregate counts, not customer-level records.",
        "- Flags identify items for review and do not automatically prescribe exclusions.",
        "",
        "## Delivery status distribution",
        "",
        "| Delivery status | Rows |",
        "|---|---:|",
    ]
    counts = status.value_counts(dropna=False)
    for label, count in counts.items():
        safe_label = "(missing)" if pd.isna(label) else str(label)
        lines.append(f"| {safe_label.replace('|', '\\|')} | {int(count):,} |")

    lines += [
        "",
        "## Order status distribution",
        "",
        "| Order status | Rows |",
        "|---|---:|",
    ]
    order_status = df["Order Status"].astype("string").str.strip()
    for label, count in order_status.value_counts(dropna=False).items():
        safe_label = "(missing)" if pd.isna(label) else str(label)
        lines.append(f"| {safe_label.replace('|', '\\|')} | {int(count):,} |")

    lines += [
        "",
        "## Validation results",
        "",
        "| Check | Field | Issues | Rows checked | Issue % | Interpretation |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in results:
        check = row["check"].replace("|", "\\|")
        field = row["field"].replace("|", "\\|")
        note = row["interpretation"].replace("|", "\\|")
        lines.append(
            f'| {check} | {field} | {row["issue_count"]:,} | '
            f'{row["rows_checked"]:,} | {row["issue_percent"]:.4f}% | {note} |'
        )

    lines += [
        "",
        "## Interpretation and limitations",
        "",
        "- Zero durations are flagged for review, not automatically treated as errors.",
        "- Date-duration mismatches may result from different calculation conventions.",
        "- Delivery-status/risk combinations are consistency checks, not proof of incorrect data.",
        "- No rows are deleted, corrected, or excluded by this script.",
        "- Any exclusion rules should be documented and approved before analysis.",
        "",
        f"Machine-readable summary: `{summary_path.relative_to(PROJECT_ROOT)}`",
        "",
    ]
    report_path = REPORT_DIR / "date_status_validation_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Rows checked: {total:,}")
    print(f"Summary saved: {summary_path.relative_to(PROJECT_ROOT)}")
    print(f"Report saved: {report_path.relative_to(PROJECT_ROOT)}")
    print("\nValidation checks:")
    print(summary[["check", "issue_count", "issue_percent"]].to_string(index=False))


if __name__ == "__main__":
    main()
