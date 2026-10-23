from __future__ import annotations

from typing import Iterable


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_score(value: float) -> str:
    return f"{value:.3f}"


def humanize_label(label: str) -> str:
    return label.replace("_", " ")


def join_list(values: Iterable[str]) -> str:
    items = [value for value in values if value]
    return ", ".join(items)
