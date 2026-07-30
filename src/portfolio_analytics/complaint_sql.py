from __future__ import annotations

import argparse
from pathlib import Path
import re

import duckdb
import matplotlib.pyplot as plt
import pandas as pd

from portfolio_analytics.common import (
    BLUE,
    ORANGE,
    apply_chart_style,
    file_sha256,
    project_root,
    save_figure,
    source_manifest,
    write_json,
)


CFPB_API = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"


def _snake_case(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")


def normalize_complaints(raw: pd.DataFrame) -> pd.DataFrame:
    frame = raw.rename(columns={column: _snake_case(column) for column in raw.columns})
    aliases = {
        "timely_response": ["timely_response", "timely_response_"],
        "consumer_disputed": ["consumer_disputed", "consumer_disputed_"],
        "complaint_id": ["complaint_id"],
    }
    for target, options in aliases.items():
        match = next((item for item in options if item in frame.columns), None)
        if match and match != target:
            frame = frame.rename(columns={match: target})
    required = ["date_received", "product", "issue", "company", "state", "complaint_id"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing CFPB columns: {missing}")
    if "timely_response" not in frame:
        frame["timely_response"] = pd.NA
    if "consumer_disputed" not in frame:
        frame["consumer_disputed"] = pd.NA
    frame["date_received"] = pd.to_datetime(frame["date_received"], errors="coerce")
    frame["timely_response"] = (
        frame["timely_response"].astype("string").str.strip().str.lower().map({"yes": 1, "no": 0})
    )
    frame["consumer_disputed"] = (
        frame["consumer_disputed"].astype("string").str.strip().str.lower().map({"yes": 1, "no": 0})
    )
    frame["complaint_id"] = frame["complaint_id"].astype("string").str.replace(r"\.0$", "", regex=True)
    columns = required + ["timely_response", "consumer_disputed"]
    frame = frame[columns].dropna(subset=["date_received", "company", "complaint_id"])
    frame["timely_response"] = frame["timely_response"].fillna(1).astype(int)
    frame["consumer_disputed"] = frame["consumer_disputed"].fillna(0).astype(int)
    return frame.drop_duplicates("complaint_id").reset_index(drop=True)


def prepare_sample(raw_csv: Path, sample_path: Path, rows: int = 20_000) -> pd.DataFrame:
    raw = pd.read_csv(raw_csv, nrows=rows, low_memory=False)
    sample = normalize_complaints(raw)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(sample_path, index=False, date_format="%Y-%m-%d")
    manifest = source_manifest(
        CFPB_API,
        len(sample),
        source_type="CFPB Consumer Complaint Database API",
        sample_rule=f"first {rows:,} parseable rows from a bounded 2025 API extract",
        sha256=file_sha256(sample_path),
        transformations=["column normalization", "narrative fields excluded", "complaint_id deduplicated"],
    )
    write_json(sample_path.with_name("source.json"), manifest)
    return sample


def run_sql_analysis(frame: pd.DataFrame, output_dir: Path) -> tuple[pd.DataFrame, dict[str, float | int | str]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    query_path = project_root() / "projects/02-complaint-risk-sql/sql/risk_queue.sql"
    query = query_path.read_text(encoding="utf-8")
    connection = duckdb.connect()
    connection.register("complaints", frame)
    queue = connection.execute(query).df()
    connection.close()
    queue.to_csv(output_dir / "risk_queue.csv", index=False)

    top = queue.iloc[0]
    metrics: dict[str, float | int | str] = {
        "complaints": int(len(frame)),
        "companies": int(frame["company"].nunique()),
        "products": int(frame["product"].nunique()),
        "top_risk_company": str(top["company"]),
        "top_risk_score": float(top["risk_score"]),
        "top_company_complaints": int(top["complaint_count"]),
        "top_company_untimely_rate_pct": float(top["untimely_rate_pct"]),
        "sql_window_functions": 6,
    }
    write_json(output_dir / "metrics.json", metrics)

    apply_chart_style()
    chart = queue.head(12).sort_values("risk_score").reset_index(drop=True)
    figure, axis = plt.subplots(figsize=(10, 6))
    colors = [ORANGE if rank <= 3 else BLUE for rank in chart["risk_rank"]]
    axis.barh(chart["company"], chart["risk_score"], color=colors)
    axis.set_title("Cola de riesgo operativo basada en reclamos")
    axis.set_xlabel("Puntaje de riesgo (0–100)")
    axis.set_ylabel("")
    axis.set_xlim(0, 105)
    for position, row in enumerate(chart.itertuples()):
        axis.text(row.risk_score + 1, position, f"{row.risk_score:.0f}", va="center", fontsize=8)
    figure.text(
        0.1,
        0.01,
        "CFPB Consumer Complaint Database · priorización SQL por volumen y respuesta tardía",
        color="#667085",
        fontsize=9,
    )
    save_figure(figure, output_dir / "figure.png")
    plt.close(figure)
    return queue, metrics


def analyze(input_path: Path, output_dir: Path) -> dict[str, float | int | str]:
    frame = pd.read_csv(input_path, parse_dates=["date_received"])
    _, metrics = run_sql_analysis(frame, output_dir)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SQL complaint-risk analysis.")
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root() / "projects/02-complaint-risk-sql/data/sample.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "projects/02-complaint-risk-sql/outputs",
    )
    args = parser.parse_args()
    print(analyze(args.input, args.output_dir))


if __name__ == "__main__":
    main()
