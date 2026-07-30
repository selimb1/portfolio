# Technical Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir los cinco briefs en análisis ejecutables con datos, código, SQL, modelos, notebooks, figuras, métricas, pruebas y CI.

**Architecture:** Un paquete Python común implementa adquisición, análisis y visualización; cada proyecto conserva sus datos, SQL y outputs junto al brief. Scripts raíz orquestan la carga, ejecución y notebooks, mientras un validador comprueba el contrato técnico completo.

**Tech Stack:** Python 3.11+, Pandas, NumPy, DuckDB, scikit-learn, Matplotlib, PyArrow, nbformat/nbclient, pytest, GitHub Actions.

---

## File map

- `pyproject.toml`: paquete, dependencias y pytest.
- `Makefile`: interfaz reproducible.
- `.gitignore`: cachés, entorno y raw voluminoso.
- `.github/workflows/ci.yml`: verificación offline.
- `src/portfolio_analytics/common.py`: rutas, JSON, estilo, hashing y figuras.
- `src/portfolio_analytics/working_capital.py`: SEC y ratios.
- `src/portfolio_analytics/complaint_sql.py`: orquestación DuckDB.
- `src/portfolio_analytics/behavioral_finance.py`: segmentos y regresión.
- `src/portfolio_analytics/payment_risk.py`: generador y clasificación.
- `src/portfolio_analytics/spend_anomalies.py`: reglas y anomalías.
- `projects/02-complaint-risk-sql/sql/*.sql`: transformación SQL visible.
- `scripts/bootstrap_data.py`: muestras reales y sintética.
- `scripts/run_all.py`: ejecución offline.
- `scripts/build_notebooks.py`: creación y ejecución de cinco notebooks.
- `scripts/validate_portfolio.py`: contrato editorial/técnico.
- `tests/test_*.py`: pruebas por dominio e integración.

### Task 1: Reproducible project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `.gitignore`
- Create: `.github/workflows/ci.yml`
- Modify: `scripts/validate_portfolio.py`
- Modify: `tests/test_validate_portfolio.py`

- [ ] Write failing tests that require `data/sample.csv`, `data/source.json`, `notebooks/analysis.ipynb`, `outputs/metrics.json` and `outputs/figure.png` in each project.
- [ ] Run `python3 -m unittest tests/test_validate_portfolio.py -v`; expect failure because technical artifacts are absent.
- [ ] Add package dependencies and Make targets:

```text
setup -> create .venv and install editable package
data -> scripts/bootstrap_data.py
analysis -> scripts/run_all.py
notebooks -> scripts/build_notebooks.py
test -> pytest -q and validate_portfolio.py
all -> analysis + notebooks + test
```

- [ ] Extend `validate_repository` to validate artifacts, finite JSON metrics and executed notebook outputs.
- [ ] Keep the new test red until project artifacts exist; commit the scaffold independently.

### Task 2: Common library and data bootstrap

**Files:**
- Create: `src/portfolio_analytics/__init__.py`
- Create: `src/portfolio_analytics/common.py`
- Create: `scripts/bootstrap_data.py`
- Create: `tests/test_common.py`

- [ ] Test deterministic hashing, finite JSON serialization and figure export.
- [ ] Implement:

```python
def project_root() -> Path: ...
def write_json(path: Path, payload: dict) -> None: ...
def read_json(path: Path) -> dict: ...
def save_figure(fig, path: Path) -> None: ...
def source_manifest(url: str, rows: int, retrieved_at: str, **extra) -> dict: ...
```

- [ ] Implement a CLI with `--project`, `--refresh` and `--offline` semantics.
- [ ] Create a consistent Matplotlib style using ink `#17212b`, blue `#1f5aa6`, orange `#d97706` and neutral greys.
- [ ] Run common tests and commit.

### Task 3: Working-capital evidence

