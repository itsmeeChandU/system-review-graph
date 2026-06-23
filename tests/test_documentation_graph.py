import json
from pathlib import Path

from system_review_graph.builder import build_system_review
from system_review_graph.cli import main
from system_review_graph.documentation_graph import load_documentation_graph_context
from system_review_graph.mcp_server import handle_message
from system_review_graph.render import render_markdown
from system_review_graph.validate import validate_manifest


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_manifest_documentation_graph_renders_and_validates():
    manifest = {
        "title": "Documentation graph",
        "systems": [],
        "artifacts": [],
        "schemas": [],
        "decision_gates": [],
        "workflows": [],
        "documentation_sources": [
            {
                "artifact": "data/intelligence/global_repository_documentation_rows.jsonl",
                "role": "complete row-per-file documentation catalog",
                "incorporated_information": ["path", "owner", "purpose"],
            }
        ],
        "knowledge_nodes": [
            {"node_id": "concept:stock_selection", "type": "concept", "label": "Stock selection"},
            {
                "node_id": "file:graph/trading_command_board.py",
                "type": "file",
                "label": "graph/trading_command_board.py",
                "attributes": {"flow_stage": "lane_engines", "cleanup_action": "KEEP"},
            },
        ],
        "knowledge_edges": [
            {
                "source": "concept:stock_selection",
                "relation": "HAS_FILE",
                "target": "file:graph/trading_command_board.py",
            }
        ],
    }

    errors = validate_manifest(manifest)
    graph = build_system_review(manifest)
    markdown = render_markdown(graph, depth="deep")

    assert errors == []
    assert graph.documentation_sources[0].artifact.endswith(
        "global_repository_documentation_rows.jsonl"
    )
    assert graph.knowledge_nodes[0].node_id == "concept:stock_selection"
    assert "## Documentation Knowledge Graph" in markdown
    assert "Stock selection" in markdown


def test_manifest_validation_catches_unknown_knowledge_edge():
    manifest = {
        "title": "Broken documentation graph",
        "systems": [],
        "artifacts": [],
        "schemas": [],
        "decision_gates": [],
        "workflows": [],
        "knowledge_nodes": [{"node_id": "concept:known", "type": "concept", "label": "Known"}],
        "knowledge_edges": [
            {"source": "concept:known", "relation": "POINTS_TO", "target": "concept:missing"}
        ],
    }

    errors = validate_manifest(manifest)

    assert "knowledge_edges[0] references unknown target node concept:missing" in errors


def test_documentation_graph_context_loader_filters_from_start_node(tmp_path):
    nodes = tmp_path / "nodes.jsonl"
    edges = tmp_path / "edges.jsonl"
    _write_jsonl(
        nodes,
        [
            {"id": "concept:stock_selection", "type": "concept", "label": "Stock selection"},
            {"id": "owner:stock_market_system", "type": "owner_module", "label": "stock"},
            {"id": "file:graph/trading_command_board.py", "type": "file", "label": "board"},
        ],
    )
    _write_jsonl(
        edges,
        [
            {
                "src": "concept:stock_selection",
                "type": "USES_OWNER",
                "dst": "owner:stock_market_system",
            },
            {
                "src": "owner:stock_market_system",
                "type": "OWNS_FILE",
                "dst": "file:graph/trading_command_board.py",
            },
        ],
    )

    context = load_documentation_graph_context(
        nodes_path=nodes,
        edges_path=edges,
        start_node="concept:stock_selection",
    )

    assert context["summary"]["total_nodes"] == 3
    assert context["summary"]["selected_edges"] == 1
    assert "LLMs" in context["agent_context_contract"]["primary_users"]
    assert any(node["id"] == "concept:stock_selection" for node in context["nodes"])


def test_cli_load_documentation_graph_context(tmp_path, capsys):
    nodes = tmp_path / "nodes.jsonl"
    edges = tmp_path / "edges.jsonl"
    _write_jsonl(
        nodes,
        [{"id": "concept:algorithm_usage", "type": "concept", "label": "Algorithms"}],
    )
    _write_jsonl(edges, [])

    exit_code = main(
        [
            "load-documentation-graph-context",
            "--nodes",
            str(nodes),
            "--edges",
            str(edges),
            "--node-type",
            "concept",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "concept:algorithm_usage" in captured.out


def test_mcp_load_documentation_graph_context_tool(tmp_path):
    nodes = tmp_path / "nodes.jsonl"
    edges = tmp_path / "edges.jsonl"
    _write_jsonl(nodes, [{"id": "concept:source_data", "type": "concept", "label": "Source data"}])
    _write_jsonl(edges, [])

    tools = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert tools is not None
    names = [tool["name"] for tool in tools["result"]["tools"]]
    assert "srg_load_documentation_graph_context" in names

    response = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "srg_load_documentation_graph_context",
                "arguments": {
                    "nodes_path": str(nodes),
                    "edges_path": str(edges),
                    "node_type": "concept",
                },
            },
        }
    )

    assert response is not None
    text = response["result"]["content"][0]["text"]
    assert "concept:source_data" in text
