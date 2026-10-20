# Order Volume and Trends Over Time

## 1. Objective

Analyze order volume over time using the DataCo supply-chain dataset to identify monthly and yearly patterns.

## 2. Dataset and Methodology

- Dataset: `data/raw/DataCoSupplyChainDataset.csv`
- Total dataset rows: 180,519
- Total unique orders: 65,752
- Order date field: `order date (DateOrders)`
- Order identifier: `Order Id`
- Date range: January 1, 2015 to January 31, 2018
- Missing or invalid order dates/order IDs: 0 rows

The dataset contains order-item-level records, so counting rows would overstate the number of orders. This analysis counts distinct `Order Id` values within each month and year.

## 3. Key Findings

- The dataset contains 65,752 unique orders across 180,519 rows.
- The highest monthly order count was 2,124 in December 2017.
- The highest yearly order count was 21,866 in 2017.
- The yearly counts were 20,904 in 2015, 20,859 in 2016, and 21,866 in 2017.
- January 2018 contained 2,123 orders, but the dataset ends on January 31, 2018. This is a partial year and should not be compared directly with complete calendar years.

## 4. Outputs

- `reports/monthly_order_volume.csv` — unique orders by month.
- `reports/yearly_order_volume.csv` — unique orders by year.
- `reports/order_volume_summary.csv` — key dataset and order-volume statistics.
- `reports/figures/monthly_order_volume.png` — monthly order-volume trend chart.
- `reports/figures/yearly_order_volume.png` — yearly order-volume chart.

## 5. Limitations

- The dataset covers January 2015 through January 2018 only.
- Monthly and yearly figures count distinct order IDs within each period.
- These are descriptive findings. The analysis does not establish the causes of changes in order volume.
- The 2018 total represents January only, not a complete year.

## 6. Conclusion

Order volume was broadly similar across 2015 and 2016, increased in 2017, and reached its highest monthly level in December 2017. These results provide an initial view of order-volume trends and can support further analysis of delivery performance and operational patterns.
