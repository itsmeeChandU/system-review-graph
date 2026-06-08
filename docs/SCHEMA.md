# Manifest Schema

System Review Graph uses a JSON manifest. The manifest is deliberately simple so teams can generate it from any language or architecture.

## Top-Level Fields

| Field | Type | Purpose |
|---|---|---|
| `title` | string | Report title. |
| `one_line` | string | One-sentence distinction or summary. |
| `scope` | string | What the report covers. |
| `current_truth` | object | Honest status snapshot. |
| `bigger_picture` | string | Narrative context. |
| `systems` | array | Major subsystems, services, lanes, bounded contexts, or product surfaces. |
| `artifacts` | array | Reports, APIs, tables, files, UI pages, queues, or generated outputs. |
| `schemas` | array | Public, internal, or sanitized contracts. |
| `decision_gates` | array | Rules that advance, block, route, or require review. |
| `workflows` | array | Lifecycle steps. |
| `edges` | array | Optional explicit graph edges. |
| `source_links` | array | Public links used for a public-safe report. |
| `architecture_patterns` | array | How different project styles map into this model. |
| `walkthroughs` | array | Human-readable examples. |
| `review_questions` | array | Questions a maintainer, auditor, reviewer, or AI agent should ask. |
| `rebuild_recipe` | array | Commands or steps to reproduce the report. |
| `known_boundaries` | array | What this report does not prove. |

## Systems

Systems can be services, apps, libraries, lanes, workflows, agent roles, data layers, or control surfaces.

Required:

- `system_id`
- `name`
- `purpose`

Useful optional fields:

- `owner`
- `language_stack`
- `architecture_style`
- `lifecycle`
- `code_surfaces`
- `artifacts`
- `decision_gates`
- `truth_boundary`
- `ideal_target`
- `example`

## Artifacts

Artifacts are inspectable things.

Examples:

- API response,
- Markdown report,
- JSONL ledger,
- database table,
- event stream,
- UI page,
- CI job,
- model card,
- deployment manifest.

Fields:

- `artifact_id`
- `name`
- `kind`
- `path`
- `owner`
- `schema`
- `purpose`
- `redaction`

## Schemas

Schemas do not have to expose production data. A private company can publish a safe contract like:

```json
{
  "name": "CustomerTicketContract",
  "kind": "sanitized_event",
  "required_fields": ["ticket_id", "created_at", "status", "priority", "redacted_subject"],
  "privacy_notes": "No customer names, emails, body text, or account ids are included."
}
```

## Decision Gates

Decision gates explain system behavior.

Example:

```json
{
  "gate_id": "human_approval_gate",
  "name": "Human Approval Gate",
  "inputs": ["action_intent", "risk_level"],
  "outputs": ["approved", "blocked", "needs_review"],
  "human_gate": true,
  "rules": [
    { "if": "risk_level == high", "then": "needs_review" },
    { "if": "missing evidence", "then": "blocked" }
  ],
  "risk_boundary": "No external send occurs without approval."
}
```

## Workflow Steps

Workflow steps show movement.

```json
{
  "step_id": "capture_outcome",
  "name": "Capture Outcome",
  "actor": "Outcome Worker",
  "consumes": ["action_intent"],
  "gates": ["human_approval_gate"],
  "produces": ["outcome_ledger"],
  "next_steps": ["learn_from_outcome"],
  "purpose": "Turn action into reality feedback."
}
```

## Source Links

Use `source_links` when a report maps public repos, papers, standards, docs, or
sanitized internal references.

```json
{
  "label": "GitHub repository",
  "url": "https://github.com/example/project",
  "notes": "Primary public source used for paths and architecture surfaces."
}
```

## Review Questions

Use `review_questions` to turn the report into an audit checklist:

```json
[
  "Which gate blocks unsafe downstream action?",
  "Which artifact proves the action outcome?",
  "What can be reviewed if the database is private?"
]
```

## Privacy Levels

Use `redaction` on artifacts:

- `safe_to_share`
- `public_summary_only`
- `schema_only`
- `counts_only`
- `private_do_not_publish`

## Design Principle

If the database is private, describe the contract and boundary. A reviewer should still understand what the system does.

## Report Depth

The manifest does not need to change when you want more or less detail. Choose
depth at render time:

```bash
system-review-graph build --manifest system_review_manifest.json --out-dir reports --depth overview
system-review-graph build --manifest system_review_manifest.json --out-dir reports --depth standard
system-review-graph build --manifest system_review_manifest.json --out-dir reports --depth deep
```

`deep` reports add relationship graphs, schema examples, and per-system
artifact/gate/workflow expansion.

## JSON Schema

A machine-readable JSON Schema is available at:

```text
docs/schema/system_review_manifest.schema.json
```

Use it in editors, CI checks, or external tooling.
