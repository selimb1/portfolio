from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import time

import numpy as np
import pandas as pd
import requests

from portfolio_analytics.common import (
    BLUE,
    INK,
    ORANGE,
    apply_chart_style,
    project_root,
    save_figure,
    source_manifest,
    write_json,
)


SEC_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
SEC_SOURCE = (
    "https://www.sec.gov/search-filings/"
    "edgar-application-programming-interfaces"
)
COHORT = {
    "Caterpillar": "0000018230",
    "Deere": "0000315189",
    "3M": "0000066740",
    "Honeywell": "0000773840",
}
TICKERS = {
    "Caterpillar": "CAT",
    "Deere": "DE",
    "3M": "MMM",
    "Honeywell": "HON",
}
TAG_MAP: dict[str, tuple[str, ...]] = {
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "Revenues",
    ),
    "cogs": (
        "CostOfRevenue",
        "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
        "CostOfGoodsAndServicesSold",
    ),
    "accounts_receivable": (
        "AccountsReceivableNetCurrent",
        "AccountsAndNotesReceivableNetCurrent",
        "ReceivablesNetCurrent",
    ),
    "inventory": ("InventoryNet", "InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings"),
    "accounts_payable": (
        "AccountsPayableCurrent",
        "AccountsPayableAndAccruedLiabilitiesCurrent",
    ),
    "operating_cash_flow": ("NetCashProvidedByUsedInOperatingActivities",),
    "capex": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsForAdditionsToPropertyPlantAndEquipment",
    ),
}
DURATION_METRICS = {
    "revenue",
    "cogs",
    "operating_cash_flow",
    "capex",
}


