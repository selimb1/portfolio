from pathlib import Path

import numpy as np
import pandas as pd

from portfolio_analytics.behavioral_finance import clean_special_codes, fit_segments


def test_clean_special_codes_replaces_nonresponse_values() -> None:
    frame = pd.DataFrame(
        {
            "FWBscore": [55, -1, -4],
            "SAVEHABIT": [6, -1, 3],
            "ABSORBSHOCK": [4, 8, -1],
        }
    )
    result = clean_special_codes(frame)
    assert np.isnan(result.loc[1, "FWBscore"])
    assert np.isnan(result.loc[2, "FWBscore"])
    assert np.isnan(result.loc[1, "ABSORBSHOCK"])


def test_fit_segments_is_deterministic_and_profiles_every_row(tmp_path: Path) -> None:
    rng = np.random.default_rng(7)
    blocks = []
    for center in [(25, 2, 2, 2), (45, 3, 4, 3), (65, 5, 5, 4), (80, 6, 6, 5)]:
        blocks.append(rng.normal(center, [2, 0.2, 0.2, 0.2], size=(30, 4)))
    matrix = np.vstack(blocks)
    frame = pd.DataFrame(
        matrix,
        columns=["FWBscore", "SAVEHABIT", "SUBKNOWL1", "SCFHORIZON"],
    )
    first, profiles, stability = fit_segments(frame, random_state=42)
    second, _, _ = fit_segments(frame, random_state=42)
    assert first["segment"].tolist() == second["segment"].tolist()
    assert len(first) == 120
    assert len(profiles) == 4
    assert stability > 0.9
