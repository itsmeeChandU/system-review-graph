# Roadmap

System Review Graph is intentionally small today. The goal is to become a
practical bridge between code review, system design, audits, and AI-agent repo
orientation.

## Completed In 0.1.x

- Validation for duplicate IDs, unknown references, and unresolved explicit graph nodes.
- Real public repo examples for FastAPI, DuckDB, and OpenTelemetry Collector.
- HTML rendering for easier visual navigation.
- Optional Graphviz DOT export.
- JSON Schema for manifests.
- `doctor` command for report quality checks.
- `scan` command that creates starter manifests for mixed-language repositories.
- Starter language detection for C, C++, Java, C#, Python, JavaScript/TypeScript, Go, and Rust.
- README Mermaid visuals.

## Near Term

- Add more real public repo examples across languages and architectures.
- Detect OpenAPI, protobuf, SQL migrations, package metadata, docs, and tests in more detail.
- Add deeper language-specific scanners for Python, TypeScript, Go, Rust, Java, C#, C, and C++.
- Add an interactive review mode that asks missing-methodology questions.
- Add hosted documentation pages.

## Later

- Publish to PyPI.
- Add GitHub Actions release workflow with trusted publishing.
- Add examples contributed by other maintainers.
