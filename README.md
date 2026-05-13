# Notebook Pipeline Converter

Python utility scaffold for turning exploratory Jupyter notebooks into modular, repeatable, and testable batch pipelines.

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

This repository currently ships a showcase-state implementation:

- A Python CLI scaffold in `src/notebook_pipeline_converter/`
- Typed project metadata in `project.json`
- Architecture and roadmap notes in `docs/`
- Baseline regression coverage in `tests/`
- A Vercel-ready landing page (`index.html`, `styles.css`) for demos and portfolio visibility

## Repository Layout

- `src/notebook_pipeline_converter/`: CLI entrypoint, models, and catalog metadata
- `docs/`: roadmap and architecture notes
- `tests/`: baseline contract tests
- `index.html` and `styles.css`: static project site

## Quickstart

```bash
git clone https://github.com/IgnazioDS/notebook-pipeline-converter.git
cd notebook-pipeline-converter
uv sync

uv run notebook-pipeline-converter summary
uv run notebook-pipeline-converter capabilities
uv run notebook-pipeline-converter roadmap
```

## Planned Stack Direction

Python, nbformat, Jinja, CLI tooling, data-pipeline generation

## Showcase Site

The repository includes a static landing page for lightweight demos and public previews.

```bash
vercel deploy -y
```

## License

MIT — see [LICENSE](./LICENSE).