**Files:**
- Create: `src/portfolio_analytics/working_capital.py`
- Create: `tests/test_working_capital.py`
- Create: `projects/01-working-capital/data/sample.csv`
- Create: `projects/01-working-capital/data/source.json`
- Create: `projects/01-working-capital/outputs/metrics.json`
- Create: `projects/01-working-capital/outputs/figure.png`
- Create: `projects/01-working-capital/outputs/company_metrics.csv`
- Modify: `projects/01-working-capital/README.md`

- [ ] Write failing tests for DSO/DIO/DPO/CCC using known balances and for SEC fact deduplication.
- [ ] Implement `calculate_working_capital(df)` with average balances and 365-day annual ratios.
- [ ] Implement SEC Companyfacts refresh for a documented cohort and tag fallback map.
- [ ] Create a real processed sample with at least four companies and five annual periods.
- [ ] Produce a scatter with at least 12 comparable company-period observations.
- [ ] Save metrics identifying the largest latest-year CCC deterioration and approximate cash effect.
- [ ] Update README with actual outputs, reproduction commands and caveats.
- [ ] Run domain tests and commit.

### Task 4: SQL-first complaint evidence

**Files:**
- Create: `src/portfolio_analytics/complaint_sql.py`
- Create: `projects/02-complaint-risk-sql/sql/00_staging.sql`
- Create: `projects/02-complaint-risk-sql/sql/01_quality.sql`
- Create: `projects/02-complaint-risk-sql/sql/02_metrics.sql`
- Create: `tests/test_complaint_sql.py`
- Create: `projects/02-complaint-risk-sql/data/sample.csv`
- Create: `projects/02-complaint-risk-sql/data/source.json`
- Create: `projects/02-complaint-risk-sql/outputs/metrics.json`
- Create: `projects/02-complaint-risk-sql/outputs/figure.png`
- Create: `projects/02-complaint-risk-sql/outputs/risk_queue.csv`
- Modify: `projects/02-complaint-risk-sql/README.md`

- [ ] Write a failing integration test against a six-row fixture with duplicate ID, late response and two months.
- [ ] Implement SQL staging with `ROW_NUMBER`, typed dates and routing days.
- [ ] Implement quality views and monthly/product metrics with `LAG`, 3-month windows, percent ranks and minimum denominators.
- [ ] Implement Python orchestration that registers CSV, executes the SQL files and exports only aggregated tables.
- [ ] Refresh a bounded CFPB API sample and version the canonical columns.
- [ ] Create a product-issue heatmap from the SQL aggregate.
- [ ] Update README with executed row count, finding and explicit denominator caveat.
- [ ] Run domain tests and commit.

### Task 5: Behavioral-finance evidence

**Files:**
- Create: `src/portfolio_analytics/behavioral_finance.py`
- Create: `tests/test_behavioral_finance.py`
- Create: `projects/03-behavioral-finance/data/sample.csv`
- Create: `projects/03-behavioral-finance/data/source.json`
- Create: `projects/03-behavioral-finance/outputs/metrics.json`
- Create: `projects/03-behavioral-finance/outputs/figure.png`
- Create: `projects/03-behavioral-finance/outputs/segment_profiles.csv`
- Modify: `projects/03-behavioral-finance/README.md`

- [ ] Write failing tests for special-code null handling, deterministic labels and segment stability.
- [ ] Load selected real CFPB PUF columns and preserve the survey weight.
- [ ] Build interpretable dimensions: skill, knowledge, confidence, saving habit, planning horizon and shock resilience.
- [ ] Fit a standardized K-Means pipeline, assign descriptive labels from profiles and repeat across seeds.
- [ ] Fit a descriptive weighted regression for financial well-being.
- [ ] Create a knowledge-confidence scatter with segment profile summary.
- [ ] Save stability, sample size, segment gap and regression diagnostics.
- [ ] Update README with associative language and ethical limits.
- [ ] Run domain tests and commit.

### Task 6: Payment-risk predictive evidence

