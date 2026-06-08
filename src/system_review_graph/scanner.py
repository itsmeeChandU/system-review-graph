"""Language-neutral starter manifest scanner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

LANGUAGE_RULES = [
    {
        "id": "python",
        "name": "Python Surface",
        "extensions": {".py"},
        "markers": {"pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"},
        "stack": ["Python"],
    },
    {
        "id": "javascript_typescript",
        "name": "JavaScript / TypeScript Surface",
        "extensions": {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"},
        "markers": {"package.json", "tsconfig.json", "vite.config.ts", "next.config.js"},
        "stack": ["JavaScript", "TypeScript"],
    },
    {
        "id": "c_cpp",
        "name": "C / C++ Surface",
        "extensions": {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hh"},
        "markers": {"CMakeLists.txt", "Makefile", "configure.ac"},
        "stack": ["C", "C++"],
    },
    {
        "id": "java",
        "name": "Java Surface",
        "extensions": {".java", ".kt"},
        "markers": {"pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"},
        "stack": ["Java", "Kotlin"],
    },
    {
        "id": "csharp_dotnet",
        "name": "C# / .NET Surface",
        "extensions": {".cs", ".csproj", ".sln"},
        "markers": {"Directory.Build.props", "global.json"},
        "stack": ["C#", ".NET"],
    },
    {
        "id": "go",
        "name": "Go Surface",
        "extensions": {".go"},
        "markers": {"go.mod", "go.sum"},
        "stack": ["Go"],
    },
    {
        "id": "rust",
        "name": "Rust Surface",
        "extensions": {".rs"},
        "markers": {"Cargo.toml", "Cargo.lock"},
        "stack": ["Rust"],
    },
]

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "dist",
    "build",
    "__pycache__",
}


def _iter_files(root: Path, limit: int) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.append(path)
        if len(files) >= limit:
            break
    return files


def _relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _top_dirs(files: list[Path], root: Path, extensions: set[str]) -> list[str]:
    dirs: set[str] = set()
    for path in files:
        if path.suffix.lower() not in extensions:
            continue
        relative = path.relative_to(root)
        if len(relative.parts) > 1:
            dirs.add(relative.parts[0] + "/")
        else:
            dirs.add(_relative(path, root))
    return sorted(dirs)[:12]


def _marker_hits(files: list[Path], root: Path, markers: set[str]) -> list[str]:
    hits = []
    for path in files:
        if path.name in markers:
            hits.append(_relative(path, root))
    return sorted(hits)[:20]


def _directory_exists(root: Path, names: set[str]) -> list[str]:
    return sorted(
        f"{path.name}/"
        for path in root.iterdir()
        if path.is_dir() and path.name.lower() in names
    )


def scan_repository(root: Path, title: str | None = None, file_limit: int = 6000) -> dict[str, Any]:
    """Create a starter manifest from a repository directory."""

    root = root.resolve()
    files = _iter_files(root, file_limit)
    systems: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    workflows: list[dict[str, Any]] = []
    detected_language_ids: list[str] = []

    for rule in LANGUAGE_RULES:
        code_surfaces = _top_dirs(files, root, rule["extensions"])
        marker_hits = _marker_hits(files, root, rule["markers"])
        if not code_surfaces and not marker_hits:
            continue
        language_label = rule["name"].replace(" Surface", "")
        detected_language_ids.append(rule["id"])
        artifact_id = f"{rule['id']}_source_surface"
        artifacts.append(
            {
                "artifact_id": artifact_id,
                "name": rule["name"],
                "kind": "source_surface",
                "path": ", ".join(code_surfaces or marker_hits),
                "owner": "unknown",
                "schema": "SourceSurface",
                "purpose": f"Detected {language_label} source and build surfaces.",
                "redaction": "safe_to_share",
            }
        )
        systems.append(
            {
                "system_id": rule["id"],
                "name": rule["name"],
                "purpose": f"Detected {language_label} code and build surfaces for review.",
                "owner": "unknown",
                "language_stack": rule["stack"],
                "architecture_style": "detected source surface",
                "lifecycle": "source files -> build/test docs -> inferred system role",
                "code_surfaces": code_surfaces,
                "artifacts": [artifact_id],
                "decision_gates": ["manual_review_gate"],
                "truth_boundary": "Detected from repository files; runtime behavior is not proven.",
                "ideal_target": (
                    "Replace this starter node with exact subsystem ownership "
                    "and workflows."
                ),
            }
        )

    docs_dirs = _directory_exists(root, {"docs", "doc", "documentation"})
    test_dirs = _directory_exists(root, {"test", "tests", "spec", "specs", "__tests__"})
    config_files = [
        _relative(path, root)
        for path in files
        if path.name
        in {
            "Dockerfile",
            "docker-compose.yml",
            "compose.yml",
            "Makefile",
            "CMakeLists.txt",
            "pyproject.toml",
            "package.json",
            "pom.xml",
            "go.mod",
            "Cargo.toml",
        }
    ][:30]

    if docs_dirs:
        artifacts.append(
            {
                "artifact_id": "documentation_surface",
                "name": "Documentation Surface",
                "kind": "docs",
                "path": ", ".join(docs_dirs),
                "owner": "unknown",
                "schema": "DocumentationSurface",
                "purpose": "Detected documentation directories that may explain system behavior.",
                "redaction": "safe_to_share",
            }
        )
    if test_dirs:
        artifacts.append(
            {
                "artifact_id": "test_surface",
                "name": "Test Surface",
                "kind": "tests",
                "path": ", ".join(test_dirs),
                "owner": "unknown",
                "schema": "TestSurface",
                "purpose": "Detected test directories that may prove behavior.",
                "redaction": "safe_to_share",
            }
        )
    if config_files:
        artifacts.append(
            {
                "artifact_id": "config_build_surface",
                "name": "Config And Build Surface",
                "kind": "config",
                "path": ", ".join(config_files),
                "owner": "unknown",
                "schema": "ConfigSurface",
                "purpose": "Detected build, package, container, or configuration files.",
                "redaction": "safe_to_share",
            }
        )

    if detected_language_ids:
        first_step = "inspect_source_surfaces"
        workflows.append(
            {
                "step_id": first_step,
                "name": "Inspect Source Surfaces",
                "actor": "Reviewer",
                "consumes": [
                    f"{language_id}_source_surface"
                    for language_id in detected_language_ids
                ],
                "produces": ["candidate_system_map"],
                "gates": ["manual_review_gate"],
                "next_steps": ["refine_workflows"],
                "purpose": "Turn detected code/build surfaces into a human-reviewed system map.",
            }
        )
        workflows.append(
            {
                "step_id": "refine_workflows",
                "name": "Refine Workflows",
                "actor": "Maintainer",
                "consumes": ["candidate_system_map"],
                "produces": ["system_review_manifest"],
                "gates": ["manual_review_gate"],
                "next_steps": [],
                "purpose": "Replace inferred surfaces with exact workflows, gates, and boundaries.",
            }
        )

    repo_name = root.name
    return {
        "title": title or f"{repo_name} Starter System Review Graph",
        "one_line": (
            "Starter manifest generated from repository language, build, docs, "
            "and test surfaces."
        ),
        "scope": f"Generated starter manifest for {root}.",
        "bigger_picture": (
            "This is an inferred starter map. It detects language and project surfaces, "
            "then asks maintainers or agents to refine actual workflows, gates, and boundaries."
        ),
        "current_truth": {
            "scanner": "language_neutral_starter",
            "file_limit": file_limit,
            "files_seen": len(files),
            "detected_languages": detected_language_ids,
            "runtime_behavior_proven": False,
        },
        "source_links": [],
        "schemas": [
            {
                "name": "SourceSurface",
                "kind": "detected_contract",
                "required_fields": ["path", "language_stack", "build_markers"],
                "purpose": "A detected source/build surface that needs human review.",
                "privacy_notes": "Only paths and coarse metadata are included.",
            },
            {
                "name": "DocumentationSurface",
                "kind": "detected_contract",
                "required_fields": ["path", "purpose"],
                "purpose": "Detected docs that may explain system behavior.",
            },
            {
                "name": "TestSurface",
                "kind": "detected_contract",
                "required_fields": ["path", "purpose"],
                "purpose": "Detected tests that may prove behavior.",
            },
            {
                "name": "ConfigSurface",
                "kind": "detected_contract",
                "required_fields": ["path", "purpose"],
                "purpose": "Detected build/config/deployment surface.",
            },
        ],
        "artifacts": artifacts,
        "decision_gates": [
            {
                "gate_id": "manual_review_gate",
                "name": "Manual Review Gate",
                "inputs": ["detected surfaces", "maintainer knowledge"],
                "outputs": ["accepted", "needs_refinement", "rejected"],
                "human_gate": True,
                "risk_boundary": (
                    "Scanner output is a starting point, not proof of runtime behavior."
                ),
                "rules": [
                    {"if": "surface matches real subsystem", "then": "accepted"},
                    {"if": "surface is too broad or ambiguous", "then": "needs_refinement"},
                    {"if": "surface is generated/noise", "then": "rejected"},
                ],
            }
        ],
        "systems": systems,
        "workflows": workflows,
        "edges": [],
        "architecture_patterns": [
            {
                "name": "Mixed-language repository",
                "works_for": (
                    "C, C++, Java, C#, Python, JavaScript/TypeScript, Go, "
                    "Rust, and mixed repos"
                ),
                "mapping": (
                    "Detect language/build/test/doc surfaces first, then refine "
                    "into exact systems and workflows."
                ),
                "redaction": "Publish paths and contracts, not private records or secrets.",
            }
        ],
        "walkthroughs": [
            {
                "name": "From scan to real system review",
                "story": (
                    "Run scan, inspect detected surfaces, replace broad language "
                    "nodes with real subsystems, then add workflows and gates."
                ),
                "example": {
                    "scan": "system-review-graph scan --repo . --out system_review_manifest.json",
                    "refine": ["systems", "artifacts", "workflows", "decision_gates"],
                },
            }
        ],
        "review_questions": [
            "Which detected language surfaces are real subsystems?",
            "Which directories are generated or vendor noise?",
            "Where are APIs, CLIs, configs, migrations, docs, and tests?",
            "Which workflows move data or decisions end to end?",
            "Which gates block unsafe or unreviewed behavior?",
        ],
        "rebuild_recipe": [
            {
                "phase": "scan",
                "goal": "Generate a starter manifest from repository surfaces.",
                "commands": [
                    "system-review-graph scan --repo . --out system_review_manifest.json"
                ],
            }
        ],
        "known_boundaries": [
            "Scanner output is inferred from file paths and markers.",
            "Runtime behavior, production deployment, and ownership are not proven.",
            (
                "Maintainers or agents should refine workflows, gates, and "
                "boundaries before audit use."
            ),
        ],
    }
