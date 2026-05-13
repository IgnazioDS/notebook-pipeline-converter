# Notebook Pipeline Converter

Python utility for turning exploratory Jupyter notebooks into modular, repeatable, and testable batch pipelines.

## What It Does

`notebook-pipeline-converter` is aimed at data teams that prototype in notebooks but need to graduate working logic into code that can be reviewed, scheduled, and tested like a normal software artifact.

Core outcomes:

- Inspect notebook structure and execution flow
- Extract cells into reusable modules and pipeline steps
- Generate a runnable batch entrypoint
- Produce starter tests around the converted pipeline contract

## Why It Exists

Notebooks are excellent for exploration and weak as long-term production assets. The moment a notebook becomes a dependency for scheduled work, onboarding, or regulated reporting, teams need an explicit conversion path into maintainable Python modules and pipeline entrypoints.

## What Ships Today

This repository now ships a real narrow conversion path:

- `inspect` reads a notebook and reports cells, detected functions, constants, and pipeline order
- `convert` turns the bundled churn example into `config.py`, `steps.py`, `pipeline.py`, and `tests/test_pipeline_contract.py`
- Example notebook input lives in `examples/churn_model.ipynb`
- Baseline regression coverage verifies both the CLI and the generated pipeline contract

## Repository Layout

- `src/notebook_pipeline_converter/`: CLI entrypoint, models, and catalog metadata
- `examples/`: bundled notebook conversion demo
- `docs/`: roadmap and architecture notes
- `tests/`: baseline contract tests
- `index.html` and `styles.css`: static project site

## Quickstart

```bash
git clone https://github.com/IgnazioDS/notebook-pipeline-converter.git
cd notebook-pipeline-converter
uv sync

uv run notebook-pipeline-converter summary
uv run notebook-pipeline-converter inspect examples/churn_model.ipynb
uv run notebook-pipeline-converter convert examples/churn_model.ipynb --out generated/churn_pipeline
uv run python -m unittest generated/churn_pipeline/tests/test_pipeline_contract.py
```

## Current Stack Direction

Python, notebook JSON parsing, CLI tooling, generated pipeline scaffolds

## Showcase Site

The repository includes a static landing page for lightweight demos and public previews.

```bash
vercel deploy -y
```

## License

MIT — see [LICENSE](./LICENSE).
