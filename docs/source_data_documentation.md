# Source Data Documentation

## 1. Purpose

This document records the source files used or considered for the
E-commerce Delivery & Logistics Performance Analysis project. It documents
source-file integrity, intended use, known limitations, and handling rules.

## 2. Source-file inventory

All three files below were found in `data/raw/` and compared with files in
`~/Downloads/Data/`.

| File | Intended role | Integrity check |
|---|---|---|
| `DataCoSupplyChainDataset.csv` | Primary order, shipment, delivery, and customer/order analysis dataset | SHA-256 matched the local Downloads copy |
| `DescriptionDataCoSupplyChain.csv` | Supporting descriptions of dataset fields | SHA-256 matched the local Downloads copy |
| `tokenized_access_logs.csv` | Separate access-log dataset; use only if confirmed relevant to the approved project scope | SHA-256 matched the local Downloads copy |

The access-log file is not assumed to be required for the core delivery
performance analysis. Its relevance, provenance, and permission for use
should be confirmed before it is incorporated into analysis.

## 3. Integrity verification

SHA-256 hashes were calculated using `shasum -a 256` for each file in
`data/raw/` and its corresponding file in `~/Downloads/Data/`.

| File | SHA-256 |
|---|---|
| `DataCoSupplyChainDataset.csv` | `fa6d022ed437155e1a2f0378710602848703c8a7f203f7ff5d77805bf8480aa6` |
| `DescriptionDataCoSupplyChain.csv` | `9828e34669bd6d77e3b4463364cc44a5d52446b5e246fc258758cfe592566c4b` |
| `tokenized_access_logs.csv` | `7a4372df63a1e87f5add68bc036bb6064db09069998f25a679aec39f1a8d7765` |

All three repository files matched their corresponding local Downloads copies.
This confirms byte-for-byte equality with those local copies at the time of
verification. It does not independently establish the original publisher,
authenticity, license, or permission to redistribute the files.

## 4. Primary dataset profile

Initial local inspection of `DataCoSupplyChainDataset.csv` reported:

- Rows: 180,519
- Columns: 53
- Order-date range: 2015-01-01 through 2018-01-31
- Shipping-date range: 2015-01-03 through 2018-02-06
- Exact duplicate rows in the earlier profile: 0
- Unique order IDs in the earlier profile: 65,752
- Unique order-item IDs in the earlier profile: 180,519

The dataset contains order and delivery fields such as:

- `Order Id` and `Order Item Id`
- `Order Status` and `Delivery Status`
- `order date (DateOrders)` and `shipping date (DateOrders)`
- `Days for shipping (real)` and `Days for shipment (scheduled)`
- `Late_delivery_risk`

These values describe the dataset as inspected locally and should be
revalidated if a different source file is introduced.

## 5. Known field and interpretation limitations

- An order may contain multiple order-item rows. Repeated `Order Id` values
  are not automatically duplicate records.
- `Order Status` and `Delivery Status` describe different concepts and
  should not be treated as interchangeable.
- Actual and scheduled shipping durations are distinct fields.
- Date-derived calendar-day differences may use a different convention from
  the dataset's reported duration values.
- Zero duration values should be investigated in context; they are not
  automatically invalid.
- A reported association between delivery status and another field does not
  by itself establish causation.
- Earlier profiling found `Product Description` missing for all rows and
  `Order Zipcode` missing for a large proportion of rows. Review
  `reports/missing_values_report.csv` for the detailed missingness results.

## 6. Source provenance and licensing

The original publisher, original download URL, acquisition date, and license
or redistribution terms have not yet been independently verified in this
repository documentation. Record these details only after checking the
original source or its accompanying license.

Do not assume that a file being available locally or online grants permission
to publish it in a public repository.

## 7. Privacy and repository handling

The primary dataset includes customer-related fields. Before publishing raw
data, confirm its provenance, license, permitted use, and privacy implications.
Do not expose personal or sensitive information without explicit authorization
and an appropriate review.

The raw files must remain unchanged. Analysis scripts should read from
`data/raw/` and write derived results to `reports/` or other designated
output directories. Any cleaning or exclusions must be documented separately;
they must not silently overwrite the source files.

## 8. Day 2 integrity and validation outputs

- `src/validate_dates_status.py` performs aggregate date, duration, and
  delivery-status checks.
- `reports/date_status_validation_summary.csv` stores machine-readable
  validation counts.
- `reports/date_status_validation_report.md` describes the validation checks
  and their results.

These reports flag potential issues for review. They do not automatically
correct or exclude records.
