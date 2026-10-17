# Data-quality log

| Check | Finding | Decision/action | Owner | Status |
|---|---|---|---|---|
| Column names and types | Pending | Profile source data | TBD | Not started |
| Missing values | Pending | Quantify before deciding treatment | TBD | Not started |
| Exact duplicate rows | Pending | Audit separately from repeated order IDs | TBD | Not started |
| Category consistency | Pending | Inspect distinct labels; document normalization | TBD | Not started |
| Date fields | Pending | Validate formats and ranges | TBD | Not started |
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

**Initial handling decisions**

1. Preserve the raw source files unchanged.
2. Exclude the fully missing `Product Description` column from analyses that do not require it.
3. Avoid using customer-identifying fields in public reports.
4. Parse order and shipping date fields before calculating time-based metrics.
5. Treat `Late_delivery_risk` as a supplied dataset flag, not as an independently validated outcome.
6. Define delivery KPIs carefully and handle canceled shipments separately.
7. Distinguish order counts from order-item row counts.

**Additional data sources**

- `DescriptionDataCoSupplyChain.csv`: field descriptions.
- `tokenized_access_logs.csv`: product access events with date, hour, category, department, IP, and URL fields. Relationship to order records remains to be verified.

**Status:** Initial profiling complete; further validation required before cleaning and KPI calculations.