**Files:**
- Create: `src/portfolio_analytics/payment_risk.py`
- Create: `tests/test_payment_risk.py`
- Create: `projects/04-payment-risk/data/sample.csv`
- Create: `projects/04-payment-risk/data/source.json`
- Create: `projects/04-payment-risk/outputs/metrics.json`
- Create: `projects/04-payment-risk/outputs/figure.png`
- Create: `projects/04-payment-risk/outputs/gain_curve.csv`
- Create: `projects/04-payment-risk/MODEL_CARD.md`
- Modify: `projects/04-payment-risk/README.md`

- [ ] Write failing tests for deterministic generation, chronological splits and a forbidden-feature leakage guard.
- [ ] Generate at least 20.000 invoices over 36 months with customer risk, amount, terms, exposure, history, macro shock and payment outcome.
- [ ] Implement a pre-issue feature contract and temporal train/validation/test split.
- [ ] Fit logistic regression and baselines; calibrate on validation only.
- [ ] Compute PR-AUC, Brier, top-decile lift, amount captured and value under a fixed capacity.
- [ ] Create a gain curve comparing model, amount rule and random.
- [ ] Write model card with intended use, exclusions, metrics and monitoring.
- [ ] Update README with backtest results clearly labeled synthetic.
- [ ] Run domain tests and commit.

### Task 7: Spend-anomaly evidence

**Files:**
- Create: `src/portfolio_analytics/spend_anomalies.py`
- Create: `tests/test_spend_anomalies.py`
- Create: `projects/05-spend-anomalies/data/sample.csv`
- Create: `projects/05-spend-anomalies/data/source.json`
- Create: `projects/05-spend-anomalies/outputs/metrics.json`
- Create: `projects/05-spend-anomalies/outputs/figure.png`
- Create: `projects/05-spend-anomalies/outputs/review_queue.csv`
- Create: `projects/05-spend-anomalies/MODEL_CARD.md`
- Modify: `projects/05-spend-anomalies/README.md`

- [ ] Write failing tests for duplicate reason codes, concentration and separation of injected labels from real flags.
- [ ] Download a bounded real Parquet sample derived from Checkbook NYC.
- [ ] Normalize vendor, agency, date, category and amount while retaining originals.
- [ ] Implement deterministic rules and peer-group features.
- [ ] Inject labeled anomalies into a copy, fit Isolation Forest and evaluate top-K retrieval.
- [ ] Produce a hybrid queue with reason codes and no fraud label.
- [ ] Create exposure-vs-evidence scatter.
- [ ] Update README and model card with validation and limitations.
- [ ] Run domain tests and commit.

### Task 8: Executed notebooks, portfolio front page and CI

**Files:**
- Create: `scripts/run_all.py`
- Create: `scripts/build_notebooks.py`
- Create: five `projects/*/notebooks/analysis.ipynb`
- Modify: `README.md`
- Modify: five project READMEs

- [ ] Implement `run_all.py` to call each analysis against checked samples and fail on non-finite metrics.
- [ ] Implement notebook generation with `nbformat` and execution with `nbclient`.
- [ ] Ensure every notebook includes tl;dr, methods, data, results and takeaways.
- [ ] Update root README with an evidence matrix, executed metrics, embedded figures, run command, CI badge and architecture.
- [ ] Run `make all`; expect all notebooks executed and validator green.
- [ ] Inspect all five PNGs and revise visual defects.
- [ ] Commit notebooks and presentation.

### Task 9: Final validation and publication

**Files:**
- No additional production files.

- [ ] Run:

```bash
.venv/bin/pytest -q
.venv/bin/python scripts/run_all.py --offline
.venv/bin/python scripts/build_notebooks.py
.venv/bin/python scripts/validate_portfolio.py
git diff --check origin/main...HEAD
```

- [ ] Recompute headline metrics from output tables and compare with `metrics.json`.
- [ ] Confirm each notebook contains executed outputs and every figure is at least 1400 × 800.
- [ ] Review the exact diff and exclude raw downloads, virtualenvs and unrelated temporary files.
- [ ] Push `agent/technical-evidence`, open a PR, mark ready and squash-merge to `main`.
- [ ] Delete the merged branch only after verifying the main tree matches.
