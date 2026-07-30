from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import adjusted_rand_score
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


SURVEY_URL = "https://www.consumerfinance.gov/documents/5614/NFWBS_PUF_2016_data.csv"
SELECTED_COLUMNS = [
    "PUF_ID",
    "FWBscore",
    "FSscore",
    "SUBKNOWL1",
    "SAVEHABIT",
    "SCFHORIZON",
    "ABSORBSHOCK",
    "PPINCIMP",
    "finalwt",
    "LMscore",
    "FINGOALS",
    "SELFCONTROL_1",
]
CLUSTER_FEATURES = ["FWBscore", "SAVEHABIT", "SUBKNOWL1", "SCFHORIZON"]


def clean_special_codes(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    survey_columns = [column for column in result.columns if column not in {"PUF_ID", "finalwt"}]
    for column in survey_columns:
        result[column] = pd.to_numeric(result[column], errors="coerce")
        result.loc[result[column] < 0, column] = np.nan
    if "ABSORBSHOCK" in result:
        result.loc[~result["ABSORBSHOCK"].between(1, 4), "ABSORBSHOCK"] = np.nan
    return result


def _segment_names(profiles: pd.DataFrame) -> dict[int, str]:
    wellbeing_order = profiles["FWBscore"].sort_values().index.tolist()
    names = {
        wellbeing_order[0]: "Vulnerables reactivos",
        wellbeing_order[-1]: "Resilientes planificadores",
    }
    middle = wellbeing_order[1:-1]
    if len(middle) == 2:
        knowledge_order = profiles.loc[middle, "SUBKNOWL1"].sort_values().index.tolist()
        names[knowledge_order[0]] = "Ahorradores en desarrollo"
        names[knowledge_order[1]] = "Informados inconsistentes"
    return names


def fit_segments(
    frame: pd.DataFrame, random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    missing = [column for column in CLUSTER_FEATURES if column not in frame]
    if missing:
        raise ValueError(f"Missing behavioral features: {missing}")
    data = frame.dropna(subset=CLUSTER_FEATURES).copy()
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    matrix = scaler.fit_transform(imputer.fit_transform(data[CLUSTER_FEATURES]))
    base = KMeans(n_clusters=4, random_state=random_state, n_init=20)
    labels = base.fit_predict(matrix)
    stability_scores = []
    for seed in [11, 29, 71, 101]:
        candidate = KMeans(n_clusters=4, random_state=seed, n_init=20).fit_predict(matrix)
        stability_scores.append(adjusted_rand_score(labels, candidate))
    data["_cluster"] = labels
    profiles = data.groupby("_cluster")[CLUSTER_FEATURES].mean()
    names = _segment_names(profiles)
    data["segment"] = data["_cluster"].map(names)
    data = data.drop(columns="_cluster")
    profiles = profiles.assign(segment=profiles.index.map(names)).reset_index(drop=True)
    counts = data["segment"].value_counts(normalize=True).mul(100)
    profiles["sample_share_pct"] = profiles["segment"].map(counts)
    profiles = profiles.sort_values("FWBscore").reset_index(drop=True)
    return data, profiles, float(np.mean(stability_scores))


def prepare_sample(raw_csv: Path, sample_path: Path) -> pd.DataFrame:
    sample = pd.read_csv(raw_csv, usecols=SELECTED_COLUMNS)
    sample = clean_special_codes(sample)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(sample_path, index=False)
    write_json(
        sample_path.with_name("source.json"),
        source_manifest(
            SURVEY_URL,
            len(sample),
            source_type="CFPB National Financial Well-Being Survey public-use file",
            survey_year=2016,
            selected_columns=SELECTED_COLUMNS,
            sha256=file_sha256(sample_path),
            special_codes="negative nonresponse codes converted to null; ABSORBSHOCK=8 converted to null",
        ),
    )
    return sample


def analyze(input_path: Path, output_dir: Path) -> dict[str, float | int | str]:
    frame = clean_special_codes(pd.read_csv(input_path))
    segmented, profiles, stability = fit_segments(frame)
    output_dir.mkdir(parents=True, exist_ok=True)
    profiles.to_csv(output_dir / "segment_profiles.csv", index=False)
    segmented[["PUF_ID", "segment"]].to_csv(output_dir / "respondent_segments.csv", index=False)

    model_columns = [
        "SAVEHABIT",
        "SUBKNOWL1",
        "SCFHORIZON",
        "ABSORBSHOCK",
        "PPINCIMP",
        "FSscore",
    ]
    model_frame = frame.dropna(subset=["FWBscore", "finalwt", *model_columns]).copy()
    scaler = StandardScaler()
    design = scaler.fit_transform(model_frame[model_columns])
    regression = LinearRegression().fit(
        design,
        model_frame["FWBscore"],
        sample_weight=model_frame["finalwt"],
    )
    coefficients = pd.Series(regression.coef_, index=model_columns)
    strongest_driver = str(coefficients.abs().idxmax())
    highest = profiles.iloc[-1]
    lowest = profiles.iloc[0]
    metrics: dict[str, float | int | str] = {
        "respondents": int(len(frame)),
        "clustered_respondents": int(len(segmented)),
        "segments": 4,
        "cluster_stability_ari": round(stability, 3),
        "highest_wellbeing_segment": str(highest["segment"]),
        "lowest_wellbeing_segment": str(lowest["segment"]),
        "wellbeing_gap_points": round(float(highest["FWBscore"] - lowest["FWBscore"]), 1),
        "strongest_association": strongest_driver,
        "weighted_regression_r2": round(
            float(regression.score(design, model_frame["FWBscore"], sample_weight=model_frame["finalwt"])),
            3,
        ),
    }
    write_json(output_dir / "metrics.json", metrics)

    apply_chart_style()
    figure, axis = plt.subplots(figsize=(10, 6))
    palette = [ORANGE, "#8a4fff", BLUE, "#16836b"]
    label_offsets = {
        "Vulnerables reactivos": (8, 8),
        "Ahorradores en desarrollo": (8, 14),
        "Informados inconsistentes": (8, -20),
        "Resilientes planificadores": (8, 8),
    }
    for color, row in zip(palette, profiles.itertuples()):
        axis.scatter(
            row.SAVEHABIT,
            row.FWBscore,
            s=max(row.sample_share_pct, 1) * 35,
            color=color,
            alpha=0.9,
            edgecolor="white",
            linewidth=1.5,
        )
        axis.annotate(
            f"{row.segment}\n{row.sample_share_pct:.1f}% de la muestra",
            (row.SAVEHABIT, row.FWBscore),
            xytext=label_offsets[row.segment],
            textcoords="offset points",
            fontsize=9,
        )
    axis.set_title("La conducta de ahorro separa perfiles con distinto bienestar")
    axis.set_xlabel("Hábito de ahorro promedio (1–6)")
    axis.set_ylabel("Bienestar financiero promedio (0–100)")
    axis.set_xlim(2.1, 6.2)
    figure.text(
        0.1,
        0.01,
        "CFPB National Financial Well-Being Survey · burbuja = participación muestral",
        color="#667085",
        fontsize=9,
    )
    save_figure(figure, output_dir / "figure.png")
    plt.close(figure)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the behavioral-finance segmentation.")
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root() / "projects/03-behavioral-finance/data/sample.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "projects/03-behavioral-finance/outputs",
    )
    args = parser.parse_args()
    print(analyze(args.input, args.output_dir))


if __name__ == "__main__":
    main()
