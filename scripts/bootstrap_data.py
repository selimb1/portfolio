from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

import requests

from portfolio_analytics.behavioral_finance import SURVEY_URL, prepare_sample as prepare_survey
from portfolio_analytics.payment_risk import prepare_sample as prepare_invoices
from portfolio_analytics.spend_anomalies import SOURCE_URL, prepare_sample as prepare_spending
from portfolio_analytics.working_capital import fetch_yahoo_sample
from portfolio_analytics.common import project_root


def _download(url: str, destination: Path) -> None:
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destination.open("wb") as target:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                target.write(chunk)


def refresh_reliable_sources(root: Path) -> None:
    fetch_yahoo_sample(root / "projects/01-working-capital/data/sample.csv")
    with TemporaryDirectory(prefix="portfolio-data-") as temp:
        temp_dir = Path(temp)
        survey_raw = temp_dir / "survey.csv"
        spending_raw = temp_dir / "spending.parquet"
        _download(SURVEY_URL, survey_raw)
        prepare_survey(
            survey_raw,
            root / "projects/03-behavioral-finance/data/sample.csv",
        )
        _download(SOURCE_URL, spending_raw)
        prepare_spending(
            spending_raw,
            root / "projects/05-spend-anomalies/data/sample.csv",
        )
    prepare_invoices(root / "projects/04-payment-risk/data/sample.csv")
    print(
        "Project 02 keeps its versioned bounded CFPB extract to avoid downloading "
        "the multi-gigabyte full complaint archive."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh reproducible project samples.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh network-backed sources; otherwise verify that samples exist.",
    )
    args = parser.parse_args()
    root = project_root()
    if args.refresh:
        refresh_reliable_sources(root)
    missing = [
        project / "data" / "sample.csv"
        for project in sorted((root / "projects").iterdir())
        if project.is_dir() and not (project / "data" / "sample.csv").is_file()
    ]
    if missing:
        raise SystemExit(f"Missing samples: {missing}")
    print("All five project samples are available.")


if __name__ == "__main__":
    main()
