# Notebook Pipeline Converter

A utility that helps convert exploratory notebooks into repeatable, testable batch pipelines.

## Problem

Important data logic often gets trapped in notebooks that are hard to review, schedule, or maintain.

## Users

Data scientists, analytics engineers, ML teams

## Core Capabilities

- Analyze notebook structure
- Extract cells into modules and steps
- Generate a runnable pipeline entrypoint
- Create a starter test suite

## Why This Matters

The gap between experimentation and production remains a recurring bottleneck in data work.

## Architecture

- `core`: domain logic for notebook pipeline converter.
- `cli`: operator-facing entrypoint for local workflows and smoke checks.
- `docs/`: product notes, roadmap, and architecture decisions.
- `tests/`: baseline regression coverage for the project contract.

## Local Usage

```bash
uv run notebook-pipeline-converter summary
uv run notebook-pipeline-converter capabilities
uv run notebook-pipeline-converter roadmap
```

## Initial Stack Direction

Python, nbformat, Jinja, CLI

## Delivery Standard

- Clear product thesis
- Setup that works locally
- Tests for the primary contract
- Documentation for roadmap and architecture
- Space for production integrations in the next iteration
