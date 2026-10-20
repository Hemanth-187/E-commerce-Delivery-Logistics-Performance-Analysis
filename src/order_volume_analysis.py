"""Analyze order volume and trends over time."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"
REPORT_DIR = PROJECT_ROOT / "reports"
FIGURE_DIR = REPORT_DIR / "figures"

DATE_COLUMN = "order date (DateOrders)"
ORDER_ID_COLUMN = "Order Id"


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading order data...")
    df = pd.read_csv(DATA_FILE, encoding="latin1", low_memory=False)

    required = [DATE_COLUMN, ORDER_ID_COLUMN]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Required columns not found: {missing}")

    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
    valid = df.dropna(subset=[DATE_COLUMN, ORDER_ID_COLUMN]).copy()

    if valid.empty:
        raise ValueError("No valid order dates and order IDs were found.")

    valid["Order Month"] = valid[DATE_COLUMN].dt.to_period("M").dt.to_timestamp()
    valid["Order Year"] = valid[DATE_COLUMN].dt.year

    # Dataset rows represent order items, so count distinct Order Id values.
    monthly = (
        valid.groupby("Order Month")[ORDER_ID_COLUMN]
        .nunique()
        .reset_index(name="Unique Orders")
    )
    monthly.to_csv(REPORT_DIR / "monthly_order_volume.csv", index=False)

    yearly = (
        valid.groupby("Order Year")[ORDER_ID_COLUMN]
        .nunique()
        .reset_index(name="Unique Orders")
    )
    yearly.to_csv(REPORT_DIR / "yearly_order_volume.csv", index=False)

    summary = pd.DataFrame(
        [
            {"Metric": "Dataset rows", "Value": len(df)},
            {"Metric": "Rows with valid order date and order ID", "Value": len(valid)},
            {"Metric": "Rows with invalid or missing order date or order ID",
             "Value": len(df) - len(valid)},
            {"Metric": "Unique orders in valid rows",
             "Value": valid[ORDER_ID_COLUMN].nunique()},
            {"Metric": "First order date", "Value": valid[DATE_COLUMN].min()},
            {"Metric": "Last order date", "Value": valid[DATE_COLUMN].max()},
            {"Metric": "Month with most unique orders",
             "Value": monthly.loc[monthly["Unique Orders"].idxmax(), "Order Month"].strftime("%Y-%m")},
            {"Metric": "Highest monthly unique-order count",
             "Value": int(monthly["Unique Orders"].max())},
            {"Metric": "Year with most unique orders",
             "Value": int(yearly.loc[yearly["Unique Orders"].idxmax(), "Order Year"])},
            {"Metric": "Highest yearly unique-order count",
             "Value": int(yearly["Unique Orders"].max())},
        ]
    )
    summary.to_csv(REPORT_DIR / "order_volume_summary.csv", index=False)

    plt.figure(figsize=(12, 6))
    plt.plot(monthly["Order Month"], monthly["Unique Orders"], marker="o")
    plt.title("Monthly Order Volume")
    plt.xlabel("Order month")
    plt.ylabel("Number of unique orders")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "monthly_order_volume.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.bar(yearly["Order Year"].astype(str), yearly["Unique Orders"])
    plt.title("Yearly Order Volume")
    plt.xlabel("Order year")
    plt.ylabel("Number of unique orders")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "yearly_order_volume.png", dpi=150)
    plt.close()

    print("\nAnalysis complete.")
    print(f"Dataset rows: {len(df):,}")
    print(f"Rows included: {len(valid):,}")
    print(f"Unique orders: {valid[ORDER_ID_COLUMN].nunique():,}")
    print(f"Date range: {valid[DATE_COLUMN].min()} to {valid[DATE_COLUMN].max()}")
    print("\nMonthly order volume:")
    print(monthly.to_string(index=False))
    print("\nYearly order volume:")
    print(yearly.to_string(index=False))
    print("\nFiles created:")
    print(f"- {REPORT_DIR / 'monthly_order_volume.csv'}")
    print(f"- {REPORT_DIR / 'yearly_order_volume.csv'}")
    print(f"- {REPORT_DIR / 'order_volume_summary.csv'}")
    print(f"- {FIGURE_DIR / 'monthly_order_volume.png'}")
    print(f"- {FIGURE_DIR / 'yearly_order_volume.png'}")


if __name__ == "__main__":
    main()
