from __future__ import annotations

import json
import math
import time
from typing import Optional

from rich import box
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from syshealth import __version__
from syshealth.collector import SystemCollector, SystemSnapshot
from syshealth.utils import (
    format_bytes,
    format_speed,
    format_uptime,
    get_status_color,
    get_status_label,
)


def _metric_bar(label: str, percent: float, detail: str):
    color = get_status_color(percent)
    progress = Progress(
        TextColumn("[bold]{task.description:<5}"),
        BarColumn(
            bar_width=None,
            style="grey23",
            complete_style=color,
            finished_style=color,
        ),
        TextColumn("{task.percentage:>5.1f}%", style=f"bold {color}"),
        TextColumn("{task.fields[detail]}", style="dim"),
        expand=True,
    )
    progress.add_task(label, total=100, completed=percent, detail=detail)
    return progress.get_renderable()


def build_header(snapshot: SystemSnapshot) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="right", ratio=1)
    grid.add_row(
        Text(f"SysHealth CLI v{__version__}", style="bold cyan"),
        Text(f"{snapshot.hostname} · {snapshot.os_name}", style="bold"),
        Text(
            f"Uptime {format_uptime(snapshot.uptime_seconds)} · "
            f"{snapshot.timestamp.replace('T', ' ')}",
            style="dim",
        ),
    )
    return Panel(grid, box=box.ROUNDED, border_style="cyan")


def build_metrics_panel(snapshot: SystemSnapshot) -> Panel:
    cpu, mem, swap, disk = snapshot.cpu, snapshot.memory, snapshot.swap, snapshot.disk

    swap_detail = (
        f"{format_bytes(swap.used)} / {format_bytes(swap.total)}"
        if swap.total > 0
        else "tidak aktif"
    )
    bars = Group(
        _metric_bar("CPU", cpu.total_percent, f"{cpu.core_count} core"),
        _metric_bar(
            "RAM",
            mem.percent,
            f"{format_bytes(mem.used)} / {format_bytes(mem.total)}",
        ),
        _metric_bar("Swap", swap.percent, swap_detail),
        _metric_bar(
            "Disk",
            disk.percent,
            f"{format_bytes(disk.used)} / {format_bytes(disk.total)} ({disk.path})",
        ),
    )
    return Panel(
        bars,
        title="[bold]Metrik Utama[/bold]",
        box=box.ROUNDED,
        border_style="green",
        padding=(1, 1),
    )


def build_cores_panel(snapshot: SystemSnapshot) -> Panel:
    cores = snapshot.cpu.per_core_percent
    columns = 2 if len(cores) > 8 else 1
    rows = math.ceil(len(cores) / columns) if cores else 0

    grid = Table.grid(padding=(0, 2), expand=True)
    for _ in range(columns):
        grid.add_column(justify="right", no_wrap=True)
        grid.add_column(ratio=1)
        grid.add_column(justify="right", no_wrap=True)

    for row in range(rows):
        cells: list = []
        for col in range(columns):
            idx = row + col * rows
            if idx < len(cores):
                pct = cores[idx]
                color = get_status_color(pct)
                cells.extend(
                    [
                        Text(f"C{idx}", style="dim"),
                        ProgressBar(
                            total=100,
                            completed=pct,
                            style="grey23",
                            complete_style=color,
                            finished_style=color,
                        ),
                        Text(f"{pct:5.1f}%", style=color),
                    ]
                )
            else:
                cells.extend(["", "", ""])
        grid.add_row(*cells)

    return Panel(
        grid,
        title="[bold]CPU per Core[/bold]",
        box=box.ROUNDED,
        border_style="magenta",
    )


def build_network_panel(snapshot: SystemSnapshot) -> Panel:
    net = snapshot.network
    grid = Table.grid(padding=(0, 2), expand=True)
    grid.add_column(justify="left", no_wrap=True)
    grid.add_column(justify="right", no_wrap=True)
    grid.add_row(
        Text("↑ Upload", style="bold green"),
        Text(format_speed(net.upload_speed), style="green"),
    )
    grid.add_row(
        Text("↓ Download", style="bold cyan"),
        Text(format_speed(net.download_speed), style="cyan"),
    )
    grid.add_row(Text("Total terkirim", style="dim"), Text(format_bytes(net.bytes_sent)))
    grid.add_row(Text("Total diterima", style="dim"), Text(format_bytes(net.bytes_recv)))
    return Panel(
        grid,
        title="[bold]Network I/O[/bold]",
        box=box.ROUNDED,
        border_style="blue",
        padding=(1, 1),
    )


def build_process_table(snapshot: SystemSnapshot) -> Panel:
    table = Table(box=box.SIMPLE_HEAD, expand=True, header_style="bold")
    table.add_column("PID", justify="right", no_wrap=True)
    table.add_column("Name", overflow="ellipsis", no_wrap=True, ratio=1)
    table.add_column("CPU %", justify="right", no_wrap=True)
    table.add_column("MEM %", justify="right", no_wrap=True)

    for proc in snapshot.processes:
        table.add_row(
            str(proc.pid),
            Text(proc.name),  # Text agar karakter '[' pada nama proses aman
            Text(f"{proc.cpu_percent:.1f}", style=get_status_color(proc.cpu_percent)),
            Text(f"{proc.memory_percent:.1f}", style=get_status_color(proc.memory_percent)),
        )

    sort_label = "CPU" if snapshot.process_sort == "cpu" else "RAM"
    return Panel(
        table,
        title=f"[bold]Top {len(snapshot.processes)} Proses (urut: {sort_label})[/bold]",
        box=box.ROUNDED,
        border_style="yellow",
    )


