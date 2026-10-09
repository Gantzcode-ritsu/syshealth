from __future__ import annotations

import os
import platform
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable

import psutil

SORT_CHOICES = ("cpu", "memory")


@dataclass
class CPUData:
    total_percent: float
    per_core_percent: list[float]
    core_count: int


@dataclass
class MemoryData:
    total: int
    used: int
    free: int
    available: int
    percent: float


@dataclass
class SwapData:
    total: int
    used: int
    free: int
    percent: float


@dataclass
class DiskData:
    path: str
    total: int
    used: int
    free: int
    percent: float


@dataclass
class NetworkData:
    bytes_sent: int
    bytes_recv: int
    upload_speed: float
    download_speed: float


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


@dataclass
class SystemSnapshot:
    timestamp: str
    hostname: str
    os_name: str
    uptime_seconds: float
    cpu: CPUData
    memory: MemoryData
    swap: SwapData
    disk: DiskData
    network: NetworkData
    processes: list[ProcessInfo]
    process_sort: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clamp_percent(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


class SystemCollector:
    def __init__(
        self,
        top_n: int = 5,
        sort_by: str = "cpu",
        disk_path: str | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if top_n < 1:
            raise ValueError("top_n harus bernilai minimal 1.")
        sort_by = sort_by.lower()
        if sort_by not in SORT_CHOICES:
            raise ValueError(
                f"sort_by harus salah satu dari {SORT_CHOICES}, bukan '{sort_by}'."
            )

        self.top_n = top_n
        self.sort_by = sort_by
        self.disk_path = disk_path or os.path.abspath(os.sep)
        self._clock = clock
        self._last_net: tuple[int, int, float] | None = None
        self._cpu_count = psutil.cpu_count(logical=True) or 1

        psutil.cpu_percent(interval=None, percpu=True)

    def collect_cpu(self) -> CPUData:
        per_core = [
            round(_clamp_percent(v), 1)
            for v in psutil.cpu_percent(interval=None, percpu=True)
        ]
        total = round(sum(per_core) / len(per_core), 1) if per_core else 0.0
        return CPUData(
            total_percent=total,
            per_core_percent=per_core,
            core_count=len(per_core) or self._cpu_count,
        )

    def collect_memory(self) -> MemoryData:
        vm = psutil.virtual_memory()
        return MemoryData(
            total=int(vm.total),
            used=int(vm.used),
            free=int(vm.free),
            available=int(vm.available),
            percent=round(_clamp_percent(vm.percent), 1),
        )

    def collect_swap(self) -> SwapData:
        try:
            sw = psutil.swap_memory()
        except (OSError, psutil.Error):
            return SwapData(total=0, used=0, free=0, percent=0.0)
        return SwapData(
            total=int(sw.total),
            used=int(sw.used),
            free=int(sw.free),
            percent=round(_clamp_percent(sw.percent), 1),
        )

    def collect_disk(self) -> DiskData:
        usage = psutil.disk_usage(self.disk_path)
        return DiskData(
            path=self.disk_path,
            total=int(usage.total),
            used=int(usage.used),
            free=int(usage.free),
            percent=round(_clamp_percent(usage.percent), 1),
        )

    def collect_network(self) -> NetworkData:
        counters = psutil.net_io_counters()
        if counters is None:
            return NetworkData(0, 0, 0.0, 0.0)

        now = self._clock()
        sent = int(counters.bytes_sent)
        recv = int(counters.bytes_recv)
        upload_speed = 0.0
        download_speed = 0.0

        if self._last_net is not None:
            last_sent, last_recv, last_time = self._last_net
            elapsed = now - last_time
            if elapsed > 0:
                upload_speed = max(0, sent - last_sent) / elapsed
                download_speed = max(0, recv - last_recv) / elapsed

        self._last_net = (sent, recv, now)
        return NetworkData(
            bytes_sent=sent,
            bytes_recv=recv,
            upload_speed=upload_speed,
            download_speed=download_speed,
        )

    def collect_processes(self) -> list[ProcessInfo]:
        attrs = ["pid", "name", "cpu_percent", "memory_percent"]
        processes: list[ProcessInfo] = []

        for proc in psutil.process_iter(attrs=attrs, ad_value=None):
            info = proc.info
            pid = info.get("pid")
            if pid is None or pid == 0:
                continue
            cpu = (info.get("cpu_percent") or 0.0) / self._cpu_count
            memory = info.get("memory_percent") or 0.0
            processes.append(
                ProcessInfo(
                    pid=int(pid),
                    name=str(info.get("name") or "?"),
                    cpu_percent=round(_clamp_percent(cpu), 1),
                    memory_percent=round(_clamp_percent(memory), 2),
                )
            )

        if self.sort_by == "cpu":
            processes.sort(key=lambda p: (p.cpu_percent, p.memory_percent), reverse=True)
        else:
            processes.sort(key=lambda p: (p.memory_percent, p.cpu_percent), reverse=True)

        return processes[: self.top_n]

    def collect(self) -> SystemSnapshot:
        return SystemSnapshot(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            hostname=platform.node() or "unknown",
            os_name=f"{platform.system()} {platform.release()}".strip(),
            uptime_seconds=max(0.0, time.time() - psutil.boot_time()),
            cpu=self.collect_cpu(),
            memory=self.collect_memory(),
            swap=self.collect_swap(),
            disk=self.collect_disk(),
            network=self.collect_network(),
            processes=self.collect_processes(),
            process_sort=self.sort_by,
        )

    def warm_up(self, delay: float = 0.5) -> None:
        self.collect()
        time.sleep(delay)
