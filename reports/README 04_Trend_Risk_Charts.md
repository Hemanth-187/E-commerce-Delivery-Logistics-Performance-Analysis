# Week 3 Day 4 — Member 4: Trend & Risk Charts

## Deliverable
`16_Trend_Risk_Charts.xlsx`

## What it contains
- **Trend Charts:** monthly on-time rate, average delay proxy, and on-time trend for five highest-volume regions.
- **Monthly Trend Data:** month-level counts, distinct orders, on-time/late counts and duration statistics.
- **Regional Summary:** overall regional volumes and outcomes.
- **Top Region Trends:** monthly region data for selected regions.
- **Region Rate Chart Data:** pivot data supporting the regional trend chart.
- **Method & Limitations:** field definitions, date coverage, exclusions, and caveats.

## Method
- Month is based on `order date (DateOrders)`.
- Primary grain is item-level rows; distinct Order Id is reported separately.
- Eligible statuses: `Advance shipping`, `Shipping on time`, and `Late delivery`.
- Provisional on-time statuses: `Advance shipping` and `Shipping on time`.
- Delay proxy = `Days for shipping (real)` − `Days for shipment (scheduled)`.

## Important limitations
- This is descriptive trend analysis, not a predictive risk model.
- Delay proxy does not separate processing from transit.
- `shipping date (DateOrders)` is not assumed to be dispatch or actual delivery.
- Regional comparisons are descriptive and not causal.
- Rates are item-row weighted; multiple items may belong to the same order.
- A predictive model should only be reported if Member 3 evaluates it on a held-out set against a simple baseline.
