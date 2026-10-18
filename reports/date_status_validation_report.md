# Date and Status Validation Report

## Scope

- Source: `data/raw/DataCoSupplyChainDataset.csv`
- Rows checked: 180,519
- The source CSV was read only; no source rows were modified.
- This report contains aggregate counts, not customer-level records.
- Flags identify items for review and do not automatically prescribe exclusions.

## Delivery status distribution

| Delivery status | Rows |
|---|---:|
| Late delivery | 98,977 |
| Advance shipping | 41,592 |
| Shipping on time | 32,196 |
| Shipping canceled | 7,754 |

## Order status distribution

| Order status | Rows |
|---|---:|
| COMPLETE | 59,491 |
| PENDING_PAYMENT | 39,832 |
| PROCESSING | 21,902 |
| PENDING | 20,227 |
| CLOSED | 19,616 |
| ON_HOLD | 9,804 |
| SUSPECTED_FRAUD | 4,062 |
| CANCELED | 3,692 |
| PAYMENT_REVIEW | 1,893 |

## Validation results

| Check | Field | Issues | Rows checked | Issue % | Interpretation |
|---|---|---:|---:|---:|---|
| Missing or unparseable order dates | order date (DateOrders) | 0 | 180,519 | 0.0000% | Review rows where the order date is unavailable or cannot be parsed. |
| Missing or unparseable shipping dates | shipping date (DateOrders) | 0 | 180,519 | 0.0000% | Review rows where the shipping date is unavailable or cannot be parsed. |
| Shipping date before order date | shipping date (DateOrders) vs order date (DateOrders) | 0 | 180,519 | 0.0000% | Potential chronology issue; investigate before deciding whether to exclude. |
| Missing or nonnumeric duration | Days for shipping (real) | 0 | 180,519 | 0.0000% | Duration is missing or could not be converted to a number. |
| Negative duration | Days for shipping (real) | 0 | 180,519 | 0.0000% | Negative durations are potential data-quality issues. |
| Zero duration | Days for shipping (real) | 5,080 | 180,519 | 2.8141% | Flagged for review only; zero may be valid under the dataset's conventions. |
| Missing or nonnumeric duration | Days for shipment (scheduled) | 0 | 180,519 | 0.0000% | Duration is missing or could not be converted to a number. |
| Negative duration | Days for shipment (scheduled) | 0 | 180,519 | 0.0000% | Negative durations are potential data-quality issues. |
| Zero duration | Days for shipment (scheduled) | 9,737 | 180,519 | 5.3939% | Flagged for review only; zero may be valid under the dataset's conventions. |
| Unexpected delivery status | Delivery Status | 0 | 180,519 | 0.0000% | Expected labels are based on the four observed delivery-status categories. |
| Risk flag missing or nonnumeric | Late_delivery_risk | 0 | 180,519 | 0.0000% | Review rows where the risk flag is unavailable or nonnumeric. |
| Risk flag outside expected 0/1 values | Late_delivery_risk | 0 | 180,519 | 0.0000% | This dataset's observed risk flag uses 0 and 1. |
| Canceled delivery with risk flag 1 | Delivery Status + Late_delivery_risk | 0 | 180,519 | 0.0000% | Review this combination; do not assume it is invalid without business rules. |
| Late delivery with risk flag 0 | Delivery Status + Late_delivery_risk | 0 | 180,519 | 0.0000% | Review potential disagreement between delivery label and risk flag. |
| Non-late delivery with risk flag 1 | Delivery Status + Late_delivery_risk | 0 | 180,519 | 0.0000% | Review potential disagreement between delivery label and risk flag. |
| Calendar-day difference vs reported actual duration mismatch | order date (DateOrders), shipping date (DateOrders), Days for shipping (real) | 0 | 180,519 | 0.0000% | Review mismatches; date-based calendar days may differ from the source's duration definition. |

## Interpretation and limitations

- Zero durations are flagged for review, not automatically treated as errors.
- Date-duration mismatches may result from different calculation conventions.
- Delivery-status/risk combinations are consistency checks, not proof of incorrect data.
- No rows are deleted, corrected, or excluded by this script.
- Any exclusion rules should be documented and approved before analysis.

Machine-readable summary: `reports/date_status_validation_summary.csv`
