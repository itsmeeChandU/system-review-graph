# System Review Graph

Code-review graphs tell you what code exists. System Review Graph tells you what the system actually does.

It turns a public or sanitized manifest into:

- a system-level graph,
- a reverse-engineering report,
- architecture and workflow maps,
- decision-gate documentation,
- schema and artifact references,
- walkthrough examples for reviewers, maintainers, and AI agents.

This project is meant for open-source maintainers, platform teams, audit teams, AI coding agents, and new engineers who need to understand a repo as an operating system rather than a pile of files.

## Why This Exists

Most repo maps stop at modules, classes, functions, imports, and calls. That is useful, but it does not answer the questions a real reviewer asks:

- What does this system do?
- What are the decision gates?
- What data or artifacts feed each stage?
- What actions can happen downstream?
- What is blocked by human/legal/security review?
- What can be shared publicly when the database is private?
- How could someone rebuild the system from the report?

System Review Graph is the opposite side of a code-review graph:

| Map | Answers |
|---|---|
| Code-review graph | What code exists and how it connects. |
| System Review Graph | What the system does, how it moves, what it trusts, and what it blocks. |

## Quick Start

```bash
python -m pip install -e .
system-review-graph validate --manifest examples/fictional_ai_ops/system_review_manifest.json
system-review-graph build \
  --manifest examples/fictional_ai_ops/system_review_manifest.json \
  --out-dir examples/fictional_ai_ops/reports \
  --depth deep
```

Open:

```text
examples/fictional_ai_ops/reports/system_review_graph.md
```

Try an actual public repo example:

```bash
system-review-graph build \
  --manifest examples/actual_repos/fastapi/system_review_manifest.json \
  --out-dir examples/actual_repos/fastapi/reports
```

## Example Gallery

| Example | What It Teaches | Generated Report |
|---|---|---|
| Fictional AI Ops | End-to-end `source -> fact -> decision -> action -> outcome -> lesson` flow | `examples/fictional_ai_ops/reports/system_review_graph.md` |
| FastAPI | Framework/API runtime mapping | `examples/actual_repos/fastapi/reports/system_review_graph.md` |
| DuckDB | Database/query-engine mapping | `examples/actual_repos/duckdb/reports/system_review_graph.md` |
| OpenTelemetry Collector | Component pipeline and API-only review mapping | `examples/actual_repos/opentelemetry_collector/reports/system_review_graph.md` |

The actual-repo examples are educational public-review maps, not official
maintainer audits.

## Depth Levels

Reports are generated with `--depth deep` by default.

| Depth | Use When | Includes |
|---|---|---|
| `overview` | You need the fastest orientation. | Current truth, source links, lifecycle map, expansion index, systems, architecture patterns, walkthroughs, review questions. |
| `standard` | You want a normal audit handoff. | Overview plus artifact/schema map, gate map, system details, artifacts, schemas, gates, and workflows. |
| `deep` | You want blueprint-level inspection. | Standard plus relationship graph, schema examples, and per-system artifact/gate/workflow drill-downs. |

```bash
system-review-graph build \
  --manifest examples/actual_repos/duckdb/system_review_manifest.json \
  --out-dir /tmp/duckdb-system-review \
  --depth deep
```

## Manifest-First Design

The tool is intentionally manifest-first. A project can expose a safe system map without exposing private tables, production data, model weights, vendor contracts, or internal credentials.

That matters for:

- public open-source projects,
- enterprise services with private databases,
- data platforms,
- ML systems,
- agent systems,
- microservice platforms,
- embedded or hardware-adjacent systems,
- regulated or security-sensitive environments.

## What You Describe

A manifest describes:

- systems,
- artifacts,
- schemas,
- decision gates,
- workflows,
- graph edges,
- source links,
- current truth,
- architecture patterns,
- walkthroughs,
- review questions,
- rebuild recipe,
- known boundaries.

Example system row:

```json
{
  "system_id": "action_engine",
  "name": "Action Engine",
  "purpose": "Turns approved recommendations into bounded action intents.",
  "architecture_style": "event-driven service",
  "language_stack": ["Python", "PostgreSQL", "OpenAPI"],
  "truth_boundary": "Can propose actions, but cannot execute restricted actions without a human gate.",
  "ideal_target": "Every action has an outcome and lesson."
}
```

## Public-Safe Reviews

Companies often cannot publish database schemas, architecture details, or source data. This tool supports sanitized reporting:

- publish interface schemas instead of raw tables,
- publish field names without sample values,
- publish evidence counts instead of records,
- publish redacted artifact paths,
- publish decision rules without secrets,
- publish risk boundaries and human gates.

The goal is not to leak the system. The goal is to explain the system.

## Repository Layout

```text
src/system_review_graph/
  builder.py      # manifest -> graph object
  render.py       # Markdown and Mermaid rendering
  cli.py          # system-review-graph CLI
  models.py       # typed graph structures
docs/
  WALKTHROUGH.md
  SCHEMA.md
  ARCHITECTURE_PATTERNS.md
examples/
  fictional_ai_ops/
    system_review_manifest.json
    reports/system_review_graph.md
  actual_repos/
    fastapi/
    duckdb/
    opentelemetry_collector/
```

## Development

```bash
python -m pip install -e .
python -m pytest
python -m ruff check .
```

A GitHub Actions CI template is available at
`docs/ci/github-actions-ci.yml`. Copy it to `.github/workflows/ci.yml` in your
own repository if you want automated lint, tests, and example-report builds.

## Philosophy

Knowledge is not enough. A useful system map should show how knowledge becomes:

```text
source -> fact -> candidate -> decision -> action -> outcome -> lesson
```

That is the path from information to operational wisdom.
