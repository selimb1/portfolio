from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

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


SOURCE_URL = "https://nyc-databook-spending.s3.amazonaws.com/fiscal_year=2024/chunk_0001.parquet"
SOURCE_PAGE = "https://databook.nyc/procurement/data-sources"


def apply_audit_rules(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["check_amount"] = pd.to_numeric(result["check_amount"], errors="coerce")
    result["issue_date"] = pd.to_datetime(result["issue_date"], errors="coerce")
    duplicate_keys = ["agency", "payee_name", "check_amount", "issue_date"]
    result["duplicate_like"] = result.duplicated(duplicate_keys, keep=False).astype(int)
    contract_spend = result["spending_category"].astype("string").str.contains(
        "Contract", case=False, na=False
    )
    contract_missing = result["contract_id"].isna() | result["contract_id"].astype(
        "string"
    ).str.strip().isin(["", "N/A", "None", "<NA>"])
    result["missing_contract"] = (contract_spend & contract_missing).astype(int)
    result["round_amount"] = (
        result["check_amount"].ge(10_000)
        & np.isclose(result["check_amount"] % 10_000, 0, atol=0.01)
    ).astype(int)
    log_amount = np.log1p(result["check_amount"].clip(lower=0))
    category = result["expense_category"].fillna("Unknown")
    median = log_amount.groupby(category).transform("median")
    absolute_deviation = (log_amount - median).abs()
    mad = absolute_deviation.groupby(category).transform("median").replace(0, np.nan)
    robust_z = 0.6745 * (log_amount - median) / mad
    global_mad = float((log_amount - log_amount.median()).abs().median()) or 1.0
    fallback_z = 0.6745 * (log_amount - log_amount.median()) / global_mad
    result["category_outlier"] = robust_z.fillna(fallback_z).gt(3.5).astype(int)
    return result


def score_spending(frame: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    scored = apply_audit_rules(frame)
    amount = pd.to_numeric(scored["check_amount"], errors="coerce").fillna(0).clip(lower=0)
    payee_frequency = scored["payee_name"].map(scored["payee_name"].value_counts())
    agency_frequency = scored["agency"].map(scored["agency"].value_counts())
    feature_frame = pd.DataFrame(
        {
            "log_amount": np.log1p(amount),
            "payee_frequency": np.log1p(payee_frequency),
            "agency_frequency": np.log1p(agency_frequency),
            "missing_contract": scored["missing_contract"],
            "duplicate_like": scored["duplicate_like"],
            "round_amount": scored["round_amount"],
            "category_outlier": scored["category_outlier"],
        }
    ).fillna(0)
    matrix = StandardScaler().fit_transform(feature_frame)
    detector = IsolationForest(
        n_estimators=180,
        contamination=0.02,
        random_state=random_state,
        n_jobs=-1,
    )
    detector.fit(matrix)
    scored["anomaly_score"] = -detector.score_samples(matrix)
    anomaly_percentile = scored["anomaly_score"].rank(pct=True)
    materiality_percentile = amount.rank(pct=True)
    rule_columns = ["duplicate_like", "missing_contract", "round_amount", "category_outlier"]
    scored["rule_count"] = scored[rule_columns].sum(axis=1)
    scored["evidence_score"] = (
        45 * anomaly_percentile
        + 35 * (scored["rule_count"].clip(upper=3) / 3)
        + 20 * materiality_percentile
    ).clip(0, 100)
    return scored


def validate_with_injected_anomalies(
    frame: pd.DataFrame, random_state: int = 42, injections: int = 100
) -> float:
    rng = np.random.default_rng(random_state)
    base = frame.reset_index(drop=True).copy()
    injections = min(injections, max(1, len(base) // 3))
    selected = rng.choice(len(base), size=injections, replace=False)
    injected = base.iloc[selected].copy()
    injected["check_amount"] = (
        pd.to_numeric(injected["check_amount"], errors="coerce").fillna(1) * 75
    )
    injected["contract_id"] = None
    injected["payee_name"] = [f"INJECTED_VENDOR_{number}" for number in range(injections)]
    combined = pd.concat([base.assign(_injected=0), injected.assign(_injected=1)], ignore_index=True)
    scored = score_spending(combined, random_state=random_state)
    review_count = max(injections * 2, int(len(scored) * 0.02))
    reviewed = scored.nlargest(review_count, "evidence_score")
    return float(reviewed["_injected"].sum() / injections)


def prepare_sample(
    parquet_path: Path, sample_path: Path, rows: int = 25_000, seed: int = 42
) -> pd.DataFrame:
    raw = pd.read_parquet(parquet_path)
    raw["check_amount"] = pd.to_numeric(raw["check_amount"], errors="coerce")
    raw["issue_date"] = pd.to_datetime(raw["issue_date"], errors="coerce")
    raw = raw.dropna(subset=["agency", "payee_name", "check_amount", "issue_date"])
    sample = raw.sample(n=min(rows, len(raw)), random_state=seed).sort_values(
        ["issue_date", "agency", "payee_name"]
    )
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(sample_path, index=False, date_format="%Y-%m-%d")
    write_json(
        sample_path.with_name("source.json"),
        source_manifest(
            SOURCE_URL,
            len(sample),
            source_type="NYC Databook parquet derived from Checkbook NYC",
            source_page=SOURCE_PAGE,
            fiscal_year=2024,
            sample_seed=seed,
            source_rows=int(len(raw)),
            sha256=file_sha256(sample_path),
        ),
    )
    return sample


def analyze(input_path: Path, output_dir: Path) -> dict[str, float | int | str]:
    frame = pd.read_csv(input_path, parse_dates=["issue_date"], low_memory=False)
    scored = score_spending(frame)
    review_queue = scored.nlargest(250, "evidence_score").copy()
    output_dir.mkdir(parents=True, exist_ok=True)
    review_columns = [
        "agency",
        "payee_name",
        "check_amount",
        "issue_date",
        "spending_category",
        "expense_category",
        "contract_id",
        "duplicate_like",
        "missing_contract",
        "round_amount",
        "category_outlier",
        "anomaly_score",
        "rule_count",
        "evidence_score",
    ]
    review_queue[review_columns].to_csv(output_dir / "review_queue.csv", index=False)
    injection_sample = frame.sample(n=min(5_000, len(frame)), random_state=17)
    injection_recall = validate_with_injected_anomalies(
        injection_sample, random_state=17, injections=100
    )
    top = review_queue.iloc[0]
    metrics: dict[str, float | int | str] = {
        "payments": int(len(frame)),
        "agencies": int(frame["agency"].nunique()),
        "payees": int(frame["payee_name"].nunique()),
        "total_exposure_usd": round(float(frame["check_amount"].sum()), 2),
        "review_queue_rows": int(len(review_queue)),
        "review_queue_exposure_usd": round(float(review_queue["check_amount"].sum()), 2),
        "injected_anomaly_recall": round(injection_recall, 3),
        "top_evidence_payee": str(top["payee_name"]),
        "top_evidence_score": round(float(top["evidence_score"]), 2),
        "missing_contract_flags": int(scored["missing_contract"].sum()),
        "duplicate_like_flags": int(scored["duplicate_like"].sum()),
    }
    write_json(output_dir / "metrics.json", metrics)

    apply_chart_style()
    plot = scored.sample(n=min(6_000, len(scored)), random_state=42)
    highlighted = review_queue.head(50)
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.scatter(
        plot["evidence_score"],
        plot["check_amount"],
        s=12,
        alpha=0.25,
        color=BLUE,
        label="Pagos analizados",
    )
    axis.scatter(
        highlighted["evidence_score"],
        highlighted["check_amount"],
        s=35,
        alpha=0.9,
        color=ORANGE,
        label="Top 50 para revisión",
    )
    axis.set_yscale("log")
    axis.set_title("La cola combina evidencia de anomalía y exposición")
    axis.set_xlabel("Puntaje explicable de evidencia (0–100)")
    axis.set_ylabel("Importe del pago, USD (escala log)")
    axis.legend()
    figure.text(
        0.1,
        0.01,
        "NYC Databook / Checkbook NYC · reglas contables + Isolation Forest",
        color="#667085",
        fontsize=9,
    )
    save_figure(figure, output_dir / "figure.png")
    plt.close(figure)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the spend-anomaly review queue.")
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root() / "projects/05-spend-anomalies/data/sample.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "projects/05-spend-anomalies/outputs",
    )
    args = parser.parse_args()
    print(analyze(args.input, args.output_dir))


if __name__ == "__main__":
    main()
