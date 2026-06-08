"""Markdown and Mermaid rendering."""

from __future__ import annotations

import json
import re

from system_review_graph.models import SystemReviewGraph

REPORT_DEPTHS = {"overview", "standard", "deep"}


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


def _as_set(values: list[str]) -> set[str]:
    return {value for value in values if value}


def _label_map(graph: SystemReviewGraph) -> dict[str, str]:
    labels: dict[str, str] = {}
    labels.update({system.system_id: system.name for system in graph.systems})
    labels.update({artifact.artifact_id: artifact.name for artifact in graph.artifacts})
    labels.update({gate.gate_id: gate.name for gate in graph.gates})
    labels.update({step.step_id: step.name for step in graph.workflows})
    labels.update({schema.name: schema.name for schema in graph.schemas})
    return labels


def _artifact_map(graph: SystemReviewGraph):
    return {artifact.artifact_id: artifact for artifact in graph.artifacts}


def _gate_map(graph: SystemReviewGraph):
    return {gate.gate_id: gate for gate in graph.gates}


def _schema_map(graph: SystemReviewGraph):
    return {schema.name: schema for schema in graph.schemas}


def _touches_system(step, system) -> bool:
    system_refs = _as_set(system.artifacts + system.decision_gates + system.code_surfaces)
    system_refs.update({system.system_id, system.name})
    step_refs = _as_set(step.consumes + step.produces + step.gates + step.next_steps)
    step_refs.update({step.actor})
    return bool(system_refs & step_refs) or step.actor == system.name


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


def render_artifact_mermaid(graph: SystemReviewGraph) -> str:
    """Render system -> artifact -> schema relationships."""

    labels = _label_map(graph)
    lines = ["flowchart LR"]
    for system in graph.systems:
        system_id = _node_id(f"system_{system.system_id}")
        lines.append(f'  {system_id}["{_label(system.name)}"]')
        for artifact_id in system.artifacts:
            artifact_label = labels.get(artifact_id, artifact_id)
            artifact_node = _node_id(f"artifact_{artifact_id}")
            lines.append(f'  {system_id} --> {artifact_node}["{_label(artifact_label)}"]')
            artifact = _artifact_map(graph).get(artifact_id)
            if artifact and artifact.schema:
                schema_node = _node_id(f"schema_{artifact.schema}")
                lines.append(
                    f'  {artifact_node} --> {schema_node}["{_label(artifact.schema)}"]'
                )
    if len(lines) == 1:
        lines.append('  empty["No artifacts declared"]')
    return "\n".join(lines)


def render_gate_mermaid(graph: SystemReviewGraph) -> str:
    """Render gates around workflow steps."""

    labels = _label_map(graph)
    lines = ["flowchart LR"]
    for gate in graph.gates:
        gate_node = _node_id(f"gate_{gate.gate_id}")
        lines.append(f'  {gate_node}{{"{_label(gate.name)}"}}')
        for output in gate.outputs:
            output_node = _node_id(f"out_{gate.gate_id}_{output}")
            lines.append(f'  {gate_node} --> {output_node}["{_label(output)}"]')
    for step in graph.workflows:
        step_node = _node_id(f"step_{step.step_id}")
        for gate_id in step.gates:
            gate_label = labels.get(gate_id, gate_id)
            gate_node = _node_id(f"gate_{gate_id}")
            lines.append(
                f'  {gate_node}{{"{_label(gate_label)}"}} '
                f'--> {step_node}["{_label(step.name)}"]'
            )
    if len(lines) == 1:
        lines.append('  empty["No decision gates declared"]')
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


def _add_visuals(lines: list[str], graph: SystemReviewGraph, depth: str) -> None:
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
    if depth in {"standard", "deep"}:
        lines.extend(
            [
                "",
                "## Artifact And Schema Map",
                "",
                "```mermaid",
                render_artifact_mermaid(graph),
                "```",
                "",
                "## Gate Map",
                "",
                "```mermaid",
                render_gate_mermaid(graph),
                "```",
            ]
        )
    if depth == "deep":
        lines.extend(
            [
                "",
                "## Relationship Graph",
                "",
                "```mermaid",
                render_mermaid(graph),
                "```",
            ]
        )


