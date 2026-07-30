from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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


NUMERIC_FEATURES = [
    "amount",
    "payment_terms_days",
    "prior_late_rate",
    "prior_avg_delay_days",
    "dispute_flag",
    "days_since_last_payment",
    "macro_pressure",
]
CATEGORICAL_FEATURES = ["segment"]
TARGET = "late_30"


def generate_invoices(rows: int = 20_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    customer_count = max(300, rows // 8)
    customer_ids = np.array([f"C{number:05d}" for number in range(customer_count)])
    customer_risk = rng.beta(1.8, 5.5, customer_count)
    customer_segment = rng.choice(
        ["Enterprise", "Mid-market", "SMB"],
        size=customer_count,
        p=[0.12, 0.30, 0.58],
    )
    customer_index = rng.integers(0, customer_count, size=rows)
    day_offset = rng.integers(0, 365 * 3, size=rows)
    invoice_date = pd.Timestamp("2023-01-01") + pd.to_timedelta(day_offset, unit="D")
    segment = customer_segment[customer_index]
    risk = customer_risk[customer_index]
    amount = np.exp(rng.normal(7.5, 1.05, rows)).clip(100, 75_000)
    amount *= np.select(
        [segment == "Enterprise", segment == "Mid-market"],
        [4.5, 2.0],
        default=1.0,
    )
    terms = rng.choice([15, 30, 45, 60], rows, p=[0.12, 0.58, 0.20, 0.10])
    prior_late_rate = np.clip(risk + rng.normal(0, 0.06, rows), 0, 1)
    prior_delay = np.clip(45 * risk + rng.normal(0, 5, rows), 0, 60)
    dispute_flag = rng.binomial(1, np.clip(0.025 + 0.22 * risk, 0, 0.35))
    days_since_last_payment = np.clip(
        rng.gamma(2.3, 8, rows) + 30 * risk,
        0,
        120,
    )
    macro_pressure = (
        (invoice_date >= pd.Timestamp("2024-07-01")).astype(float)
        + (invoice_date >= pd.Timestamp("2025-04-01")).astype(float)
    ) / 2
    segment_effect = np.select(
        [segment == "SMB", segment == "Enterprise"],
        [0.35, -0.30],
        default=0.0,
    )
    logit = (
        -3.3
        + 4.4 * prior_late_rate
        + 0.028 * prior_delay
        + 1.1 * dispute_flag
        + 0.008 * days_since_last_payment
        + 0.45 * macro_pressure
        + segment_effect
        + rng.normal(0, 0.45, rows)
    )
    probability = 1 / (1 + np.exp(-logit))
    late = rng.binomial(1, probability)
    frame = pd.DataFrame(
        {
            "invoice_id": [f"INV{number:07d}" for number in range(rows)],
            "customer_id": customer_ids[customer_index],
            "invoice_date": invoice_date,
            "due_date": invoice_date + pd.to_timedelta(terms, unit="D"),
            "amount": np.round(amount, 2),
            "segment": segment,
            "payment_terms_days": terms,
            "prior_late_rate": np.round(prior_late_rate, 4),
            "prior_avg_delay_days": np.round(prior_delay, 2),
            "dispute_flag": dispute_flag,
            "days_since_last_payment": np.round(days_since_last_payment, 1),
            "macro_pressure": macro_pressure,
            TARGET: late,
        }
    )
    return frame.sort_values(["invoice_date", "invoice_id"]).reset_index(drop=True)


def temporal_split(
    frame: pd.DataFrame, test_fraction: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ordered = frame.sort_values("invoice_date").reset_index(drop=True)
    unique_dates = np.sort(pd.to_datetime(ordered["invoice_date"]).unique())
    cutoff_position = max(1, int(len(unique_dates) * (1 - test_fraction)))
    cutoff = unique_dates[cutoff_position]
    train = ordered[pd.to_datetime(ordered["invoice_date"]) < cutoff].copy()
    test = ordered[pd.to_datetime(ordered["invoice_date"]) >= cutoff].copy()
    if train.empty or test.empty:
        raise ValueError("Temporal split requires observations on both sides of the cutoff")
    return train, test


def _model() -> Pipeline:
    preprocessor = ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1_000)),
        ]
    )


