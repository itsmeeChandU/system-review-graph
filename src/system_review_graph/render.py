"""Markdown and Mermaid rendering."""

from __future__ import annotations

import json
import re

from system_review_graph.models import SystemReviewGraph


def _row(values: list[object]) -> str:
    return "| " + " | ".join(str(value).replace("|", "/") for value in values) + " |"


def _code_list(values: list[str]) -> str:
    if not values:
        return "`none`"
    return ", ".join(f"`{value}`" for value in values)


def _value(value: object) -> str:
    if isinstance(value, bool | int | float) or value is None:
        return json.dumps(value)
    if isinstance(value, list | dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _node_id(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z_]", "_", value)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        return "node"
    if cleaned[0].isdigit():
        return f"n_{cleaned}"
    return cleaned


def _label(value: str) -> str:
    return value.replace('"', "'")


def _relation(value: str) -> str:
    return value.replace("_", " ")


def _label_map(graph: SystemReviewGraph) -> dict[str, str]:
    labels: dict[str, str] = {}
    labels.update({system.system_id: system.name for system in graph.systems})
    labels.update({artifact.artifact_id: artifact.name for artifact in graph.artifacts})
    labels.update({gate.gate_id: gate.name for gate in graph.gates})
    labels.update({step.step_id: step.name for step in graph.workflows})
    labels.update({schema.name: schema.name for schema in graph.schemas})
    return labels


def render_lifecycle_mermaid(graph: SystemReviewGraph) -> str:
    """Render the workflow lifecycle as a compact left-to-right map."""

    labels = _label_map(graph)
    lines = ["flowchart LR"]
    for step in graph.workflows:
        lines.append(f'  {_node_id(step.step_id)}["{_label(labels.get(step.step_id, step.name))}"]')
    for step in graph.workflows:
        for next_step in step.next_steps:
            next_label = labels.get(next_step, next_step)
            lines.append(
                f'  {_node_id(step.step_id)} --> {_node_id(next_step)}["{_label(next_label)}"]'
            )
    if len(lines) == 1:
        lines.append('  empty["No workflow steps declared"]')
    return "\n".join(lines)


def render_mermaid(graph: SystemReviewGraph) -> str:
    """Render a compact Mermaid flowchart."""

    labels = _label_map(graph)
    lines = ["flowchart TD"]
    for edge in graph.edges[:80]:
        source = _node_id(edge.source)
        target = _node_id(edge.target)
        label = _label(_relation(edge.relation))
        source_label = _label(labels.get(edge.source, edge.source))
        target_label = _label(labels.get(edge.target, edge.target))
        lines.append(
            f'  {source}["{source_label}"] -- "{label}" --> {target}["{target_label}"]'
        )
    return "\n".join(lines)


def render_markdown(graph: SystemReviewGraph) -> str:
    """Render a full system review report."""

    lines = [
        f"# {graph.title}",
        "",
        f"Generated: `{graph.generated_at}`",
        f"Scope: {graph.scope}",
        f"One line: {graph.one_line}",
        "",
        "## Bigger Picture",
        "",
        graph.bigger_picture or "No bigger-picture narrative was provided.",
        "",
        "## Current Truth",
        "",
    ]
    if graph.current_truth:
        lines.extend(f"- `{key}`: `{_value(value)}`" for key, value in graph.current_truth.items())
    else:
        lines.append("- No current-truth fields were provided.")
    if graph.source_links:
        lines.extend(["", "## Source Links", "", "| Source | Notes |", "|---|---|"])
        for source in graph.source_links:
            label = source.get("label", "")
            url = source.get("url", "")
            notes = source.get("notes", "")
            link = f"[{label}]({url})" if label and url else url
            lines.append(_row([link, notes]))
    lines.extend(
        [
            "",
            "## Lifecycle Map",
            "",
            "```mermaid",
            render_lifecycle_mermaid(graph),
            "```",
        ]
    )
    lines.extend(
        [
            "",
            "## Relationship Graph",
            "",
            "```mermaid",
            render_mermaid(graph),
            "```",
            "",
            "## Systems",
            "",
            "| System | Owner | Stack | Architecture | Lifecycle | Boundary | Ideal Target |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for system in graph.systems:
        lines.append(
            _row(
                [
                    system.name,
                    system.owner,
                    ", ".join(system.language_stack),
                    system.architecture_style,
                    system.lifecycle,
                    system.truth_boundary,
                    system.ideal_target,
                ]
            )
        )
    lines.extend(
        [
            "",
            "## System Details",
            "",
        ]
    )
    for system in graph.systems:
        lines.extend(
            [
                f"### {system.name}",
                "",
                f"- Purpose: {system.purpose}",
                f"- Code surfaces: {_code_list(system.code_surfaces)}",
                f"- Artifacts: {_code_list(system.artifacts)}",
                f"- Decision gates: {_code_list(system.decision_gates)}",
                f"- Boundary: {system.truth_boundary or 'Not declared.'}",
                f"- Ideal target: {system.ideal_target or 'Not declared.'}",
                "",
            ]
        )
    lines.extend(
        [
            "## Artifacts",
            "",
            "| Artifact | Kind | Schema | Owner | Path | Redaction | Purpose |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for artifact in graph.artifacts:
        lines.append(
            _row(
                [
                    artifact.name,
                    artifact.kind,
                    artifact.schema,
                    artifact.owner,
                    artifact.path,
                    artifact.redaction,
                    artifact.purpose,
                ]
            )
        )
    lines.extend(
        [
            "",
            "## Schemas And Contracts",
            "",
            "| Name | Kind | Required Fields | Privacy Notes | Purpose |",
            "|---|---|---|---|---|",
        ]
    )
    for schema in graph.schemas:
        lines.append(
            _row(
                [
                    schema.name,
                    schema.kind,
                    ", ".join(schema.required_fields),
                    schema.privacy_notes,
                    schema.purpose,
                ]
            )
        )
    lines.extend(["", "## Decision Gates", ""])
    for gate in graph.gates:
        lines.extend(
            [
                f"### {gate.name}",
                "",
                f"- Inputs: `{', '.join(gate.inputs)}`",
                f"- Outputs: `{', '.join(gate.outputs)}`",
                f"- Human gate: `{_value(gate.human_gate)}`",
                f"- Risk boundary: {gate.risk_boundary}",
                "",
                "| If | Then |",
                "|---|---|",
            ]
        )
        for rule in gate.rules:
            lines.append(_row([rule.get("if", ""), rule.get("then", "")]))
        lines.append("")
    lines.extend(
        [
            "## Workflows",
            "",
            "| Step | Actor | Consumes | Gates | Produces | Next | Purpose |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for step in graph.workflows:
        lines.append(
            _row(
                [
                    step.name,
                    step.actor,
                    ", ".join(step.consumes),
                    ", ".join(step.gates),
                    ", ".join(step.produces),
                    ", ".join(step.next_steps),
                    step.purpose,
                ]
            )
        )
    lines.extend(["", "## Architecture Patterns", ""])
    for pattern in graph.architecture_patterns:
        lines.extend(
            [
                f"### {pattern.get('name', 'Unnamed pattern')}",
                "",
                f"- Works for: {pattern.get('works_for', '')}",
                f"- How to map it: {pattern.get('mapping', '')}",
                f"- What to redact: {pattern.get('redaction', '')}",
                "",
            ]
        )
    lines.extend(["## Walkthroughs", ""])
    for walkthrough in graph.walkthroughs:
        lines.extend(
            [
                f"### {walkthrough.get('name', 'Unnamed walkthrough')}",
                "",
                walkthrough.get("story", ""),
                "",
                "```json",
                json.dumps(walkthrough.get("example", {}), indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    if graph.review_questions:
        lines.extend(["## Review Questions", ""])
        lines.extend(f"- {item}" for item in graph.review_questions)
        lines.append("")
    lines.extend(["## Rebuild Recipe", ""])
    for phase in graph.rebuild_recipe:
        commands = phase.get("commands") if isinstance(phase.get("commands"), list) else []
        lines.extend(
            [
                f"### {phase.get('phase', 'phase')}",
                "",
                f"- Goal: {phase.get('goal', '')}",
                "",
                "```bash",
                "\n".join(str(command) for command in commands),
                "```",
                "",
            ]
        )
    lines.extend(["## Known Boundaries", ""])
    lines.extend(f"- {item}" for item in graph.known_boundaries)
    lines.append("")
    return "\n".join(lines)
