import json
from types import SimpleNamespace

import psutil
import pytest

from syshealth.collector import (
    CPUData,
    DiskData,
    MemoryData,
    NetworkData,
    ProcessInfo,
    SwapData,
    SystemCollector,
    SystemSnapshot,
)
from syshealth.utils import (
    format_bytes,
    format_speed,
    format_uptime,
    get_status_color,
    get_status_label,
)


def _is_percent(value: float) -> bool:
    return 0.0 <= value <= 100.0


@pytest.fixture
def collector() -> SystemCollector:
    return SystemCollector(top_n=5)

@pytest.mark.parametrize(
    "size, expected",
    [
        (0, "0 B"),
        (1, "1 B"),
        (1023, "1023 B"),
        (1024, "1.00 KB"),
        (1536, "1.50 KB"),
        (1024**2, "1.00 MB"),
        (1024**3, "1.00 GB"),
        (1024**4, "1.00 TB"),
        (5 * 1024**5, "5120.00 TB"),
    ],
)
def test_format_bytes(size, expected):
    assert format_bytes(size) == expected


def test_format_bytes_custom_precision():
    assert format_bytes(1536, precision=1) == "1.5 KB"
    assert format_bytes(1536, precision=0) == "2 KB"


def test_format_bytes_negative_raises():
    with pytest.raises(ValueError):
        format_bytes(-1)


def test_format_speed():
    assert format_speed(2048) == "2.00 KB/s"
    assert format_speed(0) == "0 B/s"


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, "00:00:00"),
        (3661, "01:01:01"),
        (90061, "1d 01:01:01"),
        (-10, "00:00:00"),
    ],
)
def test_format_uptime(seconds, expected):
    assert format_uptime(seconds) == expected


@pytest.mark.parametrize(
    "percent, color, label",
    [
        (0, "green", "Normal"),
        (69.9, "green", "Normal"),
        (70, "yellow", "Warning"),
        (77.5, "yellow", "Warning"),
        (85, "yellow", "Warning"),
        (85.1, "red", "Critical"),
        (100, "red", "Critical"),
    ],
)
def test_status_color_and_label(percent, color, label):
    assert get_status_color(percent) == color
    assert get_status_label(percent) == label


def test_collect_cpu(collector):
    cpu = collector.collect_cpu()
    assert isinstance(cpu, CPUData)
    assert _is_percent(cpu.total_percent)
    assert cpu.core_count >= 1
    assert len(cpu.per_core_percent) == cpu.core_count
    assert all(_is_percent(v) for v in cpu.per_core_percent)


def test_collect_memory(collector):
    mem = collector.collect_memory()
    assert isinstance(mem, MemoryData)
    assert mem.total > 0
    assert 0 <= mem.used <= mem.total
    assert 0 <= mem.free <= mem.total
    assert 0 <= mem.available <= mem.total
    assert _is_percent(mem.percent)


def test_collect_swap(collector):
    swap = collector.collect_swap()
    assert isinstance(swap, SwapData)
    assert swap.total >= 0
    assert swap.used >= 0
    assert swap.free >= 0
    assert _is_percent(swap.percent)


def test_collect_disk(collector):
    disk = collector.collect_disk()
    assert isinstance(disk, DiskData)
    assert isinstance(disk.path, str) and disk.path
    assert disk.total > 0
    assert 0 <= disk.used <= disk.total
    assert 0 <= disk.free <= disk.total
    assert _is_percent(disk.percent)


def test_collect_network_structure(collector):
    net = collector.collect_network()
    assert isinstance(net, NetworkData)
    assert net.bytes_sent >= 0
    assert net.bytes_recv >= 0
    assert net.upload_speed == 0.0 
    assert net.download_speed == 0.0

    second = collector.collect_network()
    assert second.upload_speed >= 0.0
    assert second.download_speed >= 0.0


def test_network_speed_calculation(monkeypatch):
    readings = iter(
        [
            SimpleNamespace(bytes_sent=1000, bytes_recv=2000),
            SimpleNamespace(bytes_sent=3000, bytes_recv=8000),
        ]
    )
    times = iter([10.0, 12.0])
    monkeypatch.setattr(psutil, "net_io_counters", lambda: next(readings))
    collector = SystemCollector(clock=lambda: next(times))

    first = collector.collect_network()
    assert first.upload_speed == 0.0

    second = collector.collect_network()
    assert second.bytes_sent == 3000
    assert second.bytes_recv == 8000
    assert second.upload_speed == pytest.approx(1000.0)
    assert second.download_speed == pytest.approx(3000.0)


def test_network_counter_reset_gives_zero_speed(monkeypatch):
    readings = iter(
        [
            SimpleNamespace(bytes_sent=5000, bytes_recv=5000),
            SimpleNamespace(bytes_sent=100, bytes_recv=100),
        ]
    )
    times = iter([0.0, 1.0])
    monkeypatch.setattr(psutil, "net_io_counters", lambda: next(readings))
    collector = SystemCollector(clock=lambda: next(times))

    collector.collect_network()
    after_reset = collector.collect_network()
    assert after_reset.upload_speed == 0.0
    assert after_reset.download_speed == 0.0


@pytest.mark.parametrize("sort_by", ["cpu", "memory"])
def test_collect_processes(sort_by):
    collector = SystemCollector(top_n=5, sort_by=sort_by)
    processes = collector.collect_processes()

    assert 1 <= len(processes) <= 5
    for proc in processes:
        assert isinstance(proc, ProcessInfo)
        assert isinstance(proc.pid, int) and proc.pid > 0
        assert isinstance(proc.name, str) and proc.name
        assert _is_percent(proc.cpu_percent)
        assert _is_percent(proc.memory_percent)

    key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
    values = [getattr(p, key) for p in processes]
    assert values == sorted(values, reverse=True)


def test_top_n_is_respected():
    assert len(SystemCollector(top_n=1).collect_processes()) == 1


def test_invalid_arguments():
    with pytest.raises(ValueError):
        SystemCollector(top_n=0)
    with pytest.raises(ValueError):
        SystemCollector(sort_by="network")


def test_collect_snapshot_structure_and_json(collector):
    snapshot = collector.collect()
    assert isinstance(snapshot, SystemSnapshot)
    assert snapshot.hostname
    assert snapshot.os_name
    assert snapshot.uptime_seconds >= 0
    assert snapshot.process_sort == "cpu"

    data = snapshot.to_dict()
    for key in (
        "timestamp",
        "hostname",
        "os_name",
        "uptime_seconds",
        "cpu",
        "memory",
        "swap",
        "disk",
        "network",
        "processes",
        "process_sort",
    ):
        assert key in data

    # Harus dapat diserialisasi ke JSON tanpa error.
    assert json.loads(json.dumps(data))["hostname"] == snapshot.hostname
