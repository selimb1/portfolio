from pathlib import Path
from tempfile import TemporaryDirectory
import json
import math
import unittest

from portfolio_analytics.common import file_sha256, write_json


class CommonUtilitiesTest(unittest.TestCase):
    def test_file_sha256_is_deterministic(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "data.txt"
            path.write_text("portfolio", encoding="utf-8")
            self.assertEqual(file_sha256(path), file_sha256(path))
            self.assertEqual(len(file_sha256(path)), 64)

    def test_write_json_rejects_non_finite_numbers(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "metrics.json"
            with self.assertRaisesRegex(ValueError, "finite"):
                write_json(path, {"bad": math.inf})

    def test_write_json_creates_parent_and_sorted_output(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "nested" / "metrics.json"
            write_json(path, {"z": 1, "a": 2})
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"a": 2, "z": 1},
            )
            self.assertLess(
                path.read_text(encoding="utf-8").index('"a"'),
                path.read_text(encoding="utf-8").index('"z"'),
            )


if __name__ == "__main__":
    unittest.main()
