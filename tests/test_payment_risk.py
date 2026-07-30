from pathlib import Path

import pandas as pd

from portfolio_analytics.payment_risk import (
    fit_payment_model,
    generate_invoices,
    temporal_split,
)


def test_invoice_generator_is_deterministic_and_has_no_future_features() -> None:
    first = generate_invoices(rows=500, seed=19)
    second = generate_invoices(rows=500, seed=19)
    pd.testing.assert_frame_equal(first, second)
    assert "payment_date" not in first.columns
    assert set(first["late_30"].unique()) <= {0, 1}
    assert first["amount"].gt(0).all()


def test_temporal_split_never_trains_on_future() -> None:
    frame = generate_invoices(rows=500, seed=21)
    train, test = temporal_split(frame, test_fraction=0.2)
    assert train["invoice_date"].max() < test["invoice_date"].min()


def test_model_outputs_business_metrics(tmp_path: Path) -> None:
    frame = generate_invoices(rows=2_000, seed=22)
    _, predictions, metrics = fit_payment_model(frame, tmp_path)
    assert 0 <= metrics["pr_auc"] <= 1
    assert metrics["top_decile_lift"] > 1
    assert metrics["test_invoices"] == len(predictions)
    assert (tmp_path / "model_card.md").exists()
