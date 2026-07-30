from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
import json
import math


INK = "#17212b"
BLUE = "#1f5aa6"
ORANGE = "#d97706"
LIGHT_BLUE = "#dbe9f6"
GRID = "#d9dee5"
MUTED = "#667085"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite(value: Any) -> bool:
    if value is None or isinstance(value, (str, bool)):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite(item) for item in value)
    return False


def write_json(path: Path, payload: dict[str, Any]) -> None:
    if not payload or not _finite(payload):
        raise ValueError("JSON metrics must be non-empty and finite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_manifest(
    url: str,
    rows: int,
    retrieved_at: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "url": url,
        "rows": int(rows),
        "retrieved_at": retrieved_at
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    manifest.update(extra)
    return manifest


def apply_chart_style() -> None:
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.7,
            "grid.alpha": 0.8,
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "legend.frameon": False,
        }
    )


def save_figure(figure: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        path,
        dpi=160,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "business-data-portfolio"},
    )
