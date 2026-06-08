# MCP Server

System Review Graph includes a lightweight stdio MCP server:

```bash
system-review-graph-mcp
```

It lets MCP-capable agents call SRG directly instead of shelling out manually.
The server uses newline-delimited JSON-RPC over stdin/stdout and exposes tools
for scanning, building, validating, doctoring, and loading atlas context.

## Client Config

Example MCP client configuration:

```json
{
  "mcpServers": {
    "system-review-graph": {
      "command": "system-review-graph-mcp"
    }
  }
}
```

For local development from a checkout:

```json
{
  "mcpServers": {
    "system-review-graph": {
      "command": "python",
      "args": ["-m", "system_review_graph.mcp_server"]
    }
  }
}
```

## Tools

| Tool | Purpose |
|---|---|
| `srg_validate_manifest` | Validate manifest structure and unresolved references. |
| `srg_doctor_manifest` | Report audit-readiness warnings and missing review surfaces. |
| `srg_build_report` | Build Markdown/JSON reports, with optional HTML and DOT. |
| `srg_scan_repository` | Generate a starter manifest or large-repo atlas from a local repo. |
| `srg_load_atlas_context` | Load a compact context bundle from a root atlas and optional child maps. |

## Why MCP Matters For Atlases

For a huge repository, the static report is useful for humans, but the MCP tool
surface is useful for agents:

```text
agent -> srg_load_atlas_context(root manifest)
      -> choose changed/risky child map
      -> load child context
      -> validate/doctor/build updated reports
```

That makes the atlas a live context object. A reviewer can attach one root map,
and an agent can discover the linked subsystem maps without reading the entire
repo at once.

## Example Tool Calls

Validate:

```json
{
  "name": "srg_validate_manifest",
  "arguments": {
    "manifest_path": "examples/fictional_ai_ops/system_review_manifest.json"
  }
}
```

Generate an atlas and reports:

```json
{
  "name": "srg_scan_repository",
  "arguments": {
    "repo_path": "/path/to/repo",
    "out": "reports/system-review-atlas",
    "atlas": true,
    "max_subsystems": 24,
    "build_reports": true,
    "depth": "overview"
  }
}
```

Load an atlas for an agent:

```json
{
  "name": "srg_load_atlas_context",
  "arguments": {
    "manifest_path": "reports/system-review-atlas/system_review_manifest.json",
    "include_children": true,
    "max_child_maps": 8
  }
}
```

## Boundaries

- The MCP server does not execute arbitrary shell commands.
- It reads and writes only the paths supplied by the MCP client.
- Atlas scans are source-surface maps, not proof of runtime behavior.
- Keep private data, secrets, and production records out of manifests.