def _add_expansion_index(lines: list[str], graph: SystemReviewGraph, depth: str) -> None:
    lines.extend(
        [
            "",
            "## Expansion Index",
            "",
            "| Level | Use It To Answer | Report Section |",
            "|---|---|---|",
            _row(["0. Situation", "What is true now?", "Current Truth"]),
            _row(["1. Flow", "How does the system move end to end?", "Lifecycle Map"]),
            _row(
                [
                    "2. Ownership",
                    "Which subsystem owns which artifact?",
                    "Artifact And Schema Map",
                ]
            ),
            _row(["3. Control", "Which rules advance, wait, or block?", "Gate Map"]),
            _row(
                [
                    "4. Implementation",
                    "Which files, APIs, docs, or outputs should I inspect?",
                    "System Details",
                ]
            ),
            _row(["5. Audit", "What should an external reviewer ask next?", "Review Questions"]),
        ]
    )
    if depth == "overview":
        lines.extend(
            [
                "",
                "This is an overview report. Rebuild with `--depth standard` or `--depth deep` "
                "to expand artifacts, gates, schemas, workflows, and per-system drill-downs.",
            ]
        )


def _add_system_details(lines: list[str], graph: SystemReviewGraph, depth: str) -> None:
    artifacts = _artifact_map(graph)
    gates = _gate_map(graph)
    lines.extend(["", "## System Details", ""])
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
        if depth != "deep":
            continue
        if system.artifacts:
            lines.extend(
                [
                    "Artifact expansion:",
                    "",
                    "| Artifact | Kind | Schema | Path | Why It Matters |",
                    "|---|---|---|---|---|",
                ]
            )
            for artifact_id in system.artifacts:
                artifact = artifacts.get(artifact_id)
                if not artifact:
                    lines.append(
                        _row(
                            [
                                artifact_id,
                                "missing",
                                "",
                                "",
                                "Manifest reference not found.",
                            ]
                        )
                    )
                    continue
                lines.append(
                    _row(
                        [
                            artifact.name,
                            artifact.kind,
                            artifact.schema,
                            artifact.path,
                            artifact.purpose,
                        ]
                    )
                )
            lines.append("")
        if system.decision_gates:
            lines.extend(
                [
                    "Gate expansion:",
                    "",
                    "| Gate | Inputs | Outputs | Risk Boundary |",
                    "|---|---|---|---|",
                ]
            )
            for gate_id in system.decision_gates:
                gate = gates.get(gate_id)
                if not gate:
                    lines.append(_row([gate_id, "missing", "", "Manifest reference not found."]))
                    continue
                lines.append(
                    _row(
                        [
                            gate.name,
                            ", ".join(gate.inputs),
                            ", ".join(gate.outputs),
                            gate.risk_boundary,
                        ]
                    )
                )
            lines.append("")
        touchpoints = [step for step in graph.workflows if _touches_system(step, system)]
        if touchpoints:
            lines.extend(
                [
                    "Workflow touchpoints:",
                    "",
                    "| Step | Actor | Consumes | Produces | Gates |",
                    "|---|---|---|---|---|",
                ]
            )
            for step in touchpoints:
                lines.append(
                    _row(
                        [
                            step.name,
                            step.actor,
                            ", ".join(step.consumes),
                            ", ".join(step.produces),
                            ", ".join(step.gates),
                        ]
                    )
                )
            lines.append("")


def _add_artifacts(lines: list[str], graph: SystemReviewGraph) -> None:
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


def _add_schemas(lines: list[str], graph: SystemReviewGraph, depth: str) -> None:
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
        if depth == "deep" and schema.example:
            lines.extend(["", f"Example `{schema.name}`:", "", "```json"])
            lines.append(json.dumps(schema.example, indent=2, sort_keys=True))
            lines.extend(["```", ""])


def _add_gates(lines: list[str], graph: SystemReviewGraph) -> None:
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


def _add_workflows(lines: list[str], graph: SystemReviewGraph) -> None:
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


def render_markdown(graph: SystemReviewGraph, depth: str = "deep") -> str:
    """Render a full system review report."""

    if depth not in REPORT_DEPTHS:
        raise ValueError(f"depth must be one of: {', '.join(sorted(REPORT_DEPTHS))}")
    lines = [
        f"# {graph.title}",
        "",
        f"Generated: `{graph.generated_at}`",
        f"Scope: {graph.scope}",
        f"One line: {graph.one_line}",
        f"Depth: `{depth}`",
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
    _add_visuals(lines, graph, depth)
    _add_expansion_index(lines, graph, depth)
    lines.extend(
        [
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
    if depth in {"standard", "deep"}:
        _add_system_details(lines, graph, depth)
        _add_artifacts(lines, graph)
        _add_schemas(lines, graph, depth)
        _add_gates(lines, graph)
        _add_workflows(lines, graph)
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
