from __future__ import annotations

WARNING_THRESHOLD = 70.0   #  70%   Warning (kuninG)
CRITICAL_THRESHOLD = 85.0  #  85%   Critical (merah)

_BYTE_UNITS = ("B", "KB", "MB", "GB", "TB")


def format_bytes(size: float, precision: int = 2) -> str:

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
    return f"{format_bytes(bytes_per_second, precision)}/s"


def format_uptime(seconds: float) -> str:
    total = int(max(0, seconds))
    days, remainder = divmod(total, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    if days:
        return f"{days}d {hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_status_color(percent: float) -> str:

    if percent > CRITICAL_THRESHOLD:
        return "red"
    if percent >= WARNING_THRESHOLD:
        return "yellow"
    return "green"


def get_status_label(percent: float) -> str:
    color = get_status_color(percent)
    return {"green": "Normal", "yellow": "Warning", "red": "Critical"}[color]
