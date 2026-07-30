from __future__ import annotations

import argparse
from pathlib import Path

from portfolio_analytics import (
    behavioral_finance,
    complaint_sql,
    payment_risk,
    spend_anomalies,
    working_capital,
)
from portfolio_analytics.common import project_root, write_json


ANALYSES = [
    ("01-working-capital", working_capital.analyze),
    ("02-complaint-risk-sql", complaint_sql.analyze),
    ("03-behavioral-finance", behavioral_finance.analyze),
    ("04-payment-risk", payment_risk.analyze),
    ("05-spend-anomalies", spend_anomalies.analyze),
]


def run_all(root: Path) -> dict[str, dict[str, float | int | str]]:
    results: dict[str, dict[str, float | int | str]] = {}
    for project_name, analyze in ANALYSES:
        project = root / "projects" / project_name
        print(f"Running {project_name}...")
        results[project_name] = analyze(
            project / "data" / "sample.csv",
            project / "outputs",
        )
    write_json(root / "outputs" / "portfolio_metrics.json", results)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute all five portfolio analyses.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use the versioned samples and make no network calls.",
    )
    parser.parse_args()
    results = run_all(project_root())
    for name, metrics in results.items():
        print(f"{name}: {metrics}")


if __name__ == "__main__":
    main()
