from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NotebookInspection:
    notebook_path: str
    total_cells: int
    markdown_cells: int
    code_cells: int
    functions: list[str]
    constants: dict[str, Any]
    pipeline_order: list[str]


@dataclass(frozen=True)
class ConversionResult:
    notebook_path: str
    output_dir: str
    generated_files: list[str]
    pipeline_order: list[str]


def inspect_notebook(notebook_path: str | Path) -> NotebookInspection:
    notebook = _load_notebook(notebook_path)
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    markdown_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "markdown"]

    functions: list[str] = []
    constants: dict[str, Any] = {}

    for cell in code_cells:
        source = _cell_source(cell)
        module = ast.parse(source)
        for node in module.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        try:
                            constants[target.id] = ast.literal_eval(node.value)
                        except Exception:
                            continue

    pipeline_order = _resolve_pipeline_order(constants, functions)
    return NotebookInspection(
        notebook_path=str(notebook_path),
        total_cells=len(notebook["cells"]),
        markdown_cells=len(markdown_cells),
        code_cells=len(code_cells),
        functions=functions,
        constants=constants,
        pipeline_order=pipeline_order,
    )


def convert_notebook(notebook_path: str | Path, output_dir: str | Path) -> ConversionResult:
    inspection = inspect_notebook(notebook_path)
    notebook = _load_notebook(notebook_path)
    out_dir = Path(output_dir)
    tests_dir = out_dir / "tests"
    out_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    imports: list[str] = []
    function_sources: dict[str, str] = {}
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = _cell_source(cell)
        module = ast.parse(source)
        for node in module.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_source = ast.get_source_segment(source, node)
                if import_source and import_source not in imports:
                    imports.append(import_source)
            elif isinstance(node, ast.FunctionDef):
                function_source = ast.get_source_segment(source, node)
                if function_source:
                    function_sources[node.name] = function_source

    if not inspection.pipeline_order:
        raise ValueError("Notebook does not define a detectable pipeline order.")

    constants = {key: value for key, value in inspection.constants.items() if key != "PIPELINE_ORDER"}
    config_source = _render_config(constants)
    steps_source = _render_steps(imports, constants, function_sources, inspection.pipeline_order)
    pipeline_source = _render_pipeline(inspection.pipeline_order)
    test_source = _render_test()

    files = {
        out_dir / "config.py": config_source,
        out_dir / "steps.py": steps_source,
        out_dir / "pipeline.py": pipeline_source,
        out_dir / "tests" / "test_pipeline_contract.py": test_source,
        out_dir / "__init__.py": "\"\"\"Generated pipeline package.\"\"\"\n",
    }

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    return ConversionResult(
        notebook_path=str(notebook_path),
        output_dir=str(out_dir),
        generated_files=[str(path) for path in files],
        pipeline_order=inspection.pipeline_order,
    )


def inspection_to_dict(inspection: NotebookInspection) -> dict[str, Any]:
    return {
        "notebook_path": inspection.notebook_path,
        "total_cells": inspection.total_cells,
        "markdown_cells": inspection.markdown_cells,
        "code_cells": inspection.code_cells,
        "functions": inspection.functions,
        "constants": inspection.constants,
        "pipeline_order": inspection.pipeline_order,
    }


def conversion_to_dict(result: ConversionResult) -> dict[str, Any]:
    return {
        "notebook_path": result.notebook_path,
        "output_dir": result.output_dir,
        "generated_files": result.generated_files,
        "pipeline_order": result.pipeline_order,
    }


def format_inspection(inspection: NotebookInspection) -> str:
    lines = [
        f"Notebook {inspection.notebook_path}",
        (
            f"Cells: {inspection.total_cells} total | "
            f"{inspection.markdown_cells} markdown | {inspection.code_cells} code"
        ),
        f"Functions: {', '.join(inspection.functions) if inspection.functions else 'none'}",
        f"Constants: {', '.join(sorted(inspection.constants)) if inspection.constants else 'none'}",
        (
            "Pipeline order: "
            + (" -> ".join(inspection.pipeline_order) if inspection.pipeline_order else "none detected")
        ),
    ]
    return "\n".join(lines)


