"""Save Matplotlib charts to reports/figures."""
from pathlib import Path

def save_figure(fig, filename: str) -> Path:
    output_dir = Path(__file__).resolve().parents[1] / "reports" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path
