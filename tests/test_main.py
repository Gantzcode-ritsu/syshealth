"""Test end-to-end untuk CLI (syshealth.main) memakai CliRunner Typer."""

import json

from typer.testing import CliRunner

from syshealth import __version__
from syshealth.main import app

runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_export_json(tmp_path):
    out = tmp_path / "snap.json"
    result = runner.invoke(app, ["--export", "json", "-o", str(out), "-t", "3"])
    assert result.exit_code == 0, result.output
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["memory"]["total"] > 0
    assert 1 <= len(data["processes"]) <= 3


def test_export_markdown(tmp_path):
    out = tmp_path / "nested" / "snap.md"
    result = runner.invoke(app, ["--export", "md", "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.read_text(encoding="utf-8").startswith("# SysHealth Snapshot")


def test_export_with_sort_memory(tmp_path):
    out = tmp_path / "snap_mem.json"
    result = runner.invoke(
        app, ["--export", "json", "-o", str(out), "-s", "memory", "-t", "5"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["process_sort"] == "memory"


def test_export_default_output_path(tmp_path, monkeypatch):
    # Pastikan default filename otomatis dibuat saat -o tidak diberikan.
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["--export", "json"])
    assert result.exit_code == 0, result.output
    generated = list(tmp_path.glob("syshealth_snapshot_*.json"))
    assert len(generated) == 1
    data = json.loads(generated[0].read_text(encoding="utf-8"))
    assert "hostname" in data


def test_live_mode_requires_tty():
    # CliRunner tidak menyediakan TTY, jadi mode live harus menolak dengan jelas.
    result = runner.invoke(app, [])
    assert result.exit_code == 1
    assert "terminal interaktif" in result.output


def test_interval_below_minimum_is_rejected():
    result = runner.invoke(app, ["-i", "0.1"])
    assert result.exit_code == 2


def test_top_out_of_range_is_rejected():
    result_zero = runner.invoke(app, ["-t", "0"])
    assert result_zero.exit_code == 2

    result_too_big = runner.invoke(app, ["-t", "51"])
    assert result_too_big.exit_code == 2


def test_invalid_export_format_is_rejected():
    result = runner.invoke(app, ["--export", "xml"])
    assert result.exit_code == 2


def test_invalid_sort_value_is_rejected():
    result = runner.invoke(app, ["--export", "json", "-s", "disk"])
    assert result.exit_code == 2


def test_help_flag_shows_usage():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--interval" in result.output
    assert "--export" in result.output
    assert "--top" in result.output