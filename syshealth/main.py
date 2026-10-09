import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer

from syshealth import __version__
from syshealth.collector import SystemCollector
from syshealth.formatter import (
    run_live_dashboard,
    snapshot_to_json,
    snapshot_to_markdown,
)

app = typer.Typer(
    add_completion=False,
    help="syshealth-cli: pantau kesehatan sistem (CPU, RAM, Disk, Network, Proses) "
    "langsung dari terminalk",
)


class ExportFormat(str, Enum):
    json = "json"
    md = "md"


class SortBy(str, Enum):
    cpu = "cpu"
    memory = "memory"


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"syshealth-cli {__version__}")
        raise typer.Exit()


@app.command()
def main(
    interval: Annotated[
        float,
        typer.Option(
            "--interval",
            "-i",
            min=0.5,
            help="refresh dashboard dalam detik (minimal 0.5).",
        ),
    ] = 2.0,
    top: Annotated[
        int,
        typer.Option(
            "--top",
            "-t",
            min=1,
            max=50,
            help="Jumlah proses ter atas yang ditampilkan.",
        ),
    ] = 10,
    sort: Annotated[
        SortBy,
        typer.Option("--sort", "-s", help="Urutkan proses berdasarkan cpu atau memory."),
    ] = SortBy.cpu,
    export: Annotated[
        Optional[ExportFormat],
        typer.Option(
            "--export",
            "-e",
            help="Simpan snapshot metrik ke file (json/ md) tanpa masuk mode Live.",
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            dir_okay=False,
            help="Path file hasil ekspor. Default: syshealth_snapshot_<waktu>. <format>",
        ),
    ] = None,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            callback=_version_callback,
            is_eager=True,
            help="Tampilkan versi lalu keluar.",
        ),
    ] = None,
) -> None:
    collector = SystemCollector(top_n=top, sort_by=sort.value)

    if export is not None:
        # Mode snapshot: ambil dua sampel agar CPU & jaringan akurat.
        collector.warm_up(delay=1.0)
        snapshot = collector.collect()
        content = (
            snapshot_to_json(snapshot)
            if export == ExportFormat.json
            else snapshot_to_markdown(snapshot)
        )

        if output is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = Path(f"syshealth_snapshot_{stamp}.{export.value}")

        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content, encoding="utf-8")
        except OSError as exc:
            typer.secho(f"Gagal menyimpan file: {exc}", err=True, fg=typer.colors.RED)
            raise typer.Exit(code=1) from exc

        typer.secho(f"Snapshot disimpan: {output.resolve()}", fg=typer.colors.GREEN)
        raise typer.Exit()

    if not sys.stdout.isatty():
        typer.secho(
            "Live dashboard membutuhkan terminal interaktif. "
            "Gunakan --export json|md untuk output non-interaktif.",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    run_live_dashboard(collector, interval)


if __name__ == "__main__":
    app()
