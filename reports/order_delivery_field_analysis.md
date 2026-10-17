# Order and Delivery Field Analysis

## Purpose

Inventory the order and delivery fields available in the source dataset.
This is a profiling report; it does not modify the source data.

## Dataset overview

- Rows: 180,519
- Columns: 53
- Unique order IDs: 65,752
- Unique order-item IDs: 180,519

## Field inventory

| Field | Available | Data type | Missing | Missing % | Unique values |
|---|---|---|---:|---:|---:|
| Order Id | True | int64 | 0 | 0.0 | 65752 |
| Order Item Id | True | int64 | 0 | 0.0 | 180519 |
| Order Status | True | str | 0 | 0.0 | 9 |
| order date (DateOrders) | True | str | 0 | 0.0 | 65752 |
| shipping date (DateOrders) | True | str | 0 | 0.0 | 63701 |
| Days for shipping (real) | True | int64 | 0 | 0.0 | 7 |
| Days for shipment (scheduled) | True | int64 | 0 | 0.0 | 4 |
| Delivery Status | True | str | 0 | 0.0 | 4 |
| Late_delivery_risk | True | int64 | 0 | 0.0 | 2 |

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

## Delivery status distribution

| Delivery status | Rows |
|---|---:|
| Late delivery | 98,977 |
| Advance shipping | 41,592 |
| Shipping on time | 32,196 |
| Shipping canceled | 7,754 |

## order date (DateOrders)

- Valid parsed dates: 180,519
- Unparseable or missing dates: 0
- Earliest date: 2015-01-01 00:00:00
- Latest date: 2018-01-31 23:38:00

## shipping date (DateOrders)

- Valid parsed dates: 180,519
- Unparseable or missing dates: 0
- Earliest date: 2015-01-03 00:00:00
- Latest date: 2018-02-06 22:14:00

## Date consistency check

- Rows with both dates parseable: 180,519
- Shipping dates earlier than order dates: 0

## Interpretation and limitations

- Order IDs can repeat because the dataset records order items, not just one row per order.
- Order Item Id is useful for distinguishing individual line items.
- Order status and delivery status are separate fields and should not be treated as interchangeable.
- Actual and scheduled shipping durations are distinct measures.
- The shipping-duration field should not automatically be described as total customer delivery time.
- Date parsing and chronology checks are initial diagnostics, not proof that every record is operationally correct.
- This report describes available fields and does not apply cleaning rules.

## Output files

- `reports/order_delivery_field_inventory.csv`
- `reports/order_delivery_field_analysis.md`
