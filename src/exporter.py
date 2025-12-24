# src/exporter.py
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Optional


def _safe_filename(text: str) -> str:
    return (
        text.replace("/", "-")
        .replace("\\", "-")
        .replace(":", "-")
        .replace("*", "")
        .replace("?", "")
        .replace('"', "")
        .replace("<", "")
        .replace(">", "")
        .replace("|", "-")
        .strip()
    )


def export_trend_csv(
    rows: list[tuple[int, float]],
    out_dir: str | Path,
    location: str,
    measure: str,
    metric: str,
    sex: str,
    age_group: str,
    cause: str,
    filename: Optional[str] = None,
) -> Path:
    """
    rows: [(year, value)]
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = f"trend_{_safe_filename(location)}_{_safe_filename(measure)}_{_safe_filename(metric)}.csv"

    out_path = out_dir / filename

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cause", "location", "measure", "metric", "sex", "age_group"])
        w.writerow([cause, location, measure, metric, sex, age_group])
        w.writerow([])  # blank line for readability
        w.writerow(["year", "value"])
        for year, value in rows:
            w.writerow([year, value])

    return out_path


def export_compare_csv(
    rows: list[tuple[str, float]],
    out_dir: str | Path,
    year: int,
    measure: str,
    metric: str,
    sex: str,
    age_group: str,
    cause: str,
    order: str,
    filename: Optional[str] = None,
) -> Path:
    """
    rows: [(location, value)]
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = f"compare_{year}_{_safe_filename(measure)}_{_safe_filename(metric)}_{order}.csv"

    out_path = out_dir / filename

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cause", "year", "measure", "metric", "sex", "age_group", "order"])
        w.writerow([cause, year, measure, metric, sex, age_group, order])
        w.writerow([])
        w.writerow(["location", "value"])
        for location, value in rows:
            w.writerow([location, value])

    return out_path
