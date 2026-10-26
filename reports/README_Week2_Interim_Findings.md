# Week 2 — Interim Findings (Member 4)

## Purpose
This document consolidates the preliminary Week 2 findings, KPI definitions, validation checks, and open decisions for the ecommerce logistics analysis.

## Dataset scope
- Source dataset: `DataCoSupplyChainDataset.csv`
- Total rows: 180,519
- Distinct orders (`Order Id`): 65,752
- Distinct order-item IDs (`Order Item Id`): 180,519

The data is item-level, not order-level. Each order can contain multiple items; therefore, item-row counts must not be interpreted as unique order counts.

## Business context and data structure
- The dataset contains supply-chain transaction records with order, customer, product, and logistics attributes.
- The main operational fields relevant to KPI construction include delivery status, shipping durations, order timing, order status, and category labels.
- A quality review identified no duplicate rows, but some fields are missing or incomplete, including `Product Description` and `Order Zipcode`.

## Interim findings
- `Delivery Status` includes the following categories: `Advance shipping`, `Shipping on time`, `Late delivery`, and `Shipping canceled`.
- `Delivery Status = Shipping canceled` is not interchangeable with `Order Status = CANCELED`.
- Delay proxy used for shipment performance analysis: `Days for shipping (real) - Days for shipment (scheduled)`.
- No customer-rating field was identified in the supplied dataset; any rating comparison would require a separate matched source.
- No explicit distance field was found; distance-band analysis is unsupported without a validated distance measure or geospatial conversion method.
- Processing-time interpretation requires confirmation of timestamp semantics before final KPI logic is locked in.
- Category-based analysis should be performed at the product-item level because one order can include several product categories; rate calculations should not be reported as unique-order rates.

## KPI interpretation and validation guardrails
- On-time performance is provisionally defined as `Delivery Status` in `{Advance shipping, Shipping on time}`.
- Late delivery is tracked as a distinct, non-on-time outcome and should not be merged with cancellations.
- Cancellation analysis should be based on `Delivery Status = Shipping canceled`, not on `Order Status = CANCELED`, unless the business explicitly defines both as equivalent.
- The delay proxy is not a true timestamp-based lead-time measure; it is a scheduled-versus-actual difference derived from shipping duration fields.
- Customer-level confidentiality should be preserved, especially because publicly shared outputs may include personal or location identifiers.

## Open decisions and pending confirmations
1. Confirm the business meaning of the shipping date fields to ensure the actual delay logic aligns with operational reality.
2. Decide whether cancellation metrics should use `Delivery Status`, `Order Status`, or both depending on the KPI objective.
3. Determine whether distance analysis should rely on a derived distance measure or external data.
4. Confirm how `Advance shipping` should be treated in the final on-time definition and whether it is considered equivalent to on-time delivery.
5. Validate whether any external rating or customer-satisfaction dataset will be added for benchmarking.
