# Delivery and Cancellation KPI Analysis

## 1. Objective

The objective of this analysis is to calculate the On-Time Delivery Rate and Cancellation Rate using the agreed KPI definitions. The analysis also validates the order counts used in each calculation.

## 2. Dataset

The analysis uses the cleaned interim DataCo dataset. Since the dataset contains multiple item-level records for some orders, distinct Order IDs are used to calculate order-level KPIs and prevent overcounting.

## 3. KPI Definitions and Methodology

### 3.1 On-Time Delivery Rate

The On-Time Delivery Rate measures the percentage of eligible delivered orders classified as on time or advance shipping.

**Formula:**

On-Time Delivery Rate = (On-time and advance orders / Eligible delivered orders) × 100

- Numerator: 26,849 orders
- Denominator: 62,897 orders
- Result: 42.69%

### 3.2 Cancellation Rate

The Cancellation Rate measures the percentage of distinct eligible orders marked with the Order Status of CANCELED.

**Formula:**

Cancellation Rate = (Cancelled orders / Total eligible orders) × 100

- Numerator: 1,367 orders
- Denominator: 65,752 orders
- Result: 2.08%

## 4. Validation

The cleaned dataset contains 180,519 rows and 65,752 distinct orders. Calculations are performed at the distinct-order level rather than the individual row level. The numerator counts are checked against their respective denominators to ensure that the percentages are valid.

## 5. Limitations

The dataset does not provide explicit promised and actual delivery timestamps suitable for direct comparison. Therefore, the On-Time Delivery Rate is calculated using Delivery Status categories as a proxy. Advance shipping and Shipping on time are counted as on-time outcomes, while Late delivery is excluded from the numerator. This assumption should be confirmed before the result is treated as a definitive operational KPI.

The cancellation calculation uses Order Status = CANCELED as the source of truth. The calculations cover the supplied dataset without applying a date filter.

## 6. Conclusion

The dataset-based On-Time Delivery Rate is 42.69%, while the Cancellation Rate is 2.08%. Distinct-order counting helps avoid overcounting item-level records. These results provide a baseline for delivery performance analysis, subject to the documented definition and data limitations.