def select_annual_facts(
    facts: Iterable[dict[str, Any]], duration: bool
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for fact in facts:
        if fact.get("form") not in {"10-K", "10-K/A"}:
            continue
        if fact.get("fp") != "FY" or not fact.get("end"):
            continue
        if duration and not fact.get("start"):
            continue
        if duration:
            days = (
                pd.Timestamp(fact["end"]) - pd.Timestamp(fact["start"])
            ).days
            if not 300 <= days <= 430:
                continue
        candidates.append(fact)

    latest_by_period: dict[str, dict[str, Any]] = {}
    for fact in sorted(candidates, key=lambda item: item.get("filed", "")):
        latest_by_period[fact["end"]] = fact
    return [
        latest_by_period[period]
        for period in sorted(latest_by_period)
    ]


def _metric_facts(
    companyfacts: dict[str, Any],
    tags: tuple[str, ...],
    duration: bool,
) -> pd.DataFrame:
    us_gaap = companyfacts.get("facts", {}).get("us-gaap", {})
    for tag in tags:
        concept = us_gaap.get(tag)
        if not concept:
            continue
        units = concept.get("units", {})
        facts = units.get("USD", [])
        selected = select_annual_facts(facts, duration=duration)
        if selected:
            return pd.DataFrame(
                {
                    "period_end": [fact["end"] for fact in selected],
                    "value": [float(fact["val"]) for fact in selected],
                    "filed": [fact.get("filed") for fact in selected],
                    "tag": tag,
                }
            )
    return pd.DataFrame(columns=["period_end", "value", "filed", "tag"])


def companyfacts_to_frame(
    companyfacts: dict[str, Any], company: str
) -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for metric, tags in TAG_MAP.items():
        facts = _metric_facts(
            companyfacts,
            tags,
            duration=metric in DURATION_METRICS,
        )
        metric_frame = facts[["period_end", "value"]].rename(
            columns={"value": metric}
        )
        merged = (
            metric_frame
            if merged is None
            else merged.merge(metric_frame, on="period_end", how="outer")
        )
    if merged is None:
        return pd.DataFrame()
    merged.insert(0, "company", company)
    merged["period_end"] = pd.to_datetime(merged["period_end"])
    merged = merged[merged["period_end"].dt.year >= 2018]
    required = [
        "revenue",
        "cogs",
        "accounts_receivable",
        "inventory",
        "accounts_payable",
        "operating_cash_flow",
        "capex",
    ]
    return merged.dropna(subset=required).sort_values("period_end")


def fetch_sec_sample(
    output_path: Path,
    user_agent: str = "selimb1 portfolio analytics contact via GitHub",
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    session = requests.Session()
    session.headers.update(
        {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"}
    )
    for company, cik in COHORT.items():
        response = session.get(SEC_URL.format(cik=cik), timeout=60)
        response.raise_for_status()
        frames.append(companyfacts_to_frame(response.json(), company))
        time.sleep(0.12)
    sample = pd.concat(frames, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    write_json(
        output_path.parent / "source.json",
        source_manifest(
            SEC_SOURCE,
            len(sample),
            retrieved_at=datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
            source_type="SEC Companyfacts API",
            cohort=COHORT,
            unit="company fiscal year",
            transformations=(
                "Selected latest 10-K/10-KA fact per period; standardized "
                "US-GAAP tags; retained complete observations from 2018."
            ),
        ),
    )
    return sample


def fetch_yahoo_sample(output_path: Path) -> pd.DataFrame:
    import yfinance as yf

    frames: list[pd.DataFrame] = []
    for company, ticker_symbol in TICKERS.items():
        ticker = yf.Ticker(ticker_symbol)
        income = ticker.get_income_stmt(freq="yearly")
        balance = ticker.get_balance_sheet(freq="yearly")
        cashflow = ticker.get_cash_flow(freq="yearly")
        dates = sorted(
            set(income.columns)
            & set(balance.columns)
            & set(cashflow.columns)
        )
        for period_end in dates:
            def value(frame: pd.DataFrame, labels: tuple[str, ...]) -> float:
                for label in labels:
                    if label in frame.index:
                        item = frame.at[label, period_end]
                        if pd.notna(item):
                            return float(item)
                return np.nan

            frames.append(
                pd.DataFrame(
                    [
                        {
                            "company": company,
                            "period_end": period_end,
                            "revenue": value(
                                income,
                                ("TotalRevenue", "OperatingRevenue"),
                            ),
                            "cogs": value(
                                income,
                                ("CostOfRevenue", "ReconciledCostOfRevenue"),
                            ),
                            "accounts_receivable": value(
                                balance,
                                (
                                    "AccountsReceivable",
                                    "Receivables",
                                    "GrossAccountsReceivable",
                                ),
                            ),
                            "inventory": value(
                                balance,
                                ("Inventory", "FinishedGoods"),
                            ),
                            "accounts_payable": value(
                                balance,
                                (
                                    "AccountsPayable",
                                    "Payables",
                                    "PayablesAndAccruedExpenses",
                                ),
                            ),
                            "operating_cash_flow": value(
                                cashflow,
                                (
                                    "OperatingCashFlow",
                                    "TotalCashFromOperatingActivities",
                                ),
                            ),
                            "capex": abs(
                                value(
                                    cashflow,
                                    ("CapitalExpenditure", "CapitalExpenditures"),
                                )
                            ),
                        }
                    ]
                )
            )
    sample = pd.concat(frames, ignore_index=True).dropna()
    sample = sample.sort_values(["company", "period_end"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    write_json(
        output_path.parent / "source.json",
        source_manifest(
            "https://finance.yahoo.com/",
            len(sample),
            source_type="Yahoo Finance statements via yfinance",
            official_refresh_source=SEC_SOURCE,
            cohort=TICKERS,
            unit="company fiscal year",
            transformations=(
                "Selected annual income statement, balance sheet and cash "
                "flow line items; retained complete observations."
            ),
        ),
    )
    return sample


def calculate_working_capital(source: pd.DataFrame) -> pd.DataFrame:
    data = source.copy()
    data["period_end"] = pd.to_datetime(data["period_end"])
    data = data.sort_values(["company", "period_end"]).reset_index(drop=True)
    balance_columns = {
        "accounts_receivable": "avg_accounts_receivable",
        "inventory": "avg_inventory",
        "accounts_payable": "avg_accounts_payable",
    }
    for raw, average in balance_columns.items():
        previous = data.groupby("company")[raw].shift(1)
        data[average] = (data[raw] + previous.fillna(data[raw])) / 2

    data["dso"] = data["avg_accounts_receivable"] / data["revenue"] * 365
    data["dio"] = data["avg_inventory"] / data["cogs"] * 365
    data["dpo"] = data["avg_accounts_payable"] / data["cogs"] * 365
    data["ccc"] = data["dso"] + data["dio"] - data["dpo"]
    data["free_cash_flow"] = data["operating_cash_flow"] - data["capex"]
    data["revenue_growth_pct"] = (
        data.groupby("company")["revenue"].pct_change() * 100
    )
    data["ccc_change_days"] = data.groupby("company")["ccc"].diff()
    data["cash_effect"] = (
        data["ccc_change_days"] / 365 * data["revenue"]
    )
    return data.replace([np.inf, -np.inf], np.nan)


def analyze(sample_path: Path, output_dir: Path) -> dict[str, Any]:
    source = pd.read_csv(sample_path)
    metrics_frame = calculate_working_capital(source)
    comparable = metrics_frame.dropna(
        subset=["revenue_growth_pct", "ccc_change_days"]
    )
    if comparable.empty:
        raise ValueError("Working-capital sample has no comparable periods")

    latest = (
        comparable.sort_values("period_end")
        .groupby("company", as_index=False)
        .tail(1)
    )
    focus = latest.loc[latest["ccc_change_days"].idxmax()]
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_frame.to_csv(
        output_dir / "company_metrics.csv", index=False, float_format="%.4f"
    )

    result = {
        "sample_rows": int(len(source)),
        "companies": int(source["company"].nunique()),
        "comparable_observations": int(len(comparable)),
        "latest_year": int(pd.Timestamp(focus["period_end"]).year),
        "largest_deterioration_company": str(focus["company"]),
        "largest_ccc_change_days": round(float(focus["ccc_change_days"]), 2),
        "approximate_cash_effect_usd": round(float(focus["cash_effect"]), 2),
        "median_latest_ccc_days": round(float(latest["ccc"].median()), 2),
    }
    write_json(output_dir / "metrics.json", result)

    import matplotlib.pyplot as plt

    apply_chart_style()
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.scatter(
        comparable["revenue_growth_pct"],
        comparable["ccc_change_days"],
        s=52,
        color=BLUE,
        alpha=0.58,
        edgecolor="white",
        linewidth=0.5,
        label="Años comparables",
    )
    axis.scatter(
        latest["revenue_growth_pct"],
        latest["ccc_change_days"],
        s=110,
        color=ORANGE,
        edgecolor=INK,
        linewidth=0.8,
        label="Último año por empresa",
        zorder=3,
    )
    for row in latest.itertuples():
        axis.annotate(
            row.company,
            (row.revenue_growth_pct, row.ccc_change_days),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
            color=INK,
        )
    axis.axhline(0, color=INK, linewidth=1)
    axis.axvline(0, color=INK, linewidth=1)
    axis.set_title("Crecimiento de ventas y cambio del ciclo de caja")
    axis.set_xlabel("Crecimiento anual de ventas (%)")
    axis.set_ylabel("Cambio anual del CCC (días)")
    axis.legend(loc="best")
    figure.text(
        0.1,
        0.01,
        "Estados financieros públicos vía Yahoo Finance · cohorte industrial · valores anuales",
        color="#667085",
        fontsize=9,
    )
    save_figure(figure, output_dir / "figure.png")
    plt.close(figure)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the working-capital analysis.")
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root() / "projects/01-working-capital/data/sample.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "projects/01-working-capital/outputs",
    )
    args = parser.parse_args()
    print(analyze(args.input, args.output_dir))


if __name__ == "__main__":
    main()
