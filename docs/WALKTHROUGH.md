# Walkthrough

This walkthrough uses the bundled fictional example.

## 1. Validate The Manifest

```bash
system-review-graph validate --manifest examples/fictional_ai_ops/system_review_manifest.json
```

Expected:

```text
manifest valid
```

## 2. Build The Report

```bash
system-review-graph build \
  --manifest examples/fictional_ai_ops/system_review_manifest.json \
  --out-dir examples/fictional_ai_ops/reports \
  --depth deep
```

Outputs:

```text
examples/fictional_ai_ops/reports/system_review_graph.json
examples/fictional_ai_ops/reports/system_review_graph.md
```

Depth options:

- `overview`: fastest orientation.
- `standard`: normal audit handoff.
- `deep`: blueprint-level report with relationship graph and per-system drill-downs.

## 3. Read The Report Like A Reviewer

Start with:

- Bigger Picture
- Current Truth
- System Graph
- Systems
- Decision Gates
- Workflows
- Walkthroughs

The report should answer:

- What does the system do?
- What are the major subsystems?
- What artifacts prove each subsystem exists?
- Which gates block unsafe action?
- What can be shared publicly?
- What is still unproven?

## 4. Apply To Your Project

Create your own manifest:

```bash
system-review-graph init-example --out-dir /tmp/my-system-review --force
```

Then edit:

```text
/tmp/my-system-review/system_review_manifest.json
```

Replace the fictional systems with your own:

- web app,
- API,
- database,
- data pipeline,
- ML model,
- event bus,
- admin UI,
- approval workflow,
- reporting layer.

## 5. For Private Systems

If you cannot expose internals:

- use sanitized schemas,
- remove raw sample values,
- replace database paths with logical names,
- publish counts instead of records,
- describe gates and redaction boundaries,
- include examples with fake data only.

The report should teach the architecture without leaking the company.

## 6. Check Report Quality

Run:

```bash
system-review-graph doctor --manifest examples/fictional_ai_ops/system_review_manifest.json
```

The doctor command reports missing boundaries, shallow workflows, unresolved
references, and missing review/audit surfaces.

## 7. Generate HTML Or DOT

```bash
system-review-graph build \
  --manifest examples/actual_repos/fastapi/system_review_manifest.json \
  --out-dir /tmp/fastapi-system-review \
  --depth deep \
  --html \
  --dot
```

Outputs:

```text
system_review_graph.md
system_review_graph.json
system_review_graph.html
system_review_graph.dot
```

## 8. Scan A Mixed-Language Repo

```bash
system-review-graph scan \
  --repo /path/to/repo \
  --out /tmp/system_review_manifest.json
```

The scanner detects starter surfaces for C, C++, Java, C#, Python,
JavaScript/TypeScript, Go, Rust, docs, tests, and common build/config files.
It is a starting point, not a proof of runtime behavior.

## 9. Try Actual Public Repos

The `examples/actual_repos/` folder contains public-review manifests for real
open-source repositories. They are educational maps, not official maintainer
audits.

```bash
system-review-graph build \
  --manifest examples/actual_repos/duckdb/system_review_manifest.json \
  --out-dir examples/actual_repos/duckdb/reports \
  --depth deep
```

Use these examples to learn how different architecture shapes map into the same
review grammar:

- framework repo,
- database engine,
- component pipeline.
