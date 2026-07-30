from pathlib import Path
from hashlib import sha256
import csv
import json
import math
import re
import sys


REQUIRED_SECTIONS = (
    "## 1. Título y pitch",
    "## 2. Fuente de datos",
    "## 3. Preguntas de negocio",
    "## 4. Stack técnico",
    "## 5. Estructura del análisis",
    "## 6. Visualización final",
    "## 7. Frase para el portfolio",
    "## 8. Nivel de dificultad",
)

TECHNICAL_ARTIFACTS = (
    "data/sample.csv",
    "data/source.json",
    "notebooks/analysis.ipynb",
    "outputs/metrics.json",
    "outputs/figure.png",
)


def _all_numbers_finite(value: object) -> bool:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_all_numbers_finite(item) for item in value)
    if isinstance(value, dict):
        return all(_all_numbers_finite(item) for item in value.values())
    return False


def _notebook_has_executed_output(path: Path) -> bool:
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return any(
        cell.get("cell_type") == "code"
        and cell.get("execution_count") is not None
        and cell.get("outputs")
        for cell in notebook.get("cells", [])
    )


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_rows(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as source:
        return max(0, sum(1 for _ in csv.reader(source)) - 1)


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    briefs = sorted((root / "projects").glob("*/README.md"))
    if len(briefs) != 5:
        errors.append(f"Expected 5 project briefs, found {len(briefs)}")

    main = (root / "README.md").read_text(encoding="utf-8")
    for brief in briefs:
        text = brief.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"{brief.parent.name}: missing {section}")
        relative = brief.relative_to(root).as_posix()
        if relative not in main:
            errors.append(f"README: missing link to {relative}")
        if not re.search(r"https://", text):
            errors.append(f"{brief.parent.name}: missing source URL")
        for relative_artifact in TECHNICAL_ARTIFACTS:
            artifact = brief.parent / relative_artifact
            if not artifact.is_file():
                errors.append(
                    f"{brief.parent.name}: missing {relative_artifact}"
                )
        metrics_path = brief.parent / "outputs" / "metrics.json"
        if metrics_path.is_file():
            try:
                metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"{brief.parent.name}: invalid metrics.json")
            else:
                if not metrics or not _all_numbers_finite(metrics):
                    errors.append(
                        f"{brief.parent.name}: metrics must be non-empty and finite"
                    )
        sample_path = brief.parent / "data" / "sample.csv"
        source_path = brief.parent / "data" / "source.json"
        if sample_path.is_file() and source_path.is_file():
            try:
                source = json.loads(source_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"{brief.parent.name}: invalid source.json")
            else:
                for key in ("url", "rows", "retrieved_at", "sha256"):
                    if key not in source:
                        errors.append(f"{brief.parent.name}: source.json missing {key}")
                if source.get("rows") != _csv_rows(sample_path):
                    errors.append(f"{brief.parent.name}: source row count does not match sample")
                if source.get("sha256") != _file_sha256(sample_path):
                    errors.append(f"{brief.parent.name}: source sha256 does not match sample")
        notebook_path = brief.parent / "notebooks" / "analysis.ipynb"
        if notebook_path.is_file() and not _notebook_has_executed_output(
            notebook_path
        ):
            errors.append(f"{brief.parent.name}: notebook is not executed")
    return errors


if __name__ == "__main__":
    problems = validate_repository(Path(__file__).resolve().parents[1])
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print("Portfolio validation passed.")
