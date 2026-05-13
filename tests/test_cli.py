from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from notebook_pipeline_converter.cli import run


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        self.notebook = str(repo_root / "examples" / "churn_model.ipynb")

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

    def test_inspect_command(self) -> None:
        output = run(["inspect", self.notebook])
        self.assertIn("Cells:", output)
        self.assertIn("load_customer_rows", output)
        self.assertIn("Pipeline order:", output)

    def test_inspect_command_json(self) -> None:
        output = run(["inspect", self.notebook, "--format", "json"])
        payload = json.loads(output)
        self.assertEqual(payload["code_cells"], 5)
        self.assertEqual(payload["pipeline_order"][0], "load_customer_rows")

    def test_convert_command_generates_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "generated" / "churn_pipeline"
            output = run(["convert", self.notebook, "--out", str(out_dir)])

            self.assertIn("Generated files:", output)
            self.assertTrue((out_dir / "steps.py").exists())
            self.assertTrue((out_dir / "pipeline.py").exists())
            self.assertTrue((out_dir / "config.py").exists())
            self.assertTrue((out_dir / "tests" / "test_pipeline_contract.py").exists())

    def test_generated_pipeline_contract_test_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "generated" / "churn_pipeline"
            run(["convert", self.notebook, "--out", str(out_dir)])
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    str(out_dir / "tests"),
                    "-p",
                    "test_*.py",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
