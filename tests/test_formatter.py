import json

import pytest
from rich.console import Console

from syshealth.collector import (
    CPUData,
    DiskData,
    MemoryData,
    NetworkData,
    ProcessInfo,
    SwapData,
    SystemSnapshot,
)
from syshealth.formatter import (
    build_cores_panel,
    build_header,
    build_metrics_panel,
    build_network_panel,
    build_process_table,
    render_dashboard,
    snapshot_to_json,
    snapshot_to_markdown,
)


@pytest.fixture
def snapshot() -> SystemSnapshot:
    return SystemSnapshot(
        timestamp="2026-09-28T10:00:00",
        hostname="test-host",
        os_name="TestOS 1.0",
        uptime_seconds=90061,
        cpu=CPUData(total_percent=50.0, per_core_percent=[40.0, 60.0], core_count=2),
        memory=MemoryData(
            total=16 * 1024**3,
            used=8 * 1024**3,
            free=4 * 1024**3,
            available=6 * 1024**3,
            percent=50.0,
        ),
        swap=SwapData(total=0, used=0, free=0, percent=0.0),
        disk=DiskData(
            path="/",
            total=100 * 1024**3,
            used=90 * 1024**3,
            free=10 * 1024**3,
            percent=90.0,
        ),
        network=NetworkData(
            bytes_sent=1024, bytes_recv=2048, upload_speed=512.0, download_speed=1024.0
        ),
        processes=[
            ProcessInfo(pid=1, name="init", cpu_percent=1.5, memory_percent=0.5),
            ProcessInfo(pid=2, name="we|rd[name]", cpu_percent=0.5, memory_percent=0.2),
        ],
        process_sort="cpu",
    )


def _render_text(renderable, width: int = 140, height: int = 45) -> str:
    console = Console(record=True, width=width, height=height, force_terminal=False)
    console.print(renderable)
    return console.export_text()


def test_render_dashboard_contains_all_sections(snapshot):
    text = _render_text(render_dashboard(snapshot, interval=2))
    assert "SysHealth CLI" in text
    assert "test-host" in text
    assert "Metrik Utama" in text
    assert "Network I/O" in text
    assert "CPU per Core" in text
    assert "Top 2 Proses" in text
    assert "Ctrl+C" in text


@pytest.mark.parametrize(
    "builder",
    [
        build_header,
        build_metrics_panel,
        build_cores_panel,
        build_network_panel,
        build_process_table,
    ],
)
def test_each_panel_renders_without_error(builder, snapshot):
    assert _render_text(builder(snapshot)).strip()


def test_process_name_with_brackets_is_not_treated_as_markup(snapshot):
    text = _render_text(build_process_table(snapshot))
    assert "we|rd[name]" in text


def test_swap_inactive_label(snapshot):
    assert "tidak aktif" in _render_text(build_metrics_panel(snapshot))


def test_snapshot_to_json_roundtrip(snapshot):
    data = json.loads(snapshot_to_json(snapshot))
    assert data["hostname"] == "test-host"
    assert data["cpu"]["core_count"] == 2
    assert len(data["processes"]) == 2


def test_snapshot_to_markdown(snapshot):
    md = snapshot_to_markdown(snapshot)
    assert md.startswith("# SysHealth Snapshot")
    assert "## Ringkasan Metrik" in md
    assert "## Network I/O" in md
    assert "| Disk (/) | 90.0% |" in md
    assert "Critical" in md                # disk 90% -> Critical
    assert "we\\|rd[name]" in md           # karakter '|' harus di-escape
    assert md.endswith("\n")
