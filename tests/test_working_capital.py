import unittest

import pandas as pd

from portfolio_analytics.working_capital import (
    calculate_working_capital,
    select_annual_facts,
)


class WorkingCapitalTest(unittest.TestCase):
    def test_ratios_use_average_opening_and_closing_balances(self) -> None:
        source = pd.DataFrame(
            [
                {
                    "company": "Demo",
                    "period_end": "2023-12-31",
                    "revenue": 1000.0,
                    "cogs": 600.0,
                    "accounts_receivable": 100.0,
                    "inventory": 80.0,
                    "accounts_payable": 50.0,
                    "operating_cash_flow": 120.0,
                    "capex": 30.0,
                },
                {
                    "company": "Demo",
                    "period_end": "2024-12-31",
                    "revenue": 1200.0,
                    "cogs": 720.0,
                    "accounts_receivable": 140.0,
                    "inventory": 90.0,
                    "accounts_payable": 60.0,
                    "operating_cash_flow": 140.0,
                    "capex": 35.0,
                },
            ]
        )

        result = calculate_working_capital(source)
        latest = result.iloc[-1]

        self.assertAlmostEqual(latest["dso"], 36.5, places=2)
        self.assertAlmostEqual(latest["dio"], 43.09, places=2)
        self.assertAlmostEqual(latest["dpo"], 27.88, places=2)
        self.assertAlmostEqual(latest["ccc"], 51.71, places=2)
        self.assertAlmostEqual(latest["free_cash_flow"], 105.0, places=2)

    def test_select_annual_facts_keeps_latest_filing_per_period(self) -> None:
        facts = [
            {
                "end": "2024-12-31",
                "start": "2024-01-01",
                "form": "10-K",
                "fp": "FY",
                "filed": "2025-02-01",
                "val": 100,
            },
            {
                "end": "2024-12-31",
                "start": "2024-01-01",
                "form": "10-K/A",
                "fp": "FY",
                "filed": "2025-03-01",
                "val": 110,
            },
            {
                "end": "2025-03-31",
                "start": "2025-01-01",
                "form": "10-Q",
                "fp": "Q1",
                "filed": "2025-05-01",
                "val": 30,
            },
        ]

        selected = select_annual_facts(facts, duration=True)

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["val"], 110)


if __name__ == "__main__":
    unittest.main()
