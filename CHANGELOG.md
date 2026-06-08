# Changelog

All notable changes to System Review Graph are documented here.

## 0.4.0 - 2026-06-08

Blueprint-depth release.

Added:

- `blueprint` report depth.
- `blueprint_sections` manifest support for source-evidence-backed system flows.
- Blueprint Mermaid map and detailed Markdown source-evidence, operational-flow,
  control-point, review-question, and known-gap sections.
- Blueprint summary table in HTML reports.
- MCP atlas context now includes blueprint sections.
- Linux kernel root atlas upgraded to a blueprint report with 11 major
  source-backed flows: build/config, boot/init, process scheduler, syscall
  boundary, memory, VFS/block IO, networking, driver model/probe, LSM security,
  modules/BPF/tracing, and Rust integration.

## 0.3.0 - 2026-06-08

Large-repository atlas release.

Added:

- `child_maps` manifest support for map-of-maps reports.
- Map-of-maps Mermaid visualization and child-map tables in Markdown and HTML reports.
- Atlas links in Mermaid relationship graphs and Graphviz DOT output.
- `scan --atlas` for root atlases plus child subsystem manifests.
- `scan --atlas --build-reports` for root and child report generation.
- `system-review-graph-mcp` stdio MCP server.
- MCP tools for validate, doctor, build, scan, and atlas-context loading.
- CI template step for merge-time system atlas regeneration.
- Linux kernel atlas stress-test example.

## 0.2.0 - 2026-06-08

Roadmap completion release.

Added:

- README Mermaid visualizations.
- HTML report output.
- Graphviz DOT output.
- JSON Schema for manifests.
- Stronger validation for duplicate IDs and unresolved explicit graph edges.
- `doctor` command for manifest quality checks.
- `scan` command for mixed-language starter manifests.
- Starter language detection for C, C++, Java, C#, Python, JavaScript/TypeScript, Go, and Rust.
- Generated HTML and DOT outputs for all bundled examples.

## 0.1.0 - 2026-06-08

Initial public release.

Added:

- Manifest-first system review graph builder.
- Markdown and JSON report generation.
- Mermaid lifecycle, artifact/schema, gate, and relationship visualizations.
- `overview`, `standard`, and `deep` report depth levels.
- Per-system drill-downs for artifacts, gates, and workflow touchpoints.
- CLI commands: `build`, `validate`, `init-example`, and `list-examples`.
- Bundled starter manifests for local and PyPI installs.
- Public examples for FastAPI, DuckDB, OpenTelemetry Collector, and a fictional AI Ops system.
- Tests, packaging metadata, release docs, and open-source project docs.
