# Day 3 — Member 4: Validated Issue Ranking

## Purpose
Consolidates the Day 3 robustness checks into `_Validated_Issue_Ranking.xlsx`.

## Source availability
The workspace did not contain the three upstream Day 3 workbooks (`Overall_Total_Validation.xlsx`, `Sample_Size_Analysis.xlsx`, or `Robustness_Checks.xlsx`). Therefore, the checks in this workbook were independently reproduced from the cleaned M5 dataset and the previously created issue-ranking / bottleneck workbooks. This is not a claim that the three team members' files were received or reviewed.

## Core definitions
- Data grain: item-level rows; distinct `Order Id` is separately counted.
- Eligible delivery statuses: `Advance shipping`, `Shipping on time`, `Late delivery`.
- Provisional on-time statuses: `Advance shipping` and `Shipping on time`.
- Delay proxy: `Days for shipping (real)` minus `Days for shipment (scheduled)`.
- A positive delay proxy means actual duration exceeded scheduled duration; it is not a processing- or transit-stage measure.

## Workbook contents
1. **Validated Issue Ranking** — consolidated disposition of the main issue areas.
2. **Overall Validation** — overall totals and key missingness.
3. **Reconciliation Checks** — regional and category totals compared with overall eligible/on-time totals.
4. **Regional Robustness** — regional rates, order counts, sample flags and Wilson 95% intervals.
5. **Category Sample Checks** — category volumes and rates to identify unstable small samples.
6. **Missingness by Region** — checks whether duration missingness is concentrated geographically.
7. **Outlier Sensitivity** — mean/median delay proxy before and after documented 1st/99th percentile treatments.
8. **Method & Inputs** — assumptions, unavailable team files and interpretation limits.

## Important limitations
- Rates are item-row weighted, not order-weighted.
- Wilson intervals do not account for multiple items belonging to the same order.
- Region/category differences are descriptive, not causal.
- No validated carrier field, explicit dispatch timestamp, or explicit actual-delivery timestamp was identified in the prior audits. Carrier, processing-stage and transit-stage rankings therefore remain unconfirmed.
- The timestamp called `shipping date (DateOrders)` should not be treated as dispatch until its meaning is confirmed.
