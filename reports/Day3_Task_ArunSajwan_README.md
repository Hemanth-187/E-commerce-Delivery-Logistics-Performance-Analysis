# Week 2 Day 3 — Member 4

Files: `_Category_Distance_Analysis.xlsx`, `_category_distance_analysis.py`.

- Category rates are calculated from product-item rows because an order can contain items in multiple categories. Distinct order counts are also included; do not interpret item-row rates as unique-order rates.
- On-time is provisionally defined as `Delivery Status` = `Advance shipping` or `Shipping on time`. Eligible rows include those statuses plus `Late delivery`.
- Cancellation is defined as `Delivery Status` = `Shipping canceled`, which differs from `Order Status` = `CANCELED`.
- Delay proxy = `Days for shipping (real)` minus `Days for shipment (scheduled)`; this is not timestamp-based.
- Distance bands were not calculated because no explicit distance field was found. Coordinates were not converted to distance.
- Keep row-level customer data private, especially in a public GitHub repository.

Run script: `python _category_distance_analysis.py DataCoSupplyChain_M5_cleaned.zip`
Dependencies: pandas, numpy, openpyxl.
