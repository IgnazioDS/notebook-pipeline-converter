from __future__ import annotations

import unittest

from notebook_pipeline_converter.cli import run


class CliTests(unittest.TestCase):
    def test_summary(self) -> None:
        output = run(["summary"])
        self.assertIn("Notebook Pipeline Converter", output)
        self.assertIn("Important data logic often gets trapped in notebooks that are hard to review, schedule, or maintain.", output)

    def test_capabilities(self) -> None:
        output = run(["capabilities"])
        self.assertIn("Core capabilities:", output)
        self.assertIn("Analyze notebook structure", output)

    def test_roadmap(self) -> None:
        output = run(["roadmap"])
        self.assertIn("# Roadmap", output)
        self.assertIn("## Phase 1", output)


if __name__ == "__main__":
    unittest.main()
