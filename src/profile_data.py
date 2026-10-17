
from pathlib import Path

import pandas as pd


# Project root and input file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("Loading DataCo supply-chain dataset...")
    df = pd.read_csv(DATA_FILE, encoding="latin1", low_memory=False)

    print("\n--- Dataset Overview ---")
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")
    print(f"Exact duplicate rows: {df.duplicated().sum():,}")
    print(f"Unique orders: {df['Order Id'].nunique():,}")
    print(f"Unique order items: {df['Order Item Id'].nunique():,}")

    # Missing-value report
    missing = df.isna().sum().sort_values(ascending=False)
    missing_report = missing.rename_axis("column").reset_index(name="missing_count")
    missing_report["missing_percent"] = (
        missing_report["missing_count"] / len(df) * 100
    ).round(2)

    missing_report.to_csv(
        OUTPUT_DIR / "missing_values_report.csv", index=False
    )

    # Date validation
    order_dates = pd.to_datetime(
        df["order date (DateOrders)"], errors="coerce"
    )
    shipping_dates = pd.to_datetime(
        df["shipping date (DateOrders)"], errors="coerce"
    )

    print("\n--- Date Validation ---")
    print(f"Earliest order date: {order_dates.min()}")
    print(f"Latest order date: {order_dates.max()}")
    print(f"Invalid order dates: {order_dates.isna().sum():,}")
    print(f"Invalid shipping dates: {shipping_dates.isna().sum():,}")

    # Delivery status counts
    status_report = (
        df["Delivery Status"]
        .value_counts(dropna=False)
        .rename_axis("delivery_status")
        .reset_index(name="row_count")
    )
    status_report.to_csv(
        OUTPUT_DIR / "delivery_status_report.csv", index=False
    )

    print("\n--- Missing Values (Top 10) ---")
    print(missing_report.head(10).to_string(index=False))

    print("\nReports saved in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
