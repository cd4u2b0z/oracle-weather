"""Sparkline renderer — turns a list of numbers into a compact visual trend."""

BARS = "▁▂▃▄▅▆▇█"


def sparkline(values: list, width: int = 0) -> str:
    """Render a sparkline string from a list of numeric values.

    Args:
        values: List of numbers.
        width: If >0, resample values to fit this width.

    Returns:
        A string of block characters representing the trend.
    """
    if not values:
        return ""

    # Resample if width specified and we have more data than width
    if width > 0 and len(values) > width:
        step = len(values) / width
        values = [values[int(i * step)] for i in range(width)]

    lo = min(values)
    hi = max(values)
    span = hi - lo

    if span == 0:
        return BARS[3] * len(values)  # flat line, mid-height

    result = []
    for v in values:
        idx = int((v - lo) / span * (len(BARS) - 1))
        idx = max(0, min(idx, len(BARS) - 1))
        result.append(BARS[idx])

    return "".join(result)


def sparkline_with_range(values: list, label: str = "", width: int = 20) -> str:
    """Render a sparkline with min/max annotation.

    Example: 'Temp ▁▂▃▅▇█▆▃ 55-82°F'
    """
    if not values:
        return f"{label} (no data)"

    spark = sparkline(values, width=width)
    lo = min(values)
    hi = max(values)

    if label:
        return f"{label} {spark} {lo:.0f}-{hi:.0f}"
    return f"{spark} {lo:.0f}-{hi:.0f}"
