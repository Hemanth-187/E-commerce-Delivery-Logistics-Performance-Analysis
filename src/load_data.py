"""Helpers for loading local project data."""
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

def load_csv(filename: str, **kwargs) -> pd.DataFrame:
    """Load a CSV from data/raw without changing the source file."""
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Place the approved source CSV at: {path}")
    return pd.read_csv(path, **kwargs)
