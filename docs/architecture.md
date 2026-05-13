# Architecture Notes

## Product Shape

Notebook Pipeline Converter now has a real local boundary: notebook inspection, narrow-path code extraction, and generated pipeline scaffolds with a contract test. The interface is still intentionally small so the core logic can evolve into an API, worker, or scheduled job without rework.

## Design Priorities

- Keep the product contract explicit and testable.
- Avoid framework lock-in early.
- Reserve room for persistence, telemetry, and deployment concerns.
- Treat generated output as an artifact that can be audited.

## Current Modules

- `models.py` defines the typed project metadata.
- `catalog.py` loads the shipped product spec.
- `cli.py` exposes summary, inspect, convert, capabilities, and roadmap commands.
- `converter.py` parses notebook JSON, extracts functions/constants, and renders generated pipeline files.
