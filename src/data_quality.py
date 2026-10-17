"""Basic data-quality profiling helpers."""
import pandas as pd

def profile_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return column type, missingness, and distinct-value counts."""
    return pd.DataFrame({
        "column": df.columns,
        "dtype": [str(df[c].dtype) for c in df.columns],
        "missing_count": [int(df[c].isna().sum()) for c in df.columns],
        "missing_percent": [round(float(df[c].isna().mean() * 100), 2) for c in df.columns],
        "distinct_count": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })

def duplicate_summary(df: pd.DataFrame) -> dict:
    """Summarize exact duplicate rows; repeated order IDs may be legitimate."""
    count = int(df.duplicated().sum())
    return {"row_count": int(len(df)), "exact_duplicate_rows": count,
            "exact_duplicate_percent": round(count / len(df) * 100, 2) if len(df) else 0.0}
