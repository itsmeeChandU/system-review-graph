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
            "--html",
            "--dot",
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "system_review_graph.json").exists()
    assert (tmp_path / "system_review_graph.md").exists()
    assert (tmp_path / "system_review_graph.html").exists()
    assert (tmp_path / "system_review_graph.dot").exists()
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


def test_cli_doctor(capsys):
    exit_code = main(
        [
            "doctor",
            "--manifest",
            "examples/fictional_ai_ops/system_review_manifest.json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "doctor" in captured.out


def test_cli_scan(tmp_path):
    manifest = tmp_path / "starter_manifest.json"

    exit_code = main(["scan", "--repo", ".", "--out", str(manifest)])

    assert exit_code == 0
    text = manifest.read_text()
    assert "Python Surface" in text
    assert "system_review_manifest.json" in text


def test_cli_scan_atlas(tmp_path):
    repo = tmp_path / "repo"
    (repo / "drivers").mkdir(parents=True)
    (repo / "net").mkdir()
    (repo / "fs").mkdir()
    (repo / "drivers" / "device.c").write_text("int driver(void) { return 0; }\n")
    (repo / "net" / "socket.c").write_text("int socket_layer(void) { return 0; }\n")
    (repo / "fs" / "file.c").write_text("int fs_layer(void) { return 0; }\n")
    out = tmp_path / "atlas"

    exit_code = main(
        [
            "scan",
            "--repo",
            str(repo),
            "--out",
            str(out),
            "--atlas",
            "--max-subsystems",
            "3",
            "--build-reports",
        ]
    )

    root_manifest = out / "system_review_manifest.json"
    root_report = out / "reports" / "system_review_graph.md"

    assert exit_code == 0
    assert root_manifest.exists()
    assert (out / "subsystems" / "drivers" / "system_review_manifest.json").exists()
    assert "child_maps" in root_manifest.read_text()
    assert "## Map Of Maps" in root_report.read_text()
