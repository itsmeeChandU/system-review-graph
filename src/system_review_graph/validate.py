"""Manifest validation."""

from __future__ import annotations

from typing import Any

REQUIRED_TOP_LEVEL = {"title", "systems", "artifacts", "schemas", "decision_gates", "workflows"}


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return validation errors for a manifest."""

    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(manifest))
    if missing:
        errors.append(f"missing top-level keys: {', '.join(missing)}")
    for key in ("systems", "artifacts", "schemas", "decision_gates", "workflows"):
        if key in manifest and not isinstance(manifest[key], list):
            errors.append(f"{key} must be a list")
    for index, system in enumerate(manifest.get("systems") or []):
        if not isinstance(system, dict):
            errors.append(f"systems[{index}] must be an object")
            continue
        for field in ("system_id", "name", "purpose"):
            if not system.get(field):
                errors.append(f"systems[{index}] missing {field}")
    for index, artifact in enumerate(manifest.get("artifacts") or []):
        if not isinstance(artifact, dict):
            errors.append(f"artifacts[{index}] must be an object")
            continue
        if not artifact.get("artifact_id"):
            errors.append(f"artifacts[{index}] missing artifact_id")
    artifact_ids = {
        str(artifact.get("artifact_id"))
        for artifact in manifest.get("artifacts") or []
        if isinstance(artifact, dict) and artifact.get("artifact_id")
    }
    gate_ids = {
        str(gate.get("gate_id"))
        for gate in manifest.get("decision_gates") or []
        if isinstance(gate, dict) and gate.get("gate_id")
    }
    workflow_ids = {
        str(step.get("step_id"))
        for step in manifest.get("workflows") or []
        if isinstance(step, dict) and step.get("step_id")
    }
    schema_names = {
        str(schema.get("name"))
        for schema in manifest.get("schemas") or []
        if isinstance(schema, dict) and schema.get("name")
    }
    for index, artifact in enumerate(manifest.get("artifacts") or []):
        if not isinstance(artifact, dict):
            continue
        schema = artifact.get("schema")
        if schema and str(schema) not in schema_names:
            errors.append(f"artifacts[{index}] references unknown schema {schema}")
    for index, system in enumerate(manifest.get("systems") or []):
        if not isinstance(system, dict):
            continue
        for artifact_id in system.get("artifacts") or []:
            if str(artifact_id) not in artifact_ids:
                errors.append(f"systems[{index}] references unknown artifact {artifact_id}")
        for gate_id in system.get("decision_gates") or []:
            if str(gate_id) not in gate_ids:
                errors.append(f"systems[{index}] references unknown decision gate {gate_id}")
    for index, step in enumerate(manifest.get("workflows") or []):
        if not isinstance(step, dict):
            continue
        for gate_id in step.get("gates") or []:
            if str(gate_id) not in gate_ids:
                errors.append(f"workflows[{index}] references unknown decision gate {gate_id}")
        for next_step in step.get("next_steps") or []:
            if str(next_step) not in workflow_ids:
                errors.append(f"workflows[{index}] routes to unknown workflow step {next_step}")
    return errors
