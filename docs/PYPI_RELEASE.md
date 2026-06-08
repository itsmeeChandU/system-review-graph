# PyPI Release Guide

System Review Graph is PyPI-ready, but publishing requires a PyPI account or
trusted-publishing setup controlled by the maintainer.

Official packaging flow, in plain language:

1. Keep package metadata in `pyproject.toml`.
2. Build a source distribution and wheel.
3. Check the package metadata.
4. Upload to TestPyPI first.
5. Upload to PyPI after verifying install.

## Build Locally

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

## Test The Wheel

```bash
python -m venv /tmp/srg-test
source /tmp/srg-test/bin/activate
python -m pip install dist/system_review_graph-0.1.0-py3-none-any.whl
system-review-graph list-examples
system-review-graph init-example --example fictional_ai_ops --out-dir /tmp/srg-example --force
system-review-graph build --manifest /tmp/srg-example/system_review_manifest.json --out-dir /tmp/srg-report
```

## Upload

Use TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

Then PyPI:

```bash
python -m twine upload dist/*
```

## Trusted Publishing

For a future automated release, configure PyPI trusted publishing for the
GitHub repository and add a GitHub Actions workflow. A template is kept at:

```text
docs/ci/github-actions-ci.yml
```

The current repository token used by Codex did not have GitHub `workflow` scope,
so the workflow is documented as a template instead of committed under
`.github/workflows/`.

## References

- Python Packaging User Guide: https://packaging.python.org/en/latest/flow/
- PyPI project metadata docs: https://docs.pypi.org/project_metadata/
- Twine: https://pypi.org/project/twine/
