# Data-quality log

| Check | Finding | Decision/action | Owner | Status |
|---|---|---|---|---|
| Column names and types | Initial dataset profile recorded: 180,519 rows and 53 columns | Review field meanings and data types before analysis | Member 1 / team | Initial profile recorded; further review pending |
| Missing values | Key missing-value counts documented; `Product Description` is entirely missing | Assess each field's analytical usefulness before deciding whether to exclude or retain it | Member 1 / team | Initial assessment recorded; treatment pending |
| Exact duplicate rows | 0 exact duplicate rows in the initial audit | Keep this check separate from repeated order IDs and order-item records | Member 1 / team | Initial check complete |
| Category consistency | Category-label consistency has not yet been documented in this audit | Inspect distinct labels and document any inconsistencies before normalization | Assigned team member | Pending validation |
| Date fields | Order-date range recorded; 0 invalid order dates in the initial audit | Validate shipping dates and other relevant date fields before calculating delivery metrics | Member 1 / team | Partially assessed; further validation pending |

## Initial dataset audit

**Dataset:** `DataCoSupplyChainDataset.csv`

- Rows: 180,519
- Columns: 53
- Exact duplicate rows: 0
- Unique orders: 65,752
- Unique order-item IDs: 180,519
- Order date range: 2015-01-01 to 2018-01-31
- Invalid order dates: 0
- `Product Description`: entirely missing (180,519 rows)
- `Order Zipcode`: missing in 155,679 rows
- `Customer Lname`: missing in 8 rows
- `Customer Zipcode`: missing in 3 rows
- `Late_delivery_risk = 1`: 98,977 rows
- `Late_delivery_risk = 0`: 81,542 rows

## Initial handling decisions

1. Preserve the raw source files unchanged.
2. Exclude the fully missing `Product Description` column from analyses that do not require it.
3. Avoid using customer-identifying fields in public reports.
4. Parse order and shipping date fields before calculating time-based metrics.
5. Treat `Late_delivery_risk` as a supplied dataset flag, not as an independently validated outcome.
6. Define delivery KPIs carefully and handle canceled shipments separately.
7. Distinguish order counts from order-item row counts.

## Additional data sources

- `DescriptionDataCoSupplyChain.csv`: field descriptions.
- `tokenized_access_logs.csv`: product access events with date, hour, category, department, IP, and URL fields. Relationship to order records remains to be verified.

## Overall status

**Initial profiling complete; further validation required before cleaning and KPI calculations.** The status table distinguishes completed initial checks from work that still requires validation. No raw source data has been modified.