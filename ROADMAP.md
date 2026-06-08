# Roadmap

System Review Graph is intentionally small today. The goal is to become a
practical bridge between code review, system design, audits, and AI-agent repo
orientation.

## Completed So Far

- Validation for duplicate IDs, unknown references, and unresolved explicit graph nodes.
- Real public repo examples for FastAPI, DuckDB, and OpenTelemetry Collector.
- HTML rendering for easier visual navigation.
- Optional Graphviz DOT export.
- JSON Schema for manifests.
- `doctor` command for report quality checks.
- `scan` command that creates starter manifests for mixed-language repositories.
- Starter language detection for C, C++, Java, C#, Python, JavaScript/TypeScript, Go, and Rust.
- README Mermaid visuals.
- Map-of-maps atlas support for huge repositories.
- `scan --atlas` with child subsystem manifests and optional report builds.
- MCP stdio server with scan/build/validate/doctor/load-atlas-context tools.
- Blueprint-depth reports with source evidence, operational flows, control points, and known gaps.
- Linux kernel blueprint with major source-backed operational paths.
- Merge-time atlas generation pattern for CI.
- Linux kernel atlas stress-test example.

## Near Term

- Add more real public repo examples across languages and architectures.
- Refine atlas scoring beyond top-level directories into changed files, ownership, docs, and tests.
- Add automated source-evidence extraction for blueprint sections.
- Detect OpenAPI, protobuf, SQL migrations, package metadata, docs, and tests in more detail.
- Add deeper language-specific scanners for Python, TypeScript, Go, Rust, Java, C#, C, and C++.
- Add an interactive review mode that asks missing-methodology questions.
- Add hosted documentation pages.

## Later

- Publish to PyPI.
- Add GitHub Actions release workflow with trusted publishing.
- Add examples contributed by other maintainers.
