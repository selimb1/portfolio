from pathlib import Path

import pandas as pd

from portfolio_analytics.spend_anomalies import (
    apply_audit_rules,
    score_spending,
    validate_with_injected_anomalies,
)


def _ledger() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "agency": ["A", "A", "A", "B", "B", "B"] * 20,
            "payee_name": ["Vendor 1", "Vendor 1", "Vendor 2", "V3", "V4", "V5"] * 20,
            "check_amount": [1000, 1000, 1250, 900, 1100, 1050] * 20,
            "fiscal_year": [2024] * 120,
            "issue_date": pd.to_datetime(["2024-01-02"] * 120),
            "industry": ["Services"] * 120,
            "spending_category": ["Contracts"] * 120,
            "contract_id": [None, None, "C2", "C3", "C4", "C5"] * 20,
            "department": ["Ops"] * 120,
            "expense_category": ["General"] * 120,
            "budget_code": ["01"] * 120,
            "sub_vendor": ["No"] * 120,
            "associated_prime_vendor": ["N/A"] * 120,
        }
    )


def test_rules_flag_duplicate_and_missing_contract() -> None:
    result = apply_audit_rules(_ledger())
    assert result["duplicate_like"].sum() >= 2
    assert result["missing_contract"].sum() >= 2


def test_scoring_returns_explainable_evidence(tmp_path: Path) -> None:
    scored = score_spending(_ledger(), random_state=7)
    assert {"anomaly_score", "rule_count", "evidence_score"} <= set(scored.columns)
    assert scored["evidence_score"].between(0, 100).all()


def test_injection_validation_recovers_obvious_anomalies() -> None:
    recall = validate_with_injected_anomalies(_ledger(), random_state=9, injections=12)
    assert recall >= 0.5
