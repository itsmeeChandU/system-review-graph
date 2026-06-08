"""Command line interface for System Review Graph."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from system_review_graph.builder import build_system_review
from system_review_graph.io import read_json, write_json
from system_review_graph.render import render_markdown
from system_review_graph.serialize import to_dict
from system_review_graph.validate import validate_manifest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_ROOT = PACKAGE_ROOT / "examples"
DEFAULT_EXAMPLE = "fictional_ai_ops"


def _example_choices() -> list[str]:
    return sorted(
        str(path.parent.relative_to(EXAMPLES_ROOT))
        for path in EXAMPLES_ROOT.rglob("system_review_manifest.json")
    )


def _build(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    out_dir = Path(args.out_dir)
    manifest = read_json(manifest_path)
    errors = validate_manifest(manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    graph = build_system_review(manifest)
    write_json(out_dir / "system_review_graph.json", to_dict(graph))
    (out_dir / "system_review_graph.md").parent.mkdir(parents=True, exist_ok=True)
    (out_dir / "system_review_graph.md").write_text(render_markdown(graph), encoding="utf-8")
    print(out_dir / "system_review_graph.md")
    return 0


def _validate(args: argparse.Namespace) -> int:
    errors = validate_manifest(read_json(Path(args.manifest)))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    print("manifest valid")
    return 0


def _init_example(args: argparse.Namespace) -> int:
    example_name = str(args.example).strip("/")
    source = EXAMPLES_ROOT / example_name
    if not (source / "system_review_manifest.json").exists():
        print(f"ERROR: unknown example {example_name!r}")
        print("Available examples:")
        for choice in _example_choices():
            print(f"- {choice}")
        return 2
    target = Path(args.out_dir)
    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"ERROR: {target} already exists and is not empty; pass --force to overwrite")
        return 2
    if target.exists() and args.force:
        shutil.rmtree(target)
    shutil.copytree(source, target)
    print(target)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="system-review-graph",
        description="Generate a system-level review graph from a sanitized manifest.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Build JSON and Markdown reports")
    build.add_argument("--manifest", required=True)
    build.add_argument("--out-dir", required=True)
    build.set_defaults(func=_build)

    validate = sub.add_parser("validate", help="Validate a manifest")
    validate.add_argument("--manifest", required=True)
    validate.set_defaults(func=_validate)

    init = sub.add_parser("init-example", help="Copy the bundled example project")
    init.add_argument("--out-dir", required=True)
    init.add_argument("--example", default=DEFAULT_EXAMPLE, help="Example path under examples/")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=_init_example)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