def format_conversion(result: ConversionResult) -> str:
    lines = [
        f"Converted {result.notebook_path}",
        f"Output directory: {result.output_dir}",
        f"Pipeline order: {' -> '.join(result.pipeline_order)}",
        "Generated files:",
    ]
    lines.extend(f"- {path}" for path in result.generated_files)
    return "\n".join(lines)


def _load_notebook(notebook_path: str | Path) -> dict[str, Any]:
    path = Path(notebook_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "cells" not in payload:
        raise ValueError("Notebook must be a valid .ipynb JSON document.")
    if not isinstance(payload["cells"], list):
        raise ValueError("Notebook cells must be a list.")
    return payload


def _cell_source(cell: dict[str, Any]) -> str:
    source = cell.get("source", [])
    if isinstance(source, list):
        return "".join(source)
    if isinstance(source, str):
        return source
    return ""


def _resolve_pipeline_order(constants: dict[str, Any], functions: list[str]) -> list[str]:
    raw = constants.get("PIPELINE_ORDER")
    if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        return [item for item in raw if item in functions]
    return functions


def _render_config(constants: dict[str, Any]) -> str:
    constant_lines = [f"{name} = {value!r}" for name, value in constants.items()]
    field_lines = [f"    {name.lower()}: object = {name}" for name in constants]
    return "\n".join(
        [
            "from __future__ import annotations",
            "",
            "from dataclasses import dataclass",
            "",
            *constant_lines,
            "",
            "@dataclass(frozen=True)",
            "class PipelineConfig:",
            *field_lines,
            "",
            "",
            "def default_config() -> PipelineConfig:",
            "    return PipelineConfig()",
            "",
        ]
    )


def _render_steps(
    imports: list[str],
    constants: dict[str, Any],
    function_sources: dict[str, str],
    pipeline_order: list[str],
) -> str:
    constant_names = ", ".join(constants.keys())
    blocks = ["from __future__ import annotations", ""]
    if imports:
        blocks.extend(imports)
        blocks.append("")
    if constant_names:
        blocks.append(f"from config import {constant_names}")
        blocks.append("")
    for name in pipeline_order:
        source = function_sources.get(name)
        if source is None:
            raise ValueError(f"Notebook is missing source for pipeline step '{name}'.")
        blocks.append(source.rstrip())
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def _render_pipeline(pipeline_order: list[str]) -> str:
    load_step, build_step, train_step, score_step = pipeline_order
    return "\n".join(
        [
            "from __future__ import annotations",
            "",
            "from config import PipelineConfig, default_config",
            f"from steps import {', '.join(pipeline_order)}",
            "",
            "",
            "def run_pipeline(config: PipelineConfig | None = None) -> dict[str, object]:",
            "    config = config or default_config()",
            f"    rows = {load_step}()",
            f"    feature_rows = {build_step}(rows)",
            f"    model = {train_step}(feature_rows)",
            f"    report = {score_step}(model, feature_rows)",
            "    return {",
            "        'config': config,",
            "        'rows': rows,",
            "        'feature_rows': feature_rows,",
            "        'model': model,",
            "        'report': report,",
            "    }",
            "",
            "",
            "if __name__ == '__main__':",
            "    print(run_pipeline())",
            "",
        ]
    )


def _render_test() -> str:
    return "\n".join(
        [
            "from __future__ import annotations",
            "",
            "import sys",
            "import unittest",
            "from pathlib import Path",
            "",
            "ROOT = Path(__file__).resolve().parents[1]",
            "if str(ROOT) not in sys.path:",
            "    sys.path.insert(0, str(ROOT))",
            "",
            "from pipeline import run_pipeline",
            "",
            "",
            "class PipelineContractTests(unittest.TestCase):",
            "    def test_pipeline_contract(self) -> None:",
            "        result = run_pipeline()",
            "        self.assertIn('rows', result)",
            "        self.assertIn('feature_rows', result)",
            "        self.assertIn('model', result)",
            "        self.assertIn('report', result)",
            "        self.assertGreater(len(result['rows']), 0)",
            "        self.assertGreater(len(result['feature_rows']), 0)",
            "        self.assertIn('at_risk_customers', result['report'])",
            "        self.assertIn('score_summary', result['report'])",
            "",
            "",
            "if __name__ == '__main__':",
            "    unittest.main()",
            "",
        ]
    )
