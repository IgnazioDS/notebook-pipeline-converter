from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalog import load_project
from .converter import (
    conversion_to_dict,
    convert_notebook,
    format_conversion,
    format_inspection,
    inspect_notebook,
    inspection_to_dict,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="notebook-pipeline-converter",
        description="Operate Notebook Pipeline Converter.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("summary", help="Print product summary.")
    subparsers.add_parser("capabilities", help="Print initial capabilities.")
    subparsers.add_parser("roadmap", help="Print roadmap.")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect notebook structure and detected pipeline steps.")
    inspect_parser.add_argument("notebook", help="Path to a .ipynb file.")
    inspect_parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")

    convert_parser = subparsers.add_parser("convert", help="Convert a notebook into a generated pipeline package.")
    convert_parser.add_argument("notebook", help="Path to a .ipynb file.")
    convert_parser.add_argument("--out", required=True, help="Output directory for generated files.")
    convert_parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser


def run(argv: list[str] | None = None) -> str:
    args = build_parser().parse_args(argv)
    project = load_project()

    if args.command == "summary":
        return "\n".join([
            project.name,
            "=" * len(project.name),
            project.summary,
            "",
            f"Problem: {project.problem}",
            f"Users: {project.users}",
            f"Stage: {project.stage}",
            f"Track: {project.track}",
        ])
    if args.command == "capabilities":
        lines = [project.name, "", "Core capabilities:"]
        lines.extend(f"- {item}" for item in project.mvp)
        return "\n".join(lines)
    if args.command == "roadmap":
        roadmap_path = Path(__file__).resolve().parents[2] / "docs" / "roadmap.md"
        return roadmap_path.read_text(encoding="utf-8").strip()
    if args.command == "inspect":
        inspection = inspect_notebook(args.notebook)
        if args.format == "json":
            return json.dumps(inspection_to_dict(inspection), indent=2)
        return format_inspection(inspection)
    if args.command == "convert":
        result = convert_notebook(args.notebook, args.out)
        if args.format == "json":
            return json.dumps(conversion_to_dict(result), indent=2)
        return format_conversion(result)
    raise ValueError(f"Unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    print(run(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
