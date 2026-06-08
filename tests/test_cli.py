from pathlib import Path

from system_review_graph.cli import main


def test_cli_validate_example(capsys):
    exit_code = main(
        [
            "validate",
            "--manifest",
            "examples/fictional_ai_ops/system_review_manifest.json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "manifest valid" in captured.out


def test_cli_build_example(tmp_path):
    exit_code = main(
        [
            "build",
            "--manifest",
            "examples/actual_repos/duckdb/system_review_manifest.json",
            "--out-dir",
            str(tmp_path),
            "--depth",
            "overview",
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "system_review_graph.json").exists()
    assert (tmp_path / "system_review_graph.md").exists()
    assert "Depth: `overview`" in (tmp_path / "system_review_graph.md").read_text()


def test_cli_init_named_example(tmp_path):
    target = tmp_path / "copied"

    exit_code = main(
        [
            "init-example",
            "--example",
            "actual_repos/opentelemetry_collector",
            "--out-dir",
            str(target),
        ]
    )

    assert exit_code == 0
    assert Path(target / "system_review_manifest.json").exists()


def test_cli_list_examples(capsys):
    exit_code = main(["list-examples"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "fictional_ai_ops" in captured.out
    assert "actual_repos/duckdb" in captured.out
