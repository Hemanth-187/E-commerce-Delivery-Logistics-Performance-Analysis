# Delivery Bottleneck Analysis — Member 4

## Purpose
Combine available time-based measures and document whether processing and transit stages can be separated.

## Key limitation
The dataset has order and shipping date fields, but no explicit dispatch timestamp or actual-delivery timestamp was identified by field-name audit. The meaning of `shipping date (DateOrders)` is unverified. Confirmed order-processing time and dispatch-to-delivery transit time therefore cannot be calculated from currently verified fields.

## Available measures
- Order-to-shipping timestamp interval is an observable proxy only; do not call it processing time until timestamp semantics are confirmed.
- `Days for shipping (real) - Days for shipment (scheduled)` is a duration-based delay proxy, not stage-specific.
- Regional overall outcomes can be compared, but processing vs transit cannot be isolated.

## Caveats
- Dataset is item-level; row counts are not order counts.
- Status-based on-time rate is provisional.
- No obvious carrier/shipper field was identified.
- Do not commit raw customer-level data to a public repository.