def fit_payment_model(
    frame: pd.DataFrame, output_dir: Path
) -> tuple[Pipeline, pd.DataFrame, dict[str, float | int | str]]:
    frame = frame.copy()
    frame["invoice_date"] = pd.to_datetime(frame["invoice_date"])
    train, test = temporal_split(frame)
    model = _model()
    model.fit(train[NUMERIC_FEATURES + CATEGORICAL_FEATURES], train[TARGET])
    probability = model.predict_proba(test[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[:, 1]
    predictions = test[
        ["invoice_id", "customer_id", "invoice_date", "amount", "segment", TARGET]
    ].copy()
    predictions["late_probability"] = probability
    predictions = predictions.sort_values("late_probability", ascending=False).reset_index(drop=True)
    predictions["risk_decile"] = pd.qcut(
        predictions["late_probability"].rank(method="first"),
        10,
        labels=list(range(10, 0, -1)),
    ).astype(int)
    top_count = max(1, int(len(predictions) * 0.1))
    top = predictions.head(top_count)
    prevalence = float(predictions[TARGET].mean())
    top_rate = float(top[TARGET].mean())
    late_amount = float((predictions["amount"] * predictions[TARGET]).sum())
    top_late_amount = float((top["amount"] * top[TARGET]).sum())
    metrics: dict[str, float | int | str] = {
        "train_invoices": int(len(train)),
        "test_invoices": int(len(test)),
        "test_start": str(test["invoice_date"].min().date()),
        "test_late_rate_pct": round(100 * prevalence, 2),
        "pr_auc": round(float(average_precision_score(test[TARGET], probability)), 3),
        "roc_auc": round(float(roc_auc_score(test[TARGET], probability)), 3),
        "brier_score": round(float(brier_score_loss(test[TARGET], probability)), 3),
        "top_decile_lift": round(top_rate / prevalence, 2),
        "late_amount_captured_top_decile_pct": round(
            100 * top_late_amount / late_amount if late_amount else 0,
            2,
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_dir / "payment_risk_predictions.csv", index=False)
    write_json(output_dir / "metrics.json", metrics)
    (output_dir / "model_card.md").write_text(
        "# Model card — Riesgo de pago tardío\n\n"
        "## Uso previsto\n\nPriorizar recordatorios y revisión humana; no rechazar crédito.\n\n"
        "## Diseño\n\nRegresión logística entrenada en el 80% temporal inicial y evaluada "
        "en el 20% más reciente. Solo usa información disponible al emitir la factura.\n\n"
        "## Límites\n\nDatos sintéticos, drift no monitoreado y probabilidades no válidas "
        "para otra cartera sin recalibración. Deben auditarse desempeño y trato por segmento.\n",
        encoding="utf-8",
    )

    apply_chart_style()
    ordered = predictions.sort_values("late_probability", ascending=False).reset_index(drop=True)
    x = np.arange(1, len(ordered) + 1) / len(ordered)
    cumulative = ordered[TARGET].cumsum() / max(ordered[TARGET].sum(), 1)
    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(x, cumulative, color=BLUE, linewidth=2.5, label="Modelo")
    axes[0].plot([0, 1], [0, 1], color="#98a2b3", linestyle="--", label="Selección aleatoria")
    axes[0].axvline(0.1, color=ORANGE, linestyle=":", linewidth=2)
    axes[0].set_title("Curva de ganancia")
    axes[0].set_xlabel("Proporción de facturas revisadas")
    axes[0].set_ylabel("Moras capturadas")
    axes[0].legend()
    calibration = pd.DataFrame({"probability": probability, "actual": test[TARGET]}).assign(
        bin=lambda item: pd.qcut(item["probability"], 10, duplicates="drop")
    )
    calibration = calibration.groupby("bin", observed=True).agg(
        predicted=("probability", "mean"), observed=("actual", "mean")
    )
    axes[1].plot(
        calibration["predicted"],
        calibration["observed"],
        marker="o",
        color=ORANGE,
        linewidth=2,
    )
    axes[1].plot([0, 1], [0, 1], color="#98a2b3", linestyle="--")
    axes[1].set_title("Calibración por decil")
    axes[1].set_xlabel("Probabilidad estimada")
    axes[1].set_ylabel("Tasa observada")
    figure.suptitle("El modelo concentra la mora y conserva interpretación operativa", y=1.02)
    figure.text(
        0.08,
        -0.02,
        "Cartera sintética reproducible · validación temporal · regresión logística",
        color="#667085",
        fontsize=9,
    )
    save_figure(figure, output_dir / "figure.png")
    plt.close(figure)
    return model, predictions, metrics


def prepare_sample(sample_path: Path, rows: int = 20_000, seed: int = 42) -> pd.DataFrame:
    frame = generate_invoices(rows=rows, seed=seed)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(sample_path, index=False, date_format="%Y-%m-%d")
    write_json(
        sample_path.with_name("source.json"),
        source_manifest(
            "generated://portfolio_analytics.payment_risk.generate_invoices",
            len(frame),
            source_type="deterministic synthetic accounts-receivable ledger",
            seed=seed,
            period=["2023-01-01", "2025-12-30"],
            sha256=file_sha256(sample_path),
            realism_note="customer heterogeneity, prior payment behavior, disputes, terms and macro pressure",
        ),
    )
    return frame


def analyze(input_path: Path, output_dir: Path) -> dict[str, float | int | str]:
    frame = pd.read_csv(input_path, parse_dates=["invoice_date", "due_date"])
    _, _, metrics = fit_payment_model(frame, output_dir)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the payment-risk model.")
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root() / "projects/04-payment-risk/data/sample.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "projects/04-payment-risk/outputs",
    )
    args = parser.parse_args()
    print(analyze(args.input, args.output_dir))


if __name__ == "__main__":
    main()
