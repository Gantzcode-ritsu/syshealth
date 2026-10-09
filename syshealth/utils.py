"""Fungsi bantu (helper) untuk syshealth-cli."""

from __future__ import annotations

# Ambang batas persentase penggunaan resource.
WARNING_THRESHOLD = 70.0   # >= 70%  -> Warning (kuning)
CRITICAL_THRESHOLD = 85.0  # >  85%  -> Critical (merah)

_BYTE_UNITS = ("B", "KB", "MB", "GB", "TB")


def format_bytes(size: float, precision: int = 2) -> str:
    """Ubah ukuran byte menjadi format yang mudah dibaca manusia.

    Menggunakan basis 1024 dan satuan B, KB, MB, GB, TB.
    Nilai di atas TB tetap dinyatakan dalam TB.

    >>> format_bytes(1536)
    '1.50 KB'
    """
    if size < 0:
        raise ValueError("Ukuran byte tidak boleh negatif.")
    if precision < 0:
        raise ValueError("Precision tidak boleh negatif.")

    value = float(size)
    index = 0
    while value >= 1024 and index < len(_BYTE_UNITS) - 1:
        value /= 1024
        index += 1

    if index == 0:
        return f"{int(value)} B"
    return f"{value:.{precision}f} {_BYTE_UNITS[index]}"


def format_speed(bytes_per_second: float, precision: int = 2) -> str:
    """Ubah kecepatan (byte/detik) menjadi teks seperti '1.20 MB/s'."""
    return f"{format_bytes(bytes_per_second, precision)}/s"


def format_uptime(seconds: float) -> str:
    """Ubah detik menjadi teks uptime, misalnya '1d 01:01:01' atau '01:01:01'."""
    total = int(max(0, seconds))
    days, remainder = divmod(total, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    if days:
        return f"{days}d {hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_status_color(percent: float) -> str:
    """Tentukan warna berdasarkan persentase penggunaan.

    - Normal   : < 70%     -> green
    - Warning  : 70 - 85%  -> yellow
    - Critical : > 85%     -> red
    """
    if percent > CRITICAL_THRESHOLD:
        return "red"
    if percent >= WARNING_THRESHOLD:
        return "yellow"
    return "green"


def get_status_label(percent: float) -> str:
    """Tentukan label status ('Normal', 'Warning', 'Critical') dari persentase."""
    color = get_status_color(percent)
    return {"green": "Normal", "yellow": "Warning", "red": "Critical"}[color]