def render_dashboard(snapshot: SystemSnapshot, interval: Optional[float] = None) -> Layout:
    layout = Layout(name="root")
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=1),
    )
    layout["body"].split_row(
        Layout(name="left", ratio=3),
        Layout(name="right", ratio=2),
    )
    layout["left"].split_column(
        Layout(name="metrics", size=8),
        Layout(name="processes"),
    )
    layout["right"].split_column(
        Layout(name="network", size=8),
        Layout(name="cores"),
    )

    footer_text = " Tekan Ctrl+C untuk keluar"
    if interval is not None:
        footer_text += f" · refresh tiap {interval:g}s"

    layout["header"].update(build_header(snapshot))
    layout["metrics"].update(build_metrics_panel(snapshot))
    layout["processes"].update(build_process_table(snapshot))
    layout["network"].update(build_network_panel(snapshot))
    layout["cores"].update(build_cores_panel(snapshot))
    layout["footer"].update(Text(footer_text, style="dim"))
    return layout


def run_live_dashboard(
    collector: SystemCollector,
    interval: float,
    console: Optional[Console] = None,
) -> None:
    console = console or Console()
    collector.warm_up()

    try:
        with Live(
            render_dashboard(collector.collect(), interval),
            console=console,
            screen=True,
            auto_refresh=False,
        ) as live:
            while True:
                time.sleep(interval)
                live.update(
                    render_dashboard(collector.collect(), interval),
                    refresh=True,
                )
    except KeyboardInterrupt:
        pass


def snapshot_to_json(snapshot: SystemSnapshot) -> str:
    """Serialisasi snapshot ke string JSON."""
    return json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False)


def snapshot_to_markdown(snapshot: SystemSnapshot) -> str:
    """Serialisasi snapshot ke laporan Markdown."""
    cpu, mem, swap, disk, net = (
        snapshot.cpu,
        snapshot.memory,
        snapshot.swap,
        snapshot.disk,
        snapshot.network,
    )
    swap_detail = (
        f"{format_bytes(swap.used)} / {format_bytes(swap.total)}"
        if swap.total > 0
        else "tidak aktif"
    )
    sort_label = "CPU" if snapshot.process_sort == "cpu" else "RAM"

    lines = [
        "# SysHealth Snapshot",
        "",
        f"- **Host:** {snapshot.hostname}",
        f"- **OS:** {snapshot.os_name}",
        f"- **Waktu:** {snapshot.timestamp.replace('T', ' ')}",
        f"- **Uptime:** {format_uptime(snapshot.uptime_seconds)}",
        "",
        "## Ringkasan Metrik",
        "",
        "| Metrik | Penggunaan | Detail | Status |",
        "|--------|-----------:|--------|--------|",
        f"| CPU | {cpu.total_percent:.1f}% | {cpu.core_count} core | {get_status_label(cpu.total_percent)} |",
        f"| RAM | {mem.percent:.1f}% | {format_bytes(mem.used)} / {format_bytes(mem.total)} "
        f"(available {format_bytes(mem.available)}) | {get_status_label(mem.percent)} |",
        f"| Swap | {swap.percent:.1f}% | {swap_detail} | {get_status_label(swap.percent)} |",
        f"| Disk ({disk.path}) | {disk.percent:.1f}% | {format_bytes(disk.used)} / "
        f"{format_bytes(disk.total)} (free {format_bytes(disk.free)}) | {get_status_label(disk.percent)} |",
        "",
        "## CPU per Core",
        "",
        "| Core | Penggunaan |",
        "|-----:|-----------:|",
    ]
    for idx, pct in enumerate(cpu.per_core_percent):
        lines.append(f"| {idx} | {pct:.1f}% |")

    lines += [
        "",
        "## Network I/O",
        "",
        "| Item | Nilai |",
        "|------|------:|",
        f"| Upload | {format_speed(net.upload_speed)} |",
        f"| Download | {format_speed(net.download_speed)} |",
        f"| Total terkirim | {format_bytes(net.bytes_sent)} |",
        f"| Total diterima | {format_bytes(net.bytes_recv)} |",
        "",
        f"## Top {len(snapshot.processes)} Proses (urut: {sort_label})",
        "",
        "| PID | Name | CPU % | Memory % |",
        "|----:|------|------:|---------:|",
    ]
    for proc in snapshot.processes:
        safe_name = proc.name.replace("|", "\\|")
        lines.append(
            f"| {proc.pid} | {safe_name} | {proc.cpu_percent:.1f} | {proc.memory_percent:.2f} |"
        )

    return "\n".join(lines) + "\n"
