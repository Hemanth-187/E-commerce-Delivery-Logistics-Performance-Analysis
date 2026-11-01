# Week 3 Interim Report — Supply Chain Delivery Analysis

## Files
- `_Week3_Interim_Report_Findings.xlsx` — findings populated from the cleaned dataset.
- This workbook is an evidence-backed interim draft By Member 4;

## Workbook sheets
1. Executive Summary
2. Prioritized Issues
3. Monthly Trends (includes a line chart)
4. Regional Findings
5. Cancellation by Region
6. Shipping Mode Findings
7. Status Distribution
8. Recommendations
9. Limitations
10. Week 3 Review

## Core definitions
- Eligible delivery statuses: `Advance shipping`, `Shipping on time`, and `Late delivery`.
- On-time rate: `(Advance shipping + Shipping on time) / eligible item rows`.
- Late-delivery rate: `Late delivery / eligible item rows`.
- Cancellation count: rows with `Delivery Status = Shipping canceled`.
- Delay proxy: `Days for shipping (real) - Days for shipment (scheduled)`.

## Important caveats
- Rates are item-row weighted, not order-weighted.
- The analysis is descriptive; observed differences do not establish causes.
- The cleaned dataset did not show an explicit carrier identifier, dispatch timestamp, or actual delivery timestamp. Carrier-specific claims and stage-level delay attribution are therefore not supported by this file alone.
- Regional and shipping-mode differences may reflect shipment/order mix. Show volume and validate comparisons.
- Dataset order dates are historical (2015–2018); confirm with current operational data before acting.
- Member 3 model validation (held-out set vs baseline) is not included; add it only after checking their notebook/output.
