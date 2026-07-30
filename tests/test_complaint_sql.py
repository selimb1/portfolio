from pathlib import Path

import pandas as pd

from portfolio_analytics.complaint_sql import normalize_complaints, run_sql_analysis


def test_normalize_complaints_maps_public_columns() -> None:
    raw = pd.DataFrame(
        {
            "Date received": ["2025-01-03"],
            "Product": ["Credit card"],
            "Issue": ["Fees"],
            "Company": ["Example Bank"],
            "State": ["NY"],
            "Timely response?": ["No"],
            "Consumer disputed?": ["Yes"],
            "Complaint ID": ["42"],
        }
    )
    result = normalize_complaints(raw)
    assert result.loc[0, "timely_response"] == 0
    assert result.loc[0, "consumer_disputed"] == 1
    assert result.loc[0, "complaint_id"] == "42"


def test_sql_analysis_builds_ranked_risk_queue(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        {
            "date_received": pd.to_datetime(
                ["2025-01-02", "2025-01-03", "2025-02-03", "2025-02-04", "2025-02-05"]
            ),
            "product": ["Card"] * 4 + ["Loan"],
            "issue": ["Fees"] * 5,
            "company": ["A", "A", "A", "A", "B"],
            "state": ["NY"] * 5,
            "timely_response": [0, 1, 0, 0, 1],
            "consumer_disputed": [1, 0, 1, 1, 0],
            "complaint_id": ["1", "2", "3", "4", "5"],
        }
    )
    queue, metrics = run_sql_analysis(frame, tmp_path)
    assert queue.iloc[0]["company"] == "A"
    assert queue.iloc[0]["risk_rank"] == 1
    assert metrics["complaints"] == 5
    assert metrics["sql_window_functions"] >= 4
