# Roadmap

System Review Graph is intentionally small today. The goal is to become a
practical bridge between code review, system design, audits, and AI-agent repo
orientation.

## Near Term

- Improve validation for duplicate IDs and unresolved graph nodes.
- Add more real public repo examples across languages and architectures.
- Add HTML rendering for easier visual navigation.
- Add optional Graphviz export.
- Add JSON Schema for manifests.
- Add a `doctor` command for report quality checks.

## Next

- Generate starter manifests from repository structure.
- Detect OpenAPI, protobuf, SQL migrations, package metadata, docs, and tests.
- Add language-specific scanners for Python, TypeScript, Go, Rust, and Java.
- Add an interactive review mode that asks missing-methodology questions.

## Later

- Publish to PyPI.
- Add GitHub Actions release workflow with trusted publishing.
- Add hosted documentation pages.
- Add examples contributed by other maintainers.
